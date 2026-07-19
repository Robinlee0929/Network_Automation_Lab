"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/network/day-results", label: "Evidence" },
  { href: "/network/ai-actions", label: "AI Actions" },
  { href: "/network/reports", label: "Reports" },
  { href: "/network/jobs", label: "Jobs" }
];

export function NetworkNav() {
  const pathname = usePathname();

  return (
    <nav className="network-nav" aria-label="Network automation sections">
      <p className="network-nav-label">Secondary Stage 0 surface · report-only / demo-only</p>
      <ul className="network-nav-list">
        {links.map((link) => {
          const isCurrent = pathname === link.href;

          return (
            <li key={link.href}>
              <Link aria-current={isCurrent ? "page" : undefined} href={link.href}>
                <span>{link.label}</span>
                {isCurrent ? <span className="network-current-marker">Current section</span> : null}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
