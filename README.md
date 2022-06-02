


[![Built and pushed to docker hub](https://github.com/Ridmel/foodgram-project-react/actions/workflows/push_image_to_dockerhub.yml/badge.svg?branch=master)](https://github.com/Ridmel/foodgram-project-react/actions/workflows/push_image_to_dockerhub.yml)

# Foodgram
### Description

A web application where everyone can create and share their most delicious recipes.

<img src="https://user-images.githubusercontent.com/80767090/170669580-95943292-55b9-4067-bfba-d7416c561dbb.png" alt="Your image title" width="500"/>

#### Technology stack

* Programming language: Python
* Backend: Django, Django REST framework
* Frontend: React
* Database: PostgreSQL
* Web server: Nginx
* WSGI server: Gunicorn
<br/>
  
## Deploy 
#### Demo version with pre-populated DB

*(require *docker compose v2+*)*  
Execute from `/infra/`:

    (sudo) make run_demo

The application will be available at the local address `127.0.0.1`. Two users are registered in DB - with and without admin rights:
 - ***user***  
		login: `user@user.com`  
		password: `user`  
- ***admin***  
		login: `admin@admin.com`  
   		password: `admin`

<br/>

#### Version with clean DB:  
*(require *docker compose*)*  
Create an `.env` file in `/infra/` with desired environment variables. An example file can be found in `/infra/.env.example`.  
Execute from `/infra/`:

    (sudo) make run_new
    make create_user
<br/>
<br/>
<br/>  

*Author: Roman Sergienko* 
