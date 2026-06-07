import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
log_table = dynamodb.Table('OutreachLogTable')
request_table = dynamodb.Table('BloodRequestsTable')

def lambda_handler(event, context):
    try:
        content_type = event.get('headers', {}).get('content-type', '')
        response_status = None
        request_id = None
        reply_text = "Message received."
        
        # 1. Process Twilio Webhook Payload
        if 'application/x-www-form-urlencoded' in content_type:
            import urllib.parse
            import base64
            
            raw_body = event.get('body', '')
            if event.get('isBase64Encoded', False):
                raw_body = base64.b64decode(raw_body).decode('utf-8')
                
            body_parsed = urllib.parse.parse_qs(raw_body)
            twilio_body = body_parsed.get('Body', [''])[0].strip()
            
            # Find the pending request to attach this response to
            response = request_table.scan()
            pending_requests = [r for r in response.get('Items', []) if r.get('status') == 'Searching']
            if pending_requests:
                pending_requests.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                request_id = pending_requests[0].get('request_id')
                blood_type = pending_requests[0].get('blood_type')
                hospital = pending_requests[0].get('hospital', 'the hospital')
                
                # --- AI CONTINUOUS CHAT (AMAZON BEDROCK) ---
                try:
                    # Initialize Bedrock Runtime with aggressive timeouts for Twilio webhooks
                    from botocore.config import Config
                    br_config = Config(connect_timeout=2, read_timeout=4, retries={'max_attempts': 0})
                    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1', config=br_config)
                    
                    system_prompt = (
                        f"You are Rakt Doot, an AI blood donation coordinator for an NGO. "
                        f"A Thalassemia patient urgently needs {blood_type} blood at {hospital}. "
                        f"You are chatting with a potential donor on WhatsApp.\n\n"
                        f"CONVERSATION FLOW (follow strictly):\n"
                        f"1. If the donor asks WHERE to come: Tell them '{hospital}'. Give the hospital name clearly.\n"
                        f"2. If the donor asks WHEN/TIME: Tell them 'As soon as possible - it is an emergency. You can come anytime today.'\n"
                        f"3. If the donor seems interested or says maybe: Ask them directly - 'Are you available to come to {hospital} today to donate {blood_type} blood?'\n"
                        f"4. If the donor says YES/agrees/confirms availability: Thank them warmly, tell them to come to {hospital} as soon as possible, and say a coordinator will contact them with exact details.\n"
                        f"5. If the donor says NO/declines/can't come: Say 'Thank you for your time. We really appreciate your willingness. Take care!' Do NOT pressure them.\n"
                        f"6. For any medical questions (eligibility, medications, etc.): Give a brief general answer and recommend checking with the hospital staff.\n\n"
                        f"RULES:\n"
                        f"- Keep responses SHORT (1-3 sentences max)\n"
                        f"- Be warm, empathetic, and respectful\n"
                        f"- Talk in Hinglish (mix of Hindi and English)\n"
                        f"- Ask ONE question at a time\n"
                        f"- NEVER make false promises about appointments\n\n"
                        f"SECRET WORDS (CRITICAL - you MUST use these):\n"
                        f"- If the donor CONFIRMS they will come to donate, include '[CONFIRMED]' in your response.\n"
                        f"- If the donor DECLINES or says they cannot donate, include '[DECLINED]' in your response."
                    )
                    
                    body = json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 150,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": twilio_body}
                        ],
                        "temperature": 0.3
                    })
                    
                    response_ai = bedrock.invoke_model(
                        body=body, 
                        modelId='anthropic.claude-3-haiku-20240307-v1:0', 
                        accept='application/json', 
                        contentType='application/json'
                    )
                    
                    response_body = json.loads(response_ai.get('body').read())
                    ai_response = response_body.get('content', [{}])[0].get('text', '')
                    
                    if '[CONFIRMED]' in ai_response:
                        response_status = "Accepted"
                        reply_text = ai_response.replace('[CONFIRMED]', '').strip()
                    elif '[DECLINED]' in ai_response:
                        response_status = "Declined"
                        reply_text = ai_response.replace('[DECLINED]', '').strip()
                    else:
                        reply_text = ai_response
                except Exception as e:
                    print(f"Fallback to NLP: {e}")
                    # Advanced NLP Fallback Engine
                    tb_lower = twilio_body.lower()
                    
                    if any(word in tb_lower for word in ['yes', 'haan', 'han', 'ok', 'sure', 'theek', 'aa jaunga', 'ready', 'available', 'of course', 'coming']):
                        response_status = "Accepted"
                        reply_text = f"Bahut shukriya! 🙏 Please {hospital} aayein jitna jaldi ho sake. Humare coordinator aapko thodi der mein contact karenge exact details ke sath. You are saving a life today!"
                    elif any(word in tb_lower for word in ['kaha', 'where', 'location', 'hospital', 'address', 'jagah', 'idhar']):
                        reply_text = f"Location hai: {hospital}. Patient ko abhi urgently {blood_type} blood ki jarurat hai. Kya aap wahan aa sakte hain? Please 'YES' ya 'NO' reply karein."
                    elif any(word in tb_lower for word in ['kab', 'when', 'time', 'samay', 'kitne baje', 'baje', 'aaj', 'kal', 'der']):
                        reply_text = f"Emergency hai, toh jitna jaldi ho sake (As soon as possible) aayein. {hospital} mein aaj kisi bhi waqt blood bank khula hai. Kya aap aaj available hain?"
                    elif any(word in tb_lower for word in ['no', 'nahi', 'cant', 'cannot', 'nhi', 'sorry', 'busy', 'not possible']):
                        response_status = "Declined"
                        reply_text = "Koi baat nahi, aapne time nikala uske liye shukriya. Humein samajh aata hai. Take care! 🙏"
                    elif any(word in tb_lower for word in ['hi', 'hello', 'hey', 'namaste', 'kaun', 'who']):
                        reply_text = f"Namaste! Main Rakt Doot AI hu. Ek Thalassemia patient ko {blood_type} blood ki urgently zarurat hai {hospital} mein. Kya aap aaj donate karke unki jaan bacha sakte hain?"
                    else:
                        reply_text = f"Maaf kijiye, main theek se samajh nahi paya. Ek patient ko {blood_type} blood ki urgently zarurat hai {hospital} mein. Agar aap donate karne aa sakte hain toh please 'YES' type karein."
            else:
                reply_text = "Thank you, but there are no active urgent requests right now."

        else:
            # Fallback for frontend JSON testing
            body = json.loads(event.get('body', '{}'))
            response_status = body.get('response_status')
            request_id = body.get('request_id')
            if not response_status:
                return {'statusCode': 400, 'body': json.dumps({'error': 'response_status is required'})}
            reply_text = "Response recorded successfully"

        # 2. Update Database if Donor Accepted or Escalated
        if response_status == "Accepted" and request_id:
            request_table.update_item(
                Key={'request_id': request_id},
                UpdateExpression="set #s = :s",
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={':s': 'Confirmed'}
            )
        elif response_status == "Declined" and request_id:
            # Automatic Escalation! Trigger match_donors to text the next best match
            lambda_client = boto3.client('lambda', region_name='ap-south-1')
            try:
                blood_type = pending_requests[0].get('blood_type') if pending_requests else 'O+'
                lambda_client.invoke(
                    FunctionName='match_donors',
                    InvocationType='Event',
                    Payload=json.dumps({'queryStringParameters': {'blood_type': blood_type}})
                )
                print(f"Escalation triggered for {blood_type}")
            except Exception as e:
                print(f"Escalation Failed: {e}")
        # 3. Return TwiML (for Twilio) or JSON (for frontend)
        if 'application/x-www-form-urlencoded' in content_type:
            twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply_text}</Message></Response>'
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/xml'},
                'body': twiml
            }
            
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': reply_text})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
