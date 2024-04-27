# MONK - System

Linux architecture and application for management and access control of Nihon-Kohden MFER data.

## Cloning the repository

--> Clone the repository using the command below:

```
git clone https://github.com/MONK-system/system.git
```

## Install the requirements:

```
pip install django
pip install git+https://github.com/MONK-system/library.git
pip install plotly pandas
```

Check out https://github.com/MONK-system/library for installation prerequisistes.

## Running the application

--> To run the app, we use this command in the terminal:

```
python manage.py runserver
```

### Then, the development server will be started at : http://127.0.0.1:8000/


## Access and manage the database

In order to get access to the database, you will need to create a super user / admin user.

To create a superuser for the admin interface in Django, you can use the createsuperuser management command provided by Django's authentication system. Follow these steps:

1. Open a terminal or command prompt.
2. Navigate to your Django project directory.

Run the following command:

```
python manage.py createsuperuser
```

4. You'll be prompted to enter a username, email address, and password for the superuser. Fill in the details as required.
5. Once you've entered the details, the superuser will be created and you'll receive a confirmation message.
   
After creating the superuser, you can now access the Django admin interface by running your Django development server (python manage.py runserver) and navigating to /admin in your web browser. Log in using the username and password of the superuser you just created, and you'll have access to the admin interface to manage your Django application's data. Log in with the admin user via the "Log in as admin" link at the login page. 


## Create a virtual environment (Not mandatory, but recommended)

--> installs the virutalenv first

```
pip install virtualenv
```

--> Then we create our virtual environment

```
virtualenv {your environment name}
```

--> Activate the virtual environment:
Windows:

```
{your environment name}\scripts\activate
```

Linux:

```
source {your environment name}/bin/activate
```
