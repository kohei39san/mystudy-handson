# MCPサーバーセットアップガイド

## インストール手順

### 1. VSCodeのインストール
- [公式サイト](https://code.visualstudio.com/)からダウンロードしてインストール

### 2. GitHub Copilot無料版の有効化
- GitHubアカウントでログインし、無料版を有効化

### 3. 拡張機能のインストール
- Cline
- GitHub Copilot

### 4. GitHub PATの発行
- GitHubの設定画面から読み取り専用のPersonal Access Token (PAT)を発行

### 5. uvxのインストール
- 公式ドキュメントに従ってインストール

### 6. MCPサーバーの設定
- 設定ファイルは [mcp-servers-config.json](../src/016.setup-mcp-with-vscode/mcp-servers-config.json) に配置

### 7. VSCode拡張機能Github CopilotでのMCP使用手順
1. VSCode左下の歯車マーク->設定を押下する
2. 「mcp」というキーワードで検索する
3. MCP モデルコンテキストプロトコルサーバー構成の「settings.jsonで編集」を押下
4. settings.jsonを書き直す
5. settings.json編集画面から「起動」を押下してMCPサーバーを起動する
6. Github Copilotをエージェントに切り替える

## GitHub Issueからの開発手順

### 1. Issueへのアクセス
- 対象のリポジトリのGitHubページにアクセス
- Issueタブを開く

### 2. Copilot Agent Modeの起動
- Issue詳細画面で `Code with Copilot Agent Mode` ボタンを押下