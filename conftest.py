import os

import pandas as pd
import pymongo
import pytest


@pytest.fixture(scope="session")
def mongodb():
    uri = os.environ.get("MDB_URI", "mongodb://localhost:27017/")
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
    assert client.admin.command("ping")["ok"] != 0.0
    yield client
    client.close()


@pytest.fixture(scope="session")
def healthcare_db(mongodb):
    return mongodb["healthcare_db"]


@pytest.fixture(scope="session")
def patients_collection(healthcare_db):
    return healthcare_db["patients"]


@pytest.fixture
def df():
    return pd.read_csv("healthcare_dataset.csv")
