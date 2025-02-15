# Node.js 18の公式イメージを使用
FROM node:18

# 作業ディレクトリを設定
WORKDIR /usr/src/app

# package.json と package-lock.json を先にコピー（キャッシュを活用）
COPY package.json package-lock.json ./

# 依存関係をインストール（npm install よりも再現性の高い npm ci を使用）
RUN npm ci

# ソースコードをコピー
COPY . .

# ビルドスクリプトを実行（エラー時に握りつぶさない）
RUN npm run build && \
    echo "Contents of build directory:" && \
    ls -la build

# コンテナ外部に公開するポートを指定
EXPOSE 3000

# アプリケーションの起動
CMD ["npm", "start"]
