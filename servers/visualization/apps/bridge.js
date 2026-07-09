/* MCP Apps bridge — JSON-RPC over postMessage between this iframe (the "view")
 * and the MCP host (e.g. Claude Desktop). Implements the MCP Apps spec
 * (protocol 2026-01-26): the ui/initialize handshake, tool-input/tool-result
 * notifications, tools/call from the view, size reporting, and host theming.
 * The server inlines this file into each app template at resources/read time. */
"use strict";
window.MCPApp = (function () {
  var PROTOCOL = "2026-01-26";
  var nextId = 1;
  var pending = new Map();
  var handlers = {};
  var hostContext = {};

  function post(msg) { window.parent.postMessage(msg, "*"); }

  function request(method, params, timeoutMs) {
    return new Promise(function (resolve, reject) {
      var id = nextId++;
      var timer = timeoutMs
        ? setTimeout(function () {
            pending.delete(id);
            reject(new Error(method + " timed out"));
          }, timeoutMs)
        : null;
      pending.set(id, { resolve: resolve, reject: reject, timer: timer });
      post({ jsonrpc: "2.0", id: id, method: method, params: params || {} });
    });
  }

  function notify(method, params) {
    post({ jsonrpc: "2.0", method: method, params: params || {} });
  }

  function applyHostContext(ctx) {
    if (!ctx) return;
    Object.assign(hostContext, ctx);
    if (ctx.theme) document.documentElement.dataset.theme = ctx.theme;
    var vars = ctx.styles && ctx.styles.variables;
    if (vars) {
      Object.keys(vars).forEach(function (k) {
        try { document.documentElement.style.setProperty(k, String(vars[k])); } catch (e) { /* ignore bad var */ }
      });
    }
    if (handlers.onHostContextChanged) handlers.onHostContextChanged(hostContext);
  }

  window.addEventListener("message", function (ev) {
    var m = ev.data;
    if (!m || m.jsonrpc !== "2.0") return;
    if (m.id !== undefined && m.method === undefined) { // response to one of our requests
      var p = pending.get(m.id);
      if (!p) return;
      pending.delete(m.id);
      if (p.timer) clearTimeout(p.timer);
      if (m.error) p.reject(new Error((m.error && m.error.message) || "host error"));
      else p.resolve(m.result);
      return;
    }
    switch (m.method) {
      case "ui/notifications/tool-input":
        if (handlers.onToolInput) handlers.onToolInput(m.params || {});
        break;
      case "ui/notifications/tool-result":
        if (handlers.onToolResult) handlers.onToolResult(m.params || {});
        break;
      case "ui/notifications/host-context-changed":
        applyHostContext(m.params || {});
        break;
      case "ui/resource-teardown": // host is about to remove the view — ack so it proceeds
      case "ping":
        if (m.id !== undefined) post({ jsonrpc: "2.0", id: m.id, result: {} });
        break;
      default:
        if (m.id !== undefined) {
          post({ jsonrpc: "2.0", id: m.id, error: { code: -32601, message: "method not found: " + m.method } });
        }
    }
  });

  var sizeScheduled = false;
  function reportSize() {
    if (sizeScheduled) return;
    sizeScheduled = true;
    requestAnimationFrame(function () {
      sizeScheduled = false;
      notify("ui/notifications/size-changed", {
        width: Math.ceil(document.documentElement.scrollWidth),
        height: Math.ceil(document.documentElement.scrollHeight)
      });
    });
  }

  function connect(appInfo, h) {
    handlers = h || {};
    if (!document.documentElement.dataset.theme) { // fallback until the host says otherwise
      var dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      document.documentElement.dataset.theme = dark ? "dark" : "light";
    }
    return request("ui/initialize", {
      protocolVersion: PROTOCOL,
      capabilities: {},
      clientInfo: appInfo || { name: "canvas-app", version: "1.0.0" }
    }, 3000).then(function (res) {
      applyHostContext((res && res.hostContext) || {});
      notify("ui/notifications/initialized", {});
      return hostContext;
    }).catch(function () {
      return hostContext; // standalone/dev render (no host) — still show the UI
    }).then(function (ctx) {
      if (window.ResizeObserver) new ResizeObserver(reportSize).observe(document.body);
      reportSize();
      return ctx;
    });
  }

  function callTool(name, args) {
    return request("tools/call", { name: name, arguments: args || {} }).then(function (res) {
      if (res && res.isError) {
        var msg = "tool call failed";
        (res.content || []).forEach(function (c) { if (c.type === "text" && c.text) msg = c.text; });
        throw new Error(msg);
      }
      return res || {};
    });
  }

  /* Extract usable data from a tool result: prefer structuredContent (FastMCP
   * wraps non-dict returns as {"result": ...} — unwrap that), else parse the
   * text content as JSON, else return the raw text. */
  function dataOf(res) {
    var sc = res && res.structuredContent;
    if (sc && typeof sc === "object" && "result" in sc && Object.keys(sc).length === 1) return sc.result;
    if (sc !== undefined && sc !== null) return sc;
    var texts = [];
    ((res && res.content) || []).forEach(function (c) { if (c.type === "text" && c.text) texts.push(c.text); });
    var t = texts.join("\n");
    try { return JSON.parse(t); } catch (e) { return t; }
  }

  function openLink(url) {
    return request("ui/open-link", { url: url }).catch(function () { /* host may decline */ });
  }

  return {
    connect: connect,
    callTool: callTool,
    dataOf: dataOf,
    openLink: openLink,
    notify: notify,
    request: request,
    reportSize: reportSize,
    host: function () { return hostContext; }
  };
})();
