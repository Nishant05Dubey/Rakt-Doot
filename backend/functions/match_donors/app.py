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
                # Calculate distance
                d_lat = float(donor.get('lat', 0))
                d_lng = float(donor.get('lng', 0))
                distance = calculate_distance(lat, lng, d_lat, d_lng)
                
                donor_profile = {
                    'donor_id': donor['donor_id'],
                    'distance_km': round(distance, 1),
                    'days_since_donation': days_since_donation,
                    'reliability_score': 94 # Mocked for hackathon
                }
                eligible_donors.append(donor_profile)

        # Sort by proximity first, then reliability
        eligible_donors.sort(key=lambda x: (x['distance_km'], -x['reliability_score']))

        # Return top 5 matches
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'matches': eligible_donors[:5]})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
