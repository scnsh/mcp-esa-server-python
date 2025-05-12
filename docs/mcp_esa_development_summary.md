# esa.io MCPサーバー開発まとめ

## 概要

本プロジェクトは、esa.ioのAPIをAIアシスタントから操作できるMCPサーバーの開発を目的としています。

## サーバー設計・技術スタック

- **FastMCP**: MCPプロトコル実装
- **pytest/ruff**: テスト・フォーマット

## 主要機能

- ユーザー情報取得（user_get_info）
- 記事一覧取得（posts_get_list）
- 記事詳細取得（posts_get_detail）
- 記事作成 (posts_create)
- 記事更新 (posts_update)
- 記事削除 (posts_delete)

## 実装ポイント

- MCPツールとしてユーザー情報・記事一覧・記事詳細取得を実装
- 環境変数・エラーハンドリングの徹底
- ユニットテスト・インテグレーションテストの分離

## 技術的課題と解決策
- .envによる安全な認証情報管理
- テストのモック化・テスト対応

## 今後の課題

- 他のAPI操作の実装
- エラーハンドリングの強化
- テスト拡充・パフォーマンス最適化

---

※APIクライアントの詳細仕様・テスト構成は docs/api_client_spec.md を参照。
※利用方法・起動手順・MCPツールの説明は docs/mcp_esa_server_usage.md を参照。
