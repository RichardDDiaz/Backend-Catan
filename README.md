# Turing Complete
## Environment
The project is built and tested to run in Linux system but could run in iOS and Windows.
All the commands described next in the README are aimed to Linux system.

## Clone and prepare project

> $git clone -b dev https://gitlab.com/erellont/turing-complete.git

> $cd turing-complete/

> $python -m venv turing 

> $source turing/bin/activate

> $pip install -r requiements.txt

> $cd catan/

> $python manage.py runserver 

## Some examples :

### Register User:

To register an user you must send a POST request to the http://127.0.0.1:8000/users/login/ endpoint
with the following json structure:

```json
{
	"user":"user_test",
	"pass":"Pass1234!"
}
```
This request will send you back the status_code = 200 in case you register correctly. Otherwise it will send you an error.

### Login User:

To login with an user that is already registered, you must send a POST request to the http://127.0.0.1:8000/users/login/ endpoint
with the same json structure specified in the Register User Scope.

This request will send you back the following json structure. Otherwise it will send you an error.
```json
{
	"token":"591b01910e1c574309efd78f52f8238f479db7c5"
}
```
### Create Lobby:
Once that you're already logged in to create a lobby you've to send a POST request to http://127.0.0.1:8000/rooms/ with the following json schema:
```json
{
	"name":"Name of the lobby that you want",
	"board_id":1
}
```
where board_id is the number of the board that you want to associate the lobby with. 
By default there is 3 boards templates created, so you have to choose between 1 2 or 3, board_id.

### Join Lobby:
Once that you're already logged in to join a lobby you've to send a PUT request to http://127.0.0.1:8000/rooms/id/ where id is the id of the room that must be already created.

### Start Game:
Logged in with the owner of the lobby you've to send a PATCH request to http://127.0.0.1:8000/rooms/id/ where id is the id of the room that must be already created, and the game will start if the requirements are met.
### Get Board Status:
You should send a GET request to http://127.0.0.1:8000/games/id/board/ where id is the id of the game in context. 

### Get Game Status:
You should send a GET request to http://127.0.0.1:8000/games/id/ where id is the id of the game in context.
### Get Player's Game Status:
You should send a GET request to http://127.0.0.1:8000/games/id/player/ where id is the id of the game in context, and from the token that must be sent in the header "Authorization" as Bearer, it will hash back the user that sent it.

### Get available actions:
You should send a GET request to http://127.0.0.1:8000/games/id/player/actions/ where id is the id of the game in context and you will get back a json like:
```json
[ 
	{  
	"type": ACTION,  
	"payload": PAYLOAD  
	} 
]
```
### Post action:
You must send a POST request in your turn any of the avaialable actions described in the GET request to http://127.0.0.1:8000/games/id/player/actions/ like:
```json
{  
	"type": ACTION,  
	"payload": PAYLOAD  
} 
```

## Test cases

To execute the test cases located tests.py on each app, you should run in shell

>$ python manage.py tests

If you want to specify a single test that you want to run it should be passed in by parameter like following example

>$ python manage.py tests add\_more\_than\_allowedTestCase


## More Info:
You are able to read the complete
[API's Doc](https://docs.google.com/spreadsheets/d/10tRfyxZQ1K853KEcaBvR25k9qo9sGdnkFSxU45IyS6Y/edit#gid=1282872825)
and some details of the
[Board's Doc](https://docs.google.com/presentation/d/1dUA6Y0Mf5b0HGZiKtIt4qJujDMyWybO37TiYURFwOMY/edit#slide=id.g61b2be3b87_0_184)


