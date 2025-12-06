# Use official Node.js runtime as base image (version 14)
FROM node:14

# Set the working directory inside the container where commands will run
WORKDIR /usr/src/app

# Copy package.json and package-lock.json (if exists) from host to container
# The asterisk (*) means it will copy both files if they exist
COPY package*.json ./

# Install all dependencies listed in package.json
RUN npm install

# Copy all remaining files from current directory to the container's working directory
COPY . .

# Specify the default command to run when the container starts
# This starts the Node.js server using index.js as the entry point
CMD ["node", "index.js"]