FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY src ./src
COPY public ./public
COPY vite.config.ts tsconfig.json tsconfig.node.json ./

EXPOSE 3000

CMD ["npm", "run", "dev"]
