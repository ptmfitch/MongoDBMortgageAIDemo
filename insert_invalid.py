import pymongo
from datetime import datetime

mongodb_srv = ""

print("Connecting to MongoDB...")
client = pymongo.MongoClient(mongodb_srv)
db = client["MortgageLending"]

# This document is a 'Dud' for two reasons:
# 1. annualGrossIncome is a string, not an int
# 2. It claims to be v2 but is missing the 'dependents' field
dud_application = {
    "borrowerName": "Insert Test",
    "pdfReferenceId": "000000000000000000000000",
    "processingStatus": "EXTRACTED",
    "schemaVersion": "v2",
    "extractedData": {
        "fullName": "Dud Test",
        "annualGrossIncome": "SEVENTY THOUSAND",
        "dateOfBirth": datetime(1990, 1, 1),
        "occupation": "Software Engineer"
    }
}

print(f"Attempting to write invalid record for {dud_application['borrowerName']}...")

try:
    db.applications.insert_one(dud_application)
    print("Error: The document should have been rejected.")
except pymongo.errors.WriteError as e:
    print("\n--- DATABASE REJECTED WRITE ---")
    print("Status: 400 Bad Request (Validation Failed)")
    print(f"Server Message: {e.details.get('errmsg')}")
    print("-------------------------------\n")
