from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from anki.hooks import wrap
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from aqt.reviewer import ReviewerBottomBar
from aqt.utils import tr
from aqt.webview import WebContent
from bs4 import BeautifulSoup


def _get_value_by_class(soup: BeautifulSoup, cls: str) -> tuple[int, bool]:
    element = soup.find("span", class_=cls)
    assert element

    return int(element.get_text()), bool(element.find("u"))


def _remaining(self: Reviewer, _old: Callable[[Reviewer], str]) -> str:
    original = _old(self)
    soup = BeautifulSoup(original, "html.parser")

    new_count, is_new = _get_value_by_class(soup, "new-count")
    learn_count, _ = _get_value_by_class(soup, "learn-count")
    review_count, _ = _get_value_by_class(soup, "review-count")

    html = f"""\
<span id="summary-count"{' class="new-count"' if is_new else ''}>{new_count + learn_count + review_count}</span>
<span id="detail-count" style="display: none;">{original}</span>
"""  # noqa: E501

    return html


def _showAnswerButton(self: Reviewer) -> None:
    html = f"""\
<table cellpadding="0">
    <tr>
        <td class="stat2" align="center">
            <span class="stattxt" onclick='toggleRemaining();'>{self._remaining()}</span>
            <button title="{tr.actions_shortcut_key(val=tr.studying_space())}" id="ansbut" onclick='pycmd("ans");'>{tr.studying_show_answer()}</button>
        </td>
    </tr>
</table>
"""  # noqa: E501

    if self.card.should_show_timer():
        maxTime = self.card.time_limit() / 1000
    else:
        maxTime = 0

    self.bottom.web.eval(f"showQuestion({json.dumps(html)},{maxTime});")


def on_webview_will_set_content(
    web_content: WebContent,
    context: ReviewerBottomBar | Any | None,
) -> None:
    if not isinstance(context, ReviewerBottomBar):
        return

    css = """\
.stat2 {
    padding-top: 1.5px !important;
}
.stattxt {
    position: unset !important;
    top: unset !important;
    left: unset !important;
    transform: unset !important;
}
.stattxt {
    display: block !important;
}
#ansbut {
    margin-top: 2.5px !important;
}
"""

    js = """\
const toggleRemaining = () => {
  const summaryCount = document.getElementById("summary-count");
  const detailCount = document.getElementById("detail-count");

  if (summaryCount.style.display === "none") {
    summaryCount.style.display = "unset";
    detailCount.style.display = "none";
  } else {
    summaryCount.style.display = "none";
    detailCount.style.display = "unset";
  }
}
"""

    web_content.body += f"<script>{js}</script>"
    web_content.body += f"<style>{css}</style>"


def main() -> None:
    Reviewer._remaining = wrap(Reviewer._remaining, _remaining, "around")
    Reviewer._showAnswerButton = _showAnswerButton

    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
