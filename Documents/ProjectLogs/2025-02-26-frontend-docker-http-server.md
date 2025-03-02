## 2025-02-26 Frontend タイムスタンプ表示位置修正、JST対応、および Docker frontend 表示問題解決ログ

### 目的

1.  frontend/index.html のタイムスタンプ表示位置を画面中央から右下へ変更し、目立たないようにする。
2.  タイムスタンプを UTC 表示から JST 表示に変更する。
3.  Docker Compose で起動した frontend サービスが `http://localhost:3000` で表示されない問題を解決する。
4.  開発環境と Docker 環境でのフロントエンド serve 方法を `http-server` に統一し、`live-server` の Docker 環境での利用を停止する。

### 検討事項

1.  **HTML タイムスタンプ表示位置修正:**  `frontend/index.html` のタイムスタンプ表示位置を CSS で右下に変更する。
2.  **タイムスタンプ JST 対応:**  JavaScript (`frontend/app.js`) で UTC タイムスタンプを JST に変換する処理を追加する。
3.  **Docker frontend 表示問題:**  `docker-compose up -d frontend --build` 後、`http://localhost:3000` にアクセスしても "このページは動作していません" というエラー画面が表示される。
4.  **原因究明:**  `docker-compose.yml`, `frontend/Dockerfile`, `frontend/package.json` を精査し、設定の問題点を特定する。
5.  **`live-server` から `http-server` への移行:**  開発環境と Docker 環境でのフロントエンド serve 方法を `http-server` に統一し、`live-server` の Docker 環境での利用を停止する。

### 実行内容

1.  **HTML/CSS の修正 (タイムスタンプ表示位置と JST 対応):**
    -   `frontend/styles.css` を修正し、`#build-timestamp-footer` のスタイルを定義して右下に配置。
    -   `frontend/app.js` を修正し、タイムスタンプを UTC から JST に変換して表示するように変更。
    -   `frontend/index.html` は変更なし。
2.  **動作確認 (Docker 環境) - 1回目 (失敗):**  `docker-compose up -d frontend --build` を実行し、`http://localhost:3000` にアクセスして動作確認を試みるも、"このページは動作していません" というエラー画面が表示され、表示に失敗。
3.  **原因究明 - 1回目:**  `docker-compose.yml`, `frontend/Dockerfile`, `frontend/package.json` を精査し、`docker-compose.yml` の frontend サービスの `ports` 設定が `"80:80"` になっていることを発見。ポートマッピングの誤りを疑う。`docker-compose logs frontend` でログを確認するも、エラーは見当たらず。
4.  **docker-compose.yml の修正 (ポートマッピング修正):**  `docker-compose.yml` の frontend サービスの `ports` 設定を `"3000:3000"` に修正。
5.  **動作確認 (Docker 環境) - 2回目 (失敗):**  再度 `docker-compose up -d frontend --build` を実行し、`http://localhost:3000` にアクセスして動作確認を試みるも、依然として "このページは動作していません" というエラー画面が表示され、表示に失敗。
6.  **frontend/Dockerfile の修正 (http-server への変更) - 1回目:**  `frontend/Dockerfile` の CMD を `live-server` から `http-server build --port 3000` に変更。`live-server` が Docker 環境に不向きである可能性を考慮し、`http-server` への変更を試みる。
7.  **動作確認 (Docker 環境) - 3回目 (失敗):**  再度 `docker-compose up -d frontend --build` を実行し、`http://localhost:3000` にアクセスして動作確認を試みるも、やはり "このページは動作していません" というエラー画面が表示され、表示に失敗。
8.  **frontend/Dockerfile の修正 (live-server に戻す):**  Dockerfile を `live-server` を使用する設定に一旦戻し、`live-server` 自体に問題がないか確認するため、Dockerfile の CMD を `CMD ["npm", "start"]` に戻す。
9.  **動作確認 (Docker 環境) - 4回目 (失敗):**  再度 `docker-compose up -d frontend --build` を実行し、`http://localhost:3000` にアクセスして動作確認を試みるも、状況変わらず "このページは動作していません" というエラー画面が表示され、表示に失敗。
10. **原因究明 - 2回目 (ログ詳細確認):**  再度 `docker-compose logs frontend` を注意深く確認したところ、`Need to install the following packages: http-server@14.1.1` というログを発見。`http-server` が Docker イメージにインストールされていないことが判明。Dockerfile で `npx http-server` を使用しているにも関わらず、`http-server` が見つからないため、毎回インストールに失敗している可能性に気づく。
11. **frontend/Dockerfile の修正 (`http-server` インストール - server stage):**  Dockerfile の `server` ステージに `RUN npm install -g http-server` を追加し、`server` ステージで `http-server` が利用できるように修正。また、CMD を `CMD ["http-server", "--port", "3000"]` に修正し、`npx` を削除。
12. **frontend/package.json の修正 (`start` スクリプト変更):**  `frontend/package.json` の `scripts` セクションの `start` コマンドを `live-server` から `http-server build --port=3000` に変更。`devDependencies` から `live-server` を削除。開発環境と Docker 環境で `http-server` を統一する。
13. **動作確認 (Docker 環境) - 5回目 (成功):**  `docker-compose up -d frontend --build` を再度実行し、`http://localhost:3000` で SiteWatcher が正しく表示されることを確認。問題解決を確認。

### 今回の議論で得られた知見

*   **`live-server` の Docker 環境での不適合性:**  `live-server` はホットリロードなど開発用途に特化しており、Docker コンテナ内で serve する用途には適していない。
*   **`http-server` の Docker 環境への適合性:**  `http-server` は軽量であり、Docker コンテナ内でビルドされた静的ファイルを serve するのに適している。
*   **npm start スクリプトと Dockerfile CMD の役割分担:**  `npm start` はローカル開発環境用、Dockerfile CMD は Docker コンテナ内での実行用と、それぞれの役割を明確に区別し、混同しないようにする必要がある。
*   **Docker マルチステージビルドにおけるパッケージインストール:**  マルチステージビルドでは、各ステージは独立しているため、パッケージをインストールするステージを間違えると、意図したステージでパッケージが利用できなくなる。`CMD` で実行するコマンドに必要なパッケージは、そのコマンドが実行されるステージにインストールする必要がある。
*   **エラーログの重要性:**  エラーが解消しない場合、ログを注意深く確認することで、問題の原因特定につながることがある。

### 結論

frontend/index.html のタイムスタンプ表示位置と JST 対応に加え、Docker コンテナの表示問題を解決するために、Dockerfile と frontend/package.json を修正し、Docker 環境でのフロントエンド serve を `http-server` に統一した。開発には Docker 環境を使用する方針に基づき、今後は `live-server` を Docker 環境で使用せず、開発環境と Docker 環境で `http-server` を使い分ける。
