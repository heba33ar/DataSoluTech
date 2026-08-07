import os

import pymongo
import pytest

from dataset import load_healthcare_df
from healthcare import create_patients_collection, import_data


#one client for the whole test run, fails fast if no server is listening
@pytest.fixture(scope="session")
def mongodb():
    uri = os.environ.get("MDB_URI", "mongodb://localhost:27017/")
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
    assert client.admin.command("ping")["ok"] != 0.0
    yield client
    client.close()


#the database healthcare.py writes to
@pytest.fixture(scope="session")
def healthcare_db(mongodb):
    return mongodb["healthcare_db"]


#run the import once per session so the suite works on a fresh database, instead of
#silently depending on healthcare.py having been run by hand first
@pytest.fixture(scope="session")
def patients_collection(healthcare_db, df):
    collection = create_patients_collection(healthcare_db)
    #pass a copy, import_data rewrites the date columns in place
    import_data(collection, df.copy())
    return collection


#session scope: 55k rows are fetched and deduped once for the whole run
@pytest.fixture(scope="session")
def df():
    return load_healthcare_df()
