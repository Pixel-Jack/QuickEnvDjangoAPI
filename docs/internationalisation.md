# For internationalisation
First create a dir locale/ in your app to translate then launch in this directory 
in your container 
```bash
django-admin makemessages -l LANGUAGE_CODE
```
Then translate each string in the files in your_app.locale.
After that add the path of your app in the LOCALE_PATH.
And finally (could be launch anywhere),
```bash
django-admin compilemessages
```
or on your host
```bash
make compilemessages
```
