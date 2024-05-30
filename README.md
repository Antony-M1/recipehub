# Recipe Hub

**RecipeHub** is a web-based platform where users can share, discover, and manage recipes. Users can sign up, log in, and securely manage their recipes, performing create, read, update, and delete (CRUD) operations. Each recipe includes detailed information such as title, description, ingredients, preparation steps, cooking time, and serving size. Users can categorize recipes, search and filter them by various criteria, and rate and review recipes to share their experiences with others.

# Prerequisite
* [Python 3.10](https://www.python.org/downloads/release/python-3100/)


# .env

After cloning the project have to setup the `.env` file in the workspace folder. this file contains all the `secrets`, `credentials` & `API Keys`.

Only the eample file will be here you have to fill your own data
<details>
  <summary><h4>.env example</h4></summary>


```
SECRET_KEY=<YOUR_SECRET_KE>
```
</details>

<details>
  <summary><h1>Django Framework Usefull Commends</h1></summary>
 

### Create A Project
this command create a project in the `workspace` directory iteself
```
django-admin startproject recipehub .
```

### Create a new Django app
```
python manage.py startapp recipes
```

</details>

<details>
  <summary><h1>Project Local Setup</h1></summary>
 

### Step 1: Clone The Project
clone the repo using the below command
```
git clone <GITHUB_REPO>
```

### Step 2: Create Environment
Run the below command to create the environment
```
python3.10 -m venv .venv
```

### Step 3: Install the Requirements
```
pip install -r requirements.txt
```

### Step 4: Collect Static Files
```
python manage.py collectstatic
```

Make Sure you have edited the `.env` file

### Step 5: Run the project
```
python manage.py runserver
```

</details>


## Production Setup

For detailed production setup please refer this link [Click Here](https://github.com/Antony-M1/django-production-setup/blob/main/prod_docs/django-with-gunicorn-and-nginx.md)
