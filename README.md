# Messenger [![CI/CD](https://github.com/VyacheslavShrot/SpaApp/actions/workflows/cd.yml/badge.svg)](https://github.com/VyacheslavShrot/SpaApp/actions/workflows/cd.yml)  <br>

- Backend Service - ![Pulls](https://img.shields.io/docker/pulls/vyacheslavshrot/spa_app_backend)<br>
- Celery Service - ![Pulls](https://img.shields.io/docker/pulls/vyacheslavshrot/spa_app_celery)<br><br>

- Backend part of the application working with users and functionality of comments, chats<br><br>
- I have described in detail how to use the APIs of this project in the Postman documentation :
  - https://documenter.getpostman.com/view/26500283/2sA2rGvKJz
<br><br>
- Also in the image on my Docker Hub is always the latest version of the code using the GitHub CD :
  - https://hub.docker.com/r/vyacheslavshrot/spa_app_backend
<br><br>
  - https://hub.docker.com/r/vyacheslavshrot/spa_app_celery

# Structure

- This project is written in the latest version of Python 3.11 along with the Django framework<br><br>

- All code is written in OOP<br><br>

- NoSQL database MongoDB is connected via official images
  - Django ORM was used to work with the database<br><br>

- WebSocket chat functionality is connected, i.e. Django Channels<br><br>

- Implemented queue functionality using Celery and RabbitMQ message broker<br><br>

- Caching is used in some cases<br><br>

- The JWT token is used to authenticate the user

# Launch in Docker-Compose

- Just a few steps are enough to do:
  - Copy the already prepared file docker-compose.yml to the folder<br><br>
  
  - At the level of this file, create an .env file where you write the following variables:
    - Write a SECRET_KEY variable for the JWT token ( it can be a random value )<br><br>

    - MONGO_INITDB_ROOT_USERNAME<br><br>

    - MONGO_INITDB_ROOT_PASSWORD<br><br>
    
    - MONGO_DB_AUTH_SOURCE ( for this variable usually 'admin' value is used)<br><br>
    
    - ME_CONFIG_MONGODB_ADMINUSERNAME ( use the same data as for image mongo )<br><br>

    - ME_CONFIG_MONGODB_ADMINPASSWORD ( use the same data as for image mongo )<br><br>
    
    - ME_CONFIG_MONGODB_SERVER=mongo<br><br>

  - After installing the environment, we run:
  ```
  docker-compose up -d
  ```
  
  - After successful launch in our project folder should be created 2 folders:
    - mongodb_data<br><br>
    
    - rabbitmq_data<br><br>
    
  - It means that all started well<br><br>
  
  - And the last step is to apply the migrations in the container:
  ```
  docker exec -it backend bash
  ```
  ```
  python src/manage.py migrate
  ```
  
- Now the backend part is ready to be used)

