import { FileText } from "lucide-react";
import { createElement } from "react";
import type { DayResult, DayResultKind } from "@/lib/network-ai/schemas";

const reportCategoryLabels: Record<DayResultKind, string> = {
  device_report: "Device Check Report",
  phase_gate_report: "Readiness Gate Review",
  summary_report: "Project Summary",
  test_report: "Test Evidence",
  unknown: "Uncategorized Evidence"
};

function reportStatus(status: string) {
  const normalized = status.trim().toLowerCase();
  if (normalized.includes("pass") || normalized.includes("success") || normalized === "ok") {
    return "PASS";
  }
  if (normalized.includes("warn")) {
    return "WARN";
  }
  if (normalized.includes("fail")) {
    return "FAIL";
  }
  if (normalized.includes("block")) {
    return "BLOCKED";
  }
  if (normalized.includes("review")) {
    return "REVIEW";
  }
  return "UNKNOWN";
}

function sourceDayLabel(sourceDay: string | null) {
  const match = sourceDay?.match(/^day\s*[-_]?(\d{1,3})$/i);
  return match ? `Day ${Number(match[1])}` : "Unspecified day";
}

function creationDate(createdAt: string) {
  const timestamp = Date.parse(createdAt);
  if (!Number.isFinite(timestamp)) {
    return "Unknown date";
  }
  return new Date(timestamp).toISOString().slice(0, 10);
}

export function ReportsClient({ reports }: { reports: DayResult[] }) {
  const content = reports.length
    ? createElement(
        "div",
        { className: "result-list" },
        reports.map((report) =>
          createElement(
            "article",
            { className: "result-row", key: report.id },
            createElement(FileText, { "aria-hidden": true, size: 18 }),
            createElement(
              "span",
              null,
              createElement("strong", null, reportCategoryLabels[report.resultKind]),
              createElement("small", null, sourceDayLabel(report.sourceDay))
            ),
            createElement("em", null, creationDate(report.createdAt)),
            createElement("b", null, reportStatus(report.status))
          )
        )
      )
    : createElement(
        "div",
        { className: "status-strip", role: "status" },
        "No report evidence is currently available. This page is working, and no external service or device operation is required."
      );

  return createElement(
    "div",
    { className: "network-grid" },
    createElement(
      "section",
      { className: "network-panel network-panel-wide" },
      createElement(
        "div",
        { className: "network-toolbar" },
        createElement("h2", null, "Report Collection"),
        createElement(
          "span",
          null,
          `${reports.length} report${reports.length === 1 ? "" : "s"}`
        )
      ),
      content
    )
  );
}
