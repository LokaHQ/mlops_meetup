import datetime
import json
import numpy as np
from flask import request, Flask, Response, jsonify
from joblib import load
from whylogs import get_or_create_session
from dotenv import load_dotenv

app = Flask(__name__)
model_path = "sklearn_model.joblib"
model = load(model_path)

# load env variables
load_dotenv()

session = get_or_create_session(".whylogs.yaml")
logger = session.logger(
    dataset_name="my_deployed_model", 
    dataset_timestamp=datetime.datetime.now(datetime.timezone.utc), 
)

@app.route("/ping", methods=["GET"])
def ping():
    """Determine if the container is working and healthy.
    In this sample container, we declare
    it healthy if we can load the model successfully."""
    status = 200
    return Response(response={"state": "healthy"}, status=status, mimetype="application/json")

@app.route("/invocations", methods=["POST"])
def predict():    
    data = request.data.decode("utf-8")
    data = json.loads(data)
    vector = [float(i) for i in data.values()]
    vector = np.array(vector).reshape(1, -1)
    pred = model.predict(vector)[0]
    print(pred)
    #Log to whylabs platform
    #Log input vector as dictionary
    logger.log(data)
    
    #Log predicted class
    logger.log({"churn": pred})
    return jsonify({"prediction": str(pred)})
