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
  id: claude
  version: beta
  model: 'openai/gpt-oss-120b:free'
  max-turns: 5
  env:
    CUSTOM_API_ENDPOINT: https://openrouter.ai/api/v1
    DEBUG_MODE: "true"
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
---
Assign labels to the pull  #${{ github.event.pull_request.number }}.