# Use Node.js 20
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy frontend code
COPY . .

# Build the React app
RUN npm run build

# Serve the app using serve
RUN npm install -g serve

# Expose port 3000
EXPOSE 3000

# Run the app
CMD ["serve", "-s", "build", "-l", "3000"]