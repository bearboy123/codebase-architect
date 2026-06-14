FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY src ./src
COPY public ./public
COPY index.html ./
COPY vite.config.ts tsconfig.json tsconfig.node.json tailwind.config.js postcss.config.js ./

# Change ownership of the app directory to the node user
RUN chown -R node:node /app

# Switch to node user
USER node

EXPOSE 3000

CMD ["npm", "run", "dev"]
