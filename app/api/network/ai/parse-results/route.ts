import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json(
    {
      error: "This legacy parse-results endpoint is retired. Use the bounded latest-result projection instead."
    },
    { status: 410 }
  );
}
