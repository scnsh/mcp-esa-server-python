# MCPサーバー: esa.io 操作ガイド

## 1. 概要

このMCPサーバーは、esa.io API と連携し、記事の取得・作成・更新・削除などをAIツールから操作できます。

## 2. 環境設定

- プロジェクトルート（サーバーを起動するディレクトリ）に`.env`を配置し、ESA_TOKEN/ESA_TEAM_NAMEを設定

例 (`.env`):
```
ESA_TOKEN=your_esa_api_token_here
ESA_TEAM_NAME=your_team_name
```

## 3. 提供ツール一覧

### user_get_info()
- **説明:** 現在認証されているesa.ioユーザーの情報を取得します。
- **引数:** なし
- **戻り値:** ユーザー情報を含む辞書（例: `{ "id": ..., "name": ... }`）

### posts_get_list(q: str | None = None, page: int | None = None, per_page: int | None = None)
- **説明:** 記事の一覧を取得します。検索クエリやページネーションによる絞り込みが可能です。
- **引数:**
    - `q` (オプション): 検索クエリ文字列
    - `page` (オプション): 取得するページ番号
    - `per_page` (オプション): 1ページあたりの記事数
- **戻り値:** 記事一覧とページネーション情報を含む辞書（例: `{ "posts": [...], "meta": {...} }`）

### posts_get_detail(post_number: int)
- **説明:** 指定された記事番号の記事詳細を取得します。
- **引数:** `post_number`（記事番号）
- **戻り値:** 記事詳細情報を含む辞書（例: `{ "post": {...} }`）

### posts_create(name: str, body_md: str, tags: list[str] | None = None, category: str | None = None, wip: bool | None = True, message: str | None = None)
- **説明:** 新しい記事を作成します。
- **引数:** `name`, `body_md`, `tags`, `category`, `wip`, `message`
- **戻り値:** 作成された記事の情報（例: `{ "post": {...} }`）

### posts_update(post_number: int, name: str | None = None, body_md: str | None = None, tags: list[str] | None = None, category: str | None = None, wip: bool | None = None, message: str | None = None)
- **説明:** 既存の記事を更新します。更新したい項目のみ引数で指定します。
- **引数:** `post_number`, `name`, `body_md`, `tags`, `category`, `wip`, `message`
- **戻り値:** 更新された記事の情報（例: `{ "post": {...} }`）

### posts_delete(post_number: int)
- **説明:** 指定された記事番号の記事を削除します。
- **引数:** `post_number`
- **戻り値:** 成功時は空の辞書 `{}`

## 4. サーバーの起動

```bash
uv run mcp run main.py
```
または開発モード
```bash
uv run mcp dev main.py
```

サーバーはデフォルトで `http://localhost:6274` で起動し、MCPエンドポイントは `/mcp` です。
MCPクライアント（Cursorなど）から上記ツールを呼び出すことができます。
**ポート番号が実際に異なる可能性はあるので、表示されるログを確認してください。**

## 5. テストの実行

- テスト構成や実行方法の詳細は docs/api_client_spec.md を参照してください。

## 6. 備考

- サーバー全体の設計・開発まとめは docs/20250504/mcp_esa_development_summary.md を参照