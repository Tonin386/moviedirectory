---

<h1 id="movie-directory">Movie Directory</h1>
<p>Movie Directory is a small social network designed to share with our friends the last movies we watched.</p>
<p>Based on an original idea of my father who listed every movie he watched in a text file, I, Antonin Mathubert, developped the first versions of this platform in order to make my father’s life a bit easier.</p>
<p>The platform allows its users to perform some classic actions :</p>
<ul>
<li>Add and delete a movie to his watchlist</li>
<li>Add friends</li>
<li>See friends watchlist</li>
<li>Search movies in the database</li>
<li>Note movies</li>
<li>Comment movies</li>
</ul>
<p>More functionnalities are to be expected.</p>
<h2 id="documentation">Documentation</h2>
<p>Unfortunately, there is no documentation yet. If you’d like to help, feel free to contact me.</p>
<h2 id="setup-development-environment">Setup development environment</h2>
<p>The project uses the Django framework, so you need Python 3+ installed on your machine to start developping.</p>
<p><strong>Install Python 3+ for Windows :</strong> <a href="https://docs.python.org/3/using/windows.html">https://docs.python.org/3/using/windows.html</a> <em>You may need to add python/pip to PATH in order to perform the next steps</em></p>
<p><strong>Install Python 3+ for Linux:</strong> <code>sudo apt install python3.X</code></p>
<p>Once you are sure to have a Python version &gt;= Python3, you need to clone the repository locally :</p>
<p><code>git clone https://github.com/Tonin386/moviedirectory</code></p>
<p>Install the project requirements on your machine :</p>
<p><code>pip install -r requirements.txt</code></p>
<p>Create a <code>config.ini</code> file at the root of the project and paste this :</p>
<pre><code>[imdb_api]
key: yourapikey

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
host: smtp.gmail.com
user: youraccount@gmail.com
password: Y0urP4ssW0rdGoesHere123
port: 587
</code></pre>
<p>For the <code>key</code> field in the <code>imdb_api</code> section, you’ll need to retrieve it from <a href="https://rapidapi.com/imdb/api/movie-database-imdb-alternative">https://rapidapi.com/imdb/api/movie-database-imdb-alternative</a>. Create an account and claim a free access to this api.</p>
<p>Make sure to change your mail credentials in the <code>mail</code> section.</p>
<p>Finally, you at the root of the project you need to create a <code>local_settings.py</code> file in which you will paste this code:</p>
<pre><code>import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(os.path.realpath(__name__))

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
DEBUG = True

STATICFILES_DIRS = [
    os.path.join(SITE_ROOT, "static"),
    'static/'
]

STATIC_URL = "/static/"
STATIC_ROOT = ""

LOCALE_PATHS = ( os.path.join(SITE_ROOT, 'locale'), )
</code></pre>
<p>You can now create the database using:<br>
<code>python manage.py makemigrations</code> or <code>python3 manage.py makemigrations</code><br>
and<br>
<code>python manage.py migrate</code> or <code>python3 manage.py migrate</code></p>
<p>You should be ready to run the Django debug server locally by performing :<br>
<code>python manage.py runserver</code><br>
or<br>
<code>python3 manage.py runserver</code></p>
<p>The website can be accessed at <a href="http://localhost:8000/">http://localhost:8000/</a></p>
<p><strong>Optional:</strong> To enable translations, perform <code>python manage.py compilemessages</code><br>
You will need to have GNU gettext-tools &gt;= 0.15 installed for this command to work.</p>
<h2 id="additionnal-translation">Additionnal translation</h2>
<p>If you desire to add new translations to this project, please contact me because I haven’t figured out yet how I’ll manage supplementary translations.</p>

