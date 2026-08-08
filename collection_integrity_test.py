import datetime as dt

def test_mongodb_fixture(mongodb):
    """This test passes if `MDB_URI` is set to a valid connection
    string."""
    assert mongodb.admin.command("ping")["ok"] > 0


#the migration created the collection, this checks it really landed on the server
def test_patients_collection_exists(healthcare_db, patients_collection):
    assert "patients" in healthcare_db.list_collection_names()


#the import wrote something rather than silently inserting nothing
def test_patients_collection_has_documents(patients_collection):
    assert patients_collection.count_documents({}) > 0

#minus one column for the MongoDB _id
def test_column_number(df, patients_collection):
    assert len(df.columns) == len(list(patients_collection.find_one().keys()))-1

#every row made it in, nothing dropped by the validator
def test_document_count(df, patients_collection):
    assert len(df) == patients_collection.count_documents({})


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