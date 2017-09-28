#!/bin/bash
sudo docker run --rm -ti --name microservices_common -v $(pwd)/src:/src microservices_common bash
