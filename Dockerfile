FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /social_networking_app

WORKDIR /social_networking_app

ADD . /social_networking_app/

RUN pip install -r requirements.txt
