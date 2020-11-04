# rythmize-api 
Rymthize is a web based application that enabels you to transfer your music between music streaming services. This project is an End-of-year graduation project, required by Holberton School.

This repo represents rythmize-backend, you can see our frontend repository [HERE](https://github.com/SeifJelidi/rythmize-frontend/).

# Project Structure
```
├── config.py
├── init_db.sh
├── manager.py
├── Procfile
├── README.md
├── requirements.txt
├── run.py
├── runtime.txt
├── rythmize
│   ├── admin
│   │   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   └── v1
│   │       ├── __init__.py
│   │       └── views
│   │           ├── auth
│   │           │   ├── spotify.py
│   │           │   └── users.py
│   │           ├── __init__.py
│   │           ├── spotify_crud.py
│   │           └── users_crud.py
│   ├── clients
│   │   └── spotify.py
│   ├── extensions.py
│   ├── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── keys.py
│   │   └── user.py
│       └── __init__.cpython-38.pyc
└── tests
    └── test_user.py
```
