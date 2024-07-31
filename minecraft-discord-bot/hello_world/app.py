import json

# Import crypto packages for discord Auth
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


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

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    try:
        body = json.loads(event['body'])
            
        signature = event['headers']['x-signature-ed25519']
        timestamp = event['headers']['x-signature-timestamp']

        # validate the interaction

        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

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