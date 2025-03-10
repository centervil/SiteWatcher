#!/bin/bash
set -e

# 現在のディレクトリをスクリプトのディレクトリに変更
cd "$(dirname "$0")"

# APIキーが設定されているか確認
if [ -z "$GOOGLE_API_KEY" ]; then
  echo "エラー: GOOGLE_API_KEY 環境変数が設定されていません"
  exit 1
fi

# テスト用の入力ファイルと出力ファイルのパスを設定
INPUT_FILE="test_input.md"
OUTPUT_FILE="output/test_output.md"

echo "テストを開始します..."
echo "入力ファイル: $INPUT_FILE"
echo "出力ファイル: $OUTPUT_FILE"

# diary_converter.pyを実行
python ../diary_converter.py "$INPUT_FILE" "$OUTPUT_FILE" --debug

# 出力ファイルが生成されたか確認
if [ -f "$OUTPUT_FILE" ]; then
  echo "テスト成功: 出力ファイルが生成されました"
  echo "出力ファイルの内容:"
  echo "-----------------------------------"
  cat "$OUTPUT_FILE"
  echo "-----------------------------------"
else
  echo "テスト失敗: 出力ファイルが生成されませんでした"
  exit 1
fi

echo "テストが完了しました" 