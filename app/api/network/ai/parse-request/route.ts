import { NextResponse } from "next/server";
import { aiError, validationError } from "@/lib/ai/routeHandler";
import { parseNetworkRequestWithAi } from "@/lib/network-ai/aiNode";
import {
  createParseResultRecord,
  selectParseResultPresentationFields
} from "@/lib/network-ai/parseResultStore";
import {
  LOCAL_DEMO_DEVICE_INVENTORY,
  isNetworkAiProviderDemoEnabled,
  validateNetworkAiProviderDemoRequest
} from "@/lib/network-ai/providerDemo";

export async function POST(request: Request) {
  try {
    if (!isNetworkAiProviderDemoEnabled()) {
      return validationError(
        "Optional local AI recommendation preview is disabled."
      );
    }

    const validation = validateNetworkAiProviderDemoRequest(await request.json());
    if (!validation.ok) {
      return validationError(validation.error);
    }

    const result = await parseNetworkRequestWithAi({
      userRequest: validation.userRequest,
      deviceInventory: LOCAL_DEMO_DEVICE_INVENTORY
    });
    const parseResult = createParseResultRecord({
      userRequest: validation.userRequest,
      deviceInventory: LOCAL_DEMO_DEVICE_INVENTORY,
      output: result.output
    });

    return NextResponse.json({
      parseResult: selectParseResultPresentationFields(parseResult)
    });
  } catch (error) {
    return aiError(error);
  }
}
