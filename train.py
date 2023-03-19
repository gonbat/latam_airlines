#!/usr/bin/env python
import os
import joblib
import requests
import json
from datetime import datetime, timezone


import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
import xgboost as xgb
from xgboost import plot_importance
import boto3
import botocore


def update_report_file(metrics_dictionary: dict, hyperparameters: dict,
                       commit_hash: str, training_job_name: str,
                       prefix: str, bucket_name: str,) -> None:
    """This funtion update the report file located in the S3 bucket according to the provided metrics
    if report file doesn't exist, it will create a template based on metrics_dictionary schema and upload it to S3
    Args:
        metrics_dictionary (dict): the training job metrics with this format: {"Metric_1_Name": "Metric_1_Value", ...}
        hyperparameters (dict): the training job hyperparameters with this format: {"Hyperparameter_1_Name": "Hyperparameter_1_Value", ...}
        commit_hash (str): the 7 digit hash of the commit that started this training job
        training_job_name (str): name of the current training job
        prefix (str): name of the folder in the S3 bucket
        bucket_name (str): name of the S3 bucket
    Returns:
        None
    """
    object_key = f'{prefix}/reports.csv'

    s3 = boto3.resource('s3')

    try:
        s3.Bucket(bucket_name).download_file(object_key, 'reports.csv')

        # Load reports df
        reports_df = pd.read_csv('reports.csv')

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            columns = ['date_time', 'hyperparameters', 'commit_hash',
                       'training_job_name'] + list(metrics_dictionary.keys())
            pd.DataFrame(columns=columns).to_csv('./reports.csv', index=False)

            # Upload template reports df
            s3.Bucket(bucket_name).upload_file('./reports.csv', object_key)

            # Load reports df
            reports_df = pd.read_csv('./reports.csv')

        else:
            raise

    # Add new report to reports.csv
    # Use UTC time to avoid timezone heterogeneity
    date_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Add new row
    new_row = dict({'date_time': date_time, 'hyperparameters': json.dumps(hyperparameters), 'commit_hash': commit_hash, 'training_job_name': training_job_name},
                   **metrics_dictionary)
    new_report = pd.DataFrame(new_row, index=[0])
    reports_df = reports_df.append(new_report)

    # Upload new reports dataframe
    reports_df.to_csv('./reports.csv', index=False)
    s3.Bucket(bucket_name).upload_file('./reports.csv', object_key)

## Dataset Transformations
def temporada_alta(fecha):
    fecha_año = int(fecha.split('-')[0])
    fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
    range1_min = datetime.strptime('15-Dec', '%d-%b').replace(year = fecha_año)
    range1_max = datetime.strptime('31-Dec', '%d-%b').replace(year = fecha_año)
    range2_min = datetime.strptime('1-Jan', '%d-%b').replace(year = fecha_año)
    range2_max = datetime.strptime('3-Mar', '%d-%b').replace(year = fecha_año)
    range3_min = datetime.strptime('15-Jul', '%d-%b').replace(year = fecha_año)
    range3_max = datetime.strptime('31-Jul', '%d-%b').replace(year = fecha_año)
    range4_min = datetime.strptime('11-Sep', '%d-%b').replace(year = fecha_año)
    range4_max = datetime.strptime('30-Sep', '%d-%b').replace(year = fecha_año)
    
    if ((fecha >= range1_min and fecha <= range1_max) or 
        (fecha >= range2_min and fecha <= range2_max) or 
        (fecha >= range3_min and fecha <= range3_max) or
        (fecha >= range4_min and fecha <= range4_max)):
        return 1
    else:
        return 0
def dif_min(data):
    fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
    fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
    dif_min = ((fecha_o - fecha_i).total_seconds())/60
    return dif_min

def get_periodo_dia(fecha):
    fecha_time = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S').time()
    mañana_min = datetime.strptime("05:00", '%H:%M').time()
    mañana_max = datetime.strptime("11:59", '%H:%M').time()
    tarde_min = datetime.strptime("12:00", '%H:%M').time()
    tarde_max = datetime.strptime("18:59", '%H:%M').time()
    noche_min1 = datetime.strptime("19:00", '%H:%M').time()
    noche_max1 = datetime.strptime("23:59", '%H:%M').time()
    noche_min2 = datetime.strptime("00:00", '%H:%M').time()
    noche_max2 = datetime.strptime("4:59", '%H:%M').time()
    
    if(fecha_time > mañana_min and fecha_time < mañana_max):
        return 'mañana'
    elif(fecha_time > tarde_min and fecha_time < tarde_max):
        return 'tarde'
    elif((fecha_time > noche_min1 and fecha_time < noche_max1) or
        (fecha_time > noche_min2 and fecha_time < noche_max2)):
        return 'noche'
# Define main training function
def main():
    with open('/opt/ml/input/config/hyperparameters.json', 'r') as json_file:
        hyperparameters = json.load(json_file)
        print(hyperparameters)

    with open('/opt/ml/input/config/inputdataconfig.json', 'r') as json_file:
        inputdataconfig = json.load(json_file)
    print(inputdataconfig)

    with open('/opt/ml/input/config/resourceconfig.json', 'r') as json_file:
        resourceconfig = json.load(json_file)
    print(resourceconfig)

    training_data_path = '/opt/ml/input/data/training'
    training_data_file = os.path.join(training_data_path, 'dataset_SCL.csv')
    training_data = pd.read_csv(training_data_file)

    ##Dataset transformations
    training_data['temporada_alta'] = training_data['Fecha-I'].apply(temporada_alta)
    training_data['dif_min'] = training_data.apply(dif_min, axis = 1)
    training_data['atraso_15'] = np.where(training_data['dif_min'] > 15, 1, 0)
    training_data['periodo_dia'] = training_data['Fecha-I'].apply(get_periodo_dia)
    print(training_data)

    data = shuffle(training_data[['OPERA', 'MES', 'TIPOVUELO', 'SIGLADES', 'DIANOM', 'atraso_15']], random_state = 111)

    features = pd.concat([pd.get_dummies(data['OPERA'], prefix = 'OPERA'),pd.get_dummies(data['TIPOVUELO'], prefix = 'TIPOVUELO'), pd.get_dummies(data['MES'], prefix = 'MES')], axis = 1)
    label = data['atraso_15']

    X_train, X_test, y_train, y_test = train_test_split(features, label, test_size = 0.33, random_state = 42)

    # Fit the model
    n_estimators = int(hyperparameters['n_estimators'])
    max_depth = int(hyperparameters['max_depth'])
    learning_rate = float(hyperparameters['learning_rate'])
    random_state = int(hyperparameters['random_state'])

    modelxgb = xgb.XGBClassifier(random_state=random_state, learning_rate=learning_rate,n_estimators=n_estimators,max_depth=max_depth)
    modelxgb = modelxgb.fit(X_train, y_train)

    # Evaluate model
    y_predxgb = modelxgb.predict(X_test)
    test_report = classification_report(y_test, y_predxgb, output_dict=True)
    confusion_matrix_ = str(confusion_matrix(y_test, y_predxgb))

    metrics_dictionary = {"precision": test_report["1"]["precision"],
    "recall": test_report["1"]["recall"],
    "f1-score": test_report["1"]["f1-score"],
    "support": test_report["1"]["support"],
    "confusion_matrix": confusion_matrix_
    }


    print(metrics_dictionary)
    
    # Save the model
    model_path = '/opt/ml/model'
    model_path_full = os.path.join(model_path, 'model.joblib')
    joblib.dump(modelxgb, model_path_full)

    
    # Update the Report File
    PREFIX = os.environ['PREFIX']
    BUCKET_NAME = os.environ['BUCKET_NAME']
    GITHUB_SHA = os.environ['GITHUB_SHA']
    TRAINING_JOB_NAME = os.environ['TRAINING_JOB_NAME']

    update_report_file(metrics_dictionary=metrics_dictionary, hyperparameters=hyperparameters,
                       commit_hash=GITHUB_SHA, training_job_name=TRAINING_JOB_NAME, prefix=PREFIX, bucket_name=BUCKET_NAME)

if __name__ == '__main__':
    main()