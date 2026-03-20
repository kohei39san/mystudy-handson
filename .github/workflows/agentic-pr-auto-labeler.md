---
on:
  pull_request:
    types: [opened, reopened, synchronize]

permissions:
  contents: read
  pull-requests: write
  issues: read

# Agentic workflow runs with constrained tools and explicit safe outputs.
# Keep write operations limited and reviewable.
safe-outputs:
  add-labels:
    max: 2
    allowed: [ feature, fix, bug, major, minor, patch ]

tools:
  github:
    lockdown: true
    github-token: ${{ secrets.CUSTOM_TOKEN }}
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
- Apply at most 1 label per category (影響範囲, バージョン). Total maximum is 2 labels.
- Prioritize precision over recall.
- Do not create new labels.

Label categories:

影響範囲 (Impact Scope) — choose at most one:
- `feature`: New capability additions.
- `fix`: Corrective changes, including specification adjustments and minor defect fixes.
- `bug`: Fixes of user-visible and reproducible defects.

バージョン (Version) — choose at most one:
- `major`: Breaking changes that are incompatible with previous versions.
- `minor`: Backward-compatible new features.
- `patch`: Backward-compatible bug fixes or small corrections.

Decision rules:
1. Use PR title and body first, then changed file paths and diff summary.
2. Select at most one label from 影響範囲 if the change is classifiable; otherwise skip.
3. Select at most one label from バージョン if the change affects versioning; otherwise skip.

Execution steps:
1. Read PR metadata (number, title, body, author, base/head).
2. Read changed file list.
3. Inspect patch summaries to infer intent.
4. Choose at most one label from 影響範囲 and at most one from バージョン.
5. Emit safe output to add labels.
6. If at least one label was applied, post a comment in Japanese on the pull request explaining the reason for each label applied. Use the GitHub pull_requests tool to create the comment on PR #${{ github.event.pull_request.number }}. The comment must be in Japanese and include which label was chosen and why.

Output contract:
- Return strict JSON-compatible structure:
  - labels: string[]
  - reason: string
- `labels` must contain only allowed labels.
- Maximum 1 label from 影響範囲, maximum 1 label from バージョン.

Failure handling:
- If confidence is low, apply no labels.
- Never apply labels outside the allow-list.