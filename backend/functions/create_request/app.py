import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BloodRequestsTable')
eventbridge = boto3.client('events', region_name='ap-south-1')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        blood_type = body.get('blood_type')
        urgency = body.get('urgency', 'Urgent')
        patient_name = body.get('patient_name')
        hospital = body.get('hospital')
        city = body.get('city')
        
        if not blood_type or not patient_name:
            return {'statusCode': 400, 'body': json.dumps({'error': 'blood_type and patient_name are required'})}
            
        request_id = f"RD-{str(uuid.uuid4())[:8].upper()}"
        
        request_item = {
            'request_id': request_id,
            'blood_type': blood_type,
            'urgency': urgency,
            'patient_name': patient_name,
            'hospital': hospital,
            'city': city,
            'status': 'Searching',
            'created_at': datetime.now().isoformat()
        }
        
        table.put_item(Item=request_item)
        
        # Trigger EventBridge to start the AI Matching & Escalation Workflow
        try:
            eventbridge.put_events(
                Entries=[
                    {
                        'Source': 'com.raktdoot.requests',
                        'DetailType': 'NewBloodRequest',
                        'Detail': json.dumps({'request_id': request_id, 'blood_type': blood_type}),
                        'EventBusName': 'default'
                    }
                ]
            )
        except Exception as eb_err:
            print(f"Failed to publish to EventBridge: {eb_err}")
        
        return {
            'statusCode': 201,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Request created and AI Matcher triggered', 'request': request_item})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
