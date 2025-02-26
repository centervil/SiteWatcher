FROM node:18 AS builder

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

FROM node:18-alpine AS server

WORKDIR /usr/share/nginx/html

COPY --from=builder /usr/src/app/build .

RUN npm install -g http-server

EXPOSE 3000

CMD ["http-server", "--port", "3000"]
