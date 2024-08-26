from kfp.dsl import Input, Model, component

@component(base_image="python:3.9", 
    packages_to_install=["google-cloud-aiplatform"],
)
def upload_model(
    project_id: str,
    location: str,
    model: Input[Model],
):
    from google.cloud import aiplatform

    aiplatform.init(project=project_id, location=location)

    aiplatform.Model.upload_scikit_learn_model_file(
        model_file_path=model.path,
        display_name="Iris-Classifier",
        project=project_id,
    )

    aiplatform.Model.export_model(
    export_format_id=""
)