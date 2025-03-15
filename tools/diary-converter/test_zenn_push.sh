#!/bin/bash

# Zennリポジトリへのプッシュをテストするスクリプト
# 使用方法: ./test_zenn_push.sh [記事ファイル]

# 色付きの出力関数
print_info() {
  echo -e "\e[34m[INFO]\e[0m $1"
}

print_success() {
  echo -e "\e[32m[SUCCESS]\e[0m $1"
}

print_error() {
  echo -e "\e[31m[ERROR]\e[0m $1"
}

print_warning() {
  echo -e "\e[33m[WARNING]\e[0m $1"
}

# 環境変数のチェック
if [ -z "$ZENN_REPO" ]; then
  print_error "ZENN_REPO 環境変数が設定されていません"
  print_info "例: export ZENN_REPO=\"username/zenn-content\""
  exit 1
fi

if [ -z "$ZENN_REPO_TOKEN" ]; then
  print_error "ZENN_REPO_TOKEN 環境変数が設定されていません"
  print_info "例: export ZENN_REPO_TOKEN=\"ghp_xxxxxxxxxxxxxxxxxxxx\""
  exit 1
fi

# 一時ディレクトリの作成
TEMP_DIR=$(mktemp -d)
print_info "一時ディレクトリを作成しました: $TEMP_DIR"

# 終了時に一時ディレクトリを削除
cleanup() {
  print_info "一時ディレクトリを削除しています: $TEMP_DIR"
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# 記事ファイルの指定または検索
if [ -n "$1" ]; then
  ARTICLE_FILE="$1"
  if [ ! -f "$ARTICLE_FILE" ]; then
    print_error "指定された記事ファイルが見つかりません: $ARTICLE_FILE"
    exit 1
  fi
else
  print_info "記事ファイルが指定されていないため、最新の記事を検索します"
  ARTICLE_FILE=$(find ../../articles -type f -name "*.md" | sort -r | head -n 1)
  if [ -z "$ARTICLE_FILE" ]; then
    print_error "記事ファイルが見つかりません"
    print_info "articles ディレクトリに .md ファイルが存在するか確認してください"
    exit 1
  fi
fi

ARTICLE_FILENAME=$(basename "$ARTICLE_FILE")
print_info "処理対象の記事ファイル: $ARTICLE_FILENAME"

# Zennリポジトリのクローン
print_info "Zennリポジトリをクローンしています: $ZENN_REPO"
git clone "https://$ZENN_REPO_TOKEN@github.com/$ZENN_REPO.git" "$TEMP_DIR/zenn-repo" 2>/dev/null
if [ $? -ne 0 ]; then
  print_error "Zennリポジトリのクローンに失敗しました"
  print_info "ZENN_REPO と ZENN_REPO_TOKEN が正しいか確認してください"
  exit 1
fi
print_success "Zennリポジトリのクローンに成功しました"

# articlesディレクトリの存在確認
if [ ! -d "$TEMP_DIR/zenn-repo/articles" ]; then
  print_warning "Zennリポジトリに articles ディレクトリが存在しません"
  print_info "articles ディレクトリを作成します"
  mkdir -p "$TEMP_DIR/zenn-repo/articles"
fi

# 記事ファイルのコピー
print_info "記事ファイルをZennリポジトリにコピーしています"
cp "$ARTICLE_FILE" "$TEMP_DIR/zenn-repo/articles/"
if [ $? -ne 0 ]; then
  print_error "記事ファイルのコピーに失敗しました"
  exit 1
fi
print_success "記事ファイルのコピーに成功しました"

# 重複チェック
if [ $(find "$TEMP_DIR/zenn-repo/articles" -name "$ARTICLE_FILENAME" | wc -l) -gt 1 ]; then
  print_warning "同名の記事ファイルが既に存在します"
  print_info "既存のファイルを上書きします"
fi

# Gitの設定
cd "$TEMP_DIR/zenn-repo"
git config user.name "GitHub Actions Bot"
git config user.email "actions@github.com"

# 変更の確認
if [ -z "$(git status --porcelain)" ]; then
  print_warning "変更はありません"
  exit 0
fi

# 変更をコミット
print_info "変更をコミットしています"
git add "articles/$ARTICLE_FILENAME"
git commit -m "Add new article: $ARTICLE_FILENAME"
if [ $? -ne 0 ]; then
  print_error "コミットに失敗しました"
  exit 1
fi
print_success "コミットに成功しました"

# 変更をプッシュ
print_info "変更をプッシュしています"
if [ "$DRY_RUN" = "true" ]; then
  print_warning "ドライラン: プッシュはスキップされます"
  print_info "実際にプッシュするには DRY_RUN=false を設定してください"
else
  git push
  if [ $? -ne 0 ]; then
    print_error "プッシュに失敗しました"
    exit 1
  fi
  print_success "プッシュに成功しました"
  print_info "記事が正常にZennリポジトリにプッシュされました: $ARTICLE_FILENAME"
fi

exit 0 