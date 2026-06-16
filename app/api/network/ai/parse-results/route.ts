import { NextResponse } from "next/server";
import { listParseResultRecords } from "@/lib/network-ai/parseResultStore";

export async function GET() {
  return NextResponse.json({ parseResults: listParseResultRecords() });
}
