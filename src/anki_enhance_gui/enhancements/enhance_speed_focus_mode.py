from __future__ import annotations

from typing import Any

from aqt import gui_hooks
from aqt.reviewer import ReviewerBottomBar
from aqt.webview import WebContent


def on_webview_will_set_content(
    web_content: WebContent,
    context: ReviewerBottomBar | Any | None,
) -> None:
    if not isinstance(context, ReviewerBottomBar):
        return

    js = """\
(for (const child of document.getElementById("spdfControls").firstElementChild.childNodes) {
    if (child.id !== "spdfTime") {
        child.remove()
    }
})()
"""

    web_content.body += f"<script>{js}</script>"


def main() -> None:
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
