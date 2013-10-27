# Chicago Elections API

Getting Chicago election result data into a machine readable form

### Getting set up

This app is designed to be added as a Django app into 
[DataMade’s fork of the anthropod project](https://github.com/datamade/anthropod) 
which is really only diverges away from [Open Civic Data’s anthropod](https://github.com/opencivicdata/anthropod) 
in that it uses MongoEngine instead of the Django ORM and Django’s built in authentication 
instead of leveraging Sunlight’s OAuth API.

So, once you have the DataMade fork of Anthropod setup and running, installing 
this should be as simple as:

``` bash
$ pip install -e git+git@github.com:datamade/chicago-elections.git#egg=chicago_elections
```

Once that’s there, you’ll need to add ``chicago_elections`` to the installed apps in your 
Anthropod setup and add to the ``urlpatterns`` within Anthropod’s the main ``urls.py``

``` python
urlpatterns = patterns('',
    ...
    url(r'^elections/', include('chicago_elections.urls')),
    ...
)
```

##### Loading data

This app gives you one additional management command that scrapes all of the 
elections data off of the Chicago Board of Elections website. To get that going 
(and, fair warning, it can take more than 24 hours to complete), just run it thusly:

``` bash
$ python manage.py load_results
```


