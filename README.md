# Django Globus Portal Framework Example

The portal here serves as a starting point for bootstrapping a portal. Details
for configuration values can be found in the Documentation.

### Installation 

First, clone the portal code into your local development environment:

    git clone https://github.com/globus/django-globus-portal-framework-example.git
    cd django-globus-portal-framework-example.git
   
Next, setup a python environment. We recommend conda, but any installation with
Python 3.7+ with Pip will worok:
 
    conda create -n myportal pip
    conda activate myportal
    
Finally, install Globus Portal Framework

    pip install django-globus-portal-framework
    
### Setup

Before you start your portal, you will need to create a Globus Developer App to enable
Globus Auth in the portal. Without it, login will not work. Go to developers.globus.org,
create a new app, and ensure the following:

* Native app **is not checked**
* Redirect URL is set to http://localhost:8000/complete/globus

Create a file for storing your credentials called 'myportal/local_settings.py'.
It should reside next to the existing 'settings.py' file.

`myportal/local_settings.py`:

    SOCIAL_AUTH_GLOBUS_KEY = 'Put your Client ID here'
    SOCIAL_AUTH_GLOBUS_SECRET = 'Put your Client Secret Here'

### Running the Portal

Configure and run your portal using the local `manage.py` file:

    python manage.py migrate
    python manage.py runserver localhost:8000

Your portal should now be running at http://localhost:8000
