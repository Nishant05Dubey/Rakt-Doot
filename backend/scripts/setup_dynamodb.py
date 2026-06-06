import boto3
import time

dynamodb = boto3.client('dynamodb', region_name='ap-south-1')

tables_to_create = [
    {
        'TableName': 'DonorsTable',
        'KeySchema': [{'AttributeName': 'donor_id', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [
            {'AttributeName': 'donor_id', 'AttributeType': 'S'},
            {'AttributeName': 'blood_type', 'AttributeType': 'S'},
            {'AttributeName': 'last_donated', 'AttributeType': 'S'}
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'BloodTypeIndex',
                'KeySchema': [
                    {'AttributeName': 'blood_type', 'KeyType': 'HASH'},
                    {'AttributeName': 'last_donated', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }
        ],
        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    },
    {
        'TableName': 'BloodRequestsTable',
        'KeySchema': [{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [
            {'AttributeName': 'request_id', 'AttributeType': 'S'},
            {'AttributeName': 'status', 'AttributeType': 'S'}
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'StatusIndex',
                'KeySchema': [{'AttributeName': 'status', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }
        ],
        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    },
    {
        'TableName': 'ChatSessionsTable',
        'KeySchema': [{'AttributeName': 'session_id', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'session_id', 'AttributeType': 'S'}],
        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    },
    {
        'TableName': 'OutreachLogTable',
        'KeySchema': [{'AttributeName': 'log_id', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [
            {'AttributeName': 'log_id', 'AttributeType': 'S'},
            {'AttributeName': 'request_id', 'AttributeType': 'S'}
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'RequestIndex',
                'KeySchema': [{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }
        ],
        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    }
]

def create_tables():
    existing_tables = dynamodb.list_tables()['TableNames']
    
    for table in tables_to_create:
        if table['TableName'] not in existing_tables:
            print(f"Creating table {table['TableName']}...")
            dynamodb.create_table(**table)
        else:
            print(f"Table {table['TableName']} already exists.")

    print("Waiting for tables to be active...")
    for table in tables_to_create:
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table['TableName'])
        print(f"{table['TableName']} is active.")

if __name__ == '__main__':
    create_tables()
