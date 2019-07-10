### This is a simple CRUD API for notes management
#### To run the file, clone this repo
- clone this repo 
- Install Django. 

#### Running the app
```
django manage.py runserver
```
  
#### Running the test
```
django manage.py test
```

#### Endpoints

* **URL**

  /register

* **Method:**
  
  `POST`

* **Data Params**

  **Required:**

   `username=[string]`

   `password=[string]`


* **URL**

  /login

* **Method:**
  
  `POST`

* **Data Params**

  **Required:**

   `username=[string]`

   `password=[string]`


* **URL**

  /logout

* **Method:**
  
  `GET`

  
* **URL**

  /users

* **Method:**
  
  `POST`

* **Data Params**

  **Required:**

   `username=[string]`

   `password=[string]`

* **URL**

  /users

* **Method:**
  
  `Get`

* **URL**

  /users/int:user_id

* **Method:**
  
  `Get`

* **URL**

  /notes

* **Method:**
  
  `POST`

* **Data Params**

  **Required:**
 
   `title=[string]`
   `text=[string]`
  
* **URL**

  /notes

* **Method:**
  
  `GET`

* **URL**

  /notes/int:note_id

* **Method:**
  
  `PUT`

* **URL**

  /notes/int:note_id

* **Method:**
  
  `GET`

* **URL**

  /notes/int:note_id

* **Method:**
  
  `DELETE`
