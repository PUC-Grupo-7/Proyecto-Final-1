web: flask run --host=0.0.0.0 --port=$PORT
web: flask db upgrade && gunicorn movie_bot.app:app

