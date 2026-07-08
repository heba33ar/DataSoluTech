import datetime as dt
import pandas as pd

def test_dataframe_integrity(df):
    assert df is not None
    assert not df.empty

def test_dataframe_columns(df):
    assert len(df.columns) == 15

def test_dataframe_duplicates(df):
    assert df.duplicated().sum() == 0

def test_dataframe_null_values(df):
    assert df.isnull().sum().sum() == 0


#check if valid type, can I cast?
def test_dataframe_column_types(df):
    for val in df["Age"]:
        assert isinstance(val, (int))
    for val in df["Gender"]:
        assert (val in ["Male", "Female"]) 
    for val in df["Blood Type"]:
        assert (val in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
    for val in df["Billing Amount"]:
        assert isinstance(val, (float))
    for val in df["Room Number"]:
        assert isinstance(val, (int))
    for val in df["Test Results"]:
        assert (val in ["Normal", "Abnormal", "Inconclusive"])
    for val in df["Date of Admission"]:
        assert isinstance(val, (str, dt.datetime))
    for val in df["Discharge Date"]:
        assert isinstance(val, (str, dt.datetime))


