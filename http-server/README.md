## ООП

Для запуска через makefile требуется установленный docker

Команды make необходимо выполнять из корневой директории проекта

### Запуск сервера

```
make server
```

### Результаты unit тестов

```
make test 
docker build -t otus-http-server-test .
Sending build context to Docker daemon   16.9kB
Step 1/7 : FROM python:3
 ---> 29d2f3226daf
Step 2/7 : WORKDIR /usr/src/
 ---> Using cache
 ---> 9d22cf073a32
Step 3/7 : ADD requirements.txt .
 ---> Using cache
 ---> 17d8bda85d32
Step 4/7 : RUN apt-get update && apt-get install -y memcached telnet && apt-get clean
 ---> Using cache
 ---> f0d9a5eb217b
Step 5/7 : RUN pip install --upgrade pip
 ---> Using cache
 ---> fbaadcf0d66b
Step 6/7 : RUN pip install -r requirements.txt
 ---> Using cache
 ---> 373f9347a468
Step 7/7 : ADD . .
 ---> Using cache
 ---> 5c0f29d532c8
Successfully built 5c0f29d532c8
Successfully tagged otus-http-server-test:latest
docker run -it --rm --link server:server otus-http-server-test python httptest.py
directory index file exists ... ok
document root escaping forbidden ... ok
Send bad http headers ... ok
file located in nested folders ... ok
absent file returns 404 ... ok
urlencoded filename ... ok
file with two dots in name ... ok
slash after filename ... ok
query string after filename ... ok
filename with spaces ... ok
Content-Type for .css ... ok
Content-Type for .gif ... ok
Content-Type for .html ... ok
Content-Type for .jpeg ... ok
Content-Type for .jpg ... ok
Content-Type for .js ... ok
Content-Type for .png ... ok
Content-Type for .swf ... ok
head method support ... ok
directory index file absent ... ok
large file downloaded correctly ... ok
post method forbidden ... ok
Server header exists ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.032s

OK

```

### Результаты ab тестов 4 воркера 60s

```
ab -n 100000 -c 100 -r -s 60  http://127.0.0.1/httptest/dir2/
This is ApacheBench, Version 2.3 <$Revision: 1706008 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 10000 requests
Completed 20000 requests
Completed 30000 requests
Completed 40000 requests
Completed 50000 requests
Completed 60000 requests
Completed 70000 requests
Completed 80000 requests
Completed 90000 requests
Completed 100000 requests
Finished 100000 requests


Server Software:        Otus-http-server
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /httptest/dir2/
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   27.751 seconds
Complete requests:      100000
Failed requests:        3
   (Connect: 0, Receive: 1, Length: 1, Exceptions: 1)
Total transferred:      15099849 bytes
HTML transferred:       3399966 bytes
Requests per second:    3603.46 [#/sec] (mean)
Time per request:       27.751 [ms] (mean)
Time per request:       0.278 [ms] (mean, across all concurrent requests)
Transfer rate:          531.36 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.3      0      12
Processing:     0   22 304.2      2   27738
Waiting:        0   22 304.2      2   27738
Total:          0   23 304.3      3   27749

Percentage of the requests served within a certain time (ms)
  50%      3
  66%      3
  75%      3
  80%      4
  90%      5
  95%      6
  98%     11
  99%   1019
 100%  27749 (longest request)

```

### Результаты ab тестов 4 воркера
```
ab -n 100000 -c 100 -r http://127.0.0.1/httptest/dir2/
This is ApacheBench, Version 2.3 <$Revision: 1706008 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 10000 requests
Completed 20000 requests
Completed 30000 requests
Completed 40000 requests
Completed 50000 requests
Completed 60000 requests
Completed 70000 requests
Completed 80000 requests
Completed 90000 requests
Completed 100000 requests
Finished 100000 requests


Server Software:        Otus-http-server
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /httptest/dir2/
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   21.769 seconds
Complete requests:      100000
Failed requests:        0
Total transferred:      15100000 bytes
HTML transferred:       3400000 bytes
Requests per second:    4593.65 [#/sec] (mean)
Time per request:       21.769 [ms] (mean)
Time per request:       0.218 [ms] (mean, across all concurrent requests)
Transfer rate:          677.38 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.4      0      15
Processing:     0   21 153.7      2    3864
Waiting:        0   21 153.7      2    3864
Total:          0   21 153.8      2    3874

Percentage of the requests served within a certain time (ms)
  50%      2
  66%      3
  75%      3
  80%      3
  90%      4
  95%      6
  98%     12
  99%   1022
 100%   3874 (longest request)

```