import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Network Automation AI Node",
  description: "Structured AI node for network report analysis, action recommendation, and job creation."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
