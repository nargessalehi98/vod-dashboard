#!/bin/bash

docker run -d -p 27018:27017 --network=vod-network --name mongo mongo:latest
