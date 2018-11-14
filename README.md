# My project

## To adapt
Resarch and rename every my_project by the name of your project. So as for first_app.


## Setup a development station
1. install docker
2. install docker-compose
3. Copy the .env.example file as .env and change the value as you want
4. docker-compose up --build -d 
This will launch the scripts in the django container beginning with wait_for_postgre.

Be careful if you want to launch a prod dev without a proxy redirecting the static request to webeeld/collected_static/ you will have some visual issue in your browser.
5. Test by going on http://localhost:8000
6. (Optionnal) In django container: python manage.py createsuperuser
    Then http://localhost:8000/admin and login with your superuser
        
        
        
## Structure (TO READ)
```
my_project
|-   apps
|-  |- app_name
|-  |-  |- contrib
|-  |-  |-  |- drf # Django rest framework
|-  |-  |-  |-  |- tests
|-  |-  |-  |-  |- serializers
|-  |-  |-  |-  |- urls
|-  |-  |-  |-  |- views
|-  |-  |- fixtures # for tests
|-  |-  |- tests
|-  |-  |- migrations 
|-  |-  |- __init__
|-  |-  |- ... (everything genereated by django-admin 
                startapp except from those move into contrib/drf)
|-   env                                     # Apps env var
|-   my_project                              # All settings for this project
```
1- As Django said, every app should be independent from the project that's why we put them in a different directory. It is really important to think each app as a gear that could be used by another system in the future.
2- Since we are using Django rest framework we set this contribution in each app in a subdirectory with every files changed by this contribution so as to be able to choose another contribution one day and know exactly what we have to alter.
3- So every script or tools of an app should stay at the root of the app directory.
But views must be moved in the drf directory. And urls could be moved or should redirect to another urls in drf.




## Using python in container
Always remember to use 
```bash
python manage.py shell
```
If not you will have to do at every launch after
```python
import django
django.setup()
```
Otherwise settings in console won't be populated.
See https://docs.djangoproject.com/en/2.1/topics/settings/.
(You can setup pycharm to do it automatically in order to use its console.)
