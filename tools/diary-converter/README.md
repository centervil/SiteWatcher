# 開発日記変換ツール

このツールは、ProjectLogs以下の開発日記をLLM API（Gemini）を利用して加工し、articles配下にZenn公開用日記として配置するためのスクリプトです。

## 使い方

### ローカル環境での実行

1. 必要なライブラリをインストール：
   ```
   pip install -r requirements.txt
   ```

2. Gemini APIキーを環境変数に設定：
   ```
   export GOOGLE_API_KEY=your_api_key_here
   ```

3. スクリプトを実行：
   ```
   python diary_converter.py path/to/source/diary.md path/to/destination/article.md
   ```

### Docker環境での実行

1. イメージをビルド：
   ```
   docker-compose build diary-converter
   ```

2. Gemini APIキーを環境変数に設定：
   ```
   export GOOGLE_API_KEY=your_api_key_here
   ```

3. コンテナを実行：
   ```
   docker-compose run diary-converter input/2025-03-10-Claude-Cursor連携開発.md output/2025-03-10-claude-cursor.md
   ```

   オプションを指定する場合：
   ```
   docker-compose run diary-converter input/2025-03-10-Claude-Cursor連携開発.md output/2025-03-10-claude-cursor.md --model gemini-pro --debug
   ```

## 機能

- マークダウン形式の開発日記を読み込み
- Gemini APIを使用して内容を加工
- Zenn公開用の形式に変換（frontmatter付き）
- 変換結果を指定先に保存 