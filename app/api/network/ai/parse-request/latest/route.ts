import { NextResponse } from "next/server";
import {
  getLatestParseResultRecord,
  selectParseResultPresentationFields
} from "@/lib/network-ai/parseResultStore";

export async function GET() {
  return NextResponse.json({
    parseResult: selectParseResultPresentationFields(getLatestParseResultRecord())
  });
}
