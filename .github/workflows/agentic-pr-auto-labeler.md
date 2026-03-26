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
    allowed: [ feature, fix, bug, major, minor, patch ]
  add-comment:
    max: 1

tools:
  github:
    lockdown: true
    min-integrity: approved
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
- Use only labels listed in `safe-outputs.remove-labels.allowed` when removing labels.
- Apply at most 1 label from the impact scope category and at most 1 label from the version category (2 labels maximum in total).
- Exception: for dependabot PRs, apply only version category labels (no impact scope labels).
- Prioritize precision over recall.
- Do not create new labels.
- If existing labels conflict with the current decision, consider removing them within the safe-outputs limit.
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

Dependabot rule:
- If the PR author is `dependabot[bot]`, apply **only** version category labels (major / minor / patch). Do not apply any impact scope labels (feature / fix / bug).

Decision rules:
1. Use PR title and body first, then changed file paths and diff summary.
2. Read current PR labels and identify existing labels in the managed set: `feature`, `fix`, `bug`, `major`, `minor`, `patch`.
3. If the PR author is `dependabot[bot]`, skip impact scope label selection entirely and select at most 1 label from the version category only.
4. Otherwise, select at most 1 label from the impact scope category (feature / fix / bug).
5. Select at most 1 label from the version category (major / minor / patch).
6. For each category, if an existing managed label is different from the selected label, mark it for removal.
7. If confidence is low, do not add or remove labels.

Execution steps:
1. Read PR metadata (number, title, body, author, base/head).
2. Read current labels on the PR.
3. If the PR author is `dependabot[bot]`, skip to step 6 (version label selection only).
4. Read changed file list and inspect patch summaries to infer intent.
5. Choose at most 1 impact scope label from the allow-list (skip this step for dependabot PRs).
6. Choose at most 1 version label from the allow-list.
7. Compare selected labels with existing managed labels and decide `labels_to_remove`.
8. Emit safe output to add and/or remove labels.
9. Post a comment in Japanese on the pull request summarising which labels were applied/removed and why.

Output contract:
- Return strict JSON-compatible structure:
  - labels_to_add: string[]
  - labels_to_remove: string[]
  - reason: string (Japanese, posted as a PR comment)
- `labels_to_add` must contain only labels from `safe-outputs.add-labels.allowed`.
- `labels_to_remove` must contain only labels from `safe-outputs.remove-labels.allowed`.
- Maximum 1 label per category.
- For dependabot PRs: `labels_to_add` must contain only version category labels.

Failure handling:
- If confidence is low, apply no label changes.
- Never apply labels outside the allow-list.
