from kfp.dsl import Input, Model, component

@component(base_image="python:3.9", 
    packages_to_install=["google-cloud-aiplatform",
        "pandas==2.0.0",
        "scikit-learn==1.5.1",
        "numpy==1.23.0",
        "joblib==1.4.2"]
)
def deploy_model(
    project_id: str,
    location: str,
    model: Input[Model],
    endpoint_name: str,
    model_name: str
):
    from google.cloud import aiplatform, aiplatform_v1
    import pandas
    import sklearn
    import numpy
    import joblib

    print(pandas.__version__)
    print(sklearn.__version__)
    print(numpy.__version__)
    print(joblib.__version__)

    aiplatform.init(project=project_id, location=location)

    client = aiplatform_v1.ModelServiceClient(client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"})
    request = {
        "parent": f"projects/{project_id}/locations/{location}",
        "filter": f"display_name={model_name}"
    }
    client.list_models(request=request)
    parent_models = list(client.list_models(request=request))
    parent_model=parent_models[0] if parent_models else None
    model_name = parent_model.name.split('/')[-1]

    model = aiplatform.Model(model_name)
    print(type(model))
    print(model)
    endpoint = aiplatform.Endpoint.create(display_name=endpoint_name) # iris-endpt 
    print(endpoint)
    model.deploy(
        endpoint=endpoint,
        machine_type="n1-standard-2"  # Specify the machine type
    )

    print(f"Model deployed to endpoint {endpoint.display_name}")