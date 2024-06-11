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

3. Make changes to cred.ini as per aws, localstack, postgres credentials

4. Once that is done, on a separate terminal, run the Fetch_transform_load.py file 
What this file does is the following:
1. Fetches a batch of messages/data from the SQS queue -> main()
2. For each message in batch, masks each message's device_id and pi keys using cryptography. -> process_message()
3. Pushes a batch of masked messages into POSTGRES -> loading()
All 3 functions in Fetch_transform_load.py processes batch of messages. 

5. Shut down the docker container
docker-compose down

========================

Answering questions in the assesement pdf

●How will you read messages from the queue?
To read messages from the queue, I will summarize the main() function from the provided code:

1. Configuration Setup: I will first set up the necessary configurations by reading from a configuration file (cred.ini). This file contains my AWS credentials, SQS queue URL, and PostgreSQL database connection details.

2. AWS Credentials: I will extract the aws_access_key_id, aws_secret_access_key, aws_region, queue_url, max_msg, and timeout from the configuration file.

3. Database Parameters: I will also extract the PostgreSQL database parameters (host, database, user, password) from the configuration file.

4. SQS Client Initialization: I will create an SQS client using the boto3 library, providing it with the necessary AWS credentials and the queue URL.

5. Polling the Queue: I will continuously poll the SQS queue for new messages using a while loop. The polling will use long-polling (with a maximum wait time of 20 seconds) to minimize the number of requests made to the SQS. I wanted to pull messages in the FIFO manner but I read about this and turns out, you need a FIFO SQS queue for doing something like that. The queue which is provided in the question does not have this functionality. However, while messages are not pulled from the queue in the order they were placed in the queue, once the messages the pulled, they are processed in the order in which they were received from the queue (since we add them to a list and then iterate the list and process each in that order). 

6. Receiving Messages: When messages are received from the queue, I will check if the response contains messages. If messages are present, I will store their bodies and receipt handles in lists (message_body and delete_batch).

7. Processing Messages: I will process the messages by calling the process_message() function, which will mask the PII data and prepare the data for insertion into the PostgreSQL database. This functions is called for each batch of messages pulled from the queue. 

8. Deleting Messages: After processing the messages, I will delete them from the SQS queue using the delete_message_batch method, ensuring they are not processed again.

9. Error Handling and Sleep: I will handle any exceptions that occur during this process and include a sleep interval to control the polling rate.

● What type of data structures should be used?
For processing messages from the queue, I have used a combination of Python lists and dictionaries. Lists are useful for batch processing multiple messages at once, and dictionaries are ideal for handling individual JSON messages received from the queue. Batch of new messages are stored in a list and each message is parsed into a dictionary for further processing. Using a dictionary, we can quickly access and manipulate specific fields that need to be masked. 

● How will you mask the PII data so that duplicate values can be identified?
Advanced Encryption Standard (AES) is used. AES is a symmetric key encryption algorithm, which means the same key is used for both encryption and decryption.. 
Reasons why AES/cryptography was used:
1. Can identify duplicate values of the encrypted values/masked
2. Can convert the masked values back into the original values. 
Hashing could have been used too but that would have been a one-way road. We should've been able to detect duplicate values with hashing but we would not have been able to convert the masked values back into the original ones.

● What will be your strategy for connecting and writing to Postgres?
To connect to and write to a PostgreSQL database, I start by reading database connection parameters from a configuration file (cred.ini) using the configparser module. These parameters, including host, database name, user ID, and password, are stored in a dictionary (db_params). This setup ensures that all necessary connection details are properly managed and easily accessible.

Next, I establish a connection to the PostgreSQL database using the psycopg2 library, which allows me to execute SQL queries. I create a cursor object to facilitate database operations. This cursor is used to execute the SQL INSERT statement formulated with the processed (masked) messages. The messages, in the process_message() function are prepared by masking sensitive information and then formatted into a list of tuples that can be inserted into the user_logins table.

The data insertion process involves forming a dynamic SQL INSERT statement using the column names and values extracted from the processed messages. I then execute this SQL query using the cursor object to insert the data into the user_logins table. I insert the entire batch of messages into the table in one go. Error handling is incorporated using a try-except block to catch and manage any exceptions that might occur during database operations. This ensures that any issues are logged and handled gracefully without disrupting the overall process.

● Where and how will your application run?
Where: The application can run on a server or cloud infrastructure with access to AWS services (for production use), or locally on a developer's machine ("Steps to run" section outline how to run the application locally). The project includes configurations for running AWS services locally using tools like LocalStack. How: To run the application, follow these steps: Ensure you have Python and the required libraries installed. Set up a PostgreSQL database and create the user_logins table with the provided schema. Install and configure LocalStack if running services locally. Run the Python application, which processes messages from an SQS queue (AWS or local) and writes data to PostgreSQL. 

● How would you deploy this application in production?
To deploy this application in production, a detailed and systematic approach is necessary to ensure scalability, reliability, and security. Firstly, containerization using Docker is crucial. Create Docker images for both the application and the database, and push these images to a container registry like Docker Hub or Amazon Elastic Container Registry (ECR). Utilize Docker Compose to define and run multi-container Docker applications, ensuring that all dependencies are included.

Infrastructure as Code (IaC) tools such as Terraform or AWS CloudFormation will be used to provision and manage the infrastructure. This includes setting up services such as Amazon ECS (Elastic Container Service) or Kubernetes (EKS) for container orchestration, Amazon S3 for storage, Amazon RDS for a managed PostgreSQL database, and IAM roles for secure access management.

The deployment process should leverage Kubernetes for orchestration, deploying the application on a Kubernetes cluster (e.g., Amazon EKS). Kubernetes provides capabilities for automatic deployment, scaling, and management of containerized applications.

A robust CI/CD pipeline should be set up using tools like Jenkins, GitLab CI, or GitHub Actions to automate the build, test, and deployment processes. This pipeline will ensure that every code change is consistently tested and deployed. Security is a critical aspect, with secrets management handled by tools like AWS Secrets Manager or HashiCorp Vault. IAM roles and policies should be configured to grant least-privilege access, and SSL/TLS certificates should be used to encrypt communications.

Monitoring and logging are essential for maintaining application health. Use AWS CloudWatch for AWS service monitoring and Prometheus and Grafana for application-level metrics and alerting. The ELK (Elasticsearch, Logstash, and Kibana) stack can be deployed for centralized logging and monitoring, enabling efficient log analysis and troubleshooting.

To ensure high availability and scalability, configure auto-scaling groups to adjust the number of running instances based on demand. Use an Elastic Load Balancer (ELB) to distribute incoming traffic across multiple instances. Backup and recovery strategies should include automated backups for the PostgreSQL database using AWS RDS and a disaster recovery plan with data replication and failover mechanisms.

● What other components would you want to add to make this production ready?
To make the application production-ready, consider adding:

Logging: Implement centralized logging using tools like the ELK stack (Elasticsearch, Logstash, Kibana).

Monitoring: Use Prometheus and Grafana for monitoring application metrics and alerting.

Error Handling: Implement robust error handling and retries for transient failures.

Security: Ensure data encryption both at rest and in transit, and implement proper IAM roles and policies. Note: the current AES encryption method suggested is not very secure and is easy for hackers to crack patterns. For better security, more sophisticated encryption method should be used. 

Scalability: Use auto-scaling features of Kubernetes to handle increased load. uto-scaling will allow the application to handle varying loads by automatically adjusting the number of running instances. An Elastic Load Balancer (ELB) will distribute incoming traffic across multiple instances, ensuring high availability and reliability.

Implementing a backup and disaster recovery plan is critical. Regular automated backups of the PostgreSQL database using AWS RDS should be configured, along with a strategy for restoring data in case of failures. Data replication and failover mechanisms should be in place to minimize downtime during disasters.

● How can this application scale with a growing dataset.
1. Horizontal Scaling: Deploy multiple instances of the application to distribute the load.
2. Database Optimization: Implement database partitioning and indexing to manage large tables.
3. Caching: Use caching mechanisms like Redis or Memcached to reduce database load.
4. Implement auto-scaling for the application's compute resources using AWS Auto Scaling groups, ensuring the infrastructure can handle peak loads and scale back during low demand. 

● How can PII be recovered later on?
For this, the decrypt_value () function has been provided. It can be used in the same way as the encrypt_value() function and process_message() function is used - but just the other way round. 

● What are the assumptions you made?
1. The Localstack environment accurately simulates AWS services.
2.The PII encryption key is securely managed and accessible only by authorized components.
3.The structure of the incoming messages remains consistent and adheres to the expected format.
4.The database schema is designed to handle the encrypted data without performance degradation.
5.The incoming messages have no missing values.




