import { NextResponse } from "next/server";
import { getLatestParseResultRecord } from "@/lib/network-ai/parseResultStore";

export async function GET() {
  return NextResponse.json({ parseResult: getLatestParseResultRecord() });
}
