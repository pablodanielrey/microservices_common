#!/bin/bash
cd /src/microservices_common
git pull
cd docker/src
#pip install -e .
#pip install --trusted-host pypi.econo.unlp.edu.ar --extra-index-url http://pypi.econo.unlp.edu.ar:8080/ microservices_common
python setup.py sdist upload -r internal
