Steps to run:

Pre-requisite:
Python 3.9 or higher

Docker

Docker-Compose

pip install awscli-local

1. Make sure all the pre-reqs (above) and dependencies have been downloaded. The ones needed for this project have been mentioned in the requirements.txt file

2. Open terminal and go to the folder where project is downloaded and type:
docker-compose up 
This command will start the docker container using the docker-compose.yml file provided

test reading a message from queue:
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue

test postgres connection
psql -d postgres -U postgres -p 5432 -h localhost -W

3. Make changes to cred.ini as per aws, localstack, postgres, hashing cred Note: Once the salt and key variable are set in file after initial run do not change as these are required for decryption.

4. Once that is done, on a separate terminal, run the Fetch_transform_load.py file 
What this file does is the following:
1. Fetches the messages/data from the SQS queue
2. Masks each message's device_id and pi keys using cryptography 
3. Pushes the masked messages into POSGRES 

5. Shut down the docker container
docker-compose down

========================

Answering questions in the assesement pdf

●How will you read messages from the queue?

● What type of data structures should be used?
For processing messages from the queue, I have used a combination of Python lists and dictionaries. Lists are useful for batch processing multiple messages at once, and dictionaries are ideal for handling individual JSON messages received from the queue. Batch of new messages are stored in a list and each message is parsed into a dictionary for further processing. Using a dictionary, we can quickly access and manipulate specific fields that need to be masked. 


● How will you mask the PII data so that duplicate values can be identified?
Advanced Encryption Standard (AES) was used. AES is a symmetric key encryption algorithm, which means the same key is used for both encryption and decryption.. 
Reasons why AES/cryptography was used:
1. Can identify duplicate values of the encrypted values/masked
2. Can convert the masked values back into the original values. 
Hashing could have been used too but that would have been a one-way road. We should've been able to detect duplicate values with hashing but we would not have been able to convert the masked values back into the original ones.

● What will be your strategy for connecting and writing to Postgres?
● Where and how will your application run?

● How would you deploy this application in production?
● What other components would you want to add to make this production ready?
● How can this application scale with a growing dataset.
● How can PII be recovered later on?
● What are the assumptions you made?
1. The Localstack environment accurately simulates AWS services.
2.The PII encryption key is securely managed and accessible only by authorized components.
3.The structure of the incoming messages remains consistent and adheres to the expected format.
4.The database schema is designed to handle the encrypted data without performance degradation.
5.The incoming messages have no missing values.




