#!/bin/bash

docker run  -d -p 8000:8000 --network=vod-network --restart always --volume /var/log/docker:/vod-dashboard/logs --volume "$(pwd)":/code --name vod vod:v3