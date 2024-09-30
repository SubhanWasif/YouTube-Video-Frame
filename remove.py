import boto3
from boto3.dynamodb.conditions import Key, Attr



session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
    aws_session_token='', 
    region_name='us-east-1'
)


dynamodb = session.resource('dynamodb')
table = dynamodb.Table('Adinteractive-DB')
print("Connection is Successfull!")



# Scan for items with movie_name
response = table.scan(
    FilterExpression=Attr('video_id').eq('GgKmhDaVo48')
)

items = response.get('Items', [])
print(f"Found {len(items)} items")


# Loop through the items and delete each one
for item in items:
    table.delete_item(
        Key={
            'coordinate_id': item['coordinate_id'],  # Replace with actual key names

        }
    )
print(f"Found {len(items)} items")