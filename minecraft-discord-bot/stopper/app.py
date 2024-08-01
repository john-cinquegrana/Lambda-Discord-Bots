import json
import boto3


def lambda_handler(event, context):
    '''This lambda function reaches out to the EC2 instance that is running the
    minecraft server. If it is active, it will ping the server to find out how
    many players are currently online. If no one is online, it will stop the
    server. If players are online, or the server is already inactive, it will
    do nothing.'''

    # TODO

    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))

    return {
        "statusCode": 200,
        "body": "Success"
    }