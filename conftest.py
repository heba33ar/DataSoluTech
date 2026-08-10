import pymongo
import pytest

from dataset import load_healthcare_df
from healthcare import build_mongo_uri


#one client for the whole test run
@pytest.fixture(scope="session")
def mongodb():
    client = pymongo.MongoClient(build_mongo_uri(), serverSelectionTimeoutMS=2000)
    assert client.admin.command("ping")["ok"] != 0.0
    yield client
    client.close()


#the database the migration writes to
@pytest.fixture(scope="session")
def healthcare_db(mongodb):
    return mongodb["healthcare_db"]


#the collection created by the migration, so run healthcare.py before the tests
@pytest.fixture(scope="session")
def patients_collection(healthcare_db):
    if "patients" not in healthcare_db.list_collection_names():
        pytest.fail("collection 'patients' not found, run the migration first: python healthcare.py")
    return healthcare_db["patients"]


#downloaded once for the whole run
@pytest.fixture(scope="session")
def df():
    return load_healthcare_df()
