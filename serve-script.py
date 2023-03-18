#!/usr/bin/env python

import joblib
import json
import os
from io import StringIO

import pandas as pd
import flask
from flask import Flask, Response

model_path = '/opt/ml/model'
model = joblib.load(os.path.join(model_path, "model.joblib"))

app = Flask(__name__)


@app.route("/ping", methods=["GET"])
def ping():
    return Response(response="\n", status=200)


@app.route("/invocations", methods=["POST"])
def predict():
    if flask.request.content_type == 'application/json':
        data = flask.request.data.decode('utf-8')
        data = json.loads(data)

        response = model.predict(data)
        response = pd.DataFrame(response)
        response = response.to_csv(header=False, index=False)
    else:
        return flask.Response(response='JSON data only', status=415, mimetype='text/plain')

    return Response(response=response, status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)