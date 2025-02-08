# Node.jsを使用してビルドする
FROM node:18 AS build

WORKDIR /usr/src/app

COPY package*.json ./

# http-serverをグローバルにインストール
RUN npm install -g http-server

RUN npm install

COPY . .

# 静的ファイルをビルド
RUN npm run build

# http-serverを使用して静的ファイルを提供
CMD ["http-server", "build", "-p", "3000"]

# Nginxを使用して静的ファイルを提供
# FROM nginx:alpine

# ビルドされたファイルをNginxのデフォルトの公開ディレクトリにコピー
# COPY --from=build /usr/src/app/build /usr/share/nginx/html

# Nginxを起動
# CMD ["nginx", "-g", "daemon off;"] 