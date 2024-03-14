
The goal of this project is to allow for a few things, research of a given chain and then the implementation of the chain. All files should be saved as well to the generated_code file so that we can see it directly but it should also print out the code in the console so that we can see it on the view

The ideal state once it is ready, is it working on the backend of our code to enable endless chains to be added 

Improvements from here
- Graph DB implementation for offchain routing features
- updating our db with the neccesary generated code
- commiting the code changes in a new feature branch that we can, test, auto merge and deploy

Current Flow

Human input agent (limits request to adding a chain and nothing else) -> chain agent(sets up all of the research agents and code agents)

# Running

`python3 src/main.py`


# Deployment of chromadb to gcp gke

1. Create cluster in kubernettes engine gcp
2. `cd k8s`
3.  `gcloud container clusters get-credentials chromadb --region us-central1 --project sphereone-testing`
4. `kubectl create -f .`
5. Done, wait for pods to start with `kubectl get pods` and `kubectl get service` to get the external ip address

# Deployment of flask to cloud run

`gcloud run deploy model-creator --source .`
