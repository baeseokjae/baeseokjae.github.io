import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "@sinclair/typebox";

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "sum_numbers",
    description: "Add two integers. Registered by a runtime extension; no rebuild of Pi.",
    parameters: Type.Object({ a: Type.Number(), b: Type.Number() }),
    execute: async (_id, params) => ({
      content: [{ type: "text", text: String(params.a + params.b) }],
    }),
  } as any);

  pi.registerProvider("probe-local", {
    name: "Probe Local",
    baseUrl: "http://127.0.0.1:9/v1",
    apiKey: "$PROBE_API_KEY",
    api: "openai-completions",
    models: [{
      type: "chat", id: "probe-mini", name: "Probe Mini", reasoning: false,
      input: ["text"], cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: 8192, maxTokens: 1024,
    }],
  });
}
