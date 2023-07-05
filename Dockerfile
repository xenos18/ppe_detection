#
FROM python:3.10

#
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./app /code/app

#
#CMD ["uvicorn", "app.main:app", "--host", "127.0.0.0", "--port", "8500"]
