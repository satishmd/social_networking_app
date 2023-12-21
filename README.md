# social_networking_app

A Simple app built with Django rest framework for social networking

## API Details

1. /api/signup/ - POST call for user registration.
2. /api/login/ - POST call for login which returns access token.
3. /api/fetch-users/ - POST call for to fetch user's bansed on name or email.
4. /api/send-friend-request/ - POST call to send friend request which returns friend request id
5. /api/send-friend-request/<frnd_req_id>/ - PATCH call to accept or reject friend request.
6. /api/send-friend-request/?user=<username>&details=friends - GET call to get the friends of a user.
7. /api/send-friend-request/?user=<username>&details=friend_requests - GET call to get the received friend requests for the user.

## Installation steps

### Manual

- Create a virtualenv 

    ```Python -m venv venv```

- Activate the virtualenv

    ```Source venv/Scripts/activate```

- Install the requirements

    ```pip install -r requirements.txt```

- Apply migrations

    ```python manage.py migrate```

- Start the server

    ```python manage.py runserver```

    - Server will start at 8000 port http://localhost:8000/

### Docker

- Start container

    ```docker-compose -f docker-compose.yml up -d```

- Stop container

    ```docker-compose -f docker-compose.yml down```

- To check logs

    ```docker logs -f social_networking_app```


NOTE : 
 1. Once the server is started signup with username and password to register.
 2. Once you are registered login to get the access token.
 3. Once you get the access token use the access token in header's Authorization.
 4. All the api's and their respective request bodies are present in postman collection.
 5. If you are getting any issue like csrf failed, remove the csrf cookie for headers of request.