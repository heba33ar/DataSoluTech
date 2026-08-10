import datetime as dt

from healthcare import INDEXES, ROLES

def test_mongodb_fixture(mongodb):
    """This test passes if `MDB_URI` is set to a valid connection
    string."""
    assert mongodb.admin.command("ping")["ok"] > 0


#the migration created the collection
def test_patients_collection_exists(healthcare_db, patients_collection):
    assert "patients" in healthcare_db.list_collection_names()


#the import inserted something
def test_patients_collection_has_documents(patients_collection):
    assert patients_collection.count_documents({}) > 0

#minus one column for the MongoDB _id
def test_column_number(df, patients_collection):
    assert len(df.columns) == len(list(patients_collection.find_one().keys()))-1

#every row made it in, nothing dropped by the validator
def test_document_count(df, patients_collection):
    assert len(df) == patients_collection.count_documents({})


#the indexes were created
def test_indexes_created(patients_collection):
    existing = set(patients_collection.index_information())
    for _, name in INDEXES:
        assert name in existing, f"missing index {name}"


#the roles were created
def test_custom_roles_exist(healthcare_db):
    existing = {role["role"] for role in healthcare_db.command("rolesInfo", 1)["roles"]}
    for role in ROLES:
        assert role in existing, f"missing role {role}"


#check the stored documents match the validator in healthcare.py
def test_column_types(patients_collection):
    for doc in patients_collection.find():
        assert isinstance(doc["Age"], int)
        assert (doc["Gender"] in ["Male", "Female"])
        assert (doc["Blood Type"] in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        assert isinstance(doc["Billing Amount"], (int, float))
        assert isinstance(doc["Room Number"], int)
        assert (doc["Test Results"] in ["Normal", "Abnormal", "Inconclusive"])
        assert isinstance(doc["Date of Admission"], (str, dt.datetime))
        assert isinstance(doc["Discharge Date"], (str, dt.datetime))