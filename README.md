# Recipe API

## Overview

This is a Django-based application for recipe API. Check out the live version [https://recipe-ai.zalophus.site/](https://recipe-ai.zalophus.site/).

- For Admin Dashboard [https://recipe-ai.zalophus.site/admin](https://recipe-ai.zalophus.site/admin)

## Prerequisites

For Local Setup

- Python 3.8+
- pip
- Virtualenv (for creating a virtual environment)
- PostgreSQL
- Redis (as a Celery broker)

For Docker Setup

- Docker
- Docker Compose

## Local Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/thebishaldeb/recipe-api.git
   cd recipe-api
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**

   Copy the `.env.example` to `.env` file

   - replace the `EMAIL_USER` and `EMAIL_PASSWORD` with your gmail mail and app password and a value for `SECRET_KEY`

5. **Apply Migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**

   ```bash
   python manage.py runserver
   ```

   The application should now be running at [http://localhost:8000/](http://localhost:8000/).

   - http://localhost:8000/ has all the avaiable APIs.
   - http://localhost:8000/admin for admin login using the `email` and `password` created in the first step.

8. **Start Celery Worker and Beat**

   - In separate terminal windows, run the Celery worker and Celery Beat scheduler:

   ```bash
   python -m celery -A config worker -l info --without-gossip --pool=solo
   ```

   ```bash
   python -m celery -A config beat -l info
   ```

   - **_Celery Worker_**: Listens for and processes background tasks.

   - **_Celery Beat_**: Manages periodic tasks and schedules them to run at specified intervals.

## Running Tests

To test the application and check code coverage, follow these steps:

1. **Run Tests**

   ```bash
   coverage run -m pytest
   ```

   This command will run the tests and collect coverage data.

2. **Check Coverage Report**

   After running the tests, view the coverage report in different formats:

   - **HTML Report**

     Generate an HTML coverage report, which can be view in a web browser:

     ```bash
     coverage html
     ```

     The HTML report will be saved in the `htmlcov` directory by default. Open `htmlcov/index.html` in the web browser to view the detailed report.

   - **Terminal Report**

     Display a summary of the coverage directly in the terminal:

     ```bash
     coverage report -m
     ```

     The `-m` flag includes line numbers in the coverage report, showing which lines were missed.

3. **Clean Up Coverage Data**

   ```bash
   coverage erase
   ```

---

## Docker Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/thebishaldeb/recipe-api.git
   cd recipe-api
   ```

2. **Build Docker Images**

   Build the Docker images for the services:

   - PostgreSQL
   - Redis
   - Django server
   - Celery worker and celery beat

   ```bash
   docker-compose build
   ```

3. **Start PostgreSQL, Redis, and Django Server**

   Launch the PostgreSQL, Redis, and Django services:

   ```bash
   docker-compose up -d database redis django
   ```

   - The `-d` flag runs the containers in detached mode (background).
   - An admin user with email `admin@example.com` and password `admin` will be created automatically during the first run.
   - The migrations will be applied on the first run

4. **Start Celery Worker and Beat**

   Start the Celery worker and Celery Beat scheduler:

   ```bash
   docker-compose up -d worker scheduler
   ```

5. **Check Logs**

   To view the logs for any of the services, use:

   ```bash
   docker-compose logs <service_name>
   ```

   Replace `<service_name>` with `database`, `redis`, `django`, `worker`, or `scheduler` as needed.

6. **Stopping Services**

   To stop and remove all running containers, use:

   ```bash
   docker-compose down
   ```

7. **Managing Migrations**

   If you need to run migrations inside the Django container, use:

   ```bash
   docker-compose exec django python manage.py migrate
   ```

8. **Creating a Superuser**

   To create a superuser in the Django container, use:

   ```bash
   docker-compose exec django python manage.py createsuperuser
   ```

   Follow the prompts to create the superuser account.

9. **Accessing the Django Admin Interface**

   After starting the services, access the Django admin interface at [http://localhost:8000/admin](http://localhost:8000/admin) using the credentials for the admin user created earlier.

---
