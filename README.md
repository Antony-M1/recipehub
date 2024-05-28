# Recipe Hub
![OIG4 ZqL6udBdcp7lKbNDV2cE](https://github.com/Antony-M1/recipehub/assets/96291963/587295d0-53a1-46a5-b074-604da619d070)


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
git clone https://github.com/Antony-M1/recipehub.git
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

</details>

