FROM python:3.8

RUN pip3 install --no-cache scikit-learn pandas joblib flask requests boto3 tabulate xgboost

COPY training-script.py /usr/bin/train
COPY serve-script.py /usr/bin/serve

RUN  /usr/bin/train /usr/bin/serve

EXPOSE 8080
 
