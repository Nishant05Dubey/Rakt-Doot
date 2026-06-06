import boto3
import json

cognito = boto3.client('cognito-idp', region_name='ap-south-1')

def setup_cognito():
    pool_name = 'RaktDootAdminPool'
    print(f"Creating Cognito User Pool: {pool_name}...")
    
    try:
        # Create User Pool
        response = cognito.create_user_pool(
            PoolName=pool_name,
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': False
                }
            },
            AutoVerifiedAttributes=['email'],
            UsernameAttributes=['email'],
            AdminCreateUserConfig={
                'AllowAdminCreateUserOnly': False
            }
        )
        pool_id = response['UserPool']['Id']
        print(f"User Pool Created! ID: {pool_id}")
        
        # Create App Client
        client_name = 'RaktDootReactClient'
        client_response = cognito.create_user_pool_client(
            UserPoolId=pool_id,
            ClientName=client_name,
            GenerateSecret=False,
            ExplicitAuthFlows=[
                'ALLOW_USER_PASSWORD_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH',
                'ALLOW_USER_SRP_AUTH'
            ]
        )
        client_id = client_response['UserPoolClient']['ClientId']
        print(f"App Client Created! Client ID: {client_id}")
        
        # Save credentials to a JSON file for the frontend to use
        output = {
            'VITE_COGNITO_USER_POOL_ID': pool_id,
            'VITE_COGNITO_CLIENT_ID': client_id,
            'VITE_COGNITO_REGION': 'ap-south-1'
        }
        
        with open('../../frontend/.env.cognito', 'w') as f:
            for k, v in output.items():
                f.write(f"{k}={v}\n")
        print("Wrote credentials to frontend/.env.cognito")
        
    except Exception as e:
        print(f"Error setting up Cognito: {e}")

if __name__ == '__main__':
    setup_cognito()
