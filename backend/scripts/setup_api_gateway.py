import boto3
import json
import time

apigw = boto3.client('apigatewayv2', region_name='ap-south-1')
lambda_client = boto3.client('lambda', region_name='ap-south-1')
sts = boto3.client('sts', region_name='ap-south-1')

def create_api():
    account_id = sts.get_caller_identity()['Account']
    region = 'ap-south-1'
    
    print("Creating HTTP API Gateway...")
    api_response = apigw.create_api(
        Name='RaktDootAPI',
        ProtocolType='HTTP',
        CorsConfiguration={
            'AllowOrigins': ['*'],
            'AllowMethods': ['GET', 'POST', 'OPTIONS'],
            'AllowHeaders': ['Content-Type', 'Authorization']
        }
    )
    api_id = api_response['ApiId']
    api_endpoint = api_response['ApiEndpoint']
    
    print(f"API Created: {api_endpoint}")

    routes = [
        {'path': '/request', 'method': 'POST', 'lambda': 'create_request'},
        {'path': '/donors/match', 'method': 'GET', 'lambda': 'match_donors'},
        {'path': '/chat', 'method': 'POST', 'lambda': 'chat_bot'},
        {'path': '/donor/respond', 'method': 'POST', 'lambda': 'donor_response'},
        {'path': '/admin/dashboard', 'method': 'GET', 'lambda': 'admin_dashboard'}
    ]
    
    for route in routes:
        fn_name = route['lambda']
        lambda_arn = f"arn:aws:lambda:{region}:{account_id}:function:{fn_name}"
        
        print(f"Creating Integration for {fn_name}...")
        integration_resp = apigw.create_integration(
            ApiId=api_id,
            IntegrationType='AWS_PROXY',
            IntegrationUri=lambda_arn,
            PayloadFormatVersion='2.0'
        )
        integration_id = integration_resp['IntegrationId']
        
        print(f"Creating Route {route['method']} {route['path']}...")
        apigw.create_route(
            ApiId=api_id,
            RouteKey=f"{route['method']} {route['path']}",
            Target=f"integrations/{integration_id}"
        )
        
        print(f"Granting API Gateway permission to invoke {fn_name}...")
        try:
            lambda_client.add_permission(
                FunctionName=fn_name,
                StatementId=f"apigw-{api_id}-{fn_name}",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*"
            )
        except lambda_client.exceptions.ResourceConflictException:
            print(f"Permission already exists for {fn_name}")

    print("Creating Stage ($default)...")
    try:
        apigw.create_stage(
            ApiId=api_id,
            StageName='$default',
            AutoDeploy=True
        )
    except apigw.exceptions.ConflictException:
        print("Stage already exists")
        
    print(f"\n======================================")
    print(f"BACKEND FULLY DEPLOYED!")
    print(f"API Base URL: {api_endpoint}")
    print(f"======================================")
    
    # Save the API URL to a file so the frontend can use it later
    with open('../../frontend/.env', 'w') as f:
        f.write(f"VITE_API_URL={api_endpoint}\n")

if __name__ == '__main__':
    create_api()
