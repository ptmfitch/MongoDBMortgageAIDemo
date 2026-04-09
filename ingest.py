import pymongo
import gridfs
from datetime import datetime

mongodb_srv = ""

print("Connecting to MongoDB...")
client = pymongo.MongoClient(mongodb_srv)
db = client["MortgageLending"]
fs = gridfs.GridFS(db)

# borrower_name = "Jasper Thorne"
borrower_name = "Eleanor Vance"
file_path = f"applications/Mortgage Application - {borrower_name}.pdf"

# borrower_name = "Penelope Cruz"
# file_path = f"applications/Mortgage Application - {borrower_name} - v2.pdf"

with open(file_path, "rb") as pdf_file:
    print(f"Writing {file_path}...")
    file_id = fs.put(pdf_file, filename=file_path)

loan_application = {
    "borrowerName": borrower_name,
    "pdfReferenceId": file_id,
    "processingStatus": "NEW",
    "receivedAt": datetime.now()
}

print(f"Writing application record for {borrower_name}...")
db.applications.insert_one(loan_application)

print("Done")
