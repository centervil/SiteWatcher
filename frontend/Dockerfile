# ビルドステージ
FROM node:18 AS builder

WORKDIR /usr/src/app

COPY package.json ./
RUN npm install

RUN date '+%Y-%m-%d %H:%M:%S' > build_timestamp.txt

COPY . .
RUN npm run build

# 配信ステージ
FROM nginx:latest

# buildステージから成果物をコピー
COPY --from=builder /usr/src/app/build /usr/share/nginx/html

# ポート80でnginxをlisten (デフォルト)
# EXPOSE 80 は不要 (nginx:latest イメージがデフォルトでEXPOSE 80 を設定している)

CMD ["nginx", "-g", "daemon off;"]
