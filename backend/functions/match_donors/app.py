import json
import boto3
import math
from boto3.dynamodb.conditions import Key
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DonorsTable')

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate distance between two coordinates
    R = 6371  # Radius of earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

def lambda_handler(event, context):
    try:
        # Extract query parameters
        params = event.get('queryStringParameters', {})
        blood_type = params.get('blood_type')
        lat = float(params.get('lat', 17.39)) # Default to Hyderabad center
        lng = float(params.get('lng', 78.46))
        
        if not blood_type:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'blood_type parameter is required'})
            }

        # Query DynamoDB GSI to get all active donors matching blood_type
        response = table.query(
            IndexName='BloodTypeIndex',
            KeyConditionExpression=Key('blood_type').eq(blood_type)
        )
        donors = response.get('Items', [])

        # Filter out donors who donated in the last 90 days (Eligibility Rules)
        current_date = datetime.now()
        eligible_donors = []
        for donor in donors:
            if donor.get('status') != 'Active' or not donor.get('consent', False):
                continue
                
            last_donated_str = donor.get('last_donated', '2020-01-01')
            last_donated = datetime.strptime(last_donated_str, '%Y-%m-%d')
            days_since_donation = (current_date - last_donated).days
            
            if days_since_donation >= 90:
                # Calculate REAL distance from dataset coordinates
                d_lat = float(donor.get('lat', 0))
                d_lng = float(donor.get('lng', 0))
                distance = calculate_distance(lat, lng, d_lat, d_lng)
                
                # Since the dataset only contains an anonymized user_id hash and no Name column,
                # we will use the exact user_id from the dataset as their literal identifier.
                raw_id = donor['donor_id'].replace('\\x', '')
                name = f"Donor {raw_id[:6].upper()}"
                
                # REAL Compatibility score based on ACTUAL distance and days since donation
                # Further away = lower score.
                distance_penalty = min(30, int(distance * 1.5))
                time_bonus = 5 if days_since_donation > 180 else 0
                score = max(50, min(99, 95 - distance_penalty + time_bonus))
                
                donor_profile = {
                    'donor_id': donor['donor_id'],
                    'name': name,
                    'city': donor.get('city', 'Unknown City'),
                    'distance_km': round(distance, 1),
                    'days_since_donation': days_since_donation,
                    'reliability_score': score
                }
                eligible_donors.append(donor_profile)

        # Fetch active request to track contacted donors
        request_table = dynamodb.Table('BloodRequestsTable')
        active_requests = request_table.scan(
            FilterExpression=Key('status').eq('Searching')
        ).get('Items', [])
        
        contacted_donors = []
        active_request_id = None
        active_urgency = 'Urgent'
        if active_requests:
            active_requests.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            active_request_id = active_requests[0]['request_id']
            contacted_donors = active_requests[0].get('contacted_donors', [])
            active_urgency = active_requests[0].get('urgency', 'Urgent')

        # Filter out already contacted donors
        fresh_donors = [d for d in eligible_donors if d['donor_id'] not in contacted_donors]
        
        # Sort by proximity first, then reliability
        fresh_donors.sort(key=lambda x: (x['distance_km'], -x['reliability_score']))
        top_matches = fresh_donors[:5]

        # Trigger Twilio WhatsApp for the absolute best match
        if len(top_matches) > 0:
            import os
            import urllib.request
            import urllib.parse
            import base64
            
            best_match = top_matches[0]
            
            # Record this donor as contacted so we don't message them again
            if active_request_id:
                new_contacted = contacted_donors + [best_match['donor_id']]
                request_table.update_item(
                    Key={'request_id': active_request_id},
                    UpdateExpression="set contacted_donors = :c",
                    ExpressionAttributeValues={':c': new_contacted}
                )
                
            try:
                account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
                auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
                from_number = os.environ.get('TWILIO_PHONE_NUMBER')
                to_number = os.environ.get('VERIFIED_PHONE_NUMBER')
                
                if account_sid and auth_token and to_number:
                    best_match = top_matches[0]
                    hospital_name = active_requests[0].get('hospital', 'a nearby hospital')
                    message_body = (
                        f"*[Rakt Doot - Urgent Match]*\n"
                        f"Hello {best_match['name']}, a critical patient needs {blood_type} blood at {hospital_name}.\n"
                        f"Time: AS SOON AS POSSIBLE.\n"
                        f"Reply 'YES' to confirm your donation and save a life. You can also ask me any questions about the location or timing."
                    )
                    
                    auth_string = f"{account_sid}:{auth_token}"
                    auth_bytes = auth_string.encode('ascii')
                    base64_string = base64.b64encode(auth_bytes).decode('ascii')
                    
                    # 1. Send WhatsApp Message
                    url_wa = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
                    data_wa = urllib.parse.urlencode({
                        'From': f'whatsapp:{from_number}',
                        'To': f'whatsapp:{to_number}',
                        'Body': message_body
                    }).encode('utf-8')
                    
                    req_wa = urllib.request.Request(url_wa, data=data_wa, method='POST')
                    req_wa.add_header('Authorization', f'Basic {base64_string}')
                    req_wa.add_header('Content-Type', 'application/x-www-form-urlencoded')
                    
                    try:
                        urllib.request.urlopen(req_wa)
                        print(f"Twilio WhatsApp sent to {to_number}")
                    except Exception as e:
                        print(f"Twilio WA Error: {e}")
                        
                    # 2. Initiate Voice Call ONLY if Urgent
                    if active_urgency == 'Urgent':
                        try:
                            apigw = boto3.client('apigatewayv2', region_name='ap-south-1')
                            apis = apigw.get_apis().get('Items', [])
                            api_endpoint = next((a['ApiEndpoint'] for a in apis if a['Name'] == 'RaktDootAPI'), '')
                            
                            vapi_api_key = os.environ.get('VAPI_API_KEY')
                            vapi_phone_id = os.environ.get('VAPI_PHONE_NUMBER_ID')
                            
                            if vapi_api_key and vapi_phone_id:
                                vapi_url = "https://api.vapi.ai/call/phone"
                                
                                hospital = active_requests[0].get('hospital', 'the hospital')
                                blood_type = active_requests[0].get('blood_type', 'O+')
                                
                                system_prompt = f"""Role & Identity
You are an outbound voice AI agent representing Rakt Doot (a blood donation organization). Your primary role is to coordinate with eligible blood donors to secure the details for an upcoming donation appointment.

Context
We are calling regarding an urgent {blood_type} patient at {hospital}. You will be calling donors whose eligibility_status is currently "eligible" (they have passed their 90-day cooldown period). Some are "Bridge Donors" (attached to a specific patient), while others are general donors.

Languages
You are multilingual. Detect the caller's language (e.g., English, Hindi, Telugu) and seamlessly respond in that same language.

Goal
Your objective is strictly to collect the required information to book a donation appointment. You must gather:
1. The donor's preferred location (hospital or blood bank).
2. Their preferred day and time window for the donation.
3. Their full name and the best callback number (if it is different from the one you are currently calling).

Conversation Guidelines
- Be empathetic, appreciative, and time-efficient. Acknowledge their impact and past contributions.
- Ask one question at a time. Do not overwhelm the donor with multiple requests in a single sentence.
- If the donor is busy: Immediately offer to schedule a callback and ask for a better day/time to reach them.
- If the donor is hesitant: Briefly explain the impact (e.g., "Your specific blood group is urgently needed for a child's upcoming transfusion") and offer a low-commitment next step.

Scheduling Limitation (CRITICAL INSTRUCTION)
You do NOT have direct calendar or scheduling integrations. You must NOT claim that an appointment is booked, locked, or finalized.
Once you have collected the location, day, time, and contact info, you must close by saying: "Thanks - I'll pass these details to our scheduling team to confirm the exact slot."
Offer to have the team send a text or email confirmation once the slot is finalized.

Safety & Medical Limitations
If the caller asks medical eligibility questions, you must provide a brief, general answer and recommend confirming with the official donor eligibility guidelines at the hospital.

IMPORTANT SYSTEM ROUTING:
If the donor explicitly declines or cannot donate, you MUST include the exact secret word '[DECLINED]' anywhere in your response.
If you have successfully gathered all the required scheduling information, you MUST include the exact secret word '[CONFIRMED]' anywhere in your closing response."""

                                vapi_payload = {
                                    "phoneNumberId": vapi_phone_id,
                                    "customer": {
                                        "number": to_number
                                    },
                                    "assistant": {
                                        "name": "RaktDootAgent",
                                        "firstMessage": f"Hello! This is the Rakt Doot blood donation team calling regarding an urgent {blood_type} patient at {hospital}. Are you available to donate today? And what time would you prefer to come?",
                                        "firstMessageMode": "assistant-waits-for-user",
                                        "model": {
                                            "provider": "openai",
                                            "model": "gpt-3.5-turbo",
                                            "messages": [
                                                {"role": "system", "content": system_prompt}
                                            ]
                                        },
                                        "voice": {
                                            "provider": "vapi",
                                            "voiceId": "Elliot"
                                        },
                                        "serverUrl": f"{api_endpoint}/voice_bot",
                                        "serverUrlSecret": active_request_id
                                    }
                                }
                                
                                req_vapi = urllib.request.Request(vapi_url, data=json.dumps(vapi_payload).encode('utf-8'), method='POST')
                                req_vapi.add_header('Authorization', f'Bearer {vapi_api_key}')
                                req_vapi.add_header('Content-Type', 'application/json')
                                req_vapi.add_header('User-Agent', 'Mozilla/5.0')
                                
                                resp = urllib.request.urlopen(req_vapi)
                                print(f"Vapi AI Voice Call initiated to {to_number}")
                                print(f"Vapi Response: {resp.read().decode()}")
                        except Exception as e:
                            print(f"Vapi Call Error: {e}")
                            if hasattr(e, 'read'):
                                print(f"Vapi Error Body: {e.read().decode()}")
            except Exception as e:
                print(f"Failed to send Twilio message: {e}")

        # Return top 5 matches
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'matches': top_matches})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
