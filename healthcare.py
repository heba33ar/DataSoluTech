import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import pandas as pd

from dataset import load_healthcare_df

DATABASE = "healthcare_db"
COLLECTION = "patients"

#fields of a patient document, used by the schema validator below
PATIENT_PROPERTIES = {
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
}

#the actions each role is allowed on the patients collection
ROLES = {
    "patients_reader": ["find"],
    "patients_writer": ["find", "insert", "update"],
    "patients_admin": ["find", "insert", "update", "remove", "createIndex", "dropIndex"],
}

#one account per role
USERS = {
    "nurse": "patients_reader",
    "doctor": "patients_writer",
    "data_admin": "patients_admin",
}

#indexes to create after the import, as (field, index name)
INDEXES = [("Name", "name_idx")]


#read the credentials from .env, or from the variables docker-compose sets
def build_mongo_uri():
    load_dotenv()
    uri = os.environ.get("MDB_URI")
    if uri:
        return uri
    host = os.environ.get("MONGO_HOST", "localhost:27017")
    user = os.environ.get("MONGO_ROOT_USERNAME")
    password = os.environ.get("MONGO_ROOT_PASSWORD")
    if not user or not password:
        #no credentials, so the server runs without authentication
        return f"mongodb://{host}/"
    #quote_plus escapes characters that would break the URI
    #authSource=admin because the root account lives in the admin database
    return f"mongodb://{quote_plus(user)}:{quote_plus(password)}@{host}/?authSource=admin"


#connect to MongoDB and return the database
def connect_to_mongodb(client):
    return client[DATABASE]


#create the roles, or update them if they already exist
def create_roles(db):
    resource = {"db": DATABASE, "collection": COLLECTION}
    for role, actions in ROLES.items():
        definition = {
            "privileges": [{"resource": resource, "actions": actions}],
            "roles": [],
        }
        try:
            db.command({"createRole": role, **definition})
        except OperationFailure as error:
            #51002 means the role already exists
            if error.code != 51002:
                raise
            db.command({"updateRole": role, **definition})


#create the accounts, all sharing one password from the environment
def create_users(db):
    password = os.environ.get("MONGO_APP_PASSWORD")
    if not password:
        print("MONGO_APP_PASSWORD is not set, skipping user creation")
        return
    for user, role in USERS.items():
        definition = {"pwd": password, "roles": [{"role": role, "db": DATABASE}]}
        try:
            db.command({"createUser": user, **definition})
        except OperationFailure as error:
            #51003 means the user already exists
            if error.code != 51003:
                raise
            db.command({"updateUser": user, **definition})


#recreate the patients collection with its schema validator
def create_patients_collection(db):
    if COLLECTION in db.list_collection_names():
        db.drop_collection(COLLECTION)
    return db.create_collection(
        COLLECTION,
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "Name",
                ],
                "properties": PATIENT_PROPERTIES,
            }
        },
    )


#insert the DataFrame into MongoDB, one document per row
def import_data(collection, df):
    #the validator declares the dates as bsonType date, so convert them
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"], format='%Y-%m-%d')
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"], format='%Y-%m-%d')
    #clean names
    df["Name"] = df["Name"].str.strip().str.title()
    data = df.to_dict('records')
    collection.insert_many(list(data))


#index the collection so a search by name does not read every document
def create_indexes(collection):
    for field, name in INDEXES:
        collection.create_index(field, name=name)


#run the full import, guarded so importing this module has no side effects
def main():
    client = MongoClient(build_mongo_uri())
    db = connect_to_mongodb(client)
    create_roles(db)
    create_users(db)
    patients_collection = create_patients_collection(db)
    import_data(patients_collection, load_healthcare_df())
    create_indexes(patients_collection)
    count = patients_collection.count_documents({})
    print(f"imported {count} documents into {DATABASE}.{COLLECTION}")
    client.close()


if __name__ == "__main__":
    main()
