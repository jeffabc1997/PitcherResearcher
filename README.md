# PitcherResearcher

This a Django Project to help Fantasy Baseball GMs to find potential good pitchers for streaming.
We're going to build a table with stats of probable pitchers and their opponents' strength.

# How to use
a. you can use docker-compose to see the result directly
b. Virtual Environment 
- In the terminal, create a virtual environment`$ python -m venv venv`
- Then, install the dependencies `$ pip3 install -r requirements.txt`
- Use the command line to create the database we need. You'll see a folder called `migrations` under the `gameday` folder
```
$ python manage.py makemigrations gameday
$ python manage.py migrate
```
- run the app on port 8080! `$ python manage.py runserver 8080`

## To Do
Dockerfile need `python3 manage.py makemigrations gameday`?
We're going to save the game data in database and update it periodically.
