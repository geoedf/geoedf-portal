FROM python:3.10
USER root
SHELL ["/bin/bash", "-c"]
RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install python3 -y && apt-get install python3-pip -y &&\
    pip3 install -U --pre django-globus-portal-framework
COPY . /code/
EXPOSE 8000

# 入口
ENTRYPOINT python3 manage.py runserver 0.0.0.0:8000