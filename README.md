# PitcherResearcher

This a Django Project to help Fantasy Baseball GMs to find potential good pitchers for streaming.
We're going to build a table with stats of probable pitchers and their opponents' strength.

# How to use
- a. you can use docker-compose to build and run the app. 
- The connection port is 8001 on your machine. Type `http://127.0.0.1:8001/` on your browser, it will how result.
- b. Virtual Environment 
1. In the terminal, create a virtual environment`$ python -m venv venv`
2. Then, install the dependencies `$ pip install -r requirements.txt`
3. Use the command line to create the database we need. You'll see a folder called `migrations` under the `gameday` folder
4. run the app on port 8080! 
```
$ python manage.py makemigrations gameday
$ python manage.py migrate
$ python manage.py runserver 8080
```