#!/bin/bash
set -e

# APIキーが設定されているか確認
if [ -z "$GOOGLE_API_KEY" ]; then
  echo "エラー: GOOGLE_API_KEY 環境変数が設定されていません"
  exit 1
fi

# 引数が正しく渡されているか確認
if [ "$#" -lt 2 ]; then
  echo "使用方法: $0 <入力ファイル> <出力ファイル> [--model モデル名] [--debug]"
  echo "例: $0 input/2025-03-10-Claude-Cursor連携開発.md output/2025-03-10-claude-cursor.md"
  exit 1
fi

# 入力ファイルと出力ファイルのパスを設定
INPUT_FILE="$1"
OUTPUT_FILE="$2"
shift 2

# 残りの引数をそのまま渡す
python /app/diary_converter.py "$INPUT_FILE" "$OUTPUT_FILE" "$@" 