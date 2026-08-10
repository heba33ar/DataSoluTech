import kagglehub
from kagglehub import KaggleDatasetAdapter

DATASET = "prasad22/healthcare-dataset"
DATASET_FILE = "healthcare_dataset.csv"


#download the dataset from Kaggle into a DataFrame
def load_healthcare_df():
    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        DATASET,
        DATASET_FILE,
    )
    #the published file contains 534 duplicate rows
    return df.drop_duplicates().reset_index(drop=True)
