import type { ReactNode } from "react";
import { NetworkNav } from "@/components/network/NetworkNav";

const canonicalFlaskUrl = "http://127.0.0.1:5000/";

const stateVocabulary = [
  ["EMPTY", "A valid collection contains zero items."],
  ["MISSING", "An expected local artifact is absent."],
  ["UNAVAILABLE", "A capability is intentionally not offered in Stage 0."],
  ["ERROR", "An existing allowed read failed."],
  ["BLOCKED", "A recorded safety result prevented an operation."]
] as const;

export default function NetworkLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <div className="network-shell">
      <a className="network-skip-link" href="#network-primary-content">
        Skip to primary network content
      </a>

      <header className="network-shell-header">
        <div className="network-shell-intro">
          <p className="eyebrow">Secondary Next.js · Stage 0</p>
          <p className="network-shell-title">Network evidence demonstration</p>
          <p className="network-shell-copy">
            The Flask dashboard is the canonical reviewer surface. This secondary Next.js surface presents
            existing local evidence without changing application responsibility.
          </p>
          <a className="network-canonical-link" href={canonicalFlaskUrl}>
            Open the canonical local Flask reviewer surface
          </a>
          <p className="network-shell-note">
            The link names the local entry point; it does not claim that the Flask server is running.
          </p>
          <p className="network-stage-boundary">
            Stage 0 capability: report-only · dry-run · mock-only · demo-only · non-executing
          </p>
        </div>

        <NetworkNav />

        <details className="network-state-vocabulary">
          <summary>Stage 0 state vocabulary</summary>
          <dl>
            {stateVocabulary.map(([term, definition]) => (
              <div key={term}>
                <dt>{term}</dt>
                <dd>{definition}</dd>
              </div>
            ))}
          </dl>
        </details>
      </header>

      <div className="network-shell-content">{children}</div>
    </div>
  );
}
