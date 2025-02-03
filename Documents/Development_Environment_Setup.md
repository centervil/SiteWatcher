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
  1. ローカルのVSCodeでコード編集を行う。
  2. VSCodeまたはブラウザですべての操作を完結させる。
  3. WSL2環境を極力シンプルに保つ。
  4. Dockerコンテナ化で環境をコード化し、再現性を確保する。
  5. Docker内で開発を完結させることで、依存関係を分離し再現性を向上させる。

## GitHubリポジトリのセットアップ

### フォルダ構成
1. プロジェクトのルートディレクトリを作成し、以下のようなフォルダ構成を用意します。
   ```
   SiteWatcher/
   ├── frontend/
   ├── backend/
   ├── Documents/
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
- **フロントエンド**はGitHub Pagesを模した静的ホスティング環境を用意し、**バックエンド**はAWS LambdaとDynamoDBを使用するサーバーレス構成を模した仮想環境を用意します。

#### フロントエンド環境
1. **Dockerfileの作成**:
   - プロジェクトのルートディレクトリ内の`frontend`フォルダに`Dockerfile`を作成します。ローカルのVSCodeで以下のファイルを編集します。
   - `frontend/Dockerfile`を開き、以下を記述します。
   ```dockerfile
   # Node.jsを使用してビルドする
   FROM node:18 AS build

   WORKDIR /usr/src/app

   COPY package*.json ./

   RUN npm install

   COPY . .

   # 静的ファイルをビルド
   RUN npm run build

   # Nginxを使用して静的ファイルを提供
   FROM nginx:alpine

   # ビルドされたファイルをNginxのデフォルトの公開ディレクトリにコピー
   COPY --from=build /usr/src/app/build /usr/share/nginx/html

   # Nginxを起動
   CMD ["nginx", "-g", "daemon off;"]
   ```

#### バックエンド環境

バックエンド環境は、開発環境とテスト環境の2つに分かれています。

- **開発環境**:
  - **目的**: コードの編集と依存関係の管理。
  - **特徴**: Node.jsの通常の実行環境として動作し、Lambda特有の動作は模倣しません。
  - **使用**: `backend/Dockerfile`を使用して、ローカルでの迅速な開発サイクルをサポートします。

- **テスト環境**:
  - **目的**: AWS Lambdaの実行環境を模倣し、イベント駆動型の動作を確認。
  - **特徴**: Lambda関数がAWS上でどのように動作するかを模倣し、イベントデータを使って関数を実行します。
  - **使用**: AWS SAM CLIやLambCI Dockerイメージを使用して、Lambda特有の動作を確認します。

この2つの環境を使い分けることで、開発とテストの効率を最大化し、AWSにデプロイする前に関数の動作を確認できます。

1. **Dockerfileの作成**:
   - プロジェクトのルートディレクトリ内の`backend`フォルダに`Dockerfile`を作成します。ローカルのVSCodeで以下のファイルを編集します。
   - `backend/Dockerfile`を開き、以下を記述します。
   ```dockerfile
   # AWS Lambdaのローカル開発環境を構築するためのDockerfile

   FROM amazon/aws-lambda-nodejs:18

   # 作業ディレクトリを設定
   WORKDIR /var/task

   # package.jsonとpackage-lock.jsonをコピー
   COPY package*.json ./

   # 依存関係をインストール
   RUN npm install

   # アプリケーションコードをコピー
   COPY . .

   # Lambda関数のエントリーポイントを指定
   CMD ["app.handler"]
   ```

2. **DynamoDBローカルのセットアップ**:
   - DynamoDBをローカルで使用する場合は、AWSのDynamoDBローカルを使用します。
   - DynamoDBローカルのDockerイメージを使用して、以下のコマンドでコンテナを起動します。
   ```bash
   docker run -p 8000:8000 amazon/dynamodb-local
   ```

3. **バックエンドのローカルテスト**:
   - AWS LambdaのDockerイメージを使用して、以下のコマンドを実行します。
   ```bash
   docker run --rm -v "$PWD":/var/task lambci/lambda:nodejs18.x app.handler -e event.json
   ```

### AWS認証情報の取り扱い方法

AWSの認証情報は機密情報であり、適切に管理する必要があります。以下に、認証情報の取り扱い方法の候補を示します。

#### 1. .envファイル方式
- **概要**: 
  - 認証情報を`.env`ファイルに記載し、環境変数として読み込む方法です。
- **手順**:
  1. プロジェクトのルートディレクトリに`.env`ファイルを作成します。
  2. `.env`ファイルに以下のように認証情報を記載します。
     ```plaintext
     AWS_ACCESS_KEY_ID=your_access_key
     AWS_SECRET_ACCESS_KEY=your_secret_key
     AWS_REGION=your_region
     ```
  3. `.gitignore`に`.env`を追加し、Gitにコミットされないようにします。
- **メリット**: 簡単に設定でき、ローカル開発環境での使用に適しています。

#### 2. AWSのサービスを利用する方式
- **概要**: 
  - AWS Secrets ManagerやAWS Systems Manager Parameter Storeを使用して、認証情報を安全に管理する方法です。
- **手順**:
  1. AWSコンソールでSecrets ManagerまたはParameter Storeを設定し、認証情報を保存します。
  2. アプリケーションからAWS SDKを使用して、認証情報を動的に取得します。
- **メリット**: 認証情報をクラウド上で安全に管理でき、セキュリティが向上します。

#### 3. GitHubのサービスを利用する方式
- **概要**: 
  - GitHub ActionsのSecretsを使用して、認証情報を管理する方法です。
- **手順**:
  1. GitHubリポジトリの「Settings」タブで「Secrets and variables」から「Actions」を選択し、認証情報を追加します。
  2. GitHub Actionsのワークフロー内で、Secretsを参照して使用します。
- **メリット**: CI/CDパイプラインでの使用に適しており、GitHub上で安全に管理できます。

#### 選択する方式: .envファイル方式
- **理由**: 
  - ローカル開発環境での簡便さと設定の容易さから、`.env`ファイル方式を選択します。この方法は、開発者が迅速に環境をセットアップし、認証情報を安全に管理するのに適しています。

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

  dynamodb:
    image: amazon/dynamodb-local
    ports:
      - "8000:8000"
    command: "-jar DynamoDBLocal.jar -sharedDb"

  backend:
    build:
      context: ./backend
    volumes:
      - ./backend:/var/task
    environment:
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY
      - AWS_REGION
    command: ["app.handler"]
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