rmt
===

Ross's Monitoring Tool: Monitoring tool for a number of containers running on a number of remote devices. Created for University of Glasgow's Raspberry Pi Cloud project.

Bootstrap
=================

This software makes use of Bootstrap which is to be considered under the LICENSE file in /web/static/bootstrap/LICENSE.

License
=========

Unless otherwise stated, all work herein is to be considered under the accompanying LICENSE.

Installation
============

Just check out the repository on your server and on your host machines and follow the instructions below, ensuring you have the dependencies listed below.

Dependencies
------------

- Python 2.7
- Docker (on client-side)
- mysql (on server-side)
- mysql-server (on server-side)

These are the known python module dependencies (some may be in site-packages):
- web
- requests
- os
- urlparse
- datetime
- ConfigParser
- rfc3987

Database
--------

The database script needs to be run once on the server. To do this, simply use the following mysql command in a terminal:
```
mysql --user=USER --password=PASSWORD < PATH_TO_RMT/web/db/createDb.sql
```
If at this point you receive an error that looks like:
```
ERROR 1396 (HY000) at line 22: Operation CREATE USER failed for 'rmt-user'@'localhost'
```
Then the user 'rmt-user' already exists in the database. Dropping the user should fix the problem, eg
```
drop user 'rmt-user'@'localhost'
```

Server
------

Run the application with 
```
PATH_TO_RMT/web/server/start_server.sh 
```
This command allows you to use a single argument to provide the IP:Port or just the port for the application. For example 
```
./start_server.sh 127.0.0.1:1234 
```
will start the server on 127.0.0.1 on port 1234.

You also need to start the heartbeat server. To do this type 
```
python HeartbeatServer.py
```
Configuration for this is provided by server.cfg.

Client
------

Run the application with web/client/start_client.sh (this will ask for your root password because the application makes use of docker which always requires root access).

Again, you must start the heartbeat client which can be done by running python HeartbeatClient.py. This can be configured using hbclient.cfg which is recommended since its configuration may not match that of your network or your server application.
