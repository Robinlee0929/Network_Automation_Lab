export const LEGACY_AI_PROVIDER_DISABLED_MESSAGE =
  "Legacy AI provider features are disabled. Set LEGACY_AI_PROVIDER_ENABLED=1 for intentional local use.";

export class LegacyAiProviderDisabledError extends Error {
  constructor() {
    super(LEGACY_AI_PROVIDER_DISABLED_MESSAGE);
    this.name = "LegacyAiProviderDisabledError";
  }
}

export function isLegacyAiProviderEnabled() {
  return process.env.LEGACY_AI_PROVIDER_ENABLED?.trim() === "1";
}

export function assertLegacyAiProviderEnabled() {
  if (!isLegacyAiProviderEnabled()) {
    throw new LegacyAiProviderDisabledError();
  }
}
