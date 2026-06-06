import json
import boto3
import uuid

bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1') # Bedrock usually in us-east-1 or specific regions
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ChatSessionsTable')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        session_id = body.get('session_id', str(uuid.uuid4()))
        user_message = body.get('message')
        donor_id = body.get('donor_id', 'unknown')
        
        if not user_message:
            return {'statusCode': 400, 'body': json.dumps({'error': 'message is required'})}

        # Fetch chat history
        response = table.get_item(Key={'session_id': session_id})
        history = response.get('Item', {}).get('history', [])
        
        # Add new message to history
        history.append({"role": "user", "content": user_message})

        # Construct prompt for Claude 3 Sonnet
        system_prompt = "You are the Rakt Doot AI assistant. Your goal is to coordinate blood donations for Thalassemia patients. Speak politely. You must support answering in English, Hindi, and Telugu based on the user's language."
        
        # Format messages for Anthropic Messages API
        bedrock_messages = [{"role": m["role"], "content": [{"type": "text", "text": m["content"]}]} for m in history]

        bedrock_payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "system": system_prompt,
            "messages": bedrock_messages
        }

        # Call Bedrock
        try:
            br_response = bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps(bedrock_payload)
            )
            response_body = json.loads(br_response.get('body').read())
            ai_reply = response_body.get('content')[0].get('text')
        except Exception as br_e:
            ai_reply = "I apologize, but my AI connection is currently offline. Please try again later."
            print(f"Bedrock Error: {br_e}")

        # Save AI reply to history
        history.append({"role": "assistant", "content": ai_reply})
        
        # Update DynamoDB
        table.put_item(Item={
            'session_id': session_id,
            'donor_id': donor_id,
            'history': history
        })
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'reply': ai_reply, 'session_id': session_id})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
