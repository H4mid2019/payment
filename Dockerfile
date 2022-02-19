FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN apt-get upgrade && apt-get update -y && apt-get install postgresql postgresql-contrib -y
COPY . /app