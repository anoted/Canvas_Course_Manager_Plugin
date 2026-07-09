"""Canvas visualization MCP server.

Renders course-data charts (grade distributions, progress, per-assignment
averages) as inline PNG images for Claude Desktop / Cowork / Claude Code.
It has no Canvas credentials of its own — the client fetches numbers with
the canvas server's tools and passes them here to be drawn.

Transport: stdio by default. Set MCP_TRANSPORT=streamable-http to serve
over HTTP on MCP_HOST:MCP_PORT (default 127.0.0.1:8018) instead.
"""

from __future__ import annotations

import io
import os
import sys

import matplotlib

matplotlib.use("Agg")  # headless — MCP servers have no display to attach to
import matplotlib.pyplot as plt

from mcp.server.fastmcp import FastMCP, Image

MCP_HOST = os.environ.get("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.environ.get("MCP_PORT", "8018"))

mcp = FastMCP(
    "canvas-viz",
    instructions=(
        "Inline chart rendering for Canvas course data. Fetch the numbers with "
        "the canvas server's tools (list_submissions, list_assignments, ...), "
        "then pass them here: render_grade_distribution for a histogram of "
        "scores, render_course_progress for a graded-vs-pending donut, and "
        "render_assignment_averages for a bar chart across assignments."
    ),
    host=MCP_HOST,
    port=MCP_PORT,
    streamable_http_path="/mcp",
)


def _fig_to_image() -> Image:
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    plt.close()
    buf.seek(0)
    return Image(data=buf.read(), format="png")


@mcp.tool()
def render_grade_distribution(grades: list[float], title: str = "Grade Distribution") -> Image:
    """Render a histogram of student grades and return it as an inline image.

    Pass the numeric scores for one assignment (e.g. [85, 92, 78, 90, 88]),
    typically collected from the canvas server's list_submissions tool.
    """
    if not grades:
        raise ValueError("grades is empty — pass at least one numeric score.")
    plt.figure(figsize=(8, 5))
    plt.hist(grades, bins=min(10, max(3, len(set(grades)))), color="skyblue", edgecolor="black")
    plt.title(title)
    plt.xlabel("Score")
    plt.ylabel("Number of students")
    plt.grid(axis="y", alpha=0.5)
    return _fig_to_image()


@mcp.tool()
def render_course_progress(completed: int, total: int, title: str = "Course Progress") -> Image:
    """Render a donut chart of completed vs pending items (e.g. graded vs ungraded
    submissions, or published vs draft module items)."""
    if total <= 0 or completed < 0 or completed > total:
        raise ValueError(f"need 0 <= completed <= total with total > 0, got {completed}/{total}")
    plt.figure(figsize=(6, 6))
    plt.pie(
        [completed, total - completed],
        labels=["Completed", "Pending"],
        colors=["#4CAF50", "#FFC107"],
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"width": 0.45},
    )
    plt.title(f"{title} ({completed}/{total})")
    return _fig_to_image()


@mcp.tool()
def render_assignment_averages(
    assignment_names: list[str],
    averages: list[float],
    max_points: float | None = None,
    title: str = "Average Score by Assignment",
) -> Image:
    """Render a horizontal bar chart of average scores across assignments.

    - assignment_names and averages must be the same length.
    - max_points: optional common points-possible; draws a reference line.
    """
    if not assignment_names or len(assignment_names) != len(averages):
        raise ValueError("assignment_names and averages must be non-empty and the same length.")
    plt.figure(figsize=(8, max(3, 0.6 * len(assignment_names) + 1)))
    y = range(len(assignment_names))
    plt.barh(y, averages, color="#5B8DEF", edgecolor="black")
    plt.yticks(y, assignment_names)
    plt.gca().invert_yaxis()
    plt.xlabel("Average score")
    plt.title(title)
    if max_points is not None:
        plt.axvline(max_points, color="#9E9E9E", linestyle="--", label=f"max ({max_points:g})")
        plt.legend()
    plt.grid(axis="x", alpha=0.5)
    return _fig_to_image()


if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        print(f"Canvas viz MCP server on http://{MCP_HOST}:{MCP_PORT}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
