# latam_airlines
Para resolver este challenge use herramientas de AWS como S3, ECS, Sagemaker, Cloudwatch. 
Cuando genero un pull request desde la branch development se va a ejecutar el workflow 'pipeline' que en su primer step crea una imagen en ecs que tiene los archivos train.py y serve.py. Train contiene todo el armado del modelo y serve las rutas para cuando se genere el deploy. El proximo paso ejecuta el job de training (training-job.py) usando Sagemaker, cuando se termina el entrenamiento en el pull request te aparecen unas metricas y si lo ves bien lo mergeas a main y ahi se ejecuta la ultima action 'deploy' que genera el endpoint en sagemaker para nuestro modelo.

## Reporte de training con hiperparametros y resultados.
![image](https://user-images.githubusercontent.com/52375173/226212298-f3bdca74-cf49-4563-bd48-d7d484144fb3.png)


## Pregunta 1
Elijo XGBoost porque es más avanzado que la regresión logística, ya que utiliza árboles de decisión para modelar relaciones no lineales entre las features y la variable objetivo. Logrando capturar patrones más complejos en los datos y  generando modelos más precisos que la regresión logística.

En este caso particular las métricas de evaluación del modelo ( precisión, recall, F1-score, ) son mejores en XGBoost que en regresión logística, y pienso que es unarazón válida para elegir XGBoost. Sin embargo, en esta caso el modelo tambien es afectado por el desbalanceo entre la clase positiva/negativa y la falta de datos teniendo un performance pobre con ambos modelos. 

## Pregunta 2
Implemente el uso de hiperparametros para mejorar el rendimiento del modelo teniendo en cuenta principalmente el Recall ya que queremos predecir los vuelos que tienen atraso y son la clase minoritaria, por eso metricas como accuaracy o precision no son tan utiles para este problema.

## Pregunta 3
La API fue expuesta utilizando Sagemaker endpoints.
![image](https://user-images.githubusercontent.com/52375173/226212043-fe3e4825-c9a4-4603-8471-7f19f61f1521.png)

## Pregunta 4
No pude hacer funcionar el endpoint de sagemaker con wrk.
## Prgunta 5
Podemos asignar una instancia con mas recursos para que la api sea mas eficiente, tambien esta la posibilidad de usar AutoScale que asigna mas recursos solo cuando se lo necesita.

## Capturas Artefactos AWS

### ECS
![image](https://user-images.githubusercontent.com/52375173/226212145-28c11084-9c9f-45b1-b0a3-93fd2490eede.png)
### S3 
![image](https://user-images.githubusercontent.com/52375173/226212216-08ccb872-bf99-4970-aec7-5df81d78c041.png)
### CloudWatch
![image](https://user-images.githubusercontent.com/52375173/226212350-9ee20337-2a62-49a5-9918-0e351f39cea6.png)
