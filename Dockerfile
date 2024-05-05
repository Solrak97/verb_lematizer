# syntax=docker/dockerfile:1

FROM ubuntu:22.04
#COPY . /app


RUN apt-get update \
&& apt-get -y install wget


RUN wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.12.1-amd64.deb &&\
dpkg -i elasticsearch-8.12.1-amd64.deb &&\
systemctl start elasticsearch &&\
systemctl enable elasticsearch

CMD python /app/app.py