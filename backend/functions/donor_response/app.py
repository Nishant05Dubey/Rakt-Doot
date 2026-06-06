import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
log_table = dynamodb.Table('OutreachLogTable')
request_table = dynamodb.Table('BloodRequestsTable')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        log_id = body.get('log_id')
        response_status = body.get('response_status') # e.g. "Accepted", "Declined"
        request_id = body.get('request_id')
        
        if not log_id or not response_status:
            return {'statusCode': 400, 'body': json.dumps({'error': 'log_id and response_status are required'})}
            
        # Update Outreach Log
        log_table.update_item(
            Key={'log_id': log_id},
            UpdateExpression="set #s = :s, responded_at = :t",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':s': response_status,
                ':t': datetime.now().isoformat()
            }
        )
        
        # If accepted, update the main Blood Request to Confirmed
        if response_status == "Accepted" and request_id:
            request_table.update_item(
                Key={'request_id': request_id},
                UpdateExpression="set #s = :s, matched_donor_log_id = :l",
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':s': 'Confirmed',
                    ':l': log_id
                }
            )
            
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Response recorded successfully'})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
