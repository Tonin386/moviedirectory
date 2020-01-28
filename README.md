
# Movie Directory

[Movie Directory](http://moviedirectory.fiddlecomputers.fr/) is a small social network designed to share with our friends the last movies we watched.

Based on an original idea of my father who listed every movie he watched in a text file, I, Antonin Mathubert, developed the first versions of this platform in order to make my father’s life a bit easier.

The platform allows its users to perform some classic actions :

-   Add and delete a movie to his watchlist
-   Add friends
-   See friends watchlist
-   Search movies in the database
-   Note movies
-   Comment movies

More functionalities are to be expected.
Link : [http://moviedirectory.fiddlecomputers.fr/](http://moviedirectory.fiddlecomputers.fr/)

## Documentation

Unfortunately, there is no documentation yet. If you’d like to help, feel free to contact me.

## Setup development environment

The project uses the Django framework, so you need Python 3+ installed on your machine to start developing.

**Install Python 3+ for Windows :**  [https://docs.python.org/3/using/windows.html](https://docs.python.org/3/using/windows.html)  _You may need to add python/pip to PATH in order to perform the next steps_

**Install Python 3+ for Linux:**  `sudo apt install python3.X`

Once you are sure to have a Python version >= Python3, you need to clone the repository locally :

`git clone https://github.com/Tonin386/moviedirectory`

Install the project requirements on your machine :

`pip install -r requirements.txt`

Create a  `config.ini`  file at the root of the project and paste this :

```
[imdb_api]
key: yourapikey

```

[django]  
secret_key: yoursecretkey

[database]  
engine: django.db.backends.sqlite3  
name: db.sqlite3  
user: uselesshere  
password: uselesshere  
host: uselesshere  
port: uselesshere

[mail]  
host:  [smtp.gmail.com](http://smtp.gmail.com/)  
user:  [youraccount@gmail.com](mailto:youraccount@gmail.com)  
password: Y0urP4ssW0rdGoesHere123  
port: 587  

For the  `key`  field in the  `imdb_api`  section, you’ll need to retrieve it from  [https://rapidapi.com/imdb/api/movie-database-imdb-alternative](https://rapidapi.com/imdb/api/movie-database-imdb-alternative). Create an account and claim a free access to this api.

Make sure to change your mail credentials in the  `mail`  section.

Finally, you at the root of the project you need to create a  `local_settings.py`  file in which you will paste this code:

```
import os

```

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(**file**)))  
SITE_ROOT = os.path.dirname(os.path.realpath(**name**))

ALLOWED_HOSTS = [‘127.0.0.1’, ‘localhost’]  
DEBUG = True

STATICFILES_DIRS = [  
os.path.join(SITE_ROOT, “static”),  
‘static/’  
]

STATIC_URL = “/static/”  
STATIC_ROOT = “”

LOCALE_PATHS = ( os.path.join(SITE_ROOT, ‘locale’), )  

You can now create the database using:  
`python manage.py makemigrations`  or  `python3 manage.py makemigrations`  
and  
`python manage.py migrate`  or  `python3 manage.py migrate`

You should be ready to run the Django debug server locally by performing :  
`python manage.py runserver`  
or  
`python3 manage.py runserver`

The website can be accessed at  [http://localhost:8000/](http://localhost:8000/)

**Optional:**  To enable translations, perform  `python manage.py compilemessages`  
You will need to have GNU gettext-tools >= 0.15 installed for this command to work.

## Additional translation

If you desire to add new translations to this project, please contact me because I haven’t figured out yet how I’ll manage supplementary translations.
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTc1MjU5Mzg4MCw4NzA0ODkxMV19
-->