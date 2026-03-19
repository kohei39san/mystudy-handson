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
    max: 3
    allowed: [ feature, fix, bug ]

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
- Use only labels listed in `safe-outputs.add-labels.allow-only`.
- Apply 0 to 3 labels.
- Prioritize precision over recall.
- Do not create new labels.

Decision rules:
1. Use PR title and body first, then changed file paths and diff summary.
2. Use `feature` for new capability additions.
3. Use `fix` for corrective changes, including specification adjustments and minor defect fixes.
4. Use `bug` for fixes of user-visible and reproducible defects.

Execution steps:
1. Read PR metadata (number, title, body, author, base/head).
2. Read changed file list.
3. Inspect patch summaries to infer intent.
4. Choose labels from allow-list.
5. Emit safe output to add labels.
6. Add a short reasoning note in the workflow log.

Output contract:
- Return strict JSON-compatible structure:
  - labels: string[]
  - reason: string
- `labels` must contain only allowed labels.

Failure handling:
- If confidence is low, apply no labels.
- Never apply labels outside the allow-list.