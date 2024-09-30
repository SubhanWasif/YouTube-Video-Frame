
import boto3
import json


session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
    aws_session_token='', 
    region_name='us-east-1'
)




dynamodb = session.resource('dynamodb')
table = dynamodb.Table('Product')
print("Connection is Successfull!")


with open("granTurismo.json") as json_data_file:
    data = json.load(json_data_file)
description = data['descriptions']
label = data['labels']
link = data['links']
image = data['images']
product_id = data['product_id']

for product in description.keys():
    table.put_item(
        Item={
            'product_id': product_id.get(product, 'N/A'),
            'description': description.get(product, 'N/A'),
            'label': label.get(product, 'N/A'),
            'link': link.get(product, 'N/A'),
            'image': image.get(product, 'N/A')
        }
    )
    print(f"Item {product} inserted into DynamoDB.")




# product_id = '188845341156__c'  # Replace with the actual product_id
# new_links_value = 'www.google.com'     # Replace with the new link value

def change_link(product_id, new_link_value):
    response = table.update_item(
    Key={
        'product_id': product_id  # Primary Key for the item to be updated
    },
    UpdateExpression="set #link = :new_link",
    ExpressionAttributeNames={
        '#link': 'link'  # 'link' is a reserved keyword, so aliasing it
    },
    ExpressionAttributeValues={
        ':new_link': new_link_value
    },
    ReturnValues="UPDATED_NEW"  # This will return only the updated attributes
    )
    print("Update succeeded:", response)




def change_image(product_id, new_image_value):
    response = table.update_item(
    Key={
        'product_id': product_id  # Primary Key for the item to be updated
    },
    UpdateExpression="set #image = :new_image",
    ExpressionAttributeNames={
        '#image': 'image'  # 'image' is a reserved keyword, so aliasing it
    },
    ExpressionAttributeValues={
        ':new_image': new_image_value
    },
    ReturnValues="UPDATED_NEW"  # This will return only the updated attributes
    )
    print("Update succeeded:", response)
    
    

def change_description(product_id, new_description_value):
    response = table.update_item(
    Key={
        'product_id': product_id  # Primary Key for the item to be updated
    },
    UpdateExpression="set #description = :new_description",
    ExpressionAttributeNames={
        '#description': 'description'  # 'description' is a reserved keyword, so aliasing it
    },
    ExpressionAttributeValues={
        ':new_description': new_description_value
    },
    ReturnValues="UPDATED_NEW"  # This will return only the updated attributes
    )
    print("Update succeeded:", response)



def change_label(product_id, new_label_value):
    response = table.update_item(
    Key={
        'product_id': product_id  # Primary Key for the item to be updated
    },
    UpdateExpression="set #label = :new_label",
    ExpressionAttributeNames={
        '#label': 'label'  # 'label' is a reserved keyword, so aliasing it
    },
    ExpressionAttributeValues={
        ':new_label': new_label_value
    },
    ReturnValues="UPDATED_NEW"  # This will return only the updated attributes
    )
    print("Update succeeded:", response)

