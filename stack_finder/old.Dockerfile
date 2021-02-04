FROM python:3

WORKDIR /usr/src/app

ARG secret
ARG id

# setup environment
RUN apt-get -y update; \
    apt-get -y upgrade; \
    pip3 install setuptools

ENV CLIENT_SECRET=${secret}
ENV CLIENT_ID=${id}

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . ./

ENTRYPOINT [ "python3", "stack_finder.py" ]