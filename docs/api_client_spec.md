# MCPサーバー esa.io APIクライアント仕様

このドキュメントは、esa.io API クライアント（EsaClientクラス）の実装仕様とテスト方針を記述します。

## 1. 目的

esa.io API との通信を行うための基本的なクライアント機能を提供します。認証情報の管理、リクエストの送信、基本的なエンドポイントへのアクセス機能を含みます。

## 2. クライアント仕様

- .envからESA_TOKEN/ESA_TEAM_NAMEを取得
- requests.Sessionによる認証付き通信
- get_user, get_posts, get_postメソッドを提供
- エラー時は例外送出・ログ出力

### 2.1. EsaClient クラス

- 初期化時にdotenv.load_dotenv()で環境変数を取得し、認証情報を検証
- APIベースURL（https://api.esa.io/v1/teams/{team_name}）を構築
- 共通ヘッダー（Authorization, Content-Type）を設定
- _requestヘルパーでAPIリクエストを共通化
- get_user: 認証ユーザー情報取得
- get_posts: 記事一覧取得（q, page, per_page対応）
- get_post: 記事詳細取得（post_number指定）

## 3. テスト方針・構成

- pytestによるユニットテスト・インテグレーションテスト
- モックによる外部依存排除
- テストディレクトリ・マーカーの使い分け

### 3.1. テスト構成
- **ユニットテスト:**
    - APIクライアントやMCPツールのロジックをモックで高速に検証します。
    - テストファイル例: `tests/test_esa_client.py`, `tests/test_main_tools.py`
- **インテグレーションテスト:**
    - 実際のesa.io APIと通信し、全体の連携を検証します（.envとネットワークが必要）。
    - テストファイル例: `tests/integration/test_esa_client_integration.py`
- テストディレクトリは `tests/` 配下にあり、`integration/` サブディレクトリでインテグレーションテストを分離しています。
- pytestのマーカー（`@pytest.mark.integration`）でインテグレーションテストを区別しています。

### 3.2. ユニットテスト詳細
- 主なテストファイル:
    - `tests/test_esa_client.py`: EsaClientクラスの初期化・APIメソッドの正常系/異常系
    - `tests/test_main_tools.py`: MCPツールの引数処理・EsaClient呼び出し・エラーハンドリング
- モック・フィクスチャ:
    - `monkeypatch` で環境変数をセット
    - `unittest.mock.patch` で requests や EsaClient のメソッドをモック
- 主なテストケース例:
    - 認証情報がない場合の初期化エラー
    - get_user の正常/エラー応答
    - get_posts のパラメータ有無・エラー応答
    - MCPツールが正しいEsaClientメソッドを呼ぶか

### 3.3. インテグレーションテスト詳細
- 主なテストファイル:
    - `tests/integration/test_esa_client_integration.py`
- 内容:
    - 実際のesa.io APIと通信し、ユーザー情報・記事一覧・記事詳細の取得を検証
    - 存在しない記事番号で404エラーを検証
- 注意点:
    - `.env`ファイルに有効なESA_TOKEN/ESA_TEAM_NAMEが必要
    - ネットワーク接続が必要
    - 実行に時間がかかる場合あり

## 4. テスト実行方法

- **ユニットテストのみ実行:**
    ```bash
    uv run pytest tests/
    ```
- **インテグレーションテストのみ実行:**
    ```bash
    uv run pytest -m integration tests/integration/
    ```
- **全テスト実行:**
    ```bash
    uv run pytest
    ```
- **テストカバレッジを表示**
    ```bash
    uv run pytest --cov=. tests
    ```
---

※サーバー全体の設計・開発まとめは docs/20250504/mcp_esa_development_summary.md を参照。
※利用方法・MCPツールの説明は docs/mcp_esa_server_usage.md を参照。
