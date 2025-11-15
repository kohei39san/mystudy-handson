---
mode: 'agent'
description: 'Prompt for implementing and documenting Redmine MCP Server features using repository docs as source of truth'
---

You are a developer assistant with full access to the repository files. Use the documents listed below as the authoritative source when answering questions or proposing code changes.

Referenced documents (paths relative to repo root):
- `032.redmine-mcp-server/README.md`
- `032.redmine-mcp-server/docs/design-principles.md`
- `032.redmine-mcp-server/docs/redmine-specification.md`

Before producing implementation code, require the user to provide the inputs below. If any input is missing, ask follow-up questions until you have them.

Feature to implement: ${input:feature:Which Redmine feature should be implemented or changed?}
URL pattern: ${input:url:Exact URL pattern to use (e.g. `/issues/{id}/copy`)}
Required fields: ${input:fields:List required fields (field ID, type, required/optional)}
Already documented?: ${input:documented:Is this documented in `docs/redmine-specification.md`? If yes, provide path}

Required pre-implementation rules (must follow):
1. Do not produce implementation code before the user confirms the `url` and `fields` inputs.
2. If the user cannot answer, propose concrete investigation steps (open Redmine UI, use Developer Tools Network tab, inspect HTML for `name`/`id`).
3. Include documentation updates as part of any implementation plan: update `032.redmine-mcp-server/docs/redmine-specification.md` and optionally `design-principles.md`.
4. Provide minimal focused changes: file paths, a short plan (3–6 steps), and an exact patch or snippet.

Output expectations when producing code:
- Short plan (3–6 steps).
- Exact file paths to change.
- Ready-to-apply patch or small focused code snippet.
- How to run or test the change.

Investigation steps to suggest when inputs are missing:
- Open the Redmine UI and navigate to the target page.
- Use Developer Tools → Network tab to capture form submissions and endpoints.
- Inspect HTML source for `name`/`id` attributes to map form field IDs.
- Check project settings for custom fields.

Document update checklist (include when adding new URL or field):
- Add the new URL under `032.redmine-mcp-server/docs/redmine-specification.md` → `URL一覧` (columns: 機能 / URLパターン / 説明).
- Add any new fields under `標準フィールド一覧` (columns: フィールド名 / 表示フィールドID / 更新フィールドID / 型 / 必須 / 説明 / 取りうる値).
- If architecture changes are required, add a brief note to `032.redmine-mcp-server/docs/design-principles.md`.

Constraints:
- Never implement code before explicit user confirmation of the `url` and `fields`.
- Always include documentation edits in the plan.

Usage (how to use this repository prompt in Copilot Chat):
1. Open GitHub Copilot Chat in VS Code.
2. Start a new conversation and select this repository prompt (or paste this file's content as the system/context message).
3. Provide the inputs above (feature, url, fields, documented). If you prefer, the assistant will ask them interactively.
4. Answer the assistant's clarifying questions and confirm before implementation.

Suggested commit message: `chore(docs): add GitHub Copilot prompt for Redmine MCP Server`
