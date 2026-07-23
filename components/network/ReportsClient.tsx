import { FileText } from "lucide-react";
import { createElement } from "react";
import type { DayResult } from "@/lib/network-ai/schemas";
import { projectReportsCollection } from "./Phase2O05SafePresentation";

export function ReportsClient({ reports }: { reports: DayResult[] }) {
  const collection = projectReportsCollection(reports);
  const notices = [
    createElement(
      "p",
      { className: "safe-state", "data-state": "unavailable", key: "boundary" },
      "UNAVAILABLE — report detail, source paths, device identity, and technical payload are withheld on this Stage 0 surface."
    )
  ];

  if (collection.rejectedCount > 0) {
    notices.push(
      createElement(
        "p",
        {
          className: "safe-state",
          "data-state": "rejected",
          key: "rejected",
          role: "status"
        },
        `REJECTED — ${collection.rejectedCount} recorded report${
          collection.rejectedCount === 1 ? "" : "s"
        } withheld as malformed.`
      )
    );
  }

  let content;
  if (collection.state === "AVAILABLE") {
    content = createElement(
      "div",
      { className: "safe-report-list" },
      collection.items.map((report) =>
        createElement(
          "article",
          { className: "safe-report-row", key: report.internalId },
          createElement(FileText, { "aria-hidden": true, size: 18 }),
          createElement(
            "div",
            null,
            createElement("h3", null, report.category),
            createElement("p", null, report.dayLabel)
          ),
          createElement("span", null, `Recorded: ${report.recordedDate}`),
          createElement(
            "strong",
            {
              className: "status-badge",
              "data-tone": report.statusTone
            },
            report.status
          ),
          report.malformed
            ? createElement(
                "span",
                { className: "safe-inline-state" },
                "REJECTED — malformed local evidence"
              )
            : null
        )
      )
    );
  } else if (collection.state === "EMPTY") {
    content = createElement(
      "div",
      { className: "safe-state", "data-state": "empty", role: "status" },
      "EMPTY — No report evidence is currently available. This page is working, and no external service or device operation is required."
    );
  } else {
    content = createElement(
      "div",
      { className: "safe-state", "data-state": "error", role: "alert" },
      "ERROR — no safely displayable recorded reports."
    );
  }

  return createElement(
    "div",
    { className: "network-grid" },
    createElement(
      "section",
      {
        "aria-labelledby": "report-collection-heading",
        className: "network-panel network-panel-wide"
      },
      createElement(
        "div",
        { className: "network-toolbar" },
        createElement("h2", { id: "report-collection-heading" }, "Report Collection"),
        createElement(
          "span",
          null,
          `${collection.items.length} safely displayable report${
            collection.items.length === 1 ? "" : "s"
          }`
        )
      ),
      ...notices,
      content
    )
  );
}
