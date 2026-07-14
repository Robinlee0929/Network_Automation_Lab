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
      <span className="eyebrow">Secondary Stage 0 surface · report-only / demo-only</span>
      {links.map((link) => (
        <Link aria-current={pathname === link.href ? "page" : undefined} href={link.href} key={link.href}>
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
