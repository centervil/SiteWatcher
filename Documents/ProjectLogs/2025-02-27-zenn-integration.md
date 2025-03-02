# 2025-02-27 Zenn連携機能の追加

## 今日の目標

*   開発日記をZennに自動投稿できるようにする。
*   日々の開発サイクルをClineに提示するためのガイドドキュメントを作成する。

## 実行内容

1.  **Zenn CLIのインストール:**
    ```bash
    npm install -g zenn-cli
    ```
    Zenn CLIをグローバルにインストールしました。これにより、Zennの記事をコマンドラインから操作できるようになります。

2.  **公開ディレクトリの作成と移動:**
    ```bash
    mkdir Documents/articles
    mv Documents/ProjectLogs Documents/articles/
    ```
    Zennの記事を管理するための公開ディレクトリ `Documents/articles` を作成し、既存の開発日記ディレクトリ `Documents/ProjectLogs` をその配下に移動しました。

3.  **GitHub Actions ワークフローの修正:**
    `.github/workflows/deploy.yml` を修正し、Zennへの публикации処理をworkflowに組み込みました。具体的には、`zenn-deploy` jobを追加し、frontendデプロイ後にZennへの публикацииが実行されるように設定しました。

    ```yaml
    name: CI/CD Pipeline

    on:
      push:
        branches:
          - main
      workflow_dispatch:

    permissions:
      contents: read
      pages: write
      id-token: write

    jobs:
      frontend-deploy:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout code
            uses: actions/checkout@v2

          - name: Setup Node.js
            uses: actions/setup-node@v2
            with:
              node-version: '18'

          - name: Install dependencies (frontend) # frontend ディレクトリに移動して dependencies をインストール
            working-directory: frontend
            run: npm install

          - name: Build frontend # frontend をビルド
            working-directory: frontend
            run: npm run build

          - name: Setup Pages # Pages の設定
            uses: actions/configure-pages@v4

          - name: Upload artifact # artifact をアップロード
            uses: actions/upload-pages-artifact@v3
            with:
              path: './frontend/build'

          - name: Deploy to GitHub Pages # GitHub Pages にデプロイ
            uses: actions/deploy-pages@v4

      zenn-deploy: # Zenn deploy job を追加
        runs-on: ubuntu-latest
        needs: frontend-deploy # frontend-deploy job の完了後に実行
        steps:
          - name: Checkout code # コードをチェックアウト
            uses: actions/checkout@v2

          - name: Setup Node.js # Node.js をセットアップ
            uses: actions/setup-node@v2
            with:
              node-version: '18' # Zenn CLI が Node.js 環境で動作するため

          - name: Install zenn-cli # zenn-cli をインストール
            run: npm install -g zenn-cli

          - name: Zenn Publish # Zenn に публикацииを実行
            working-directory: Documents/articles # Zenn の記事があるディレクトリを指定
            run: zenn articles publish # articles ディレクトリにある記事を публикации

      backend-deploy:
        runs-on: ubuntu-latest
        needs: zenn-deploy # zenn-deploy job の完了後に実行 (backend は zenn-deploy に依存)
        steps:
          - name: Checkout code
            uses: actions/checkout@v2

          - name: Setup AWS CLI
            uses: aws-actions/configure-aws-credentials@v1
            with:
              aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
              aws-secret_access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              aws-region: ${{ secrets.AWS_REGION }}

          - name: Deploy to AWS Lambda
            run: |
              zip -r function.zip .
              aws lambda update-function-code --function-name your-lambda-function-name --zip-file fileb://function.zip
    ```

## 今後の課題

*   Zenn CLIの認証設定
*   Zennへの実際の публикацииテスト
*   エラーハンドリングの追加

## まとめ

今日の開発では、Zenn CLIのインストール、公開ディレクトリの作成と移動、GitHub Actionsワークフローの修正を行い、Zenn連携の基盤を構築しました。

---
