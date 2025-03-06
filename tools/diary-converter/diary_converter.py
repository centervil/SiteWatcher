#!/usr/bin/env python3
"""
開発日記変換ツール

ProjectLogs以下の開発日記をLLM API（Gemini）を利用して加工し、
articles配下にZenn公開用日記として配置するスクリプト
"""

import os
import sys
import argparse
import frontmatter
import google.generativeai as genai
from datetime import datetime
import re

# Gemini APIキーの設定
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    print("エラー: GOOGLE_API_KEY 環境変数が設定されていません")
    sys.exit(1)

genai.configure(api_key=API_KEY)

def parse_arguments():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(description="開発日記をZenn公開用に変換するツール")
    parser.add_argument("source", help="変換元の開発日記ファイルパス")
    parser.add_argument("destination", help="変換先のZenn記事ファイルパス")
    parser.add_argument("--model", default="gemini-pro", help="使用するGeminiモデル名")
    parser.add_argument("--debug", action="store_true", help="デバッグモードを有効にする")
    return parser.parse_args()

def read_source_diary(file_path):
    """開発日記ファイルを読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"エラー: ファイル読み込み中にエラーが発生しました: {e}")
        sys.exit(1)

def extract_date_from_filename(file_path):
    """ファイル名から日付を抽出する"""
    filename = os.path.basename(file_path)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        return date_match.group(1)
    return datetime.now().strftime("%Y-%m-%d")

def generate_prompt(content, date):
    """Gemini APIに送信するプロンプトを生成する"""
    prompt = f"""
以下の開発日記を、Zenn公開用の記事に変換してください。

# 入力された開発日記
{content}

# 変換ルール
1. 「会話ログ」セクションは、対話形式ではなく、ストーリー形式に書き直してください
2. 技術的な内容は保持しつつ、読みやすく整理してください
3. 「所感」セクションを充実させ、開発者の視点や感想を追加してください
4. マークダウン形式を維持し、コードブロックなどは適切に整形してください
5. 以下のfrontmatterを記事の先頭に追加してください：
   - title: "{date} 開発日記: [記事の内容を表す簡潔なタイトル]"
   - emoji: "📝"
   - type: "tech"
   - topics: ["開発日記", "プログラミング"]
   - published: false

# 出力形式
frontmatterを含むマークダウン形式の完全な記事を出力してください。
"""
    return prompt

def convert_diary_with_gemini(content, date, model_name="gemini-pro"):
    """Gemini APIを使用して開発日記を変換する"""
    prompt = generate_prompt(content, date)
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"エラー: Gemini API呼び出し中にエラーが発生しました: {e}")
        sys.exit(1)

def save_converted_article(content, file_path):
    """変換された記事を保存する"""
    try:
        # 出力先ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"変換された記事を {file_path} に保存しました")
    except Exception as e:
        print(f"エラー: ファイル保存中にエラーが発生しました: {e}")
        sys.exit(1)

def main():
    """メイン処理"""
    args = parse_arguments()
    
    # 開発日記を読み込む
    source_content = read_source_diary(args.source)
    
    # ファイル名から日付を抽出
    date = extract_date_from_filename(args.source)
    
    # デバッグモードの場合
    if args.debug:
        print(f"ソースファイル: {args.source}")
        print(f"抽出された日付: {date}")
        print(f"使用モデル: {args.model}")
    
    # Gemini APIで変換
    converted_content = convert_diary_with_gemini(source_content, date, args.model)
    
    # 変換結果を保存
    save_converted_article(converted_content, args.destination)
    
    print("変換が完了しました")

if __name__ == "__main__":
    main() 