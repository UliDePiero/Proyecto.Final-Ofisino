# Ofisino Backend

## Run it with docker
Create network for container-communication:
```
docker network create ofisino-network --subnet 172.117.117.0/24
```

Run the app (from root folder, not backend)
```
docker-compose up
```

### Create db tables
```shell
docker-compose up # Terminal 1
# On second terminal
docker exec -it ofisino_api python app/manage.py create
docker exec -it ofisino_api python app/manage.py drop
docker exec -it ofisino_api python app/manage.py recreate
docker exec -it ofisino_api python app/manage.py populate
```
Other useful commands
```shell
docker exec -it ofisino_api python app/manage.py adduser john john@doe.com  # You can also add --admin to create it as an admin
docker exec -it ofisino_api python app/manage.py listusers
# Changes the admin status
docker exec -it ofisino_api python app/manage.py admin john@doe.com
# Deletes from DB ALL the meetings and the reservations
docker exec -it ofisino_api python app/manage.py clear
# Fills the week {13/12/21 - 17/12/21} of users ('Banche', 'Chris', 'Nahue', 'Nis', 'Uli') with events
docker exec -it ofisino_api python app/manage.py fillweek
# Execute sql queries against the database
docker exec -it ofisino_db psql  -U ofisino
# SELECT * FROM public.user;
```

### Debug app models
```shell
docker-compose up # Terminal 1
# On terminal 2
# Change .env file, DATABASE_URL hostname and port to access from host to:
# DATABASE_URL=postgresql://ofisino:ofisino@localhost:54320/ofisino
# So we can access it from outside the container
cd backend
FLASK_APP=app.shell flask shell
```
Here we have an interactive shell to debug issues. All models are accesible through m.ModelName
```shell
>>> s
<sqlalchemy.orm.scoping.scoped_session object at 0x7fa9c676a790>
>>> m
<module 'app.persistence.models' from '/home/nambrosini/mine/ofisino/backend/app/persistence/models/__init__.py'>
>>> app
<Flask 'app.api'>
>>> g
<flask.g of 'app.api'>
>>> g.session is s
True
>>> m.Reservation
<class 'app.persistence.models.reservation_model.Reservation'>
>>> s.query(m.Reservation).all()
[]
```

## Tips
To configure the app more easily, we will be using environment variables.
You can install [direnv](https://direnv.net/) to automatically load variables when moving to certain folder

## Troubleshooting
### I'm getting invalid redirect uri/raw ip not allowed on google login
The explanation of this behaviour has a few steps.

1. In order to reach uvicorn server from outside the container we must specify
`--host 0.0.0.0`.
This is so the server inside docker network accepts connections from other networks,
   for example the one of our local machine (where docker host ist)
2. BUT! If we go to the server at `http://0.0.0.0:8000` google login will fail as it
   doesn't allow raw IPs for oauth flow for security reasons.
That's why even that we see a link to `http://0.0.0.0:8000` we must access the server at
`http://localhost:8000` 🎉

A precondition for this is that the redirect uri (`/auth` in our case) must be listed
on the redirect uris listed on [oauh2 client credentials](https://console.cloud.google.com/apis/credentials/oauthclient/71161164074-fs23273bvaiatifdarlhk2g803g1pbe9.apps.googleusercontent.com?authuser=1&project=ofisino)

How do i know it? I read it [here](https://stackoverflow.com/questions/11485271/google-oauth-2-authorization-error-redirect-uri-mismatch)

> If you are using ngrok https url, that one should also be listed on the redirect uris
> asociated to the oauth2 client. It's cumbersome, but works until we deploy to a public stable domain
> i.e: https://849e9056a12b.ngrok.io/auth (See the leading trailing endpoint)
