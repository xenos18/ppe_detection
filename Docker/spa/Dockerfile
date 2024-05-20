FROM node:lts-alpine

# устанавливаем простой HTTP-сервер для статики
RUN npm install -g http-server

# делаем каталог 'spa' текущим рабочим каталогом
WORKDIR /spa

# копируем оба 'package.json' и 'package-lock.json' (если есть)
COPY spa/package*.json ./

# устанавливаем зависимости проекта
RUN npm install