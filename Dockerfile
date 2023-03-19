FROM python:3.8

RUN pip3 install --no-cache scikit-learn pandas joblib flask requests boto3 tabulate xgboost

COPY training-script.py /opt/ml/code/training-script.py
COPY serve-script.py /usr/bin/serve

RUN chmod 755 /opt/ml/code /usr/bin/serve

EXPOSE 8080
 
