import os
from pymongo import MongoClient
import pandas as pd

from dataset import load_healthcare_df


#connect to MongoDB and return the database handle
def connect_to_mongodb(client):
    return client["healthcare_db"]


#recreate the patients collection with its schema validator, dropping any previous run
def create_patients_collection(db):
    if "patients" in db.list_collection_names():
        db.drop_collection("patients")
    return db.create_collection(
        "patients",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "Name",
                ],
                "properties": {
                    "Name": {"bsonType": "string"},
                    "Age": {"bsonType": "int", "minimum": 0, "maximum": 120},
                    "Gender": {"bsonType": "string", "enum": ["Male", "Female"]},
                    "Blood Type": {"bsonType": "string", "enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]},
                    "Medical Condition": {"bsonType": "string"},
                    "Date of Admission": {"bsonType": "date"},
                    "Doctor": {"bsonType": "string"},
                    "Hospital": {"bsonType": "string"},
                    "Insurance Provider": {"bsonType": "string"},
                    "Billing Amount": {"bsonType": ["double"]},
                    "Room Number": {"bsonType": "int"},
                    "Admission Type": {"bsonType": "string"},
                    "Discharge Date": {"bsonType": "date"},
                    "Medication": {"bsonType": "string"},
                    "Test Results": {"bsonType": "string", "enum": ["Normal", "Abnormal", "Inconclusive"]},
                },
            }
        },
    )


#insert the DataFrame into MongoDB, one document per row
def import_data(collection, df):
    #convert date columns to datetime, the validator declares them as bsonType date
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"], format='%Y-%m-%d')
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"], format='%Y-%m-%d')
    #clean names
    df["Name"] = df["Name"].str.strip().str.title()
    data = df.to_dict('records')
    collection.insert_many(list(data))


#run the full import, guarded so importing this module has no side effects
def main():
    uri = os.environ.get("MDB_URI", "mongodb://localhost:27017/")
    client = MongoClient(uri)
    db = connect_to_mongodb(client)
    patients_collection = create_patients_collection(db)
    import_data(patients_collection, load_healthcare_df())
    count = patients_collection.count_documents({})
    print(f"imported {count} documents into healthcare_db.patients")
    #close the connection
    client.close()


if __name__ == "__main__":
    main()
