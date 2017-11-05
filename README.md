# Item Catalog

This is Udacity fourth project

## about

This project build a web application that provides a list of item within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ablility to post, edit and delete their own items.

The project create a RESTful web application using Python framework Flask that allow user to do CRUD (create, read, update and delete) operations.

The project implement third-party OAuth authentication which allow users to log in to view and edit their own items. However, users don't need to login to view the public items.

## Technologies used in the project
- Python
- Flask
- Bootstrap
- CSS
- HTML
- SQLAchemy
- OAuth
- Google Login
- JSON endpoint

## how to run

### tools
- python2
- vagrant
- virtual machine

### setup
- install vagrant and  virtual machine
- clone this repo

### running this task
Start the Vagrant by `vagrant up` and then log into it with `vagrant ssh`

run `python lots_of_students_with_user.py` to generate sample public data

To execute the program run `prthon itemCatalog.py` in your terminal

Open `localhost:8000` in your brower in order to do operations

## Display example
### In this sample project, the homepage displays all current categories along with the latest added items.
![screen shot 2017-11-05 at 12 06 21 pm](https://user-images.githubusercontent.com/22245275/32417082-d3f482ba-c221-11e7-9f3c-d2b687016802.png)
http://localhost:8000/course or http://localhost:8000



### Selecting a specific category shows you all the items available for that category.
![screen shot 2017-11-05 at 12 06 30 pm](https://user-images.githubusercontent.com/22245275/32417086-e3e9615e-c221-11e7-96b7-89ab4335923c.png)
http://localhost:8000/course/4/student



### After logging in, a user has the ability to add, update, or delete item info.
![screen shot 2017-11-05 at 10 26 09 am](https://user-images.githubusercontent.com/22245275/32417029-f316ac78-c220-11e7-8817-33528ca43ced.png)

![screen shot 2017-11-05 at 10 26 21 am](https://user-images.githubusercontent.com/22245275/32417051-54418900-c221-11e7-9940-6da77f375d15.png)

![screen shot 2017-11-05 at 10 26 36 am](https://user-images.githubusercontent.com/22245275/32417038-19b32a28-c221-11e7-9d4f-b9b3e587b5a9.png)


![screen shot 2017-11-05 at 10 26 44 am](https://user-images.githubusercontent.com/22245275/32417063-6bdcb878-c221-11e7-9a8d-7e2d1b37471a.png)

![screen shot 2017-11-05 at 10 27 38 am](https://user-images.githubusercontent.com/22245275/32417065-764c107e-c221-11e7-8cd5-44037ffaf6db.png)

![screen shot 2017-11-05 at 10 27 59 am](https://user-images.githubusercontent.com/22245275/32417067-862caa26-c221-11e7-9b01-8f1512c9ba5e.png)

![screen shot 2017-11-05 at 10 27 47 am](https://user-images.githubusercontent.com/22245275/32417068-863d14e2-c221-11e7-9080-cb5bce181b64.png)
