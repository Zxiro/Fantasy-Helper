# 使用 Python 3.9 的 Slim 映像檔
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製程式碼到映像檔
COPY bot.py config.py ./

# 安裝 Python 套件
RUN pip install python-telegram-bot

# 設定環境變數
ENV BOT_TOKEN=config.py.tg_token

# 執行 Bot
CMD ["python", "bot.py"]