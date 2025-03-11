```markdown
---
title: "2025-03-11 開発日記: diary_converter.pyのDocker環境構築"
emoji: "📝"
type: "tech"
topics: ["開発日記", "Docker", "Python"]
published: false
---

:::message
この記事はgemini-2.0-flash-001によって自動生成されています。
:::

## はじめに

本日は、開発日記をZenn公開用の記事に変換するツール `diary_converter.py` の動作確認を行うためのDocker環境構築に取り組みました。このツールはGoogle Gemini APIを利用しており、その動作を安定させるための環境構築が急務です。

## 背景と目的

これまで、開発日記の形式を整える作業に手間がかかっていました。`diary_converter.py` はこの作業を自動化するためのツールですが、ローカル環境での動作確認だけでは不十分です。Docker環境を構築することで、再現性が高く、安定した環境で動作確認を行えるようにすることが目的です。

## 検討内容

### 課題の整理

1.  **Docker環境の構築**: `diary_converter.py` を実行するための環境が必要です。
2.  **ボリュームマウントの設定**: 入力ファイルと出力ファイルのパスを適切に設定する必要があります。

### 解決アプローチ

1.  **Dockerfileの作成**: Python 3.9をベースイメージとして使用し、必要なパッケージをインストールするDockerfileを作成します。
2.  **docker-compose.ymlの設定**: ボリュームマウントを設定し、入力ディレクトリと出力ディレクトリを指定します。

## 実装内容

まずは、Dockerfileを作成しました。

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "diary_converter.py"]
```

次に、docker-compose.ymlを作成し、ボリュームマウントを設定しました。

```yaml
version: "3.9"
services:
  app:
    build: .
    volumes:
      - ./input:/app/input
      - ./output:/app/output
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

これにより、ローカルの`input`ディレクトリがコンテナ内の`/app/input`に、ローカルの`output`ディレクトリがコンテナ内の`/app/output`にマウントされます。

## 技術的なポイント

Dockerfileでは、`pip install --no-cache-dir -r requirements.txt` を使用して、キャッシュを使用せずにパッケージをインストールしています。これにより、Dockerイメージのサイズを削減できます。

また、docker-compose.ymlでは、環境変数 `GOOGLE_API_KEY` を設定しています。これにより、APIキーをソースコードに直接記述せずに、安全に管理できます。

## 所感

Docker環境の構築は、一見すると手間がかかるように思えますが、一度構築してしまえば、環境の違いによる問題を気にせずに開発を進めることができます。特に、`diary_converter.py` のように外部APIを利用するツールの場合、APIキーの管理や環境変数の設定が重要になるため、Docker環境は非常に有効です。

今回の作業を通して、Dockerの基本的な使い方を再確認することができました。また、docker-compose.ymlを使用することで、複数のコンテナを連携させる方法についても理解が深まりました。

## 今後の課題

1.  **テストケースの作成と実行**: `diary_converter.py` の動作を検証するためのテストケースを作成し、実行する必要があります。
2.  **エラーハンドリングの改善**: エラーが発生した場合に、より詳細な情報を出力するように改善する必要があります。
3.  **他のLLM APIへの対応検討**: Google Gemini APIだけでなく、他のLLM APIにも対応できるように検討する必要があります。

## まとめ

本日は、`diary_converter.py` の動作確認のためのDocker環境を構築しました。Dockerfileとdocker-compose.ymlを作成し、必要なボリュームマウントを設定しました。これにより、開発日記をZenn公開用の記事に変換する作業が効率化されます。今後は、テストケースの作成やエラーハンドリングの改善など、より実用的なツールにするための改善を進めていきます。
