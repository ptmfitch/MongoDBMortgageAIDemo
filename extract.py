import pymongo
import gridfs
import io
from PyPDF2 import PdfReader
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI

mongodb_srv = ""
azure_api_key = ""

print("Connecting to MongoDB...")
client = pymongo.MongoClient(mongodb_srv)
db = client["MortgageLending"]
fs = gridfs.GridFS(db)

llm = AzureChatOpenAI(
#    azure_endpoint="https://peter-fitch-demo-resource.cognitiveservices.azure.com/",
#    azure_deployment="Mistral-Large-3",
#    api_version="2024-05-01-preview",
    api_key=azure_api_key,
    temperature=0
)


class MortgageV1(BaseModel):
    fullName: str
    dateOfBirth: datetime
    currentAddress: str
    employmentStatus: str
    occupation: str
    annualGrossIncome: int
    contactPhone: str
    emailAddress: str
    nationalInsuranceNo: str


class MortgageV2(MortgageV1):
    dependents: int


print("Fetching NEW application...")
application = db.applications.find_one({"processingStatus": "NEW"})

if application:
    print(f"Retrieving PDF for {application['borrowerName']} from GridFS...")
    grid_out = fs.get(application["pdfReferenceId"])
    pdf_bytes = grid_out.read()

    print("Extracting text from PDF...")
    pdf_stream = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)
    document_text = ""
    for page in reader.pages:
        document_text += page.extract_text()

    print("Classifying document version...")
    classify_prompt = f"Does this document contain information about dependents? Return 'v2' if yes, 'v1' if no: {document_text[:2000]}"
    choice = llm.invoke(classify_prompt).content.strip().lower()

    if "v2" in choice:
        print("Version v2 detected.")
        extractor = llm.with_structured_output(MortgageV2)
        schema_version = "v2"
    else:
        print("Version v1 detected.")
        extractor = llm.with_structured_output(MortgageV1)
        schema_version = "v1"

    print(f"Extracting intelligence using {schema_version} model...")
    extracted_data = extractor.invoke(document_text)

    print("Updating application record...")
    db.applications.update_one(
        {"_id": application["_id"]},
        {
            "$set": {
                "extractedData": extracted_data.model_dump(),
                "schemaVersion": schema_version,
                "processingStatus": "EXTRACTED",
                "extractedAt": datetime.now()
            }
        }
    )
    print("Done")
else:
    print("No applications with status NEW found.")
