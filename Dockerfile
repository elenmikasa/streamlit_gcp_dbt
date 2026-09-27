FROM python:3.11-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをすべてコピー
COPY . .

# ポートの指定（Cloud Runの標準ポート8080）
EXPOSE 8080

# Streamlitの起動コマンド
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]