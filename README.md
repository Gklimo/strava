# capstone_project_strava

Create Strava App

Get your client id
Access token provided will have scope:read which is not sufficient enough to access activities

In the search line run:
client_id = 123956


http://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all

http://www.strava.com/oauth/authorize?client_id=123956&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all


It will redirect you to authorisation page. Click authorise and then copy link to which it redirects you. 

http://localhost/exchange_token?state=&code=[CODE]&scope=read,activity:read_all



CODE = 9c83c00cfe17d835928da8421b29dbba6faf6bf4

Copy the [CODE] from the link

Run 
curl -X POST https://www.strava.com/oauth/token \
-d "client_id=123956" \
-d "client_secret=[YOUR_CLIENT_SECRET]" \
-d "code=[CODE]" \
-d "grant_type=authorization_code"

curl -X POST https://www.strava.com/oauth/token \
-d "client_id=YOUR_CLIENT_ID" \
-d "client_secret=YOUR_CLIENT_SECRET" \
-d "code=YOUR_CODE" \
-d "grant_type=authorization_code"

curl -X POST https://www.strava.com/oauth/token \
-d "client_id=123956" \
-d "client_secret=279893e9e9f26c9b9961c2752c25ffbd9e76b515" \
-d "code=9c83c00cfe17d835928da8421b29dbba6faf6bf4" \
-d "grant_type=authorization_code"

curl -X POST https://www.strava.com/oauth/token \
-d "client_id=123956" \
-d "client_secret=279893e9e9f26c9b9961c2752c25ffbd9e76b515" \
-d "code=cc88514314c5668a5c3f55dee47a0809d522ce84" \
-d "grant_type=authorization_code"

Copy the outpout

6402d3cd2e51d4aae47fc6b0287cdbf4f8dbb878

For routes and segments

http://www.strava.com/oauth/authorize?client_id=[YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read_all


http://localhost/exchange_token?state=&code=6402d3cd2e51d4aae47fc6b0287cdbf4f8dbb878&scope=read,read_all

CDC AIRBYTE Setup
ALTER USER postgres REPLICATION;

# launch interactive bash terminal in the container
docker exec -it <container_id> /bin/bash

# change directory to the postgresql data folder
cd /var/lib/postgresql/data

# append new lines for replication into postgresql.conf file
echo '# Replication
wal_level = logical
max_wal_senders = 1
max_replication_slots = 1
' >> postgresql.conf

# print and confirm contents of file
cat postgresql.conf

# exit
exit

docker restart <container_id>

SELECT pg_create_logical_replication_slot('airbyte_slot',  'pgoutput');

ALTER TABLE activities REPLICA IDENTITY DEFAULT;
ALTER TABLE athletes REPLICA IDENTITY DEFAULT;

CREATE PUBLICATION airbyte_publication FOR TABLE activities, athletes ;

.gitignore file was created with the following contents:
``` 
target/
logs/
.user.yml
profiles.yml
.env
```