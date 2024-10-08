from kfp.dsl import Dataset, Output, component

@component(base_image="python:3.10", 
    packages_to_install=[
        "pandas==2.0.0",
        "scikit-learn==1.5.1",
        "numpy==1.23.0",
        "google-cloud-bigquery==2.34.3"
    ],
)
def load_data(
    project_id: str,
    bq_dataset: str,
    bq_table: str,
    train_dataset: Output[Dataset],
    test_dataset: Output[Dataset],
):
    import pandas as pd
    from google.cloud import bigquery
    from sklearn.model_selection import train_test_split

    client = bigquery.Client()

    dataset_ref = bigquery.DatasetReference(project_id, bq_dataset)
    table_ref = dataset_ref.table(bq_table)
    table = bigquery.Table(table_ref)
    iterable_table = client.list_rows(table).to_dataframe_iterable()

    dfs = []
    for row in iterable_table:
        dfs.append(row)

    df = pd.concat(dfs, ignore_index=True)
    del dfs

    df["Species"].replace(
        {
            "Iris-versicolor": 0,
            "Iris-virginica": 1,
            "Iris-setosa": 2,
        },
        inplace=True,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        df.drop(["Id","Species"], axis=1),
        df["Species"],
        test_size=0.2,
        random_state=42,
    )

    X_train["Species"] = y_train
    X_test["Species"] = y_test

    X_train.to_csv(f"{train_dataset.path}", index=False)
    X_test.to_csv(f"{test_dataset.path}", index=False)