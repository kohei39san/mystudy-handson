---
on:
  pull_request:
    types: [opened, reopened, synchronize]

permissions:
  contents: read
  pull-requests: read
  issues: read

# Agentic workflow runs with constrained tools and explicit safe outputs.
# Keep write operations limited and reviewable.
safe-outputs:
  add-labels:
    max: 2
    allowed: [ feature, fix, bug, major, minor, patch ]
  remove-labels:
    max: 2
  add-comment:
    max: 1

tools:
  github:
    lockdown: true
    github-token: ${{ secrets.PAT }}
    mode: remote
    toolsets:
      - pull_requests
      - repos
      - issues
      - labels
---
# Agentic PR Auto Labeler

Objective:
- Analyze the pull request context and automatically apply the most relevant labels.
- Target pull request: #${{ github.event.pull_request.number }}

Repository policy:
- Use only labels listed in `safe-outputs.add-labels.allowed`.
- Apply at most 1 label from the impact scope category and at most 1 label from the version category (2 labels maximum in total).
- Prioritize precision over recall.
- Do not create new labels.
- After applying labels, post a comment in Japanese on the pull request explaining the reason for the label selection.

Label categories:

Impact scope (影響範囲) — choose at most 1:
- `feature`: new capability additions.
- `fix`: corrective changes, including specification adjustments and minor defect fixes.
- `bug`: fixes of user-visible and reproducible defects.

Version (バージョン) — choose at most 1:
- `major`: breaking changes that are incompatible with previous versions.
- `minor`: new backward-compatible features.
- `patch`: backward-compatible bug fixes.

Decision rules:
1. Use PR title and body first, then changed file paths and diff summary.
2. Select at most 1 label from the impact scope category (feature / fix / bug).
3. Select at most 1 label from the version category (major / minor / patch).

Execution steps:
1. Read PR metadata (number, title, body, author, base/head).
2. Read changed file list.
3. Inspect patch summaries to infer intent.
4. Choose at most 1 impact scope label and at most 1 version label from the allow-list.
5. Emit safe output to add labels.
6. Post a comment in Japanese on the pull request summarising which labels were applied and why.

Output contract:
- Return strict JSON-compatible structure:
  - labels: string[]
  - reason: string (Japanese, posted as a PR comment)
- `labels` must contain only allowed labels.
- Maximum 1 label per category.

Failure handling:
- If confidence is low, apply no labels.
- Never apply labels outside the allow-list.
