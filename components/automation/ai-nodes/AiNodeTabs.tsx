"use client";

import { ClipboardList, FileQuestion, FileText } from "lucide-react";
import { useState } from "react";
import { KnowledgeQaNode } from "./KnowledgeQaNode";
import { MeetingSummaryNode } from "./MeetingSummaryNode";
import { RequirementAnalysisNode } from "./RequirementAnalysisNode";

const tabs = [
  {
    id: "meeting",
    label: "Meeting Summary Node",
    icon: FileText
  },
  {
    id: "requirements",
    label: "Requirement Analysis Node",
    icon: ClipboardList
  },
  {
    id: "knowledge",
    label: "Knowledge QA Node",
    icon: FileQuestion
  }
] as const;

type TabId = (typeof tabs)[number]["id"];

export function AiNodeTabs() {
  const [activeTab, setActiveTab] = useState<TabId>("meeting");

  return (
    <section className="ai-workbench" aria-label="Automation AI node demos">
      <div className="tab-list" role="tablist" aria-label="Automation AI Nodes">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              aria-controls={`${tab.id}-node-panel`}
              aria-selected={activeTab === tab.id}
              className="tab-button"
              id={`${tab.id}-node-tab`}
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
        <div aria-labelledby="meeting-node-tab" id="meeting-node-panel" role="tabpanel">
          <MeetingSummaryNode />
        </div>
      )}
      {activeTab === "requirements" && (
        <div aria-labelledby="requirements-node-tab" id="requirements-node-panel" role="tabpanel">
          <RequirementAnalysisNode />
        </div>
      )}
      {activeTab === "knowledge" && (
        <div aria-labelledby="knowledge-node-tab" id="knowledge-node-panel" role="tabpanel">
          <KnowledgeQaNode />
        </div>
      )}
    </section>
  );
}
