#!/bin/bash

PROJECTDIR=/home/adidev

exec ${PROJECTDIR}/env/bin/python -u ${PROJECTDIR}/adidev/collector_worker.py
