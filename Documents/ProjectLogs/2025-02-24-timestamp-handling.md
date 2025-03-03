---
title: "DockerfileとGitHub Pagesのタイムスタンプ問題 - build scriptへの集約"
emoji: "🛠️"
type: "tech"
topics: ["Dockerfile", "GitHub Pages", "タイムスタンプ", "build script"]
published: false
---

## 🤔 タイムスタンプ問題に直面！

## 課題

開発中にふと気づいたんです。「あれ？本番環境と開発環境でタイムスタンプが違う？」

調べてみると、`frontend/Dockerfile` で `build_timestamp.txt` を作成しているのが原因でした。Dockerfileで作成したファイルは、GitHub Pagesのような静的ファイル配信環境では更新されないため、環境差異が発生してしまうんですね。これはメンテナンス性も悪いです。

## 初期提案

最初に、`frontend/Dockerfile` のビルドステージで `build_timestamp.txt` を作成するのをやめることを考えました。その代わりに、nginxステージにエントリポイントスクリプトを追加して、コンテナ起動時にタイムスタンプファイルを作成する方法を検討しました。この方法により、Dockerfile自体をよりシンプルに保ちながら、タイムスタンプファイルの作成タイミングをコンテナ起動時に統一することが可能になります。

## 実装

今日の実装では、まず `frontend/package.json` を修正しました。具体的には、`build` スクリプトに `build_timestamp.txt` を作成する処理を追加しました。これにより、ビルド時に自動的にタイムスタンプファイルが生成されるようになりました。

```json
"scripts": {
  "start": "http-server -p 3000",
  "build": "rm -rf build && mkdir build && date '+%Y-%m-%d %H:%M:%S' > build_timestamp.txt && cp *.html build/ && cp *.css build/ && cp *.js build/ && cp build_timestamp.txt build/ || { echo 'Build failed'; exit 1; }"
},
```

次に、`frontend/Dockerfile` を修正し、不要になったタイムスタンプ作成の処理を削除しました。具体的には、以下の行を取り除きました。

*   `RUN rm -f build_timestamp.txt && date '+%Y-%m-%d %H:%M:%S' > build_timestamp.txt`

最後に、`.github/workflows/deploy.yml` に関しては、既にタイムスタンプ作成処理を `build` スクリプトに集約したため、追加の修正は不要と判断しました。

```bash
git add frontend/package.json frontend/Dockerfile
git commit -m "機能追加: ビルドとデプロイのタイムスタンプ処理を改善"
```

これで、タイムスタンプの生成プロセスが一元化され、メンテナンス性が向上しました。ビルドスクリプトに集中することで、Dockerfileやデプロイワークフローの複雑さを軽減することができました。

## 今後の課題

*   特になし。

## 所感

今回のタイムスタンプ問題に取り組んだことで、DockerfileとGitHub Pagesの環境差異について深く理解することができました。初めは簡単に解決策を思いつきましたが、実際に対応してみると、シンプルな解決は難しいことに気づきました。

特に、build scriptにタイムスタンプ作成処理を集約することで、メンテナンス性が格段に向上したのは大きな成果です。修正後、動作確認を何度も繰り返しながら問題を一つずつ解決していく過程で、実際の開発現場でのトラブルシューティング能力が身についたと感じています。

まだまだ改善の余地はありますが、今回の経験を通じて、より堅牢でメンテナンスしやすい開発環境を構築する自信がつきました。これからも、この経験を活かして、効率的かつ効果的な開発を目指していきたいと思います。
