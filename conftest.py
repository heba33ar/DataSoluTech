import pymongo
import pytest

from dataset import load_healthcare_df
from healthcare import build_mongo_uri


#one client for the whole test run, fails fast if no server is listening
@pytest.fixture(scope="session")
def mongodb():
    client = pymongo.MongoClient(build_mongo_uri(), serverSelectionTimeoutMS=2000)
    assert client.admin.command("ping")["ok"] != 0.0
    yield client
    client.close()


#the database healthcare.py writes to
@pytest.fixture(scope="session")
def healthcare_db(mongodb):
    return mongodb["healthcare_db"]


#the collection the migration produced. These tests inspect it, they do not rebuild
#it, so what they check is the real result of running healthcare.py
@pytest.fixture(scope="session")
def patients_collection(healthcare_db):
    if "patients" not in healthcare_db.list_collection_names():
        pytest.fail("collection 'patients' not found, run the migration first: python healthcare.py")
    return healthcare_db["patients"]


#session scope: 55k rows are fetched and deduped once for the whole run
@pytest.fixture(scope="session")
def df():
    return load_healthcare_df()
