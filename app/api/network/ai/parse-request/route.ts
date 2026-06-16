import { NextResponse } from "next/server";
import { aiError, validationError } from "@/lib/ai/routeHandler";
import { parseNetworkRequestWithAi } from "@/lib/network-ai/aiNode";
import { createParseResultRecord } from "@/lib/network-ai/parseResultStore";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      userRequest?: unknown;
      deviceInventory?: unknown;
      availableActions?: unknown;
    };

    if (typeof body.userRequest !== "string" || !body.userRequest.trim()) {
      return validationError("userRequest is required.");
    }

    const result = await parseNetworkRequestWithAi({
      userRequest: body.userRequest.trim(),
      deviceInventory: body.deviceInventory,
      availableActions: body.availableActions
    });
    const parseResult = createParseResultRecord({
      userRequest: body.userRequest.trim(),
      deviceInventory: body.deviceInventory,
      output: result.output
    });

    return NextResponse.json({ parseResult });
  } catch (error) {
    return aiError(error);
  }
}
