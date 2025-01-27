# 開発環境構築手順

## 目次
1. [目標](#目標)
2. [GitHubリポジトリのセットアップ](#githubリポジトリのセットアップ)
   - [フォルダ構成](#フォルダ構成)
   - [GitHub Pagesの設定](#github-pagesの設定)
3. [WSL2環境のセットアップ](#wsl2環境のセットアップ)
   - [インストール](#インストール)
   - [リポジトリのクローン](#リポジトリのクローン)
4. [Docker環境のセットアップ](#docker環境のセットアップ)
   - [用意する仮想環境](#用意する仮想環境)
   - [Dockerのインストール](#dockerのインストール)
5. [CI/CD環境の準備](#cicd環境の準備)

## 目標
- AWS環境を活用したアプリケーション開発のための開発環境を構築する。
- **要件**：
  1. ローカルのVSCodeでコード編集。
  2. VSCodeまたはブラウザですべての操作を完結。
  3. WSL2環境を極力シンプルにする。
  4. Dockerコンテナ化で環境をコード化し、再現性を確保。
  5. Docker内で開発を完結することで、依存関係を分離し再現性を向上。

## GitHubリポジトリのセットアップ

### フォルダ構成
1. プロジェクトのルートディレクトリを作成し、以下のようなフォルダ構成を用意します。
   ```
   SiteWatcher/
   ├── frontend/
   ├── backend/
   ├── docs/
   └── .github/
   ```

### GitHub Pagesの設定
1. GitHubに新しいリポジトリを作成します。
2. リポジトリの「Settings」タブに移動し、「Pages」セクションを見つけます。
3. 「Source」ドロップダウンメニューから「main branch」を選択し、フォルダとして「frontend」を指定します。
4. 設定を保存し、指定したURLでホスティングを確認します。

## WSL2環境のセットアップ

### インストール
1. **PowerShellを管理者権限で開く**。
2. 以下のコマンドを実行してWSL2を有効化：
   ```powershell
   wsl --install
   ```
3. **Ubuntuをインストール**：
   ```powershell
   wsl --install -d Ubuntu
   ```
4. Ubuntuを起動して初期設定（ユーザー名とパスワードを設定）。

### リポジトリのクローン
1. WSL2上で、以下のコマンドを実行してリポジトリをクローンします。
   ```bash
   git clone https://github.com/yourusername/SiteWatcher.git
   cd SiteWatcher
   ```

## Docker環境のセットアップ

### Dockerのインストール
1. **Docker Desktopのインストール**:
   - [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)をダウンロードしてインストールします。
   - Docker Desktopの設定で「WSL2バックエンド」を有効化します。

### 用意する仮想環境
- **フロントエンド**と**バックエンド**の2つの仮想環境を用意します。

#### フロントエンド環境
1. **Dockerfileの作成**:
   - プロジェクトのルートディレクトリ内の`frontend`フォルダに`Dockerfile`を作成します。ローカルのVSCodeで以下のファイルを編集します。
   - `frontend/Dockerfile`を開き、以下を記述します。
   ```dockerfile
   FROM node:18
   WORKDIR /usr/src/app
   COPY package*.json ./
   RUN npm install
   COPY . .
   EXPOSE 3000
   CMD ["npm", "start"]
   ```

#### バックエンド環境
1. **Dockerfileの作成**:
   - プロジェクトのルートディレクトリ内の`backend`フォルダに`Dockerfile`を作成します。ローカルのVSCodeで以下のファイルを編集します。
   - `backend/Dockerfile`を開き、以下を記述します。
   ```dockerfile
   FROM node:18
   WORKDIR /usr/src/app
   COPY package*.json ./
   RUN npm install
   COPY . .
   EXPOSE 4000
   CMD ["npm", "start"]
   ```

### docker-compose.ymlの作成
- プロジェクトのルートディレクトリに`docker-compose.yml`を作成します。ローカルのVSCodeで以下のファイルを編集します。
- `docker-compose.yml`を開き、以下を記述します。
```yaml
version: "3.8"
services:
  frontend:
    build:
      context: ./frontend
    volumes:
      - ./frontend:/usr/src/app
      - /usr/src/app/node_modules
    ports:
      - "3000:3000"
    stdin_open: true
    tty: true

  backend:
    build:
      context: ./backend
    volumes:
      - ./backend:/usr/src/app
      - /usr/src/app/node_modules
    ports:
      - "4000:4000"
    stdin_open: true
    tty: true
```

### Docker環境の起動方法
1. **Docker環境の起動**:
   - プロジェクトのルートディレクトリで以下のコマンドを実行します。
   ```bash
   docker-compose up -d
   ```
   - `-d`オプションは、コンテナをバックグラウンドで実行するためのものです。

2. **コンテナの状態確認**:
   - 起動したコンテナの状態を確認するには、以下のコマンドを実行します。
   ```bash
   docker-compose ps
   ```

3. **コンテナに入る**:
   - 確認したコンテナ名を使って、以下のようにコンテナに入ることができます。
   ```bash
   docker exec -it <コンテナ名> bash
   ```

例えば、`frontend`という名前のコンテナが実行中であれば、次のように実行します。
```bash
docker exec -it frontend bash
```

4. **Docker環境の停止**:
   - Docker環境を停止するには、以下のコマンドを実行します。
   ```bash
   docker-compose down
   ```

## CI/CD環境の準備
1. **GitHub Actionsの設定**:
   - リポジトリのルートに `.github/workflows` フォルダを作成し、`deploy.yml` ファイルを作成します。

2. **`deploy.yml`の例**:
   ```yaml
   name: Deploy to GitHub Pages

   on:
     push:
       branches:
         - main

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout code
           uses: actions/checkout@v2

         - name: Setup Node.js
           uses: actions/setup-node@v2
           with:
             node-version: '18'

         - name: Install dependencies
           run: npm install

         - name: Build project
           run: npm run build

         - name: Deploy to GitHub Pages
           uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./frontend
   ```

3. **GitHub Secretsの設定**:
   - リポジトリの「Settings」タブで「Secrets and variables」から「Actions」を選択し、必要なシークレットを設定します。

---