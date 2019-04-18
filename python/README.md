# squawk-project-back
A Flask Back-End for SquawkProject

# Installation

Pre-requisite:
 - Python 3.6
 - A running MongoDB instance

Clone, install the dependencies:
```bash
$ git clone git@github.com:/shadonovitch/squawk-project-back
$ pip install -r requirements.txt
```
Specify the environnement variables, then run:
```
$ cp .env.example .env
$ nano .env
$ python3 -m squawkapi
```

Test the project:
```.env
$ nose tests
```

# Current API
Consider anything between { braces } as JSON keys.  

```api
POST /auth + {email, password} => 200 + { status, token }, 400, 404
POST /register + {username, email, password} => 200 + { status, token }, 400, 409 
POST /source + JWT + {link, name} => 201 + { status, source_id }, 400, 401 
GET /sources + JWT => 200 + { "sources": [{link, name, source_id}, ...] }
GET /source/<:id>/content + JWT => { "content": [{description, link, title}, ...], status }
```

# Objectives
This backend should support the SquawkProject. It is a REST API that will be used by
[SquawkProject Frontend](https://github.com/shadonovitch/squawk-project-front) and
[SquawkProject Desktop](https://github.com/shadonovitch/squawk-project-desktop).  
The main features to be implemented are :
 - [x] User creation and authentication
 - [x] CRUD: Squawk Sources
   * A RSS or REST link to retrieve content
 - [x] Get the list of Squawk Sources
 - [x] Get the content of a given Squawk Source

![SquawkProject](https://i.imgur.com/Z3VGJ01.png)
