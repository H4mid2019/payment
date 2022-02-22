<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/fiXiyO4.jpeg" alt="Sample Vending Machine"></a>
</p>

<h3 align="center">Simple Payment System</h3>


---

<p align="center"> This is a simple but secure vending machine (payment) system api (provides only JSON endpoint APIs)
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Tech Stack](#tech_stack)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)


## 🧐 About <a name = "about"></a>

which provides two different APIs for both roles buyer and provider (seller).
<br> the buyers can deposit into their accounts. The sellers can't. <br> 
If a seller adds a product, only that seller can change the product attributes.<br>
Product names are unique. For products, only the endpoint which shows the list of products are open to everybody without credential <br>
Both seller and buyer have to obtain a token. They have to create an account. <br>
Creating user endpoint API is callable for everybody without Token.

## Tech Stack <a name = "tech_stack"></a>

Python, Docker, PostgreSQL, Redis, Django-rest-framework

### Prerequisites

preferably Linux based operating systems (Like any Linux distros, Ubuntu or Mac)<br>
Docker and docker-compose. (the latest version)

### Installing

First, rename `.env_example` to `.env`. If you want, you can change some values there.

Then for the first time, run

```
docker-compose up --build -d
```

After that, execute the same command without a build switch for running the app. like below

```
docker-compose up -d
```

## 🔧 Running the tests <a name = "tests"></a>

After running the app, just run the below command to run all tests.

```
docker exec backend python manage.py test
```


### Break down into end to end tests

The buy, deposit, delete the product, reset the deposit, Django model, and credential requirement tested.

## 🎈 Usage <a name="usage"></a>
by default, it listens on port 8000, so for calling the endpoints, you have to call `127.0.0.1:8000/api/<some_thing>`:
first, you need to create at least two accounts, one a seller and the other as a buyer. To achieve that, you need to call:
- /create_user POST with user detail in the body of your request. like:<br>
for buyers:
`{
    "username": "whatever",
    "email": "test@test.com",
    "deposit": 100,
    "role": "buyer",
    "password": "superSecret"
}`
for sellers (the deposit field must be empty):
`
{
    "username": "whatever",
    "email": "test@test.com",
    "role": "seller",
    "password": "superSecret"
}
`
The endpoint returns all user data, including the id, unless the password.<br>

- /get_token POST you have to send username and password which you made in the last step like <br>
`{
    "username": "whatever",
    "password": "superSecret"
}`
then send it to this API, and this API returns a token in JSON format, which you have to use like below 
in the header of your request for further requests:`{Authorization: Token supersecrettoken}`.
- /user/<username> PATCH it updates one or more fields of a user.
- /user/<username> GET it retrieve the all data of a user unless the password.
- /user/<username> DELETE it removes the user from the db, as well as the token which is belonged to that user.
- /products GET returns all existing products in DB. everybody can call this endpoint. **It doesn't need Token**
- /products POST you have to send one product as JSON in the request body. It needs a token in the header. 
- /product/<product_name> PUT updates the product attributes. Only the seller who builds it can update it.
- /product/<product_name> DELETE it deletes the target product, only the seller who adds the product can perform this action.
- /buyer/deposit PATCH you have to call this with the amount you want as JSON in the body like `{"deposit": 5 }`, 
it only accepts 5,10,20,50,100. 
- /buyer/reset POST when you call this endpoint. It makes the user balance(deposit) zero.
- /buyer/buy POST call this with the name of the product which you want to buy like `{"name": "<product_name>"}` 
it returns how much did the buyer spent and remain deposit of the buyer, the product name

## 🚀 Deployment Suggestion <a name = "deployment"></a>

Use Nginx with SSL connection, HTTP2 protocol, tls1.3, and an ECDSA cert, behind a firewall, 
And top of that, Set the rate limit on Nginx. <br>
Or use GCP App Engine behind a load balancer and cloud firewall

## ⛏️ Built Using <a name = "built_using"></a>

- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Cache
- [Django](https://www.djangoproject.com/) - Server Framework
- [Django REST FrameWork](https://www.django-rest-framework.org/) - Web Framework
- [Python](https://www.python.org/) - Programming Language
- [Docker](https://www.docker.com/) - Containerized
