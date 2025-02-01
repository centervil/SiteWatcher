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