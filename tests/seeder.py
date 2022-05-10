import boto3
import os
import glob
import json

def manage_upload(s3_client,bucket,key_name_prefix,file):
    print("bucket: ", bucket)

    basename = os.path.basename(file)
    key_name = os.path.join(key_name_prefix, basename)

    print("basename: ", basename)
    print("key_name: ", key_name)

    s3_client.upload_file(
        file,
        bucket,
        key_name
    )
    print("uploaded key name: ", key_name)

def put_item(table_name, item):
    table = dynamodb_res.Table(table_name)

    table.put_item(
        Item=item,
        ReturnValues='NONE'
    )


# creates S3 client object with the simulated S3 docker service as endpoint
s3_client = boto3.client('s3', endpoint_url='http://lambda-name-s3-mock:9090')
dynamodb_res = boto3.resource(
    'dynamodb',
    endpoint_url='http://lambda-name-dynamodb-mock:8000',
    aws_access_key_id='MY_KEY_ID',
    aws_secret_access_key='MY_KEY_SECRET',
    region_name='eu-central-1'
)
dynamodb_client = boto3.client(
    'dynamodb',
    endpoint_url='http://lambda-name-dynamodb-mock:8000',
    aws_access_key_id='MY_KEY_ID',
    aws_secret_access_key='MY_KEY_SECRET',
    region_name='eu-central-1'
)

# S3 seeding
key_name_prefix = 'wearhealth.dev/4148b53e-28bc-4a32-ac1b-a85d8d1f810e/1'
dir_stopover_seeds = '/var/task/s3_seeds/'
list_files = glob.glob("{}{}".format(dir_stopover_seeds,r'/*.csv'))

# stopover/sync seeds
for file in list_files:
    manage_upload(s3_client, os.environ.get('BUCKET_NAME'), key_name_prefix, file)


# dynamodb seeding
dir_ddb_seeds = '/var/task/dynamodb_seeds/'
list_existing_tables_names = dynamodb_client.list_tables()['TableNames']
list_table_schemas = glob.glob("{}{}".format(dir_ddb_seeds,r'/*schema.json'))

for table_schema in list_table_schemas:
    with open(table_schema) as f:
        params = json.load(f)
    if not params['TableName'] in list_existing_tables_names:
        table = dynamodb_res.create_table(**params)
        table.wait_until_exists()


list_table_items = glob.glob("{}{}".format(dir_ddb_seeds,r'/*seed.json'))
print("list_table_items: ", list_table_items)

for file_item in list_table_items:
    print("ddb file_item: ", file_item)
    table_name = file_item.split('/')[-1].replace(".seed.json", "")
    with open(file_item) as f:
        item_json = json.load(f)
    put_item(table_name, item_json)


