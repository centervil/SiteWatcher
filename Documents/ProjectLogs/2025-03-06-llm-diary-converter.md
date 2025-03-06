# 2025-03-06 LLM APIを利用した開発日記自動加工スクリプトの開発

## 今日の開発テーマ

今日の開発テーマは、ProjectLogs以下の開発日記をLLM APIを利用して加工し、articles配下にZenn公開用日記として配置するスクリプトのプロトタイプ作成です。

## 会話ログ

- ユーザー: この内容で進めましょう。今日は、zenn公開用に変換するスクリプトのプロトタイプを作成するところまで進めたいです。その他は明日以降にしましょう。では、テーマが決まったところで、今日の開発日記を作ってください。今後の対話は開発日記に記録してください。
- Claude: 了解しました。今日のテーマは「LLM APIを利用した開発日記の自動加工スクリプトのプロトタイプ作成」に決定しました。開発日記を作成しました。これから、スクリプト開発を進めていきましょう。まず、どのLLM APIを利用するか検討する必要があります。OpenAI API、Anthropic Claude API、その他のAPIなど選択肢がありますが、どのAPIを利用する予定でしょうか？また、スクリプトの実装言語は何を想定されていますか？
- ユーザー: まずは無料利用できるGeminiのAPIを使います。スクリプトの実装言語は何でもいいですが、CI/CDパイプラインから実行しやすいものがいいですね
- Claude: Gemini APIを使用し、CI/CDパイプラインから実行しやすい言語を選ぶという方針ですね。GitHub Actionsの環境を考慮すると、Node.jsかPythonが適していると思います。どちらもGitHub Actionsの標準環境で利用可能で、Gemini APIのクライアントライブラリも充実しています。個人的にはPythonをお勧めします。理由は以下の通りです：

1. Gemini APIのPythonクライアントライブラリが公式でサポートされている
2. テキスト処理に強く、マークダウンの解析や生成が容易
3. GitHub Actionsでの実行環境が整っている
4. 依存関係の管理が比較的シンプル

Pythonで実装する場合、以下のような構成が考えられます：

1. `diary_converter.py`: メインスクリプト
2. 必要なライブラリ: 
   - `google-generativeai`: Gemini APIクライアント
   - `markdown`: マークダウン処理
   - `pyyaml`: frontmatter処理

この構成でよろしいでしょうか？または別の言語/構成をご希望でしたら、お知らせください。

- ユーザー: これでよいです。実際に作ってください。
- Claude: 了解しました。提案した構成に基づいて、必要なディレクトリとファイルを作成します。まず、ディレクトリ構造を作成し、次に各ファイルの内容を実装していきます。

まず、ディレクトリ構造を作成します：

```
tools/
  diary-converter/
    diary_converter.py
    requirements.txt
    README.md
```

それでは各ファイルを作成していきます：

```python:tools/diary-converter/diary_converter.py
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
```

```text:tools/diary-converter/requirements.txt
google-generativeai>=0.3.0
pyyaml>=6.0
python-frontmatter>=1.0.0
```

```markdown:tools/diary-converter/README.md
# 開発日記変換ツール

このツールは、ProjectLogs以下の開発日記をLLM API（Gemini）を利用して加工し、articles配下にZenn公開用日記として配置するためのスクリプトです。

## 使い方

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

## 機能

- マークダウン形式の開発日記を読み込み
- Gemini APIを使用して内容を加工
- Zenn公開用の形式に変換（frontmatter付き）
- 変換結果を指定先に保存
```

これでプロトタイプの実装は完了しました。このスクリプトは以下の機能を持っています：

1. 開発日記ファイルを読み込む
2. ファイル名から日付を抽出
3. Gemini APIを使用して開発日記をZenn公開用に変換
4. 変換結果を指定先に保存

このスクリプトを実行するには、Gemini APIキーを環境変数 `GOOGLE_API_KEY` に設定する必要があります。また、必要なライブラリをインストールするために `pip install -r requirements.txt` を実行する必要があります。

何か修正や追加が必要な点はありますか？
ユーザー: 今日の作業はここまでにします。明日は、作成したスクリプトのローカルでの動作確認を行います。その後、必要に応じてスクリプトを修正し、完成させる予定です。CI/CDパイプラインへの組み込みは、明後日以降に取り組む予定です。

Claude: 承知しました。今日はLLM APIを利用した開発日記自動加工スクリプトのプロトタイプ作成が完了しました。明日は以下の予定で進めましょう：

- 作成したスクリプトのローカルでの動作確認
- 必要に応じたスクリプトの修正・改善
- スクリプトの完成

CI/CDパイプラインへの組み込みは明後日以降ですね。

今日の成果として、以下のファイルを作成しました：

- `tools/diary-converter/diary_converter.py`
- `tools/diary-converter/requirements.txt`
- `tools/diary-converter/README.md`

お疲れ様でした。明日の開発も楽しみにしています。

## 課題

- ProjectLogs以下の開発日記をZenn公開用に変換するスクリプトのプロトタイプ作成
- Gemini APIの利用方法の調査と実装
- 変換ルールの設計
- CI/CD環境での実行を考慮したスクリプト設計
- スクリプトを配置する適切なディレクトリ構造の決定

## 解決策

- Gemini APIを利用したPythonスクリプトを実装
- `tools/diary-converter/` ディレクトリに以下のファイルを作成:
  - `diary_converter.py`: 開発日記変換スクリプト
  - `requirements.txt`: 必要なライブラリの一覧
  - `README.md`: 使用方法の説明
- 変換ルールをプロンプトとして実装
- コマンドライン引数でソースとデスティネーションを指定できる設計
- 環境変数でAPIキーを設定する方式を採用

## 所感

- Gemini APIを利用することで、開発日記の変換作業を自動化できそうです
- プロンプトエンジニアリングが重要な要素となり、適切な指示を与えることで質の高い変換が期待できます
- 今回はプロトタイプとして基本機能を実装しましたが、今後はエラーハンドリングの強化やテスト機能の追加が必要かもしれません
- CI/CD環境での実行を考慮し、環境変数でAPIキーを設定する方式を採用しました
``` 