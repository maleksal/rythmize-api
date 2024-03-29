# Rythmize api [![Generic badge](https://img.shields.io/badge/Python-3.8.5-<COLOR>.svg)](https://shields.io/)
<p align="center">
  <img src="https://github.com/maleksal/rythmize-api/blob/main/screenshots/c0a3f61c-cf72-41d4-8b45-567cb4e2ee97_200x200.png" alt="Sublime's custom image"/>
</p>

## Introduction:
Rymthize is a web based application that enabels you to transfer your music between music streaming services. This project is an end-of-foundations project, required by Holberton School.
- Blog post about our journey [HERE](https://cyberxtech.medium.com/how-i-built-my-project-rythmize-657f7fe985e2)
- Linkdin profile: [Malek Salem](https://www.linkedin.com/in/malek-salem)
- Our deployed API: https://rythmize.herokuapp.com/
- our API documentation : [API docs](https://web.postman.co/collections/4200498-016390b8-711c-4da1-abee-f6813d455b3e?workspace=ce1094ed-f324-4076-8a32-761325692d1d)

## Installation:
- **Install requirements**
```terminal
$ pip install -r requirements.txt
```
- **Setup .env file**
```bash
CONFIG_ENV=Development
FLASK_ADMIN_SWATCH=cerulean
SECRET_KEY= secret_key_here
DEV_DATABASE_URI = link_to_database 
PROD_DATABASE_URI= link_to_production_database (optional in case of development)

MAIL_SERVER= your_smtp_mail_server
MAIL_USERNAME= mail_username
MAIL_PASSWORD= mail_password
MAIL_PORT= mail_port
MAIL_DEFAULT_SENDER = mail_default_sender
CLIENT_ID = spotify_client_id
CLIENT_SECRET= spotify_client_secret
CLIENT_REDIRECT_URI=http://127.0.0.1:5000/api/v1/auth/connect/spotify/callback/
```
- **Init database**
```
$ ./init_db.sh
```

## Usage:
- **Run App**
```terminal
$ python3 manager.py runserver

OUTPUT:
 * Serving Flask app "rythmize" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 260-463-794
```
- **Run App in shell mode**
```
$ python3 manager.py shell

OUTPUT:
    In [1]: your command

```

**Screenshots:**
![](https://github.com/maleksal/rythmize-api/blob/main/screenshots/Screenshot%20from%202020-11-04%2016-17-06.png)
![](https://github.com/maleksal/rythmize-api/blob/main/screenshots/Screenshot%20from%202020-11-04%2016-17-50.png)

> run.py is used only for production

## Contributing:
Contribution is open for everyone.
## Related projects:
Rythmize frontend [repository](https://github.com/SeifJelidi/rythmize-frontend/)
## Licensing:

