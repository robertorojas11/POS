FROM node:20-alpine

WORKDIR /app

# Copy package requirements
COPY package*.json ./

# Install packages
RUN npm install

# Copy application files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server, allowing outside access via --host 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
