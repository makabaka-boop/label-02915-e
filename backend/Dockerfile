FROM python:3.11-slim

WORKDIR /app

# 安装中文字体（占位图回退方案需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple/

COPY . .

RUN chmod +x start.sh

EXPOSE 9999

CMD ["./start.sh"]
