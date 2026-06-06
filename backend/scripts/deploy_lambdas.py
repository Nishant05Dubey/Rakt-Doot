import boto3
import os
import zipfile
import time
import json

iam = boto3.client('iam')
lambda_client = boto3.client('lambda', region_name='ap-south-1')

ROLE_NAME = 'RaktDootLambdaExecutionRole'

def create_lambda_role():
    try:
        role = iam.get_role(RoleName=ROLE_NAME)
        print(f"Role {ROLE_NAME} already exists.")
        return role['Role']['Arn']
    except iam.exceptions.NoSuchEntityException:
        print(f"Creating role {ROLE_NAME}...")
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        role = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'
        )
        print("Waiting for role to propagate...")
        time.sleep(15) # Wait for IAM propagation
        return role['Role']['Arn']

def deploy_function(function_name, role_arn):
    source_dir = f'../functions/{function_name}'
    zip_path = f'./{function_name}.zip'
    
    # Check if folder exists
    if not os.path.exists(source_dir):
        print(f"Source folder for {function_name} not found. Skipping.")
        return
        
    print(f"Zipping {function_name}...")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, source_dir)
                zf.write(filepath, arcname)
                
    with open(zip_path, 'rb') as f:
        zip_bytes = f.read()
        
    try:
        print(f"Deploying {function_name}...")
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.12',
            Role=role_arn,
            Handler='app.lambda_handler',
            Code={'ZipFile': zip_bytes},
            Timeout=15,
            MemorySize=128
        )
        print(f"Successfully created lambda: {function_name}")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"Updating existing lambda: {function_name}")
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes
        )
    finally:
        os.remove(zip_path)

if __name__ == '__main__':
    role_arn = create_lambda_role()
    functions = ['create_request', 'match_donors', 'chat_bot', 'donor_response', 'admin_dashboard']
    for fn in functions:
        deploy_function(fn, role_arn)
