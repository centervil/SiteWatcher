#!/bin/bash
# diary-converterのCI/CD統合をローカルでテストするスクリプト

set -e

# 色付きの出力関数
function print_info() {
  echo -e "\033[0;34m[INFO]\033[0m $1"
}

function print_success() {
  echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

function print_error() {
  echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# APIキーが設定されているか確認
if [ -z "$GOOGLE_API_KEY" ]; then
  print_error "GOOGLE_API_KEY 環境変数が設定されていません"
  echo "以下のコマンドを実行してください："
  echo "export GOOGLE_API_KEY=your_api_key_here"
  exit 1
fi

print_info "diary-converterのCI/CD統合テストを開始します"

# 最新の開発日記ファイルを検索
print_info "最新の開発日記ファイルを検索中..."
LATEST_DIARY=$(find ../../Documents/ProjectLogs -type f -name "*.md" | sort -r | head -n 1)

if [ -z "$LATEST_DIARY" ]; then
  print_error "開発日記ファイルが見つかりませんでした"
  exit 1
fi

print_success "最新の開発日記ファイルを発見: $LATEST_DIARY"

# 出力ファイル名を生成
DIARY_FILENAME=$(basename "$LATEST_DIARY")
DATE_PART=$(echo "$DIARY_FILENAME" | grep -oP '\d{4}-\d{2}-\d{2}')

# テーマ部分を抽出し、英数字のみに変換
THEME_PART=$(echo "$DIARY_FILENAME" | sed "s/${DATE_PART}-//g" | sed "s/.md$//g")

# 日本語を含むテーマをローマ字に変換
# 一般的な日本語→ローマ字変換のマッピング
if [[ "$THEME_PART" =~ [^\x00-\x7F] ]]; then
  # 日本語が含まれている場合、ローマ字に変換
  print_info "日本語テーマをローマ字に変換します: $THEME_PART"
  
  # 日本語→ローマ字の簡易変換（よく使われるパターンのみ）
  ROMAJI_THEME=$(echo "$THEME_PART" | 
    sed 's/組み込み/kumikomi/g' | 
    sed 's/連携/renkei/g' | 
    sed 's/開発/kaihatsu/g' | 
    sed 's/改善/kaizen/g' | 
    sed 's/テンプレート/template/g' | 
    sed 's/設定/settei/g' | 
    sed 's/最適化/saitekika/g' | 
    sed 's/統合/tougou/g' | 
    sed 's/自動/jidou/g' | 
    sed 's/記録/kiroku/g' | 
    sed 's/公開/koukai/g' | 
    sed 's/日記/nikki/g' | 
    sed 's/変換/henkan/g' | 
    sed 's/ツール/tool/g' | 
    sed 's/[^a-zA-Z0-9_-]/-/g') # 残りの非英数字をハイフンに変換
  
  SLUG_THEME=$ROMAJI_THEME
else
  # 既に英数字のみの場合はそのまま使用
  SLUG_THEME=$THEME_PART
fi

# Zennのslugルールに従って調整
# 1. 大文字を小文字に変換
SLUG_THEME=$(echo "$SLUG_THEME" | tr '[:upper:]' '[:lower:]')

# 2. 先頭に日付を追加
SLUG="${DATE_PART}-${SLUG_THEME}"

# 3. 文字数をチェック（拡張子を除いて12〜50字）
SLUG_LENGTH=${#SLUG}
if [ $SLUG_LENGTH -lt 12 ]; then
  # 12文字未満の場合、接尾辞を追加
  ADDITIONAL_CHARS=$((12 - SLUG_LENGTH))
  SUFFIX="-zenn-article"
  SLUG="${SLUG}${SUFFIX}"
  print_info "slugが短すぎるため接尾辞を追加: $SLUG"
elif [ $SLUG_LENGTH -gt 50 ]; then
  # 50文字を超える場合、切り詰め
  SLUG="${SLUG:0:50}"
  print_info "slugが長すぎるため切り詰め: $SLUG"
fi

# 最終的な出力ファイル名
OUTPUT_FILENAME="${SLUG}.md"
print_info "Zennのslugルールに準拠したファイル名: $OUTPUT_FILENAME"

print_info "処理対象: $DIARY_FILENAME"
print_info "出力ファイル: $OUTPUT_FILENAME"

# articlesディレクトリが存在するか確認
if [ ! -d "../../articles" ]; then
  print_info "articlesディレクトリが存在しないため作成します"
  mkdir -p ../../articles
fi

# テスト方法の選択
echo "テスト方法を選択してください："
echo "1) Dockerを使用したテスト"
echo "2) 直接実行によるテスト"
read -p "選択 (1/2): " TEST_METHOD

case $TEST_METHOD in
  1)
    print_info "Dockerを使用したテストを実行します"
    
    # Dockerがインストールされているか確認
    if ! command -v docker &> /dev/null; then
      print_error "Dockerがインストールされていません"
      exit 1
    fi
    
    print_info "Dockerを使用してdiary-converterを実行中..."
    docker build -t diary-converter .
    
    print_info "コンテナを実行中..."
    docker run --rm \
      -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
      -v $(pwd)/../../Documents:/app/Documents \
      -v $(pwd)/../../articles:/app/articles \
      diary-converter \
      "/app/Documents/ProjectLogs/$DIARY_FILENAME" \
      "/app/articles/$OUTPUT_FILENAME" \
      --model gemini-2.0-flash-001 \
      --template "/app/Documents/zenn_template.md" \
      --debug
    ;;
    
  2)
    print_info "直接実行によるテスト"
    
    # 必要なライブラリがインストールされているか確認
    if ! pip list | grep -q "google-generativeai"; then
      print_info "必要なライブラリをインストール中..."
      pip install -r requirements.txt
    fi
    
    print_info "スクリプトを実行中..."
    python diary_converter.py \
      "../../Documents/ProjectLogs/$DIARY_FILENAME" \
      "../../articles/$OUTPUT_FILENAME" \
      --model gemini-2.0-flash-001 \
      --template "../../Documents/zenn_template.md"
    ;;
    
  *)
    print_error "無効な選択です"
    exit 1
    ;;
esac

# 結果の確認
if [ -f "../../articles/$OUTPUT_FILENAME" ]; then
  print_success "変換が完了しました"
  print_info "出力ファイル: ../../articles/$OUTPUT_FILENAME"
  
  # 出力ファイルの先頭10行を表示
  echo "出力ファイルの先頭10行:"
  head -n 10 "../../articles/$OUTPUT_FILENAME"
else
  print_error "変換に失敗しました"
  exit 1
fi

print_info "テストが完了しました"
print_info "このテストはCI/CDパイプラインでの実行をシミュレートしています"
print_info "実際のCI/CDパイプラインでは、GitHub Secretsに'GOOGLE_API_KEY'を設定する必要があります" 