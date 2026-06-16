import { NextResponse } from "next/server";
import { listNetworkJobs } from "@/lib/network-ai/jobs";

export async function GET() {
  return NextResponse.json({ jobs: listNetworkJobs() });
}
