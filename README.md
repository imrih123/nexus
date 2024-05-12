# README

Nexus is a torrent client and server network created as a school project.

--------------------------------------------------------
## Install

1. Clone project using the folowing command:
```cmd
git clone https://github.com/imrih123/nexus
```
2. in order to install al the requirements use the followwing commands:
```cmd
cd final-nexus
pip install –r requirements.txt
```

------------------------------------------------------
## Run
- Open settingSer.py and set ports and location to store files on server side.
- Open settingsCli.py and set ports, server ip, path to keep files and other settings for client.

In order to run the server use the followwing command:
```cmd
python .\serverCode\mainServer.py
```
In order to run the client aplication use the followwing commands:
```cmd
python .\clientCode\mainClient.py # In order to connect to the network
python .\clientCode\mainClientUser.py # In order to open user interface  
```
