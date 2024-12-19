#!/bin/bash

docker build -t 'nginx_balance_image' .
docker run -itd --name nginx_balance -h nginx_balance -p 2000:2000 nginx_balance_image
docker update nginx_balance --restart=always