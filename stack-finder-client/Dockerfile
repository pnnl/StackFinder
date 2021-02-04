FROM node:10

# Set the working dir
WORKDIR /usr/src/app

# Copy in the req file
COPY package*.json ./

# Install before adding code so cache is not invalidated
RUN npm install

# I need react-scripts
RUN npm install -g react-scripts

# Copy in the code
COPY . .