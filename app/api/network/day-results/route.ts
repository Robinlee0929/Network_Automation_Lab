import { NextResponse } from "next/server";
import { importDayResults } from "@/lib/network-ai/dayResults";

export async function GET() {
  return NextResponse.json({ results: importDayResults() });
}
