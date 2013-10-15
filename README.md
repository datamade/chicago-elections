## Chicago Elections

API for local chicago election data

#### Environment Setup

1. Clone the repository (`` git clone https://github.com/datamade/elections.git ``)
2. Install the requirements (preferably in a 
[python virtual environment](http://www.virtualenv.org/en/latest/))

``` bash
$ cd /path/to/cloned/repo
$ pip install -r requirements.txt
```

#### Load the data

There are a couple approaches here. You can either load the data from the SQL 
dump included in the repo or run the scraper. Keep in mind that the SQL dump was 
generated from a PostgreSQL v 9.1 database so results may vary based upon what 
type of database you are wanting to load it into. 

Running the scraper requires setting a single environmental variable called 
``ELECTIONS_CONN`` which tells SQLAlchemy how to connect to the database 
you’d like to use as a backend. If you’re using bash on Linux as your shell, 
setting that up looks something like this:

``` bash
$ echo "export ELECTIONS_CONN='sqlite:///elections.db'" >> ~/.bashrc
```

More on how to format that string for other database types can be found [here](http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html#database-urls) 

As it loads the pages on the elections site, the scraper attempts to find rows 
in the database that match incoming data before creating a new row. Because of 
this, you should be able to kill it and restart it without needing to recreate 
the database. It also caches pages on your local filesystem after it fetches 
them the first time so once it has run once all the way through, it should run 
fairly quickly on subsequent runs.

#### Run the API

Once you have your environment setup and have data loaded, running the Flask app 
that provides the API should be as simple as:

``` bash
$ python app.py
```

This will run a simple development server that you can use to test to make sure 
everything is sane. To deploy this in a production environment, you should probably 
use something like [Gunicorn](http://flask.pocoo.org/docs/deploying/others/#gunicorn) running behind a [nginx reverse proxy](http://docs.gunicorn.org/en/latest/deploy.html#nginx-configuration)
