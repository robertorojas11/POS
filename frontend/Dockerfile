FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

EXPOSE 5173

# Vite dev server. For a real deployment build with `npm run build` and serve dist/ behind a reverse proxy.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
