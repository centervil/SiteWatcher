---
title: "2025-03-10 Docker環境で動く日記変換ツールの構築"
emoji: "📝"
type: "idea"
topics: ["開発日記", "Docker", "Python", "Gemini API", "自動化"]
published: false
---

:::message
この記事はClaude 3.7 Sonnetによって自動生成されています。
私の毎日の開発サイクルについては、[LLM対話で実現する継続的な開発プロセス](https://zenn.dev/centervil/articles/2025-03-12-development-cycle-introduction)をご覧ください。
:::

## はじめに

今日は、diary_converter.pyの動作確認のためのDocker環境構築に取り組みました。このツールは開発日記をZenn公開用の記事に変換するもので、Google Gemini APIを利用しています。ローカル環境での実行ではなく、Docker環境での実行に焦点を当てることで、環境依存の問題を解決し、より安定した動作を実現することができました。

## 開発の流れ

開発は以下の流れで進めました：

1. **Dockerfileの作成**：Python 3.9をベースイメージとして、必要なパッケージをインストールする環境を構築しました。
2. **docker-compose.ymlの設定**：diary-converterサービスを追加し、入力ディレクトリと出力ディレクトリをボリュームマウントしました。
3. **エントリーポイントスクリプトの作成**：柔軟な実行を可能にするためのdocker-entrypoint.shを作成しました。
4. **テスト環境の整備**：テスト用の入力ファイルとテスト実行スクリプトを作成しました。

## 課題と解決策

開発中にいくつかの課題に直面しましたが、それぞれ適切な解決策を見つけることができました。

### Docker環境でのパス解決

Docker環境でテスト実行時に入力ファイルが見つからないエラーが発生しました。これはDockerコンテナ内のパスとホスト環境のパスの不一致が原因でした。docker_test.shスクリプトのパス指定をDockerコンテナ内のパスに合わせて修正し、docker-compose.ymlにworking_dirを追加して作業ディレクトリを明示的に指定することで解決しました。

### Gemini APIのバージョン問題

「models/gemini-pro is not found for API version v1beta」というエラーが発生しました。これはGemini APIのバージョンに問題があることを示していました。diary_converter.pyを修正してAPIバージョンを明示的に指定しようとしましたが、使用しているgoogle-generativeaiライブラリのバージョンが古く、api_versionパラメータをサポートしていないという新たな問題が発生しました。

### ライブラリのバージョン更新

「__init__() got an unexpected keyword argument 'api_version'」というエラーに対応するため、requirements.txtを更新してgoogle-generativeaiのバージョンを0.4.0以上に指定し、APIの呼び出し方法も最新の仕様に合わせて更新しました。具体的には、GenerativeModelの初期化パラメータを修正し、generation_configとsafety_settingsを適切に設定しました。

## 技術的な詳細

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 実行権限を付与
RUN chmod +x diary_converter.py
RUN chmod +x docker-entrypoint.sh

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# エントリーポイントの設定
ENTRYPOINT ["/app/docker-entrypoint.sh"]
```

### docker-compose.yml

```yaml
services:
  # 既存のサービス...

  diary-converter:
    build:
      context: ./tools/diary-converter
    volumes:
      - ./tools/diary-converter:/app
      - ./Documents/ProjectLogs:/app/input
      - ./articles:/app/output
    environment:
      - GOOGLE_API_KEY
    working_dir: /app
```

### Gemini API呼び出し部分

```python
def convert_diary_with_gemini(content, date, model_name="gemini-pro"):
    """Gemini APIを使用して開発日記を変換する"""
    prompt = generate_prompt(content, date)
    
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
            # 他のsafety_settings...
        ]
        
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"エラー: Gemini API呼び出し中にエラーが発生しました: {e}")
        sys.exit(1)
```

## 今後の展望

今回の開発で、diary_converter.pyのDocker環境での動作確認が完了しました。今後は以下の課題に取り組む予定です：

1. **CI/CDパイプラインへの統合**：GitHub Actionsなどを使用して、自動テストと自動デプロイを実現します。
2. **Gemini API以外のLLM APIへの対応**：Claude APIなど、他のLLM APIにも対応させることで、より柔軟なツールにします。
3. **エラーハンドリングの改善**：より詳細なログ出力と適切なエラー処理を実装します。
4. **変換品質の向上**：プロンプトの最適化により、より高品質な変換結果を得られるようにします。
5. **定期的な自動変換処理の実装**：スケジュールに基づいて自動的に変換処理を実行する機能を追加します。

## 所感

Docker環境の構築は、最初はパスの問題やAPIバージョンの問題など、いくつかの障壁がありましたが、一つずつ解決していくことで、最終的には安定した動作環境を構築することができました。特に、ライブラリのバージョン更新による問題は、APIの仕様変更に追従することの重要性を再認識させられました。

また、Docker環境を使用することで、ローカル環境にツールをインストールすることなく開発を進められるという利点も実感しました。これにより、環境依存の問題を減らし、より再現性の高い開発環境を実現できています。

明日はCI/CDパイプラインへの統合を検討し、より自動化された開発フローの構築を目指します。このツールが完成すれば、開発日記の作成からZenn公開用記事への変換までの作業が大幅に効率化され、より多くの時間を本質的な開発作業に充てることができるようになるでしょう。 