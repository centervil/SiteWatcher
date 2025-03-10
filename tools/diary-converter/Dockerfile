FROM python:3.9-slim

WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 実行権限を付与
RUN chmod +x diary_converter.py
RUN chmod +x docker-entrypoint.sh

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# エントリーポイントの設定
ENTRYPOINT ["/app/docker-entrypoint.sh"] 