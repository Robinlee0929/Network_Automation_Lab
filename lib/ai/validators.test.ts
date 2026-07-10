import { describe, expect, it } from "vitest";

import {
  MAX_INPUT_CHARS,
  validateAutomationKnowledgePayload,
  validateAutomationMeetingPayload,
  validateAutomationRequirementPayload,
  validateKnowledgePayload,
  validateMeetingPayload,
  validateRequiredText,
  validateRequirementPayload,
} from "./validators";

describe("validateRequiredText", () => {
  it.each([undefined, null, 0, false, {}, []])("rejects non-string input %#", (value) => {
    expect(validateRequiredText(value, "欄位")).toEqual({
      ok: false,
      error: "欄位不可為空。",
    });
  });

  it.each(["", "   ", "\t\n"])("rejects empty or whitespace-only text %#", (value) => {
    expect(validateRequiredText(value, "欄位")).toEqual({
      ok: false,
      error: "欄位不可為空。",
    });
  });

  it("uses the supplied field label in the error", () => {
    expect(validateRequiredText("", "自訂欄位")).toEqual({
      ok: false,
      error: "自訂欄位不可為空。",
    });
  });

  it("accepts non-empty text", () => {
    expect(validateRequiredText("有效內容", "欄位")).toEqual({ ok: true });
  });

  it("accepts text at exactly MAX_INPUT_CHARS", () => {
    expect(validateRequiredText("a".repeat(MAX_INPUT_CHARS), "欄位")).toEqual({ ok: true });
  });

  it("rejects text above MAX_INPUT_CHARS", () => {
    expect(validateRequiredText("a".repeat(MAX_INPUT_CHARS + 1), "欄位")).toEqual({
      ok: false,
      error: `欄位不可超過 ${MAX_INPUT_CHARS.toLocaleString()} characters。`,
    });
  });

  it("returns plain success and error objects", () => {
    const success = validateRequiredText("有效內容", "欄位");
    const error = validateRequiredText("", "欄位");

    expect(Object.getPrototypeOf(success)).toBe(Object.prototype);
    expect(Object.getPrototypeOf(error)).toBe(Object.prototype);
  });
});

describe("validateMeetingPayload", () => {
  it.each([undefined, null, "not-an-object"])("rejects a missing or non-object body %#", (body) => {
    expect(validateMeetingPayload(body)).toEqual({ ok: false, error: "請提供會議內容。" });
  });

  it("delegates validation to content with the meeting-content label", () => {
    expect(validateMeetingPayload({ content: "" })).toEqual({
      ok: false,
      error: "會議內容不可為空。",
    });
  });

  it("accepts a valid content payload", () => {
    expect(validateMeetingPayload({ content: "會議記錄" })).toEqual({ ok: true });
  });
});

describe("validateRequirementPayload", () => {
  it.each([undefined, null, "not-an-object"])("rejects a missing or non-object body %#", (body) => {
    expect(validateRequirementPayload(body)).toEqual({ ok: false, error: "請提供原始需求。" });
  });

  it("delegates validation to content with the requirement label", () => {
    expect(validateRequirementPayload({ content: "" })).toEqual({
      ok: false,
      error: "原始需求不可為空。",
    });
  });

  it("accepts a valid content payload", () => {
    expect(validateRequirementPayload({ content: "需求內容" })).toEqual({ ok: true });
  });
});

describe("validateKnowledgePayload", () => {
  it.each([null, "not-an-object"])("rejects a non-object body %#", (body) => {
    expect(validateKnowledgePayload(body)).toEqual({
      ok: false,
      error: "請提供文件內容與問題。",
    });
  });

  it("validates document before question", () => {
    expect(validateKnowledgePayload({ document: "", question: "" })).toEqual({
      ok: false,
      error: "文件內容不可為空。",
    });
  });

  it.each([undefined, 42])("returns the document error for invalid document %#", (document) => {
    expect(validateKnowledgePayload({ document, question: "問題" })).toEqual({
      ok: false,
      error: "文件內容不可為空。",
    });
  });

  it("returns the question error after a valid document", () => {
    expect(validateKnowledgePayload({ document: "文件", question: "" })).toEqual({
      ok: false,
      error: "使用者問題不可為空。",
    });
  });

  it("accepts a valid document and question", () => {
    expect(validateKnowledgePayload({ document: "文件", question: "問題" })).toEqual({ ok: true });
  });
});

describe("validateAutomationMeetingPayload", () => {
  it.each([undefined, null, "not-an-object"])("rejects a non-object body %#", (body) => {
    expect(validateAutomationMeetingPayload(body)).toEqual({
      ok: false,
      error: "請提供 meetingText。",
    });
  });

  it("validates only the meetingText field boundary", () => {
    expect(validateAutomationMeetingPayload({ content: "ignored" })).toEqual({
      ok: false,
      error: "meetingText不可為空。",
    });
  });

  it("accepts a valid meetingText payload", () => {
    expect(validateAutomationMeetingPayload({ meetingText: "會議內容" })).toEqual({ ok: true });
  });
});

describe("validateAutomationRequirementPayload", () => {
  it.each([undefined, null, "not-an-object"])("rejects a non-object body %#", (body) => {
    expect(validateAutomationRequirementPayload(body)).toEqual({
      ok: false,
      error: "請提供 requirementText。",
    });
  });

  it("validates only the requirementText field boundary", () => {
    expect(validateAutomationRequirementPayload({ content: "ignored" })).toEqual({
      ok: false,
      error: "requirementText不可為空。",
    });
  });

  it("accepts a valid requirementText payload", () => {
    expect(validateAutomationRequirementPayload({ requirementText: "需求內容" })).toEqual({
      ok: true,
    });
  });
});

describe("validateAutomationKnowledgePayload", () => {
  it.each([undefined, null, "not-an-object"])("rejects a non-object body %#", (body) => {
    expect(validateAutomationKnowledgePayload(body)).toEqual({
      ok: false,
      error: "請提供 documentText 與 question。",
    });
  });

  it("validates documentText before question", () => {
    expect(validateAutomationKnowledgePayload({ documentText: "", question: "" })).toEqual({
      ok: false,
      error: "documentText不可為空。",
    });
  });

  it("returns the question error after a valid documentText", () => {
    expect(validateAutomationKnowledgePayload({ documentText: "文件", question: "" })).toEqual({
      ok: false,
      error: "question不可為空。",
    });
  });

  it("accepts a valid documentText and question", () => {
    expect(validateAutomationKnowledgePayload({ documentText: "文件", question: "問題" })).toEqual({
      ok: true,
    });
  });
});
