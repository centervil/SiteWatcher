# diary-converterのCI/CD統合

このドキュメントでは、diary-converterツールをCI/CDパイプラインに統合する方法について説明します。

## 概要

diary-converterは、開発日記をZenn公開用の記事に変換するツールです。CI/CDパイプラインに組み込むことで、以下のメリットがあります：

- 開発日記の変換作業を自動化
- 一貫した形式でZenn記事を生成
- 手動操作によるミスを防止

## CI/CD統合の仕組み

GitHub Actionsワークフロー（`.github/workflows/deploy.yml`）に`diary-converter`ジョブを追加しています。このジョブは以下の処理を行います：

1. 最新の開発日記ファイルを検索
2. 出力ファイル名を生成
3. Dockerイメージをビルド
4. コンテナを実行して開発日記をZenn記事に変換

## 前提条件

CI/CDパイプラインでdiary-converterを実行するには、以下の設定が必要です：

1. GitHub Secretsに`GOOGLE_API_KEY`を追加
   - リポジトリの「Settings」→「Secrets and variables」→「Actions」から設定
   - Gemini APIキーを値として設定

2. 必要なディレクトリ構造
   - `Documents/ProjectLogs/`: 開発日記が保存されるディレクトリ
   - `articles/`: 変換されたZenn記事が保存されるディレクトリ

## ローカルでのテスト方法

CI/CDパイプラインにプッシュする前に、ローカル環境でテストすることをお勧めします。

### Dockerを使用したテスト

```bash
# カレントディレクトリをdiary-converterディレクトリに変更
cd tools/diary-converter

# 最新の開発日記ファイルを検索
LATEST_DIARY=$(find ../../Documents/ProjectLogs -type f -name "*.md" | sort -r | head -n 1)

# 出力ファイル名を生成
DIARY_FILENAME=$(basename "$LATEST_DIARY")
DATE_PART=$(echo "$DIARY_FILENAME" | grep -oP '\d{4}-\d{2}-\d{2}')
THEME_PART=$(echo "$DIARY_FILENAME" | sed "s/${DATE_PART}-//g" | sed "s/.md$//g")
OUTPUT_FILENAME="${DATE_PART}-${THEME_PART}.md"

echo "処理対象: $LATEST_DIARY"
echo "出力ファイル: $OUTPUT_FILENAME"

# Dockerイメージをビルド
docker build -t diary-converter .

# コンテナを実行
docker run --rm \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -v $(pwd)/../../Documents/ProjectLogs:/app/input \
  -v $(pwd)/../../articles:/app/output \
  diary-converter \
  "/app/input/$DIARY_FILENAME" \
  "/app/output/$OUTPUT_FILENAME" \
  --model gemini-2.0-flash-001
```

### 直接実行によるテスト

```bash
# カレントディレクトリをdiary-converterディレクトリに変更
cd tools/diary-converter

# 最新の開発日記ファイルを検索
LATEST_DIARY=$(find ../../Documents/ProjectLogs -type f -name "*.md" | sort -r | head -n 1)

# 出力ファイル名を生成
DIARY_FILENAME=$(basename "$LATEST_DIARY")
DATE_PART=$(echo "$DIARY_FILENAME" | grep -oP '\d{4}-\d{2}-\d{2}')
THEME_PART=$(echo "$DIARY_FILENAME" | sed "s/${DATE_PART}-//g" | sed "s/.md$//g")
OUTPUT_FILENAME="${DATE_PART}-${THEME_PART}.md"

echo "処理対象: $LATEST_DIARY"
echo "出力ファイル: $OUTPUT_FILENAME"

# 直接実行
python diary_converter.py \
  "../../Documents/ProjectLogs/$DIARY_FILENAME" \
  "../../articles/$OUTPUT_FILENAME" \
  --model gemini-2.0-flash-001
```

## トラブルシューティング

### APIキーの問題

エラーメッセージ: `エラー: GOOGLE_API_KEY 環境変数が設定されていません`

解決策:
- ローカル環境: `export GOOGLE_API_KEY=your_api_key_here`を実行
- CI/CD環境: GitHub Secretsに`GOOGLE_API_KEY`が正しく設定されているか確認

### パスの問題

エラーメッセージ: `エラー: ファイル読み込み中にエラーが発生しました`

解決策:
- ファイルパスが正しいか確認
- ボリュームマウントが正しく設定されているか確認

### Dockerの問題

エラーメッセージ: `docker: command not found`

解決策:
- Dockerがインストールされているか確認
- CI/CD環境でDockerが利用可能か確認

## 注意事項

- APIキーは機密情報です。コード内に直接記述しないでください。
- 大量の開発日記を一度に処理すると、APIの利用制限に達する可能性があります。
- 変換結果は必ず確認してから公開してください。 