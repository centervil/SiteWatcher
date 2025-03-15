# diary-converterのCI/CD統合

このドキュメントでは、diary-converterをCI/CDパイプラインに統合する方法について説明します。

## 概要

diary-converterは、開発日記をZenn公開用の記事に変換するツールです。CI/CDパイプラインに統合することで、以下のメリットがあります：

1. 自動化された変換プロセス
2. 一貫した出力形式
3. 手動操作によるミスの防止
4. 開発ワークフローの効率化

## CI/CD統合の仕組み

diary-converterのCI/CD統合は、以下の流れで動作します：

1. GitHub Actionsのワークフロー（`.github/workflows/deploy.yml`）内に`diary-converter`ジョブを定義
2. 最新の開発日記ファイルを自動的に検出
3. Dockerを使用してdiary-converterを実行
4. 変換された記事を`articles`ディレクトリに出力
5. 生成された記事をZenn連携用リポジトリにプッシュ

## 必要な環境変数とシークレット

diary-converterのCI/CD統合には、以下の環境変数とシークレットが必要です：

1. `GOOGLE_API_KEY`: Gemini APIを使用するためのAPIキー（GitHub Secretsに設定）
2. `ZENN_REPO`: Zenn連携用リポジトリのURL（GitHub Secretsに設定）
3. `ZENN_REPO_TOKEN`: ZennリポジトリにプッシュするためのPersonal Access Token（GitHub Secretsに設定）

## GitHub Secretsの設定方法

1. GitHubリポジトリの「Settings」タブを開く
2. 左側のメニューから「Secrets and variables」→「Actions」を選択
3. 「New repository secret」ボタンをクリック
4. 以下のシークレットを追加：
   - `GOOGLE_API_KEY`: Gemini APIキー
   - `ZENN_REPO`: Zenn連携用リポジトリのURL（例：`username/zenn-content`）
   - `ZENN_REPO_TOKEN`: GitHubのPersonal Access Token（リポジトリへの書き込み権限が必要）

## Personal Access Tokenの作成方法

1. GitHubの「Settings」→「Developer settings」→「Personal access tokens」→「Tokens (classic)」を開く
2. 「Generate new token」→「Generate new token (classic)」をクリック
3. トークンの名前を入力（例：`ZENN_REPO_ACCESS`）
4. 有効期限を設定（推奨：90日）
5. スコープを選択：`repo`（すべてのリポジトリ権限）
6. 「Generate token」ボタンをクリック
7. 生成されたトークンをコピーし、GitHub Secretsの`ZENN_REPO_TOKEN`に設定

## ローカルでのテスト方法

CI/CD統合をローカルでテストするには、`test_ci_integration.sh`スクリプトを使用します：

```bash
cd tools/diary-converter
chmod +x test_ci_integration.sh
./test_ci_integration.sh
```

このスクリプトは、以下の機能を提供します：

1. Dockerを使用したテスト
2. 直接実行によるテスト
3. 環境変数の設定
4. 詳細なログ出力

## Zennリポジトリへのプッシュ機能

diary-converterで生成された公開用日記は、自動的にZenn連携用リポジトリにプッシュされます。この機能は以下の流れで動作します：

1. diary-converterジョブで生成されたファイル情報を環境変数に保存
2. zenn-pushジョブでZenn連携用リポジトリをチェックアウト
3. 生成された記事ファイルをZennリポジトリの`articles`ディレクトリにコピー
4. 変更をコミットしてプッシュ

### Zennリポジトリへのプッシュをローカルでテストする方法

Zennリポジトリへのプッシュ機能をローカルでテストするには、以下の手順を実行します：

1. 環境変数を設定：
   ```bash
   export ZENN_REPO="username/zenn-content"
   export ZENN_REPO_TOKEN="your-personal-access-token"
   ```

2. テストスクリプトを実行：
   ```bash
   cd tools/diary-converter
   ./test_zenn_push.sh
   ```

このスクリプトは、以下の処理を行います：
- 一時ディレクトリにZennリポジトリをクローン
- 最新の生成記事をZennリポジトリにコピー
- 変更をコミットしてプッシュ

## トラブルシューティング

### 一般的な問題と解決策

1. **APIキーの問題**
   - エラーメッセージ: `Error: API key not found or invalid`
   - 解決策: GitHub Secretsに`GOOGLE_API_KEY`が正しく設定されているか確認

2. **ファイルパスの問題**
   - エラーメッセージ: `Error: Template file not found`
   - 解決策: Dockerfileのマウント設定を確認し、パスが正しいか確認

3. **出力ファイル名の問題**
   - エラーメッセージ: `Error: Invalid output filename`
   - 解決策: 出力ファイル名がZennのslugルールに準拠しているか確認

4. **Zennリポジトリへのプッシュ失敗**
   - エラーメッセージ: `Error: Authentication failed`
   - 解決策: 
     - `ZENN_REPO_TOKEN`が正しく設定されているか確認
     - トークンに適切な権限が付与されているか確認
     - リポジトリ名（`ZENN_REPO`）が正しいか確認

5. **ファイルコピーの失敗**
   - エラーメッセージ: `Error: No such file or directory`
   - 解決策: 
     - 環境変数`GENERATED_ARTICLE_FILENAME`が正しく設定されているか確認
     - ファイルパスが正しいか確認

### ログの確認方法

CI/CDパイプラインのログを確認するには：

1. GitHubリポジトリの「Actions」タブを開く
2. 該当するワークフロー実行を選択
3. `diary-converter`ジョブまたは`zenn-push`ジョブをクリック
4. ログ出力を確認

## 今後の改善点

1. エラーハンドリングの強化
2. 通知機能の追加
3. 定期実行の検討
4. 変換結果の検証
5. 重複記事の検出と処理
6. 記事メタデータの自動更新
7. プッシュ結果の通知
8. 記事の品質チェック 