FROM python:3.10-slim

WORKDIR dep
COPY requirements.txt .
RUN apt-get update \
&& apt-get --assume-yes install build-essential \
&& apt-get install ffmpeg libsm6 libxext6  -y \
&& pip install -r requirements.txt

WORKDIR /app

CMD ["python", "main.py"]
