from kfp.dsl import Dataset, Input, Metrics, Model, Output, component

@component(base_image="python:3.10", 
    packages_to_install=[
        "pandas==2.0.0",
        "scikit-learn==1.5.1",
        "numpy==1.23.0",
        "joblib==1.4.2",
        "fsspec==2024.6.1",
        "gcsfs==2024.6.1"
    ],
)
def choose_best_model(
    test_dataset: Input[Dataset],
    decision_tree_model: Input[Model],
    random_forest_model: Input[Model],
    metrics: Output[Metrics],
    best_model: Output[Model],
):
    import joblib
    import pandas as pd
    from sklearn.metrics import accuracy_score
    import os, pickle, fsspec, gcsfs

    test_data = pd.read_csv(test_dataset.path)

    dt = joblib.load(decision_tree_model.path)
    rf = joblib.load(random_forest_model.path)

    dt_pred = dt.predict(test_data.drop("Species", axis=1))
    rf_pred = rf.predict(test_data.drop("Species", axis=1))

    dt_accuracy = accuracy_score(test_data["Species"], dt_pred)
    rf_accuracy = accuracy_score(test_data["Species"], rf_pred)
    print(dt_accuracy)
    print(rf_accuracy)

    metrics.log_metric("Decision Tree (Accuracy)", (dt_accuracy))
    metrics.log_metric("Random Forest (Accuracy)", (rf_accuracy))

    filepath=best_model.path.replace("/gcs/", "gs://")
    filename='model.joblib'
    fs, _ = fsspec.core.url_to_fs(filepath)
    fs.makedirs(filepath, exist_ok=True)
    model_uri = os.path.join(filepath, filename)
    with fs.open(model_uri, "wb") as f:
        if rf_accuracy >= dt_accuracy:
           joblib.dump(rf, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
           joblib.dump(rf, f, protocol=pickle.HIGHEST_PROTOCOL)
        

    # if rf_accuracy >= dt_accuracy:
    #     joblib.dump(dt, best_model.path)
    # else:
    #     joblib.dump(rf, best_model.path)