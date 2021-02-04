FROM node:latest AS UI

#COPY ./ /usr/src/app
ADD ./ /usr/src/app
WORKDIR /usr/src/app/stack-finder-client
## get npm packages
RUN npm install i
RUN npm run build

# copy build stuff from UI build and 
# pass it onto the server
FROM python:3 AS SERVER
#ADD ./ /usr/src/app
COPY --from=UI /usr/src/app /usr/src/app
WORKDIR /usr/src/app/stack_finder
RUN pip3 install -r requirements.txt


