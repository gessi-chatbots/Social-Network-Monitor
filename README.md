# Social Network Monitor
Project based in the Final Degree Project made by @lucasares. 

## How to execute
### Local development
For local development you need to:

**In progress...**


### Local execution
#### 1 - Install pipenv (if not already installed)
```pip install pipenv```

#### 2 - Install requirements
```pipenv install```

#### 3 - Execute virtual environment
```pipenv shell```

#### 4 - Create and fill .env file
```
MYSQL_ENGINE=django.db.backends.mysql
MYSQL_DATABASE=marketplaces
MYSQL_USER=USER_NAME
MYSQL_PASSWORD=PASSWORD
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

#### 5 - Create migrations for database
```python manage.py makemigrations```

#### 6 - Execute migrations in database
```python manage.py migrate```

#### 7 - Execute monitor
```python manage.py runserver```


---
## How to deploy
**In progress...**
