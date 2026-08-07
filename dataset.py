import kagglehub
from kagglehub import KaggleDatasetAdapter

DATASET = "prasad22/healthcare-dataset"
DATASET_FILE = "healthcare_dataset.csv"


#load the dataset straight from Kaggle into a DataFrame, no local file needed
def load_healthcare_df():
    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        DATASET,
        DATASET_FILE,
    )
    #the published dataset holds 534 exact duplicate rows, drop them before use
    return df.drop_duplicates().reset_index(drop=True)
