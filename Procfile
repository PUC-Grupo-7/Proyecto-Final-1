web: flask run --host=0.0.0.0 --port=$PORT
release: python -m flask db upgrade
web: gunicorn movie_bot.app:app
