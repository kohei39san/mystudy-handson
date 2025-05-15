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

### 7. GitHub CopilotでMCPを使用する手順
#### 7.1 VSCodeの設定ファイルを編集
- VSCodeの設定ファイル（settings.json）に以下の設定を追加します
- 設定例は [settings.json](../src/016.setup-mcp-with-vscode/settings.json) を参照してください

```json
{
    "git.autofetch": true,
    "github.copilot.advanced": {},
    "chat.mcp.discovery.enabled": true,
    "mcp": {
        "inputs": [],
        "servers": {
            "awslabs.aws-documentation-mcp-server": {
                "command": "uvx",
                "args": [
                    "--from",
                    "awslabs-aws-documentation-mcp-server",
                    "awslabs.aws-documentation-mcp-server.exe"
                ]
            },
            "awslabs.cost-analysis-mcp-server": {
                "command": "uvx",
                "args": [
                    "--from",
                    "awslabs-cost-analysis-mcp-server",
                    "awslabs.cost-analysis-mcp-server.exe"
                ]
            }
        }
    }
}
```

#### 7.2 MCPサーバーの起動確認
- VSCodeを再起動します
- GitHub Copilotのチャットパネルを開きます
- チャットパネル上部の「@」をクリックし、MCPサーバーが表示されることを確認します
- 表示されたMCPサーバーを選択すると、そのサーバーに対してクエリを実行できます

#### 7.3 MCPサーバーの使用方法
- チャットパネルで「@」を押してMCPサーバーを選択します
- 選択したMCPサーバーに対して質問を入力します
- 例: 「@aws-docs AWSのS3バケットの作成方法を教えてください」

#### 7.4 トラブルシューティング
- MCPサーバーが表示されない場合は、VSCodeを再起動してみてください
- それでも解決しない場合は、設定ファイルの内容を確認してください
- uvxコマンドが正しくインストールされているか確認してください

## GitHub Issueからの開発手順

### 1. Issueへのアクセス
- 対象のリポジトリのGitHubページにアクセス
- Issueタブを開く

### 2. Copilot Agent Modeの起動
- Issue詳細画面で `Code with Copilot Agent Mode` ボタンを押下