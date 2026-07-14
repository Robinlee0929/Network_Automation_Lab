import { createElement, Fragment } from "react";

function note(strongText: string, detail: string) {
  return createElement(
    "section",
    { className: "network-panel network-panel-wide" },
    createElement(
      "div",
      { className: "status-strip", role: "note" },
      createElement("strong", null, strongText),
      detail
    )
  );
}

export function EvidenceStage0Presentation() {
  return note(
    "Stage 0 safe Demo · report-only · provider-unavailable.",
    " Provider analysis controls are not rendered on this Demo surface. Review evidence and any existing analysis record as read-only information."
  );
}

export function AiActionsStage0Presentation() {
  return createElement(
    Fragment,
    null,
    note(
      "Stage 0 safe Demo · demo-only · provider-unavailable.",
      " Provider parsing and job-creation controls are not rendered. This surface shows only the existing action catalog and any recorded parse result."
    ),
    createElement(
      "section",
      { className: "network-panel" },
      createElement(
        "div",
        { className: "network-toolbar" },
        createElement("h2", null, "Recorded Request Context"),
        createElement("span", null, "Read-only")
      ),
      createElement(
        "p",
        { className: "muted-copy" },
        "Request input is unavailable in the Stage 0 Demo. No provider request can be submitted from this page."
      )
    )
  );
}
