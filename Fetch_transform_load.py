import boto3
import time
import json
import psycopg2
from datetime import datetime
import configparser

import binascii
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64


# In[131]:

# Configuration for crytography
AES_KEY = b'your_32_byte_key_here'  # This key must be exactly 32 bytes long

# Ensure the key is 32 bytes long
AES_KEY = AES_KEY.ljust(32, b'\0')[:32]

# Generate a key for encryption and decryption
# This key must be stored securely and used for both encryption and decryption

def pad(data):
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data


def encrypt_value(value):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.ECB(), backend=backend)
    encryptor = cipher.encryptor()
    padded_value = pad(value.encode())
    encrypted = encryptor.update(padded_value) + encryptor.finalize()
    return base64.b64encode(encrypted).decode()


#functions for decryption 
def unpad(data):
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(data) + unpadder.finalize()
    return unpadded_data

def decrypt_value(encrypted_value):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.ECB(), backend=backend)
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(base64.b64decode(encrypted_value)) + decryptor.finalize()
    unpadded_value = unpad(decrypted)
    return unpadded_value.decode()


# Define a function to process messages
def process_message(message,db_param):
    
    """
    Function to mask data field ip and device id.
    Crytography has been used for two reasons
    1. Can detect duplicates
    2. Can retrieve the original values
    
    Hashing not used because hashing is a one way method. It can help detect duplicates
    but we cannot convert back to the original calues 
    """


    # Storing all transformed data into a list data type
    masked_msg=[]
    for json_obj in message:
        
        tmp=json.loads(json_obj) #concert to JSON as its easy to work with dictonaries
        
        # Masking Data field Masked_ip and Device_id
        if list(tmp.keys()) != ["foo","bar"]:
            
            
            tmp['masked_ip'] = encrypt_value(tmp['ip'])
            tmp['masked_device_id'] = encrypt_value(tmp['device_id'])
  
        # Removing the unmasked fields
            
            del tmp["ip"]
            del tmp["device_id"]
            masked_msg.append(tuple(tmp.values())) #append to list

    col=str(tuple(tmp.keys())).replace("\'", "") #gettng all the columsns of the JSON object
    loading(masked_msg,col,db_param) #fucntion to load everything to postgres





def loading(msg,col,db_params):
    
    """
    Function to push data to postgres using psycopg library
    """
       
        # Connect to the PostgreSQL database
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Define the INSERT statement with data
        columns=col
        value=str(msg).replace("[","").replace("]","").replace("None","NULL")
        insert_query = "INSERT INTO user_logins %s VALUES %s"%(col,value)
        
        # Insert the data into the database
        cursor.execute(insert_query)

        connection.commit()

        print("Data inserted successfully")

    except (Exception, psycopg2.Error) as error:
        print(f"Error inserting data: {error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def main():
    
    """
    Main function that connect to sqs and call subroutine for 
    transforming, loading data into postgres and poll continuosly
    waiting for new message
    """
    
    #first let us set up the configs
    config = configparser.ConfigParser()
    config.read('cred.ini')
    
    # Getting all the credential/configuration value from cred.ini
    aws_access_key_id = config.get('aws', 'key_id')
    aws_secret_access_key = config.get('aws', 'access_key')
    aws_region = config.get('aws', 'region')
    queue_url = config.get('sqs', 'url')
    max_msg = int(config.get('sqs', 'max_message'))
    timeout = int(config.get('sqs', 'message_timeout'))
    

    db_params = {
        "host": config.get('postgres', 'host'),
        "database": config.get('postgres', 'db'),
        "user": config.get('postgres', 'user_id'),
        "password": config.get('postgres', 'password')}


    # Create an SQS client to retrieve information from the queue
    sqs = boto3.client('sqs',endpoint_url=queue_url,region_name=aws_region,aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key= aws_secret_access_key)

    # Continuously poll the queue for new messages
    while True:
        try:
            # Receive messages from the queue with long-polling (wait up to 20 seconds)
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=max_msg,  
                WaitTimeSeconds=timeout  
            )

            # Process received messages
            if 'Messages' in response: #to make sure the responseis not empty
                delete_batch = []
                message_body=[] #populate all messages into a list

                for message in response.get('Messages'):
                    message_body.append(message['Body'])
                    #kessages to delete from the queue
                    delete_batch.append({'Id': message['MessageId'], 'ReceiptHandle': message['ReceiptHandle']})

                #process the messages 
                process_message(message_body,db_params)
                # Delete the message from the queue
                if delete_batch:
                    sqs.delete_message_batch(QueueUrl=queue_url, Entries=delete_batch)


        except Exception as e:
            print(f"Error: {e}")

        # Added optional sleep to control the polling rate
        time.sleep(1)  


# In[129]:


if __name__ == "__main__":
    main()


# In[ ]:




