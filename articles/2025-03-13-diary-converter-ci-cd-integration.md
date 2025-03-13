---
title: "2025-03-13 開発日記: diary-converter-CI-CD組み込み"
emoji: "📝"
type: "tech"
topics: ["開発日記", "プログラミング", "CI/CD"]
published: false
---

:::message
この記事はgemini-2.0-flash-001によって自動生成されています。
:::

## はじめに

今日のテーマは、開発日記をZenn記事に変換する`diary_converter.py`をCI/CDパイプラインに組み込むことです。昨日はZenn公開用日記テンプレートの改善を行い、記事の品質向上を目指しました。今日は、そのテンプレートを活用し、自動化された記事生成の仕組みを構築します。

## 背景と目的

開発日記からZenn記事への変換作業は、これまで手動で行っていました。しかし、この作業は時間がかかり、人的ミスも発生しやすいという課題がありました。そこで、CI/CDパイプラインに`diary_converter.py`を組み込むことで、このプロセスを自動化し、効率的かつ高品質な記事生成を実現することを目指します。

## 検討内容

### 課題の整理

1. **CI/CDパイプラインへの組み込み**: `diary_converter.py`をGitHub Actionsのワークフローに組み込む方法を検討する必要があります。
2. **APIキーの安全な管理**: Gemini APIキーを安全に管理する方法を確立する必要があります。
3. **最新の日記の特定**: CI/CD環境で最新の開発日記を自動的に特定し、適切な出力ファイル名を生成する必要があります。
4. **ローカルでのテスト**: CI/CDパイプラインにプッシュする前にローカルでテストする方法が必要です。
5. **ファイルパスの問題**: Dockerコンテナ内でテンプレートファイルが見つからないエラーを解決する必要があります。

### 解決アプローチ

1. **GitHub Actionsワークフローの拡張**: 既存の`deploy.yml`ファイルに新しいジョブを追加し、Dockerを使用して`diary_converter.py`を実行します。
2. **GitHub Secretsの利用**: GitHub Secretsを使用してAPIキーを安全に管理し、環境変数としてコンテナに渡します。
3. **シェルスクリプトの活用**: `find`コマンドと`sort`を使用して最新の日記ファイルを特定し、ファイル名から日付とテーマを抽出して出力ファイル名を生成します。
4. **テストスクリプトの作成**: ローカルでCI/CD統合をテストするためのシェルスクリプトを作成し、Dockerを使用したテストと直接実行によるテストをサポートします。
5. **マウント設定の変更**: DockerコンテナにDocumentsディレクトリ全体をマウントするように設定を変更し、テンプレートファイルへのアクセスを可能にします。

## 実装内容

### GitHub Actionsワークフローの拡張

既存の`deploy.yml`ファイルに`diary-converter`ジョブを追加しました。このジョブは、Dockerを使用して`diary_converter.py`を実行し、最新の開発日記を自動的に変換してZenn記事として出力します。

```yaml
jobs:
  frontend-deploy:
    # ... (既存のジョブ)

  diary-converter:
    runs-on: ubuntu-latest
    needs: frontend-deploy
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python 3.9
        uses: actions/setup-python@v3
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run diary-converter
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        run: |
          # 最新の日記ファイルを特定
          LATEST_DIARY=$(find Documents -name "2025-*-*.md" | sort | tail -n 1)
          # 出力ファイル名を生成
          OUTPUT_FILE="articles/$(echo $LATEST_DIARY | grep -oP '2025-\d{2}-\d{2}')-$(echo $LATEST_DIARY | grep -oP 'diary-.*' | sed 's/diary-//g' | sed 's/.md//g').md"
          # diary-converterを実行
          docker run -v $(pwd):/app -e GOOGLE_API_KEY=$GOOGLE_API_KEY your-docker-image python diary_converter.py "$LATEST_DIARY" --output "$OUTPUT_FILE" --template "/app/Documents/zenn_template.md"
      - name: Commit and push changes
        run: |
          git config --global user.email "your-email@example.com"
          git config --global user.name "Your Name"
          git add .
          git commit -m "feat: Automated diary conversion"
          git push
```

### GitHub Secretsの利用

GitHub Secretsに`GOOGLE_API_KEY`を設定し、ワークフロー内で環境変数として利用できるようにしました。これにより、APIキーをコード内に直接記述することなく、安全に管理できます。

### シェルスクリプトの作成

ローカルでCI/CD統合をテストするためのシェルスクリプト`test_ci_integration.sh`を作成しました。このスクリプトは、Dockerを使用したテストと直接実行によるテストをサポートし、詳細なログ出力とエラーハンドリングを実装しています。

```bash
#!/bin/bash

# Dockerを使用するかどうか
USE_DOCKER=true

# APIキーを設定
export GOOGLE_API_KEY="YOUR_API_KEY"

# 最新の日記ファイルを特定
LATEST_DIARY=$(find Documents -name "2025-*-*.md" | sort | tail -n 1)

# 出力ファイル名を生成
OUTPUT_FILE="articles/$(echo $LATEST_DIARY | grep -oP '2025-\d{2}-\d{2}')-$(echo $LATEST_DIARY | grep -oP 'diary-.*' | sed 's/diary-//g' | sed 's/.md//g').md"

# Dockerを使用する場合
if [ "$USE_DOCKER" = true ]; then
  echo "Testing with Docker..."
  docker run -v $(pwd):/app -e GOOGLE_API_KEY=$GOOGLE_API_KEY your-docker-image python diary_converter.py "$LATEST_DIARY" --output "$OUTPUT_FILE" --template "/app/Documents/zenn_template.md"
# 直接実行する場合
else
  echo "Testing without Docker..."
  python diary_converter.py "$LATEST_DIARY" --output "$OUTPUT_FILE" --template "Documents/zenn_template.md"
fi

# 結果を確認
if [ $? -eq 0 ]; then
  echo "Test successful!"
else
  echo "Test failed."
  exit 1
fi
```

### マウント設定の変更

Dockerコンテナ内でテンプレートファイルが見つからないエラーが発生したため、Documentsディレクトリ全体をコンテナにマウントするように設定を変更しました。

```dockerfile
# Dockerfileの例
FROM python:3.9-slim-buster

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "diary_converter.py"]
```

## 技術的なポイント

*   **最新ファイルの特定**: `find`コマンドと`sort`コマンドを組み合わせることで、日付順にソートされたファイルリストから最新のファイル名を効率的に取得できます。
*   **ファイル名からの情報抽出**: `grep`コマンドと`sed`コマンドを使用することで、ファイル名から日付やテーマなどの必要な情報を抽出できます。
*   **Dockerコンテナ内でのパス解決**: Dockerコンテナ内でのファイルパスは、ホストOSとは異なるため、マウント設定を適切に行い、パスを修正する必要があります。

## 所感

今日の開発では、`diary_converter.py`をCI/CDパイプラインに組み込むという、少しハードルの高いタスクに挑戦しました。最初はGitHub ActionsのワークフローやDockerの設定に苦戦しましたが、一つずつ問題を解決していくうちに、自動化された記事生成の仕組みが完成していく過程に大きな達成感を感じました。特に、ローカルでのテスト環境を構築し、CI/CDパイプラインにプッシュする前に動作確認できたことは、品質向上に大きく貢献したと思います。

また、APIキーの安全な管理や、Dockerコンテナ内でのファイルパスの問題など、セキュリティや環境構築に関する知識も深めることができました。今回の経験を通じて、CI/CDパイプラインの重要性を改めて認識し、今後の開発においても積極的に活用していきたいと考えています。

## 今後の課題

1.  **エラーハンドリングの強化**: CI/CDパイプライン内で`diary_converter.py`が失敗した場合の適切なエラーハンドリングとリトライメカニズムの実装。
2.  **通知機能の追加**: 変換処理が完了したら、Slackやメールなどで通知する機能の追加。
3.  **定期実行の検討**: 定期的（例：毎日または毎週）に開発日記を変換するスケジュールジョブの設定。
4.  **変換結果の検証**: 変換されたZenn記事の品質を自動的にチェックする仕組みの導入。
5.  **GitHub Secretsの設定**: リポジトリ設定でGOOGLE_API_KEYのSecretを追加する必要がある。

## まとめ

今日の開発では、`diary_converter.py`をCI/CDパイプラインに組み込むための重要なステップを踏み出すことができました。GitHub Actionsワークフローの拡張、セキュリティ対策、自動化プロセスの構築、ドキュメント作成、テスト環境の構築、問題解決と改善など、多岐にわたる成果を得ることができました。

これにより、開発日記からZenn記事への変換プロセスが自動化され、手動操作によるミスを防止できるようになりました。今後は、エラーハンドリングの強化や通知機能の追加など、さらなる改善を進めていく予定です。