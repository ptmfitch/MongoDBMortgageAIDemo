import pymongo

mongodb_srv = ""

print("Connecting to MongoDB...")
client = pymongo.MongoClient(mongodb_srv)
db = client["MortgageLending"]

shared_fields = {
    "fullName": { "bsonType": "string" },
    "annualGrossIncome": { "bsonType": "int", "minimum": 0 },
    "dateOfBirth": { "bsonType": "date" }
}

validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["extractedData", "schemaVersion"],
        "anyOf": [
            {
                "description": "Must at least meet v1 requirements",
                "properties": {
                    "schemaVersion": { "enum": ["v1"] },
                    "extractedData": {
                        "bsonType": "object",
                        "required": ["fullName", "annualGrossIncome", "dateOfBirth"],
                        "properties": { **shared_fields }
                    }
                }
            },
            {
                "description": "Specific check for v2 fields",
                "properties": {
                    "schemaVersion": { "enum": ["v2"] },
                    "extractedData": {
                        "required": ["dependents"],
                        "properties": { "dependents": { "bsonType": "int" } }
                    }
                }
            }
        ]
    }
}

print("Applying validation...")
db.command("collMod", "applications", validator=validator)
