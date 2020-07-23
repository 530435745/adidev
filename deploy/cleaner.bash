#!/bin/bash

PROJECTDIR=/home/adidev

exec ${PROJECTDIR}/env/bin/python -u ${PROJECTDIR}/adidev/cleaner_worker.py
