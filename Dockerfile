FROM python:3.8

RUN pip3 install --no-cache scikit-learn pandas joblib flask requests boto3 tabulate xgboost sagemaker-training

# Copies the training code inside the container
COPY training-script.py /opt/ml/code/training-script.py

# Defines training-script.py as script entrypoint
ENV SAGEMAKER_PROGRAM training-script.py
 
