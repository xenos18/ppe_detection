FROM python:3.10-slim

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt


WORKDIR /app

CMD ["python", "app.py"]