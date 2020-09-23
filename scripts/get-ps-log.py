import json
import boto3
import time
import csv


def lambda_handler(event, context):
    if isinstance(event, str):
        event = json.loads(event)
    client = assume_role(f"arn:aws:iam::{event['account_id']}:role/aws-controltower-AdministratorExecutionRole",
                         "demisto", 'ssm', event['region'])

    response = client.send_command(
        InstanceIds=[
            event['instance_id'],
        ],
        Targets=[{"Key": "InstanceIds", "Values": [event['instance_id']]}],
        DocumentName='AWS-RunShellScript',
        DocumentVersion='1',
        TimeoutSeconds=600,
        Parameters={"workingDirectory": [""], "executionTimeout": ["3600"], "commands": [
            'ps -e -o %p\; -o %u\; -o lstart -o \;%C\; -o %mem -o \;%c -o \;%a | grep -v -F "ps -e -o"']},
        MaxConcurrency='50',
        MaxErrors='0'
    )
    result = None
    statusCode = 200
    for i in range(0, 9):
        time.sleep(10)
        try:
            response_2 = client.get_command_invocation(CommandId=response["Command"]["CommandId"],
                                                       InstanceId=event['instance_id'])

            if response_2["Status"] in ['Success']:
                statusCode = 200
                result = response_2["StandardOutputContent"]
                break

            if response_2['Status'] in ['Canncelled', 'TimedOut', 'Failed', 'Cancelling']:
                statusCode = 400
                result = response_2["Status"]
                break
        except:
            pass

    dr = csv.DictReader(result.splitlines(), delimiter=";")

    r = []
    for row in dr:
        d = {}
        for k, v in row.items():
            d[k.strip()] = v.strip()
        r.append(d)

    return r


def assume_role(arn, session_name, service, region):
    client = boto3.client('sts')

    response = client.assume_role(RoleArn=arn, RoleSessionName=session_name)

    session = boto3.Session(aws_access_key_id=response['Credentials']['AccessKeyId'],
                            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                            aws_session_token=response['Credentials']['SessionToken'],
                            region_name=region)

    return session.client(service)