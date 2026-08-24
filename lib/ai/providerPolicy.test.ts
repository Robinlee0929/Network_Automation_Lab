import { afterEach, describe, expect, it } from "vitest";
import {
  LegacyAiProviderDisabledError,
  assertLegacyAiProviderEnabled,
  isLegacyAiProviderEnabled
} from "./providerPolicy";

const originalLegacyProviderFlag = process.env.LEGACY_AI_PROVIDER_ENABLED;

afterEach(() => {
  if (originalLegacyProviderFlag === undefined) {
    delete process.env.LEGACY_AI_PROVIDER_ENABLED;
  } else {
    process.env.LEGACY_AI_PROVIDER_ENABLED = originalLegacyProviderFlag;
  }
});

describe("legacy AI provider policy", () => {
  it.each([undefined, "", "   ", "0", "true", "yes", " 0 ", "unexpected"])(
    "fails closed for %s",
    (value) => {
      if (value === undefined) {
        delete process.env.LEGACY_AI_PROVIDER_ENABLED;
      } else {
        process.env.LEGACY_AI_PROVIDER_ENABLED = value;
      }

      expect(isLegacyAiProviderEnabled()).toBe(false);
      expect(() => assertLegacyAiProviderEnabled()).toThrow(LegacyAiProviderDisabledError);
    }
  );

  it.each(["1", " 1 "])("allows exact trimmed opt-in %s", (value) => {
    process.env.LEGACY_AI_PROVIDER_ENABLED = value;

    expect(isLegacyAiProviderEnabled()).toBe(true);
    expect(() => assertLegacyAiProviderEnabled()).not.toThrow();
  });
});
