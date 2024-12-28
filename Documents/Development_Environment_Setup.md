# **開発環境構築手順**

## **目標**
- AWS環境を活用したアプリケーション開発のための開発環境を構築する。
- **要件**：
  1. ローカルのVSCodeでコード編集。
  2. VSCodeまたはブラウザですべての操作を完結。
  3. WSL2環境を極力シンプルにする。
  4. Dockerコンテナ化で環境をコード化し、再現性を確保。
  5. Docker内で開発を完結することで、依存関係を分離し再現性を向上。

---

## **ステップ 1: WSL2の準備**

### **ステップ 1.1: WSL2のインストール**
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

---

### **ステップ 1.2: 必要なツールのインストール**
1. **Ubuntuにログイン**し、以下を実行：
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y git curl unzip
   ```

---

## **ステップ 2: Dockerの準備**

### **ステップ 2.1: Docker Desktopのインストール**
1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)をダウンロードしてインストール。
2. Docker Desktopの設定で「WSL2バックエンド」を有効化。
   - **Settings → General → Use the WSL 2 based engine** をオン。
3. DockerのWSL2統合を有効化：
   - **Settings → Resources → WSL Integration** でUbuntuを有効にする。

### **ステップ 2.2: Docker Composeのインストール確認**
Docker DesktopにDocker Composeが含まれているため、以下でバージョンを確認：
```bash
docker-compose --version
```

---

## **ステップ 3: Docker環境のセットアップ**

### **ステップ 3.1: WSL2上での作業**
以下の作業はすべて**WSL2環境**で実行します。

1. **プロジェクトのディレクトリを作成**
   ```bash
   mkdir -p ~/SiteWatcher
   cd ~/SiteWatcher
   ```

2. **Dockerfileの作成**
   ```bash
   nano Dockerfile
   ```
   以下を記述し保存：
   ```dockerfile
   FROM node:18
   WORKDIR /usr/src/app
   COPY package*.json ./
   RUN npm install
   COPY . .
   EXPOSE 3000
   CMD ["npm", "start"]
   ```

3. **docker-compose.ymlの作成**
   ```bash
   nano docker-compose.yml
   ```
   以下を記述し保存：
   ```yaml
   version: "3.8"
   services:
     frontend:
       build: .
       volumes:
         - .:/usr/src/app
         - /usr/src/app/node_modules
       ports:
         - "3000:3000"
       stdin_open: true
       tty: true
   ```

4. **Dockerイメージのビルド**
   ```bash
   docker compose build
   ```

5. **Dockerコンテナの起動**
   ```bash
   docker compose up -d
   ```

6. **Dockerコンテナに入る**
   ```bash
   docker exec -it sitewatcher_frontend_1 bash
   ```

---

## **ステップ 4: Node.jsプロジェクトのセットアップ**

以下の手順は、**Dockerコンテナ内**で行います。

1. **`package.json`の初期化**
   ```bash
   npm init -y
   ```

2. **必要なパッケージのインストール**
   ```bash
   npm install lite-server --save-dev
   ```

3. **`scripts`セクションの更新**
   `package.json`の`scripts`セクションに以下を追加：
   ```json
   "scripts": {
       "start": "lite-server"
   }
   ```

4. **サンプルHTMLファイルの作成**
   ```bash
   mkdir public
   echo "<!DOCTYPE html><html><head><title>SiteWatcher</title></head><body><h1>Welcome to SiteWatcher!</h1></body></html>" > public/index.html
   ```

5. **ローカルサーバーの起動**
   ```bash
   npm start
   ```

---

## **ステップ 5: 開発環境の使用**

### **ステップ 5.1: ブラウザで確認**
- ローカル環境でサーバーを起動すると、`http://localhost:3000`でアプリを確認できます。

### **ステップ 5.2: コンテナの管理**
- 停止：
  ```bash
  docker compose down
  ```
- 再起動：
  ```bash
  docker compose up -d
  ```

---
