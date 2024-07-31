import json
import os

# Import crypto packages for discord Auth
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Import the AWS SDK boto3
import boto3


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:

        body = json.loads(event['body'])
            
        signature = event['headers']['x-signature-ed25519']
        timestamp = event['headers']['x-signature-timestamp']

        # Bring down the key for the Discord Bot
        bot_token = get_bot_key()

        # validate the interaction

        verify_key = VerifyKey(bytes.fromhex(bot_token))

        message = timestamp + event['body']
        
        try:
            verify_key.verify(message.encode(), signature=bytes.fromhex(signature))
        except BadSignatureError:
            return {
                'statusCode': 401,
                'body': json.dumps('invalid request signature')
            }
        
        # handle the interaction

        t = body['type']

        if t == 1:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 1
                })
            }
        elif t == 2:
            return command_handler(body)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps('unhandled request type')
            }
    except:
        raise

def command_handler(body):
  command = body['data']['name']

  if command == 'hello':
    return {
      'statusCode': 200,
      'headers' : {'Content-Type': 'application/json'},
      'body': json.dumps({
        'type': 4,
        'data': {
          'content': 'Hello, World.',
        }
      })
    }
  else:
    return {
      'statusCode': 400,
      'body': json.dumps('unhandled command')
    }
  
def get_bot_key():
    """This function reaches out to AWS Parameter Store in order to get the bot
    key under the id discord_alex_bot_token without any encryption.
    """
    # Create an SSM client
    ssm = boto3.client('ssm')

    # Create an SSM client
    # Get the bot key from AWS Parameter Store
    response = ssm.get_parameter(Name='discord_alex_bot_token')

    ''' Response syntax is as follows defined at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/get_parameter.html
        {
            'Parameter': {
                'Name': 'string',
                'Type': 'String'|'StringList'|'SecureString',
                'Value': 'string',
                'Version': 123,
                'Selector': 'string',
                'SourceResult': 'string',
                'LastModifiedDate': datetime(2015, 1, 1),
                'ARN': 'string',
                'DataType': 'string'
            }
        }
    '''

    return response['Parameter']['Value']