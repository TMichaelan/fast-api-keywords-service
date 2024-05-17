# Keyword Service

This is a simple Python service that receives on-going events of sentences and counts the occurrences of specific keywords: "checkpoint", "avanan", "email", and "security".

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Stress Testing](#stress-testing)
- [Linting](#linting)

## Installation

### Requirements
* Docker
* docker-compose

### Clone the repository
```sh
git clone https://github.com/TMichaelan/fast-api-keywords-service.git
cd fast-api-keywords-service
```
### Run docker-compose
```sh
docker-compose up --build
```

## Usage

### Example usage via CLI

#### Adding an event
```sh
curl -X POST 'http://localhost:8000/api/v1/events' -d 'Avanan is a leading Enterprise Solution for Cloud Email and Collaboration Security'
```
```sh
curl -X POST 'http://localhost:8000/api/v1/events' -d 'CheckPoint Research have been observing an enormous rise in email attacks since the beginning of 2020'
```

#### Getting statistics

```sh
curl 'http://localhost:8000/api/v1/stats?interval=60'
```

#### Response:
```json
{
    "checkpoint": 1,
    "avanan": 1,
    "email": 2,
    "security": 1
}
```

Interval is in seconds. The above command will return the statistics for the last 60 seconds. (*?interval=60*)

## Running Tests
```sh
docker-compose exec app pytest
```

## Stress Testing

### Setup venv
```sh
python3 -m venv venv
```
```sh
source venv/bin/activate
```
### Install Locust
```sh
pip install locust
```
### Start Locust
```sh
locust -f locustfile.py --host=http://localhost:8000
```
#### Open browser and go to http://localhost:8089
#### Set the number of users and spawn rate and click on "Start" button


## Linting
```sh
docker-compose exec app black .
```
```sh
docker-compose exec app mypy app
```
```sh
docker-compose exec app pylint app
```

![Build Status](https://github.com/TMichaelan/fast-api-keywords-service/actions/workflows/ci.yml/badge.svg)