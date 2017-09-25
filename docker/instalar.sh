#!/bin/bash
cd /src/microservices_common
git pull
pip install --extra-index-url http://pypi.econo.unlp.edu.ar:8080/ microservices_common
