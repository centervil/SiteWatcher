# タイムスタンプファイルの扱いについて改善

## 課題

*   `frontend/Dockerfile` 内でタイムスタンプファイル (`build_timestamp.txt`) が作成されているが、本番環境 (Github Pages) との差異が発生する。
*   メンテナンス性の問題。

## 初期提案

*   `frontend/Dockerfile` のbuild stageで `build_timestamp.txt` を作成するのをやめ、nginx stageにentrypoint scriptを追加してcontainer起動時に作成する。

## Github Pages環境への対応

*   Github Pagesはdocker containerとは異なり、静的ファイルを直接配信する環境であるため、Dockerfileの修正では対応できない。
*   Github Actionsのworkflow (`.github/workflows/deploy.yml`) を修正し、Github Pagesへのdeploy前に `build_timestamp.txt` を作成するstepを追加する。

## メンテナンス性の問題

*   タイムスタンプの作成処理がDockerfileとdeploy.yml に分散してしまうため、メンテナンス性が悪い。

## 最終的な解決策

*   `frontend/package.json` の build script に、`build_timestamp.txt` を作成する処理を追加する。
*   Dockerfileとworkflowファイルから、既存のタイムスタンプ作成処理を削除する。

## 実装

1.  `frontend/package.json` の修正:

    ```json
    "scripts": {
      "start": "http-server -p 3000",
      "build": "rm -rf build && mkdir build && date '+%Y-%m-%d %H:%M:%S' > build_timestamp.txt && cp *.html build/ && cp *.css build/ && cp *.js build/ && cp build_timestamp.txt build/ || { echo 'Build failed'; exit 1; }"
    },
    ```

2.  `frontend/Dockerfile` の修正:

    *   `RUN rm -f build_timestamp.txt && date '+%Y-%m-%d %H:%M:%S' > build_timestamp.txt` を削除。

3.  `.github/workflows/deploy.yml` の修正:

    *   修正不要。

## コミット

```bash
git add frontend/package.json frontend/Dockerfile
git commit -m "feat: Improve timestamp handling for build and deployment"
```

## 今後の課題

*   特になし。

## 考察

今回の修正では、タイムスタンプファイルの作成方法を改善し、本番環境と開発環境での差異を解消しました。また、build scriptに処理を集約することで、メンテナンス性を向上させることができました。
今後は、同様の問題が発生した場合、build scriptに処理を集約することを検討します。
