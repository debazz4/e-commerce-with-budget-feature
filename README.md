
### *** Deprecation warning ***

This project was created 2023. Newer versions of the project can be found [here](https://github.com/debazz4/molla.git)

---

# Django E-commerce

This is a very simple e-commerce website with spending control built with Django.

## Quick demo

https://thinktwicez.pythonanywhere.com/"

!!!
This demo will be disabled after three months of launch.
---

## Project Summary

The website displays products. Users can add and remove products to/from their cart while also specifying the quantity of each item. They can then enter their address and choose Stripe to handle the payment processing.
Before payment is proccessed, a spending control system is integrated to ensure customers does not spend beyond their budgets for specified period of time which they must have set on their budget page.

---

## Running this project

To get this project up and running you should start by having Python installed on your computer. It's advised you create a virtual environment to store your projects dependencies separately. You can install virtualenv with

```
pip install virtualenv
```

Clone or download this repository and open it in your editor of choice. In a terminal (mac/linux) or windows terminal, run the following command in the base directory of this project

```
py -m venv project-name (preferably estore_env for project name)

That will create a new folder `env` in your project directory. Next activate it with this command on windows:

```
project-name\scripts\activate
```
Change directory into the estor folder where manage.py file is
cd estore
```
Then install the project dependencies with

```
pip install -r requirements.txt
```

Now you can run the project with this command

```
python manage.py runserver
```
## GOODLUCK ON SHOPPING AND MAKE SURE YOU SET BUDGET LIMIT.
## THANKS!!!



