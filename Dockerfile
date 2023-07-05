#

FROM python:3.10-slim

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade opencv-python
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#
WORKDIR /app

CMD ["python", "app.py"]