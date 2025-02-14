FROM node:18

# 作業ディレクトリを設定
WORKDIR /usr/src/app

# package.json と package-lock.json を先にコピーして依存関係をインストール（キャッシュ利用のため）
COPY package*.json ./
RUN npm install

# ソースコードをすべてコピー
COPY . ./

# build スクリプトを実行して、静的ファイルを build ディレクトリに生成
RUN npm run build && echo "Contents of build directory:" && ls -la build || echo "Build failed"

# コンテナ外部に公開するポートを指定
EXPOSE 3000

# package.json の start スクリプト (http-server を起動) を使ってサーバーを開始
CMD ["npm", "start"]