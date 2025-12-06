# Use official Node.js runtime as base image (version 14)
FROM node:14

# Set the working directory inside the container where commands will run
WORKDIR /usr/src/app

# Accept build arguments for environment variables
ARG REACT_APP_BACKEND_URL=http://localhost:3500/api/tasks

# Set environment variable from build argument
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

# Copy package.json and package-lock.json (if exists) from host to container
# The asterisk (*) means it will copy both files if they exist
COPY package*.json ./

# Install all dependencies listed in package.json
RUN npm install

# Copy all remaining files from current directory to the container's working directory
COPY . .

# Specify the default command to run when the container starts
CMD [ "npm", "start" ]
