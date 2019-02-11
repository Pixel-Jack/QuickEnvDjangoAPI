# YOUR_PROJECT-api
API server as backend.


## Adapt for your project
Search for these terms and adapt the code with what you want: (case insensitive)
- YOUR_PROJECT
- YOUR_DOMAIN
- YOUR_NO_REPLY_EMAIL
- YOUR_CONTACT_EMAIL

## Architecture
See the whole architecture scheme [here](docs/architecture.md).


## Guideline first install
1. Finish this document
2. Read this [one](CONTRIBUTING.md)
3. Then run 
```bash
make settings
vim .env
```
4. Fill this file with your settings.
5. Run ```make```

## Development 
This will launch the scripts in the django container beginning with wait_for_postgre.sh
5. Test by going on http://localhost:8000
6. (Optionnal) In django container: ```python manage.py createsuperuser```
    Then http://localhost:8000/admin and login with your superuser
        
## Staging and Prod
In order to be able to launch the staging architecture in the same host than prod (For test purpose)
we must adapt some part. 
The code must NOT change, only docker-compose file are allowed to change.  
Staging ports are the same as prod shift by +10000. So when you add a new service be sure to put this shift in the 
docker-compose.staging.yml

## Structure (TO READ)
```
YOUR_PROJECT
|-   apps
|-  |- app_name
|-  |-  |- contrib
|-  |-  |-  |- drf # Django rest framework: so basically put every files that import rest_framework
|-  |-  |-  |-  |- tests
|-  |-  |-  |-  |- serializers
|-  |-  |-  |-  |- views
|-  |-  |- fixtures # for tests
|-  |-  |- tests
|-  |-  |- migrations 
|-  |-  |- __init__
|-  |-  |- urls
|-  |-  |- models
|-  |-  |- ... (everything genereated by django-admin 
                startapp except from those move into contrib/drf)
|-   env                                     # Apps env var
|-   YOUR_PROJECT                              # All settings for this project
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

# API doc
See the full api documentation [here](docs/api.md).

# Internationalisation
The description for translating your apps is [here](docs/internationalisation.md)

# WARNING
- Default language is en-US if you want to set french make your request with :
```
Accept-Language: fr
```
It is really important especially when the server will send an email.
- It is really important to distinct ValidationError of Django from ValidationError from rest_framework because it is the last one which will be automatically handle by the exception handling in REST framework. We add a new exception_handler in YOUR_PROJECT.contrib.drf.custom_exception_handler.exception_handler that now handle also ValidationError by django.