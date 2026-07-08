import os
from pymongo import MongoClient
import pandas as pd
import datetime as dt

uri = os.environ.get("MDB_URI", "mongodb://localhost:27017/")
client = MongoClient(uri)
df = pd.read_csv("healthcare_dataset.csv")


#connect to MongoDB and create a database
def connect_to_mongodb(client):
    db = client["healthcare_db"]
    if "patients" in db.list_collection_names():
        db.drop_collection("patients")
    return db

#create a collection for patients with target types
def create_patients_collection(db):
    if "patients" not in db.list_collection_names():
        patients_collection = db.create_collection(
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
    else:
        patients_collection = db.get_collection("patients")
    return patients_collection
#df data types
def get_dataframe_dtypes(df):
    return df.dtypes.to_dict()


#import data from CSV
def import_data(collection, df):
    #convert date columns to datetime
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"],format='%Y-%m-%d')
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"],format='%Y-%m-%d')
    #clean names
    df["Name"] = df["Name"].str.strip().str.title()
    data = df.to_dict('records')
    collection.insert_many(list(data))

db = connect_to_mongodb(client)
patients_collection = create_patients_collection(db)
import_data(patients_collection, df)
#get date type from MongoDB
print()




#print(df.dtypes)
#close the connection
client.close()