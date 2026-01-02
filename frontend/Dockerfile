FROM node:20-slim

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

# Install pnpm
RUN npm install -g pnpm

RUN pnpm install

CMD ["pnpm", "dev", "--host"]
