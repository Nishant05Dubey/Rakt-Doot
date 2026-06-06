import csv
import json
from datetime import datetime

input_file = "../../Dataset.csv"
output_file = "../cleaned_donors.json"

blood_group_map = {
    "A Positive": "A+",
    "B Positive": "B+",
    "O Positive": "O+",
    "AB Positive": "AB+",
    "A Negative": "A-",
    "B Negative": "B-",
    "O Negative": "O-",
    "AB Negative": "AB-"
}

cleaned_data = []

with open(input_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        donor_id = row.get("user_id")
        blood_group_raw = row.get("blood_group")
        lat = row.get("latitude")
        lng = row.get("longitude")
        last_donated = row.get("last_donation_date")
        status = row.get("user_donation_active_status")

        # Basic filtering
        if not donor_id or not blood_group_raw or not lat or not lng:
            continue
            
        # Standardize blood group
        blood_type = blood_group_map.get(blood_group_raw, blood_group_raw)
        
        # If last_donation_date is missing, default to a past date
        if not last_donated:
            last_donated = "2020-01-01"

        # Format for our DynamoDB Schema
        donor_record = {
            "donor_id": donor_id,
            "blood_type": blood_type,
            "last_donated": last_donated,
            "lat": float(lat),
            "lng": float(lng),
            "consent": True, # Synthesized for hackathon requirements
            "status": status if status else "Active"
        }
        cleaned_data.append(donor_record)

with open(output_file, mode="w", encoding="utf-8") as out:
    json.dump(cleaned_data, out, indent=2)

print(f"Successfully cleaned {len(cleaned_data)} donor records and saved to {output_file}.")
