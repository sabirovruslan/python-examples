FROM golang:latest

RUN mkdir -p /usr/src/app/

# set working directory
WORKDIR /usr/src/app/

ADD . .

RUN go build -o memc_load .

CMD ["./memc_load"]
