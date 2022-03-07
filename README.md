# twitter-graph
Programa para crear un grafo social usando la API de Twitter.

Librerias usadas:
- pickle: cargar y guardar objetos de python
- tweepy: para poder acceder a la API de twitter
- networkx: analisis de grafos

Para poder ejecutar el programa primero hay que obtener las credenciales de twitter para poder hacer uso de su API y seleccionar una cuenta para generar el grafo desde esta.

La función 'crawler()' recibe dos parámetros, el usuario desde el que parte el algoritmo y el número máximo de nodos que se usarán para crear el grafo, se recomienda que este valor no sea >20, sino se quieren ejecuciones muy largas. La ejecución puede llevar más de una hora en finalizar.

Al acabarse la ejecución se guardará el grafo resultante en el directorio actual.

Imagen de un grafo obtenido con el programa al cual se le han aplicado algoritmos de reducción de tamaño para poder visualizarlo mejor:
- el color de los nodos: rosa (usuari no verificado), verde (usuario verificado)
- el tamaño de los nodes en función del nombre de followers
![image](https://user-images.githubusercontent.com/81804797/157102671-ac0d57f1-e776-4dc1-be7b-e5a659104522.png)
(visualización realizada mediante Gephi)
