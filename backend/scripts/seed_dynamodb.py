import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('DonorsTable')

input_file = '../cleaned_donors.json'

def seed_data():
    print(f"Loading data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        donors = json.load(f, parse_float=Decimal)
    
    print(f"Seeding {len(donors)} records to DynamoDB DonorsTable (this may take a moment)...")
    
    # Use batch writer to efficiently load data
    with table.batch_writer() as batch:
        for i, donor in enumerate(donors):
            batch.put_item(Item=donor)
            if i > 0 and i % 500 == 0:
                print(f"Loaded {i} records...")
                
    print(f"Successfully seeded {len(donors)} records.")

if __name__ == '__main__':
    seed_data()
