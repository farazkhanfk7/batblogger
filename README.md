# flask-blog [![Build Status](https://travis-ci.org/farazkhanfk7/blog-flask.svg?branch=main)](https://travis-ci.org/farazkhanfk7/blog-flask)
A simple blog app made using flask
> Continous Integration pipeline on Travis CI


## Setup project using Docker
* Clone repo : ```$ git clone https://github.com/farazkhanfk7/blog-flask.git```
* ```$ cd blog-flask```
* Build Docker Image : ```$ docker-compose build```
* Set environment variables with ```$ docker exec -i <containerid> <bash command>```
* Run container : ```$ docker-compose up```

## Setup project locally
> Use a virtual env
* Clone repo : ```$ git clone https://github.com/farazkhanfk7/blog-flask.git```
* ```$ cd blog-flask```
* Create a virtualenv: ```$ mkvirtualenv env``` or ```$ python -m venv env```
* Activate env : ```$ workon env``` or ```$ source env/bin/activate```
* Install dependencies : ```$ pip install -r requirements.txt``` and set environment variables
* Run project : ```$ python run.py```