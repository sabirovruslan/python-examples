FROM python:3.6

# set working directory
WORKDIR /usr/src/

ENV STORE_DIR /usr/src/store

# add requirements (to leverage Docker cache)
ADD requirements.txt .

# install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD . .
