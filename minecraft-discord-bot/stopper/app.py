import json
import os
import boto3
from mcipc.query import Client

# The list of EC2 states that are considered stopped or stopping
STOP_STATES = ['shutting-down','terminated','stopping','stopped']

def lambda_handler(event, context):
    '''This lambda function reaches out to the EC2 instance that is running the
    minecraft server. If it is active, it will ping the server to find out how
    many players are currently online. If no one is online, it will stop the
    server. If players are online, or the server is already inactive, it will
    do nothing.'''

    try:

        # Grab the id of the EC2 instance running the Minecraft server
        instance_id = os.environ['MC_INSTANCE_ID']

        ec2 = boto3.client('ec2')

        # Check if the EC2 instance is running
        response = ec2.describe_instances(InstanceIds=[instance_id])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        
        # If the EC2 instance is not running, return
        if state != 'running':
            print("Minecraft Server is not currently running")
            return {
                "statusCode": 200,
                "body": "Server is not running"
            }

        # Get the ip address of the EC2 instance so we can query it
        ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

        # Ping the server using mcipc to see if anyone is online
        # If no one is online, stop the server
        with mcipc.Client(ip_address, 25575) as client:
            basic_stats = dict( client.stats() )

        num_players = basic_stats['num_players']

        # If no one is online, stop the server
        if num_players == 0:
            print("Stopping Minecraft Server")
            response = ec2.stop_instances(InstanceIds=[instance_id])
            # If the server is now stopping return successfully, otherwise error
            current_state = response['StoppingInstances'][0]['CurrentState']['Name']
            
            if current_state in STOP_STATES:
                return {
                    "statusCode": 200,
                    "body": "Server Stopping"
                }
            else:
                return {
                    "statusCode": 400,
                    "body": "Error"
                }


        print(f"There are {num_players} players online, server will not stop")
        return {
            "statusCode": 200,
            "body": "Players online"
        }
    # Catch any error and return a 400
    except Exception as e:
        print(f"Encounterd exception: {e}")
        return {
            "statusCode": 400,
            "body": "Error"
        }