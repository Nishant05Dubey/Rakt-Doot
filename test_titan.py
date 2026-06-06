import boto3
import json
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
try:
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-premier-v1:0',
        body=json.dumps({"inputText": "hello"}),
        accept='application/json',
        contentType='application/json'
    )
    print('Titan Premier Access OK')
except Exception as e:
    print('Titan Premier Error:', e)
