# Feedis backend

## Setup a development station
1. install docker
2. install docker-compose
3. create a directory 'env' (it won't be pushed)

    a/ create a file django_variables.env
    
    b/ set:
    ```text
    SECRET_KEY=#SET A KEY#
    ```
    
    c/ create a file db_postgres_variables.env
    
    d/ set:
    ```text
    DB_USER=feedis
    DB_DATABASE=feedis
    DB_PASSWORD=#SET A PASSWORD#
    ```
        
4. docker-compose up --build -d 
5. docker-compose exec django /bin/bash
6. python manage.py migrate
7. python manage.py createsuperuser
        
        
## Structure
```
my_project
|-   env                                     # Apps env var
|-   my_project                              # All django logic
```

## Settings
Be careful when you need to work in the python's server console you should first launch.
```python
import django
django.setup()
```
Otherwise settings in console won't be populated.
See https://docs.djangoproject.com/en/2.1/topics/settings/.
(You can setup pycharm to do it automatically)
