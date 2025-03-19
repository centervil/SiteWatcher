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
    parser.add_argument("--model", default="gemini-2.0-flash-001", help="使用するGeminiモデル名")
    parser.add_argument("--debug", action="store_true", help="デバッグモードを有効にする")
    parser.add_argument("--template", default="./templates/zenn_template.md", help="使用するテンプレートファイルのパス")
    parser.add_argument("--cycle-article", default="", help="開発サイクルの紹介記事へのリンク")
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

def read_template(template_path):
    """テンプレートファイルを読み込む"""
    try:
        # 相対パスを解決
        if not os.path.isabs(template_path):
            # スクリプトの実行ディレクトリからの相対パス
            script_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(script_dir, template_path)
        
        # テンプレートファイルの存在確認
        if not os.path.exists(template_path):
            print(f"エラー: テンプレートファイル '{template_path}' が見つかりません")
            print(f"カレントディレクトリ: {os.getcwd()}")
            print(f"スクリプトディレクトリ: {os.path.dirname(os.path.abspath(__file__))}")
            print(f"ディレクトリ内容:")
            
            # テンプレートファイルのディレクトリを確認
            template_dir = os.path.dirname(template_path)
            if os.path.exists(template_dir):
                print(f"{template_dir} の内容:")
                for item in os.listdir(template_dir):
                    print(f"  - {item}")
            else:
                print(f"ディレクトリ '{template_dir}' が見つかりません")
                
                # 親ディレクトリを確認
                parent_dir = os.path.dirname(template_dir)
                if os.path.exists(parent_dir):
                    print(f"{parent_dir} の内容:")
                    for item in os.listdir(parent_dir):
                        print(f"  - {item}")
                else:
                    print(f"親ディレクトリ '{parent_dir}' も見つかりません")
            
            sys.exit(1)
            
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"エラー: テンプレートファイル読み込み中にエラーが発生しました: {e}")
        print(f"テンプレートファイル '{template_path}' が見つかりません。")
        sys.exit(1)

def extract_date_from_filename(file_path):
    """ファイル名から日付を抽出する"""
    filename = os.path.basename(file_path)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        return date_match.group(1)
    return datetime.now().strftime("%Y-%m-%d")

def extract_theme_from_filename(file_path):
    """ファイル名からテーマを抽出する"""
    filename = os.path.basename(file_path)
    # 日付部分を除去
    theme_part = re.sub(r'\d{4}-\d{2}-\d{2}-', '', filename)
    # 拡張子を除去
    theme = os.path.splitext(theme_part)[0]
    return theme

def generate_prompt(content, date, theme, model_name, cycle_article_link="", template_content=None):
    """Gemini APIに送信するプロンプトを生成する"""
    if not template_content:
        print("エラー: テンプレート内容が提供されていません")
        sys.exit(1)
        
    # テンプレートからfrontmatterを抽出
    template_fm = None
    try:
        # frontmatterライブラリを使用してfrontmatterを抽出
        post = frontmatter.loads(template_content)
        template_fm = post.metadata
        
        if not template_fm:
            print("警告: テンプレートからfrontmatterを抽出できませんでした。デフォルト値を使用します。")
            template_fm = {
                "title": f"{date} [テーマ名]",
                "emoji": "📝",
                "type": "tech",
                "topics": ["開発日記", "プログラミング"],
                "published": False
            }
        else:
            print(f"テンプレートからfrontmatterを抽出しました: {template_fm}")
    except Exception as e:
        print(f"警告: テンプレートからfrontmatterを抽出できませんでした: {e}")
        template_fm = {
            "title": f"{date} [テーマ名]",
            "emoji": "📝",
            "type": "tech",
            "topics": ["開発日記", "プログラミング"],
            "published": False
        }
    
    # テンプレートの記述ガイドラインを抽出
    guidelines_match = re.search(r'## 記述ガイドライン.*', template_content, re.DOTALL)
    guidelines = guidelines_match.group(0) if guidelines_match else ""
    
    # テンプレートの構造を抽出（frontmatterとガイドライン部分を除く）
    template_structure = template_content
    if guidelines_match:
        template_structure = template_content.split(guidelines_match.group(0))[0]
    
    # frontmatterを除去
    template_structure = re.sub(r'^---\n.*?\n---\n', '', template_structure, flags=re.DOTALL)
    
    # LLMモデル名と開発サイクル紹介記事のリンクを設定
    llm_model_info = f"この記事は{model_name}によって自動生成されています。"
    cycle_article_info = ""
    if cycle_article_link:
        cycle_article_info = f"私の毎日の開発サイクルについては、{cycle_article_link}をご覧ください。"
    
    # テーマ名を設定
    theme_name = theme.replace("-", " ").title()
    
    # frontmatterテンプレート
    frontmatter_template = f"""---
title: "{date} {theme_name}"
emoji: "{template_fm.get('emoji', '📝')}"
type: "{template_fm.get('type', 'tech')}"
topics: {template_fm.get('topics', ['開発日記', 'プログラミング'])}
published: {str(template_fm.get('published', False)).lower()}
---"""

    # メッセージボックステンプレート
    message_box_template = f""":::message
{llm_model_info}
{cycle_article_info}
:::"""
    
    prompt = f"""以下の開発日記を、Zenn公開用の記事に変換してください。

# 入力された開発日記
{content}

# 変換ルール
1. 「会話ログ」セクションは、対話形式ではなく、ストーリー形式に書き直してください
2. 技術的な内容は保持しつつ、読みやすく整理してください
3. 「所感」セクションを充実させ、開発者の視点や感想を追加してください
4. マークダウン形式を維持し、コードブロックなどは適切に整形してください
5. 記事の先頭に以下のfrontmatterを追加してください：

{frontmatter_template}

6. frontmatterの直後に以下のメッセージボックスを追加してください：

{message_box_template}

# テンプレート構造
以下のテンプレート構造に従って記事を作成してください。各セクションの目的と内容を理解し、開発日記の内容に合わせて適切に変換してください：

{template_structure}

# 記述ガイドライン
{guidelines}

# 出力形式
frontmatterを含むマークダウン形式の完全な記事を出力してください。テンプレートの構造に従いつつ、開発日記の内容を適切に反映させてください。
以下の点に注意してください：
1. コードブロックは必要な場合のみ使用し、記事全体をコードブロックで囲まないでください
2. 記事の先頭や末尾に余分なコードブロックマーカー（```）を付けないでください
3. 記事の先頭に```markdownなどの言語指定を付けないでください
"""
    return prompt

def convert_diary_with_gemini(content, date, theme, model_name, cycle_article_link="", template_content=None):
    """Gemini APIを使用して開発日記を変換する"""
    prompt = generate_prompt(content, date, theme, model_name, cycle_article_link, template_content)
    
    try:
        # 最新バージョンのライブラリに対応した呼び出し方法
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        response = model.generate_content(prompt)
        
        # 余分なコードブロックマーカーを削除
        converted_text = response.text.strip()
        if converted_text.startswith("```markdown"):
            converted_text = converted_text[len("```markdown"):].strip()
        elif converted_text.startswith("```"):
            converted_text = converted_text[3:].strip()
        if converted_text.endswith("```"):
            converted_text = converted_text[:-3].strip()
            
        return converted_text
    except Exception as e:
        print(f"エラー: Gemini API呼び出し中にエラーが発生しました: {e}")
        sys.exit(1)

def save_converted_article(content, file_path):
    """変換された記事を保存する"""
    try:
        # 出力先ディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(file_path)
        print(f"出力先ディレクトリ: {output_dir}")
        print(f"出力先ディレクトリの存在確認: {os.path.exists(output_dir)}")
        
        if not os.path.exists(output_dir):
            print(f"出力先ディレクトリを作成します: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
            print(f"出力先ディレクトリの作成完了: {os.path.exists(output_dir)}")
        
        print(f"ファイルを保存します: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"変換された記事を {file_path} に保存しました")
        
        # ファイルの存在確認
        if os.path.exists(file_path):
            print(f"ファイルの保存を確認しました: {file_path}")
            print(f"ファイルサイズ: {os.path.getsize(file_path)} bytes")
        else:
            print(f"警告: ファイルが保存されていません: {file_path}")
            
    except Exception as e:
        print(f"エラー: ファイル保存中にエラーが発生しました: {e}")
        print(f"エラーの詳細: {str(e)}")
        print(f"現在の作業ディレクトリ: {os.getcwd()}")
        print(f"出力先パス: {file_path}")
        print(f"出力先ディレクトリの存在: {os.path.exists(os.path.dirname(file_path))}")
        sys.exit(1)

def main():
    """メイン処理"""
    args = parse_arguments()
    
    # 開発日記を読み込む
    source_content = read_source_diary(args.source)
    
    # ファイル名から日付とテーマを抽出
    date = extract_date_from_filename(args.source)
    theme = extract_theme_from_filename(args.source)
    
    # テンプレートを読み込む
    template_content = read_template(args.template)
    
    # デバッグモードの場合
    if args.debug:
        print(f"ソースファイル: {args.source}")
        print(f"抽出された日付: {date}")
        print(f"抽出されたテーマ: {theme}")
        print(f"使用モデル: {args.model}")
        print(f"テンプレートファイル: {args.template}")
        print(f"開発サイクル紹介記事リンク: {args.cycle_article}")
    
    # Gemini APIで変換
    converted_content = convert_diary_with_gemini(
        source_content, 
        date, 
        theme, 
        args.model, 
        args.cycle_article, 
        template_content
    )
    
    # 変換結果を保存
    save_converted_article(converted_content, args.destination)
    
    print("変換が完了しました")

if __name__ == "__main__":
    main()
