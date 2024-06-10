Steps to run:

Pre-requisite:
Python 3.9 or higher

Docker

Docker-Compose

pip install awscli-local

1. Make sure all the pre-reqs (above) and dependencies have been downloaded. The ones needed for this project have been mentioned in the requirements.txt files

2. Open terminal and go to the folder where project is downloaded and type:
docker-compose up 
This command will start the docker container using the docker-compose.yml ile provided

3. Once that is done, on a separate terminal, run the Fetch_transform_load.py file 
What this file does is the following:
1. Fetches the messages/data from the queue
2. Masks each message using cryptography 
3. Pushes the messages into POSGRES

Reasons why cryptography was used:
1. Can identify duplicate values of the encrypted values
/masked
2. Can concert the masked values back into the original values. 
Hashing could have been used too but that would have been a one-way road. We should've been able to detect duplicate values with hashing but we would not have been able to convert the masked values back into the original ones. 


