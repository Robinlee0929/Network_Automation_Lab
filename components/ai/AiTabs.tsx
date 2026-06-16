"use client";

import { ClipboardList, FileQuestion, FileText } from "lucide-react";
import { useState } from "react";
import { KnowledgeQaForm } from "./KnowledgeQaForm";
import { MeetingSummaryForm } from "./MeetingSummaryForm";
import { RequirementAnalysisForm } from "./RequirementAnalysisForm";

const tabs = [
  {
    id: "meeting",
    label: "會議摘要",
    icon: FileText
  },
  {
    id: "requirements",
    label: "需求整理",
    icon: ClipboardList
  },
  {
    id: "knowledge",
    label: "知識庫問答",
    icon: FileQuestion
  }
] as const;

type TabId = (typeof tabs)[number]["id"];

export function AiTabs() {
  const [activeTab, setActiveTab] = useState<TabId>("meeting");

  return (
    <section className="ai-workbench" aria-label="AI Project Assistant tools">
      <div className="tab-list" role="tablist" aria-label="AI 功能">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              aria-controls={`${tab.id}-panel`}
              aria-selected={activeTab === tab.id}
              className="tab-button"
              id={`${tab.id}-tab`}
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              role="tab"
              type="button"
            >
              <Icon aria-hidden="true" size={18} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {activeTab === "meeting" && (
        <div aria-labelledby="meeting-tab" id="meeting-panel" role="tabpanel">
          <MeetingSummaryForm />
        </div>
      )}
      {activeTab === "requirements" && (
        <div aria-labelledby="requirements-tab" id="requirements-panel" role="tabpanel">
          <RequirementAnalysisForm />
        </div>
      )}
      {activeTab === "knowledge" && (
        <div aria-labelledby="knowledge-tab" id="knowledge-panel" role="tabpanel">
          <KnowledgeQaForm />
        </div>
      )}
    </section>
  );
}
