import json
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
lambda_client = boto3.client('lambda', region_name='ap-south-1')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', {})
        
        # Vapi sends different types of messages to the Server URL
        # We only care about the end-of-call report to update our DB.
        if message.get('type') == 'end-of-call-report':
            analysis = message.get('analysis', {})
            summary = analysis.get('summary', '')
            transcript = message.get('transcript', '')
            
            # The active_request_id was passed via serverUrlSecret in the Vapi payload
            request_id = message.get('call', {}).get('serverUrlSecret')
            
            if not request_id:
                print("No request_id found in Vapi webhook")
                return {'statusCode': 200, 'body': 'OK'}
            
            request_table = dynamodb.Table('BloodRequestsTable')
            
            # Check if the AI confirmed the donor
            if '[CONFIRMED]' in summary or '[CONFIRMED]' in transcript:
                print(f"Donor Confirmed for request {request_id}")
                request_table.update_item(
                    Key={'request_id': request_id},
                    UpdateExpression="set #s = :s",
                    ExpressionAttributeNames={'#s': 'status'},
                    ExpressionAttributeValues={':s': 'Confirmed'}
                )
            elif '[DECLINED]' in summary or '[DECLINED]' in transcript:
                print(f"Donor Declined for request {request_id}. Escalating.")
                # Retrieve blood type to trigger next match
                req_item = request_table.get_item(Key={'request_id': request_id}).get('Item', {})
                blood_type = req_item.get('blood_type', 'O+')
                
                # Re-trigger match_donors to find the next donor
                try:
                    lambda_client.invoke(
                        FunctionName='match_donors',
                        InvocationType='Event',
                        Payload=json.dumps({'queryStringParameters': {'blood_type': blood_type}})
                    )
                except Exception as e:
                    print(f"Escalation error: {e}")
                    
        return {'statusCode': 200, 'body': 'OK'}
        
    except Exception as e:
        print(f"Vapi Webhook Error: {e}")
        return {'statusCode': 500, 'body': str(e)}
