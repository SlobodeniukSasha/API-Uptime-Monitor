# Health-Monitor API

API Uptime Monitor is a service that automates API endpoint availability checks.
It allows users to add their own URLs for monitoring, receive status information, response times, and errors, and
receive notifications in the event of failures.
---

## Setup Instructions

### Clone the repo

```bash
git clone https://github.com/SlobodeniukSasha/API-Uptime-Monitor
cd API-Health-Monitor
```

### Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Set up environment variables

#### Create .env based on .env.example:

### Run migrations

```
alembic revision --autogenerate -m "Initial DB"
alembic upgrade head
```

### Run the development server

```commandline
python manage.py runserver
```

### Swagger & ReDoc

* Swagger UI → http://localhost:8000/swagger/
* ReDoc → http://localhost:8000/redoc/

### Running tests

```commandline
pytest
```

### Docker

```
docker-compose up --build
```










