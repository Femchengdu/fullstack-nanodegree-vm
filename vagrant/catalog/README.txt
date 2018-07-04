
# Description

This is an item catalog used to itemize the skills I am learning in the fullstack nanodegree program.
- It is created using Python 2 and Flask framework.

- The database is powered using Sqlite and Sqlalchemy. It is prepopulated with the data I used to test the Fullstack Catalog.

- Authentication and authorization id done through Google.

- API endpoints are available for each category and category item and can be accessed by clicking the API Link on the site.

# Files included:
- The main code base for the site.
```sh
application.py
```
- File to populate the database
```sh
lotsofskill.py
```
- Setup the database
```sh
database_setup.py
```
- A templates folder including the templates usesd.
- A static folder including the css file to style the site.
- The database categoryskillwtihuser.db is also included.

# Instructions

Generate OAuth Credentials from the following link: [GoogleCred]

Follow the prompts for creating a new project and note that 

The key settings are shown below:

- Authorized JavaScript origins
http://localhost:8000
- Authorized redirect URI's
 http://localhost:800/gconnect

After setting things up, download the json file and save is as:
```sh 
client_secrets.json
``` 
and place it in the same location as the main file:
```sh
application.py 
```

# Environment
You would need to install [Vagrant] and [Virtualbox]
Clone the fullstack  virtual environment provided by the udacity fsnd

setup instructions can be found [here]


# Dependencies
To run the code successfully you may need to upgrade some libraries.
I followed the docoumentation for setting up a web application on the google site here: [webapp]
Here is a brief summary:
>Python 2.6 or greater
>The Google APIs Client Library for Python:
>pip install --upgrade google-api-python-client
>The google-auth, google-auth-oauthlib, and google-auth-httplib2 for user authorization.
>pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
>The Flask Python web application framework.
>pip install --upgrade flask
>The requests HTTP library.
>pip install --upgrade requests
>google oauth2 prerequisites

   [here]: <https://www.udacity.com/wiki/ud088/vagrant>
   [GoogleCred]: <https://console.cloud.google.com/apis/credentials>
   [Vagrant]: <https://www.vagrantup.com>
   [Virtualbox]: <https://www.virtualbox.org>
   [webapp]:<https://developers.google.com/api-client-library/python/auth/web-app>
   