FROM python:3.10-alpine

COPY requirements.txt requirements.txt

RUN /usr/local/bin/python3.10 -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt 

# Cmake is a dependency for building libgit2

RUN apk update && apk add bash

COPY . .
