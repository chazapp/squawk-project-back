# squawk-project-back
A Scala Back-End for SquawkProject

# Installation

Pre-requisite:
 - Install JDK (We recommend Oracle JDK 8 or OpenJDK 8).
 - Install sbt.
 - A running MongoDB instance

Clone, install the dependencies:
```bash
$ git clone git@github.com:/chazapp/squawk-project-back
$ sbt run
```

Test the project:
```
$ sbt test
```

# Current API
Consider anything between { braces } as JSON keys.  

```api
#  Application
GET     /                           controllers.Application.index
GET     /profile                    controllers.Application.profile

# Rest api
GET      /rest/profile              controllers.RestApi.profile
GET      /rest/rss                  controllers.RestApi.rss

# Authentication
GET     /auth/signup                controllers.Auth.startSignUp
POST    /auth/signup                controllers.Auth.handleStartSignUp
GET     /auth/signup/:token         controllers.Auth.signUp(token:String)

GET     /auth/signin                controllers.Auth.signIn
POST    /auth/authenticate          controllers.Auth.authenticate
GET     /auth/signout               controllers.Auth.signOut
```

# Objectives
This backend should support the SquawkProject. It is a REST API that will be used by
[SquawkProject Frontend](https://github.com/chazapp/squawk-project-front) and
[SquawkProject Desktop](https://github.com/chazapp/squawk-project-desktop).  
The main features to be implemented are :
 - [x] User creation and authentication
 - [x] CRUD: Squawk Sources
   * A RSS or REST link to retrieve content
 - [x] Get the list of Squawk Sources
 - [x] Get the content of a given Squawk Source

![SquawkProject](https://i.imgur.com/Z3VGJ01.png)
