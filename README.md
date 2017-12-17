# Precedent
A tool for finding OS projects which use a particular package


# Development
precedent consists of a React frontend which provides an interface to a Django-based backend API. The backend also makes use of Celery to handle async
requests for querying GitHub. The frontend was bootstrapped using the `create-react-app` project. This provides a simple config-free way of starting a 
project which requires a dynamic frontend. The backend requires a few additional application dependencies, namely:
* PostgreSQL
* Redis

To simplify the initial project setup process docker containers are used to deploy the backend dependencies in the development environment. This also 
makes it simple to test the application against a number of different versions of the dependencies. The process to get a development instance of 
precedent runnning is as follows:

    git clone https://github.com/lewisjared/precedent.git
    cd precedent
    npm install
    virtualenv venv
    source venv/bin/active
    pip install -r requirements.txt

    # If your node is not currently a member of a swarm:
    docker swarm init --advertise-addr=192.168.1.3
    # Create the Redis and postgres instances
    docker stack up -c docker-stack.yml precedent
    
Finally, once we have the stack setup, we can run the frontend and backend applications. These commands should be run in separate terminal prompts

    npm run start
    python manage.py runserver
    
The application will now be served on http://localhost:8000


# Tests
The tests can be run using:

    npm run test

# Contributors
