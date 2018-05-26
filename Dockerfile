FROM python:3

# set working directory
WORKDIR /usr/src/

# add requirements (to leverage Docker cache)
ADD requirements.txt .

# install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
