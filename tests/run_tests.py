import requests
import json,glob, os
import boto3
from decimal import Decimal
from test_helper import compare_jsons

class bcolors:
    HEADER = '\033[95m'
    GOOD = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    NORMAL = '\033[37m'

def put_item(table_name, item):
    table = dynamodb.Table(table_name)

    table.put_item(
        Item=item,
        ReturnValues='NONE'
    )

def delete_item(table_name, key):
    table = dynamodb.Table(table_name)

    table.delete_item(
        Key=key
    )

def get_item(self, table_name, key):
    table = self.dynamodb.Table(table_name)

    return table.get_item(Key=key)

def create_request_arguments(payload_file_json, leisure_mode = "0"):

    url = "http://dtpln-lambda-name:9001/2015-03-31/functions/FunctionName/invocations"
    with open(payload_file_json) as f:
        payload = json.load(f)
    headers = {
        'Content-Type': 'application/json',
        'leisure-mode': leisure_mode
    }
    return url, payload, headers

# check if content of processed RRSignal is as expected
def verify_saved_Signal(file_saved, file_expected, bucket_name, message):

    with open('tmp_processed_Signal.txt', 'wb') as f:
        s3_client.download_fileobj(bucket_name, file_saved, f)

    file_saved_str = open('tmp_processed_Signal.txt').read()
    file_expected_str = open(file_expected).read()

    # if content is same
    if file_saved_str.replace("\n", "") == file_expected_str.replace("\n", ""):
        print(bcolors.GOOD + "{}{}".format(message,"Processed Signal as expected!"))
    # if content differs, print out processed RRSignal and compare line by line
    else:
        print(bcolors.FAIL + "{}{}".format(message,"Processed Signal IS NOT as expected!"))
        print("received Signal:\n", file_saved_str[:400])

def verify_dynamodb_item(file_expected_table_json, table_name, primary_key, message):

    with open(file_expected_table_json) as f:
        expected_table_json = json.load(f)

    key = {
        primary_key: expected_table_json[primary_key],
        "date": expected_table_json['date']
    }

    table = dynamodb.Table(table_name)

    received_item = {}
    try:
        received_item = table.get_item(
            Key = key
        )['Item']
    except:
        print(bcolors.FAIL + "Can't find item for ", table_name)

    compare_jsons(received_item, file_expected_table_json, message=message)

def verify_dynamodb_items(path_test_case, name_test_case):

    verify_dynamodb_item(
        "{}{}".format(path_test_case, '/expected_ddb_table_user_session.json'), 
        table_name = 'dtpln-user-session', 
        primary_key = 'session_id',
        message = "{}{}".format(name_test_case, ", DynamobDB Table User-Session: ")
    )

def restore_initial_dynamodb_state(path_test_case):

    list_table_items = glob.glob("{}{}".format('var/task/dynamodb_seeds',r'/*seed.json'))
    # list_table_items.append('var/task/dynamodb_seeds/dtpln-user-session.seed.json')
    # list_table_items.append('var/task/dynamodb_seeds/dtpln-mental-load-signal.seed.json')

    for file_item in list_table_items:
        table_name = file_item.split('/')[-1].replace(".seed.json", "")
        with open(file_item) as f:
            item_json = json.load(f)

        if path_test_case.endswith("test_case_new_session"):

            if table_name == 'dtpln-user-session':
                key = {
                    "session_id": item_json['session_id'],
                    "date": item_json['date']
                }
            elif table_name == 'dtpln-mental-load-signal':
                key = {
                    "signal_id": item_json['signal_id'],
                    "date": item_json['date']
                }
            else:
                continue

            delete_item(
                table_name = table_name,
                key = key
            )
        else:   
            put_item(table_name, item_json)

def restore_initial_s3_state(file_seed, s3_key_name):

    s3_client.upload_file(
        file_seed,
        os.environ.get('BUCKET_NAME'),
        s3_key_name
    )

def test_cases():

    test_case_1 = {
        "path_test_case": "/var/task/test_case_1",
        "name_test_case": "Case 1 ",
        "s3_path_expected": "/var/task/test_case_1/expected_s3_object.csv",
        "s3_path_seed": "/var/task/s3_seeds/2020-07-15T11:36:06.281000+02:00_RRSignal.csv",
        "s3_key_name": "wearhealth.dev/4148b53e-28bc-4a32-ac1b-a85d8d1f810e/1/2020-07-15T11:36:06.281000+02:00_RRSignal.csv",
        "leisure_mode": "0"
    }

    list_test_cases = [test_case_1]

    for test_case in list_test_cases:
        url,payload,headers = create_request_arguments("{}{}".format(test_case['path_test_case'],'/payload.json'), leisure_mode=test_case['leisure_mode'])
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        try:
            response_json = json.loads(response.text)
        except Exception as e:
            print(bcolors.FAIL + "Case Sync, Unexpected Response, cant turn to json", "\nReceived Response:\n",response.text)
            return

        print("response_json:\n", response_json)

        verify_dynamodb_items(
            path_test_case = test_case['path_test_case'],
            name_test_case = test_case['name_test_case']   
        )

        restore_initial_dynamodb_state(test_case['path_test_case'])

        verify_saved_Signal(
            test_case['s3_key_name'], 
            test_case['s3_path_expected'],
            os.environ.get('BUCKET_NAME'),
            message=f"{test_case['name_test_case']}, Signal "
        )

        restore_initial_s3_state(
            test_case_1['s3_path_seed'],
            test_case_1['s3_key_name']
        )

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://lambda-name-dynamodb-mock:8000',
    aws_access_key_id='MY_KEY_ID',
    aws_secret_access_key='MY_KEY_SECRET',
    region_name='eu-central-1'
)
s3_client = boto3.client('s3',endpoint_url='http://lambda-name-s3-mock:9090')

test_cases()