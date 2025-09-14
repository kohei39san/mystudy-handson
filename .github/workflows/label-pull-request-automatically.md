---
on:
  workflow_dispatch:
  pull_request:
    types: [opened, labeled]

permissions:
  contents: read
  pull-requests: write

tools:
  github:
    allowed: [update_issue]

timeout_minutes: 10

engine:
  id: codex
  version: 0.29.0
  model: 'openai/gpt-oss-120b:free'
  env:
    OPENAI_BASE_URL: https://openrouter.ai/api/v1
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
---
Assign labels to the pull request #${{ github.event.pull_request.number }}.