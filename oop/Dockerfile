FROM python:3

# set working directory
WORKDIR /usr/src/

# add requirements (to leverage Docker cache)
ADD requirements.txt .

RUN apt-get update && apt-get install -y memcached && apt-get clean

# install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD . .
