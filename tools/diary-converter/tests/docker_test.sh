#!/bin/bash
set -e

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/../../.."

# APIキーが設定されているか確認
if [ -z "$GOOGLE_API_KEY" ]; then
  echo "エラー: GOOGLE_API_KEY 環境変数が設定されていません"
  exit 1
fi

echo "Docker環境でのテストを開始します..."

# イメージをビルド
echo "イメージをビルドしています..."
docker-compose build diary-converter

# テスト用の入力ファイルと出力ファイルのパスを設定
# Dockerコンテナ内のパスに合わせて変更
INPUT_FILE="tests/test_input.md"
OUTPUT_FILE="tests/output/docker_test_output.md"
TEMPLATE_FILE="tests/test_template.md"

echo "入力ファイル: $INPUT_FILE"
echo "出力ファイル: $OUTPUT_FILE"
echo "テンプレートファイル: $TEMPLATE_FILE"

# コンテナを実行
echo "コンテナを実行しています..."
docker-compose run diary-converter "$INPUT_FILE" "$OUTPUT_FILE" --debug --template "$TEMPLATE_FILE"

# 出力ファイルが生成されたか確認
if [ -f "tools/diary-converter/$OUTPUT_FILE" ]; then
  echo "テスト成功: 出力ファイルが生成されました"
  echo "出力ファイルの内容:"
  echo "-----------------------------------"
  cat "tools/diary-converter/$OUTPUT_FILE"
  echo "-----------------------------------"
else
  echo "テスト失敗: 出力ファイルが生成されませんでした"
  exit 1
fi

echo "Docker環境でのテストが完了しました" 