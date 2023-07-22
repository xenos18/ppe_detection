FROM python:3.10-slim

COPY bot/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /bot

CMD ["python", "app.py"]