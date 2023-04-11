# sa-team20

## Instagram alternative recommendation system proof-of-concept.

## Description

In this PoC, we implemented a mock user interface of Instagram UI using Python-based web framework Django. The user can interact with the UI by interacting with the post by means of liking, commenting and sharing it. These interactions are then used to recommend users with similar posts to improve user engagement. The recommendation systems are also implemented using Python. These include content-based filtering, collaborative filtering and hybrid recommendaiton system, The goal of the project is to propose an alternative recommendation system architecture that may benefit the users among other stakeholders.


![mockstagram.png](project%2Fstatic%2Fmockstagram.png)

## Installation

1. To install and use the system, clone the Gitlab repository on your local machine.
2. Create a virtual environment and activate it.  
Note: The used ``Sentence-Transformers`` library is incompatible with python 3.11 due to its ``sentencepiece`` dependency.
```console
python3 -m venv env
source env/bin/activate
```
3. Install all the dependencies listed in the requirements.txt of the project:

```console
pip install -r requirements.txt
```

3. cd into the project folder and run the following command to run the server:

```console
python manage.py runserver
```

4. Navigate to localhost address shown in the terminal. You may need to login into Django admin (``/admin/``) to use the application and add objects to the database. The username and password to the Django admin are both ```'admin'```.

## Database
This project uses SQLite and Django's built-in migration framework to manage changes to the database schema over time. 
Whenever changes are made to your models, a new migration needs to be created and applied in order to update the database schema.
This can be done by running the following commands

```console
python manage.py makemigrations
python manage.py migrate
```

For resetting the database, remove the contents of the ``media`` and ``myapp/migrations`` folders and the ``db.sqlite3`` file, before rerunning the above commands.
When resetting a database, a new superuser (admin) needs to be created which can be done through:
```console
python manage.py createsuperuser 
```

## Quality Assurance
Best coding practices were followed to ensure the code is readable and maintanable. 
Besides that to further ensure the code is properly formatted, static analysis tools have been set up.
Each of these can be run as followed inside the project folder:
```console
pylint --ignore-path=myapp/migrations --ignore-patterns=test_.*?py --disable=E1101,R0903,E0307,W0612,W0613,E0213,W0642 */
bandit -r ./myapp
mypy myapp --ignore-missing-imports
flake8 .
```

Furthermore, a Test-suite has also been created using Django's built-in unit tests, and are located in ``myapp/tests``. 
These can be run with the following commands which also includes Code coverage:
```console
coverage run --source=myapp --omit=*/migrations/*,*/tests/* ./manage.py test myapp
coverage report -m
```


## Limitations & Future Work
The Proof-of-Concept has some limitations can be addressed by the following:
- Research different types of recommendation systems through a user study instead of only evaluating through a MRR score.
- Perform experiments using different datasets to improve the models by making recommendations more general and robust.
- Improve the implemented recommendation system to make more use of a user's activity, as currently only likes, comments, and shares are used.