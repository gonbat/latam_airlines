# latam_airlines
Para resolver el challenge, utilicé varias herramientas de AWS, como S3, ECS, Sagemaker, Cloudwatch y API Gateway. Cuando genero un pull request desde la rama de desarrollo, se ejecuta el flujo de trabajo 'pipeline'. En el primer paso de este flujo, se crea una imagen en ECS que contiene los archivos train.py y serve.py. El archivo train.py contiene toda la preparación del conjunto de datos y la definición del modelo, mientras que el archivo serve.py define las rutas para el despliegue. El siguiente paso ejecuta el trabajo de entrenamiento (training-job.py) utilizando Sagemaker, donde se pueden modificar o agregar hiperparámetros y definir la instancia que se va a utilizar. Una vez finalizado el entrenamiento, aparecen las métricas de entrenamiento, los hiperparámetros, el registro y la dirección donde se guarda el modelo en el pull request. Puede volver a entrenar el modelo con otros hiperparámetros o fusionarlo con la rama principal (main) para ejecutar la última acción llamada 'deploy', que genera un endpoint en Sagemaker para nuestro modelo. Por último, cargo endpoint del modelo de Sagemaker en API Gateway para poder consumirlo desde allí.

## Reporte de training con hiperparametros y resultados.
![image](https://user-images.githubusercontent.com/52375173/226212298-f3bdca74-cf49-4563-bd48-d7d484144fb3.png)


## Pregunta 1
Elijo XGBoost porque es más avanzado que la regresión logística, ya que utiliza árboles de decisión para modelar relaciones no lineales entre las features y la variable objetivo. Logrando capturar patrones más complejos en los datos y  generando modelos más precisos que la regresión logística.

En este caso particular las métricas de evaluación del modelo ( precisión, recall, F1-score, ) son mejores en XGBoost que en regresión logística, y pienso que es unarazón válida para elegir XGBoost. Sin embargo, en esta caso el modelo tambien es afectado por el desbalanceo entre la clase positiva/negativa y la falta de datos teniendo un performance pobre con ambos modelos. 

## Pregunta 2
Implemente el uso de hiperparametros para mejorar el rendimiento del modelo teniendo en cuenta principalmente el Recall ya que queremos predecir los vuelos que tienen atraso y son la clase minoritaria, por eso metricas como accuaracy o precision no son tan utiles para este problema.

## Pregunta 3
La API fue cargada en Sagemaker, para luego ser utilizada a traves de API Gateway.
![image](https://user-images.githubusercontent.com/52375173/226212043-fe3e4825-c9a4-4603-8471-7f19f61f1521.png)

## Pregunta 4
Cargue el endpoint de Sagemaker en API Gateway asi lo puedo exponer y usar desde mi terminal.
<img width="737" alt="image" src="https://user-images.githubusercontent.com/52375173/226502983-d8f7f980-35f6-4dd8-ae13-ad0161d2678b.png">
<img width="569" alt="image" src="https://user-images.githubusercontent.com/52375173/226621683-9a6e3513-0be3-4379-a775-b4e5a7630974.png">
<img width="569" alt="image" src="https://user-images.githubusercontent.com/52375173/226622226-e767505d-d746-42aa-a53a-d223609bc275.png">
![image](https://user-images.githubusercontent.com/52375173/226623826-0fe29718-ab85-4367-b800-515776ed0b48.png)

## Prgunta 5
Se puede mejorar asignando una instancia con más recursos para que la API sea más eficiente. Además, también se puede utilizar AutoScaling, que asigna automáticamente más recursos solo cuando son necesarios, tanto en Sagemaker como en API Gateway. De esta manera, se pueden manejar grandes cargas de trabajo sin tener que preocuparse por sobrecargar el servidor o  falta de capacidad.


## Capturas Artefactos AWS


### ECS
![image](https://user-images.githubusercontent.com/52375173/226614584-dba3a166-736c-4ef7-9d4d-658bc1f7177f.png)
### Sagemaker
![image](https://user-images.githubusercontent.com/52375173/226212145-28c11084-9c9f-45b1-b0a3-93fd2490eede.png)
### S3 
![image](https://user-images.githubusercontent.com/52375173/226212216-08ccb872-bf99-4970-aec7-5df81d78c041.png)
### CloudWatch
![image](https://user-images.githubusercontent.com/52375173/226212350-9ee20337-2a62-49a5-9918-0e351f39cea6.png)
