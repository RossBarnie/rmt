rmt
===

Ross's Monitoring Tool: Monitoring tool for a number of containers running on a number of remote devices. Created for University of Glasgow's Raspberry Pi Cloud project.

Twitter Bootstrap
=================

This software makes use of Twitter's bootstrap which is to be considered under the LICENSE file in /web/static/bootstrap/LICENSE.

License
=========

Unless otherwise stated, all work herein is to be considered under the accompanying LICENSE.

Installation
============

Just check out the repository on your server and on your host machines and follow the instructions below, ensuring you have the dependencies listed below.

Dependencies
------------

Python 2.7

These are the known python module dependencies (some may be in site-packages):
- web
- requests
- os
- urlparse
- datetime
- ConfigParser
- rfc3987

Server
------

Run the application with web/server/start_server.sh 

This command allows you to use a single argument to provide the IP:Port or just the port for the application. For example ./start_server.sh 127.0.0.1:1234 will start the server on 127.0.0.1 on port 1234.

You also need to start the heartbeat server. To do this type python HeartbeatServer.py. Configuration for this is provided by server.cfg.

Client
------

Run the application with web/client/start_client.sh (this will ask for your root password because the application makes use of docker which always requires root access).

Again, you must start the heartbeat client which can be done by running python HeartbeatClient.py. This can be configured using hbclient.cfg which is recommended since its configuration may not match that of your network or your server application.
