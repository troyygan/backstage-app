FROM node:24-alpine

WORKDIR /app

# Leverage layer caching: install deps first, then copy source.
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY . .

ENV PORT=3000
EXPOSE 3000

USER node

CMD ["node", "server.js"]
