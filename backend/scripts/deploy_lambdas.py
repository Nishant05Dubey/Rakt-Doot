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
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
        )
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator'
        )
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AWSLambda_FullAccess'
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
        
    if function_name == 'donor_response':
        print(f"Installing openai dependency for {function_name} (Linux target)...")
        # Must target Linux since lambda runs on Linux, avoiding native binary issues on Windows
        os.system(f'pip install --platform manylinux2014_x86_64 --target "{source_dir}" --implementation cp --python-version 3.12 --only-binary=:all: openai')
        
    print(f"Zipping {function_name}...")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, source_dir)
                zf.write(filepath, arcname)
                
    with open(zip_path, 'rb') as f:
        zip_bytes = f.read()
        
    # Define environment variables per function
    env_vars = {}
    if function_name == 'match_donors':
        env_vars = {
            'Variables': {
                'TWILIO_ACCOUNT_SID': os.environ.get('TWILIO_ACCOUNT_SID', ''),
                'TWILIO_AUTH_TOKEN': os.environ.get('TWILIO_AUTH_TOKEN', ''),
                'TWILIO_PHONE_NUMBER': '+14155238886', # WhatsApp Sandbox
                'VAPI_API_KEY': os.environ.get('VAPI_API_KEY', 'd9000076-7e00-44a6-b4a0-8eafa9acb7c9'),
                'VAPI_PHONE_NUMBER_ID': os.environ.get('VAPI_PHONE_NUMBER_ID', '07d50b8f-ce5e-4cfa-bd4d-21068791e060'),
                'VERIFIED_PHONE_NUMBER': '+919340766550'
            }
        }
    elif function_name == 'voice_bot_escalation':
        env_vars = {
            'Variables': {
                'TWILIO_ACCOUNT_SID': os.environ.get('TWILIO_ACCOUNT_SID', ''),
                'TWILIO_AUTH_TOKEN': os.environ.get('TWILIO_AUTH_TOKEN', ''),
                'TWILIO_VOICE_NUMBER': '+15754890148',
                'VERIFIED_PHONE_NUMBER': '+919340766550',
                'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', 'sk-mock'),
                'OPENAI_BASE_URL': os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            }
        }
    elif function_name == 'donor_response':
        env_vars = {
            'Variables': {
                'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', 'sk-mock'),
                'OPENAI_BASE_URL': os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            }
        }
        
    try:
        print(f"Deploying {function_name}...")
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.12',
            Role=role_arn,
            Handler='app.lambda_handler',
            Code={'ZipFile': zip_bytes},
            Timeout=15,
            MemorySize=128,
            Environment=env_vars if env_vars else {'Variables': {}}
        )
        print(f"Successfully created lambda: {function_name}")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"Updating existing lambda: {function_name}")
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes
        )
        if env_vars:
            import time
            while True:
                status = lambda_client.get_function(FunctionName=function_name)['Configuration']['LastUpdateStatus']
                if status == 'Successful':
                    break
                print(f"Waiting for {function_name} update to finish...")
                time.sleep(2)
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                Environment=env_vars
            )
    finally:
        os.remove(zip_path)

if __name__ == '__main__':
    role_arn = create_lambda_role()
    functions = ['create_request', 'match_donors', 'chat_bot', 'donor_response', 'voice_bot_escalation', 'admin_dashboard']
    for fn in functions:
        deploy_function(fn, role_arn)
