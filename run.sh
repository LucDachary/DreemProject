#!/bin/sh
# This file has only one goal: run the worker's script.
# This could be achieved using the "command" property in the docker-compose service description,
# but it does not work because of the pipe symbol.
cat app.py | python -u manage.py shell
