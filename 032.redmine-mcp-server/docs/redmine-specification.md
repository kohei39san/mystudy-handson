# Redmine 仕様リファレンス

## 概要

Redmine MCP Serverが使用するRedmineの仕様をまとめたドキュメントです。URL、標準フィールド、検索パラメータなどの情報を含みます。

---

## URL一覧

### 基本URL

| 機能 | URLパターン | 説明 |
|------|-------------|------|
| ログイン | `{base_url}/login` | ログインページ |
| ログアウト | `{base_url}/logout` | ログアウト処理 |
| プロジェクト一覧 | `{base_url}/projects` | プロジェクト一覧ページ |
| プロジェクトメンバー | `{base_url}/projects/{project_id}/settings/members` | プロジェクトメンバー設定ページ |
| チケット一覧（全体） | `{base_url}/issues` | 全プロジェクトのチケット一覧 |
| チケット一覧（プロジェクト） | `{base_url}/projects/{project_id}/issues` | 特定プロジェクトのチケット一覧 |
| チケット詳細 | `{base_url}/issues/{issue_id}` | チケット詳細ページ |
| チケット編集 | `{base_url}/issues/{issue_id}/edit` | チケット編集ページ |
| チケット新規作成 | `{base_url}/issues/new` | 新規チケット作成ページ（全体） |
| チケット新規作成（プロジェクト） | `{base_url}/projects/{project_id}/issues/new` | 新規チケット作成ページ（プロジェクト指定） |
| チケット新規作成（トラッカー指定） | `{base_url}/projects/{project_id}/issues/new?issue[tracker_id]={tracker_id}` | トラッカーを指定した新規チケット作成ページ |

### URL変数

| 変数 | 説明 | 例 |
|------|------|-----|
| `{base_url}` | RedmineサーバーのベースURL | `http://redmine.example.com` |
| `{project_id}` | プロジェクト識別子 | `my-project` |
| `{issue_id}` | チケットID | `123` |
| `{tracker_id}` | トラッカーID | `1` |

### チケット検索

#### URLパターン

```
# 全プロジェクト横断検索
{base_url}/issues?set_filter=1&sort={sort}&q={keyword}&f[]={field}&op[{field}]={operator}&v[{field}][]={value}&f[]=&c[]={column}

# 特定プロジェクト内検索
{base_url}/projects/{project_id}/issues?set_filter=1&sort={sort}&q={keyword}&f[]={field}&op[{field}]={operator}&v[{field}][]={value}&f[]=&c[]={column}
```

**注意**: フィルターパラメータとカラムパラメータは複数指定可能です。

#### 検索パラメータ

##### 基本パラメータ

| パラメータ | 説明 | `{sort}` / `{keyword}` |
|-----------|----|-----|
| `set_filter` | フィルタ有効化 | `1`（必須） |
| `sort` | ソート順 | `id:desc`（ID降順） |
| `group_by` | グループ化 | 空文字列（グループ化なし） |
| `q` | 全文検索 | `認証`（検索キーワード） |

##### フィルターパラメータ

フィルターは`f[]`、`op[field]`、`v[field][]`の3つのパラメータで構成されます。

| フィールド | `{field}` | 説明 |
|----------|----------|------|
| ステータス | `status_id` | チケットの状態 |
| トラッカー | `tracker_id` | チケットの種類 |
| 担当者 | `assigned_to_id` | チケットの担当者 |
| 親チケット | `parent_id` | 親となるチケット |
| 全文検索 | `any_searchable` | 題名・説明・コメントを横断検索 |
| カスタムフィールド | `cf_{id}` | Redmine設定で追加されたフィールド |

##### 演算子一覧

| `{operator}` | 説明 | 使用可能フィールド | `{value}` 例 |
|--------|------|---------------------|----------|
| `=` | 等しい | `tracker_id`、`assigned_to_id`、`parent_id`、`cf_{id}` | `1`（トラッカーID）、`5`（ユーザーID）、`123`（親チケットID） |
| `!` | 等しくない | `tracker_id`、`assigned_to_id`、`parent_id`、`cf_{id}` | `1`（トラッカーID）、`5`（ユーザーID） |
| `~` | 含む | `any_searchable` | `認証`（検索キーワード） |
| `o` | 未完了 | `status_id` | 空文字列 |
| `c` | 完了 | `status_id` | 空文字列 |
| `*` | すべて | `status_id` | 空文字列 |

##### 表示カラムパラメータ

| パラメータ | 説明 | `{column}` |
|-----------|----|-----|
| `c[]` | 表示するカラム | `tracker`、`status`、`priority`、`subject`、`assigned_to`、`updated_on`、`cf_{id}` |

### 検索URL例

```
# 未完了チケット
{base_url}/issues?set_filter=1&f[]=status_id&op[status_id]=o&f[]=&c[]=tracker&c[]=subject&c[]=assigned_to

# 特定トラッカーのチケット
{base_url}/issues?set_filter=1&f[]=tracker_id&op[tracker_id]==&v[tracker_id][]=1&f[]=&c[]=status&c[]=subject

# 特定担当者のチケット
{base_url}/issues?set_filter=1&f[]=assigned_to_id&op[assigned_to_id]==&v[assigned_to_id][]=5&f[]=&c[]=tracker&c[]=subject&c[]=updated_on

# キーワード検索
{base_url}/issues?set_filter=1&f[]=any_searchable&op[any_searchable]=~&v[any_searchable][]=認証&f[]=&c[]=subject&c[]=status

# カスタムフィールドで絞り込み（カスタムフィールドを表示）
{base_url}/issues?set_filter=1&f[]=cf_4&op[cf_4]==&v[cf_4][]=1&f[]=&c[]=subject&c[]=cf_4

# 複数条件の組み合わせ（未完了かつトラッカーID=1）
{base_url}/issues?set_filter=1&f[]=status_id&op[status_id]=o&f[]=tracker_id&op[tracker_id]==&v[tracker_id][]=1&f[]=&c[]=subject&c[]=priority&c[]=assigned_to
```

---

## 標準フィールド一覧

標準フィールドは、以下のURLにアクセスした際に画面で出てくる項目です：

| URL | 使用するフィールドID | 備考 |
|-----|---------------------|------|
| `{base_url}/projects/{project_id}/issues/new` | 更新フィールドID | チケット新規作成 |
| `{base_url}/issues/{issue_id}/edit` | 更新フィールドID | チケット編集 |
| `{base_url}/issues/{issue_id}` | 表示フィールドID | チケット詳細（表示のみ） |

### フィールド一覧表

| フィールド名 | 表示フィールドID | 更新フィールドID | 型 | 必須 | 説明 | 取りうる値 |
|-------------|-------------|----------------|-----|------|------|-----------|
| トラッカー | `tracker_id` | `issue_tracker_id` | select-one | ○ | チケットの種類 | トラッカーID（数値）<br>例: `1`=課題, `2`=タスク, `3`=バグ |
| 題名 | `subject` | `issue_subject` | text | ○ | チケットのタイトル | 文字列（255文字以内推奨） |
| 説明 | `description` | `issue_description` | textarea | × | チケットの詳細説明 | 文字列（複数行可、Textile/Markdown形式） |
| ステータス | `status_id` | `issue_status_id` | select-one | ○ | チケットの状態 | ステータスID（数値）<br>例: `1`=新規, `2`=進行中, `5`=完了 |
| 優先度 | `priority_id` | `issue_priority_id` | select-one | ○ | チケットの優先度 | 優先度ID（数値）<br>例: `1`=低, `2`=通常, `3`=高, `4`=緊急 |
| 担当者 | `assigned_to_id` | `issue_assigned_to_id` | select-one | × | チケットの担当者 | ユーザーID（数値）または`me`（自分）<br>空欄可 |
| 親チケット | `parent_issue_id` | `issue_parent_issue_id` | text | × | 親となるチケット | チケットID（数値）<br>空欄可 |
| 開始日 | `start_date` | `issue_start_date` | date | × | チケットの開始予定日 | 日付（YYYY-MM-DD形式）<br>例: `2025-01-15` |
| 期日 | `due_date` | `issue_due_date` | date | × | チケットの完了予定日 | 日付（YYYY-MM-DD形式）<br>例: `2025-01-31` |
| 予定工数 | `estimated_hours` | `issue_estimated_hours` | number | × | 作業予定時間 | 数値（時間単位、小数可）<br>例: `8.5` |
| 進捗率 | `done_ratio` | `issue_done_ratio` | select-one | × | 作業の進捗状況 | 数値（0-100の10刻み）<br>例: `0`, `10`, `20`, ..., `100` |
| プライベート | `is_private` | `issue_is_private` | checkbox | × | チケットの公開/非公開 | ブール値<br>`true`=非公開, `false`=公開 |
| カスタムフィールド | `custom_field_values_{id}` | `issue_custom_field_values_{id}` | 可変 | × | Redmine設定で追加されたフィールド | フィールドの型により異なる<br>例: `1`（選択肢）、`テキスト`（文字列） |

---

## 型の詳細

| 型 | フォーマット | 備考 |
|----|-------------|------|
| date | `YYYY-MM-DD` | 例: `2025-01-15` |
| textarea | 文字列（複数行可） | Textile/Markdown形式サポート |
| checkbox | `1`/`0` または `true`/`false` | |