import { NextResponse } from "next/server";
import { getAvailableActions } from "@/lib/network-ai/actions";

export async function GET() {
  return NextResponse.json({ actions: getAvailableActions() });
}
