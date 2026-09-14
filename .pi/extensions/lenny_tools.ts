import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";

async function executeViaBridgeOrCli(toolName: string, params: Record<string, any>): Promise<any> {
  const bridgePort = process.env.LENNY_TOOLS_PORT;
  if (bridgePort) {
    try {
      const response = await fetch(`http://127.0.0.1:${bridgePort}/tool`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: toolName, params }),
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (_err) {
      // Fall through to CLI fallback
    }
  }

  // CLI fallback runner
  try {
    const backendDir = resolve(process.cwd(), "backend");
    const jsonArgs = JSON.stringify(params);
    const proc = spawnSync("python", ["-m", "app.agent.tools.runner", toolName, jsonArgs], {
      cwd: backendDir,
      encoding: "utf-8",
      timeout: 15000,
    });
    if (proc.status === 0 && proc.stdout) {
      return JSON.parse(proc.stdout.trim());
    }
    return { error: proc.stderr || "CLI tool runner execution failed" };
  } catch (err: any) {
    return { error: `Failed to execute ${toolName}: ${err?.message || String(err)}` };
  }
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "search_lenny_transcripts",
    label: "Search Lenny Transcripts",
    description:
      "Search Lenny's Podcast transcripts for relevant passages, frameworks, and guest insights. " +
      "Use this tool whenever answering questions about product management, growth loops, retention, " +
      "PLG, B2B SaaS benchmarks, and startup leadership.",
    promptSnippet: "Search Lenny's Podcast transcripts for frameworks and insights",
    promptGuidelines: [
      "Use search_lenny_transcripts to retrieve empirical quotes, data, and frameworks from guests before synthesizing your answer.",
      "Always ground your reasoning in the specific guest names and episode details returned by search_lenny_transcripts.",
    ],
    parameters: Type.Object({
      query: Type.String({
        description: "The natural language search query or topic to look up in the transcripts.",
      }),
      top_k: Type.Optional(
        Type.Integer({
          description: "Number of transcript passages to retrieve (default: 3).",
        })
      ),
    }),
    async execute(_toolCallId, params) {
      const result = await executeViaBridgeOrCli("search_lenny_transcripts", params);
      return {
        content: [{ type: "text", text: typeof result === "string" ? result : JSON.stringify(result) }],
        details: result,
      };
    },
  });

  pi.registerTool({
    name: "lookup_episode_source",
    label: "Lookup Episode Source",
    description:
      "Lookup verified source metadata for an episode (episode number, guest title, source URL, " +
      "audio URL, publication date) from the database.",
    promptSnippet: "Lookup verified metadata and sources for a podcast episode",
    promptGuidelines: [
      "Use lookup_episode_source when you need verified citation links, publication dates, or episode numbers for a specific guest.",
    ],
    parameters: Type.Object({
      episode_title_or_guest: Type.String({
        description: "The title of the episode or guest name to inspect.",
      }),
    }),
    async execute(_toolCallId, params) {
      const result = await executeViaBridgeOrCli("lookup_episode_source", params);
      return {
        content: [{ type: "text", text: typeof result === "string" ? result : JSON.stringify(result) }],
        details: result,
      };
    },
  });

  pi.registerTool({
    name: "generate_ship30_essay",
    label: "Generate Ship 30 for 30 Essay",
    description:
      "Generate an approximately 1,250-word Ship 30 for 30-style essay or actionable playbook " +
      "strictly grounded in Lenny's Podcast transcript evidence. Encodes Ship 30 writing principles: " +
      "compelling hook, 1-3-1 cadence, single core idea, narrative progression, short punchy paragraphs, " +
      "skimmable subheadings, verbatim guest quotes, and an actionable takeaway.",
    promptSnippet: "Generate a ~1,250-word Ship 30 for 30 essay grounded in Lenny's Podcast transcripts",
    promptGuidelines: [
      "Use generate_ship30_essay whenever the user asks for an essay, playbook, deep-dive guide, or Ship 30/30 synthesis on a product/growth topic.",
      "Always provide the topic parameter and optionally a source_url_or_guest to anchor the essay in specific guest transcript evidence.",
    ],
    parameters: Type.Object({
      topic: Type.String({
        description: "The core product or growth topic/framework to write the essay about.",
      }),
      source_url_or_guest: Type.Optional(
        Type.String({
          description: "Optional linked episode source URL, episode title, or guest name to anchor the essay.",
        })
      ),
    }),
    async execute(_toolCallId, params) {
      const result = await executeViaBridgeOrCli("generate_ship30_essay", params);
      return {
        content: [{ type: "text", text: typeof result === "string" ? result : JSON.stringify(result) }],
        details: result,
      };
    },
  });

  pi.registerTool({
    name: "generate_artifact",
    label: "Generate Artifact",
    description:
      "Generate a structured Markdown or standalone HTML/CSS artifact (such as a PRD, strategic framework, " +
      "growth playbook, executive summary, or landing page) grounded in Lenny's Podcast transcripts. " +
      "Supports artifact_type 'markdown' or 'html'. Treats HTML as untrusted with zero external scripts.",
    promptSnippet: "Generate a structured Markdown or standalone HTML/CSS artifact grounded in transcripts",
    promptGuidelines: [
      "Use generate_artifact whenever the user asks for a PRD, spec, document, HTML landing page, or report.",
      "Specify artifact_type as 'markdown' or 'html' based on user intent.",
      "Always provide a title and topic, and optionally specific instructions or guest sources.",
    ],
    parameters: Type.Object({
      title: Type.String({
        description: "Descriptive title for the artifact.",
      }),
      topic: Type.String({
        description: "The core product, growth framework, or operational subject for the artifact.",
      }),
      artifact_type: Type.Optional(
        Type.Union([Type.Literal("markdown"), Type.Literal("html")], {
          description: "Format of the artifact: 'markdown' (default) or 'html'.",
        })
      ),
      instructions: Type.Optional(
        Type.String({
          description: "Optional specific guidelines or sections to include (e.g. 'PRD format with metrics and risks').",
        })
      ),
      source_url_or_guest: Type.Optional(
        Type.String({
          description: "Optional guest name, episode title, or linked source to prioritize for evidence.",
        })
      ),
    }),
    async execute(_toolCallId, params) {
      const result = await executeViaBridgeOrCli("generate_artifact", params);
      return {
        content: [{ type: "text", text: typeof result === "string" ? result : JSON.stringify(result) }],
        details: result,
      };
    },
  });
}


