Este documento contiene los pasos necesarios para ejecutar localmente la aplicación web.
También se incluye una explicación sobre las funcionalidades básicas de la aplicación.

El Backend está compuesto por Flask y una base de datos PostgreSQL.
El Frontend utiliza Astro como Framework principal, combinado con componentes de React.
Adicionalmente el backend puede acceder a las bases de datos vectoriales Chroma o Milvus.

# Guía de instalación
## Instalación del backend
### Instalación de base de datos PostgreSQL
Instalar postgradesql 16.4 desde el instalador: 
https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

Cambiar contraseña del usuario postgres:
````bash
cd C:\Program Files\PostgreSQL\16\bin>
psql -U postgres
ALTER USER postgres with encrypted password '123';
````
### Instalar plugin pgvector en PostgreSQL
Instalar visual studio con herramientas: 
[https://learn.microsoft.com/en-us/cpp/build/vscpp-step-0-installation?view=msvc-170](https://learn.microsoft.com/en-us/cpp/build/vscpp-step-0-installation?view=msvc-170)

Poner herramientas en viariables de entorno: 
````
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
````

Instalar pgVector en la máquina local (es necesario ejecutar cmd como administrador, en PS no funciona): 
````
set "PGROOT=C:\Program Files\PostgreSQL\16"
cd %TEMP%
git clone --branch v0.7.2 https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win 
nmake /F Makefile.win install
````  

### Paquetes necesarios
Es necesario tener instalado python3.12.3, en otras versiones las librerías Pydantic, LangChain y Chroma dan conflictos.

Instalar los paquetes necesarios  en un entorno virtual:

````bash
cd backend

python -m venv gestion_conocimiento
gestion_conocimiento\Scripts\activate
pip install -r requirements.txt
````

### Añadir extensión pgvector a Alchemy
````bash
cd backend

flask shell
from sqlalchemy import text
from app import db

db.session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
db.session.commit()
````

### Base de datos Alchemy
````bash
cd backend

flask db stamp head
flask db migrate
````

Añadir import pgvector a la versión de la migración:

Por ejemplo, si el resultado de flask db migrate es "INFO  [alembic.runtime.migration] Running upgrade 1fd16dd13b52 -> dea9462d1738, empty message"
Entonces añadir en el fichero backend\migrations\versions\1fd16dd13b52.py: 
````
import pgvector
````
Finalmente aplicar los cambios a la base de datos:
````
flask upgrade
````

### Variables de entorno

Es necesario indicar en el fichero /backend/.env las API keys de los servicios utilizados.

Para ello se ha añadido un fichero de ejemplo en /backend/.env.example:

````
FLASK_APP=app.py
FLASK_DEBUG=1
FLASK_ENV=development
JWT_SECRET_KEY=una_clave_todo_secreta_pim_pam_pum

GOOGLE_CLIENT_ID=
GOOGLE_SECRET_KEY=
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=
OPENAI_API_KEY=
TAVILY_API_KEY=
````

Se deben rellenar todas las variables incompletas.

La clave JWT (JWT_SECRET_KEY) puede modificarse por cualquier cadena de carácteres.

## Instalación del Frontend

Es necesario tener Node.js y npm instalado. 
La única versión con la que se ha probado es con Node 20.16.0.

### Instalar dependencias

````
cd frontend

npm install
````
### Variables de entorno
Es necesario indicar en el fichero /frontend/.env las variables necesarias.

El cliente de google es el mismo que el indicado en el backend.

Para ello se ha añadido un fichero de ejemplo en /frontend/.env.example:
````
VITE_GOOGLE_CLIENT_ID=
PUBLIC_REACT_APP_BACKEND_URL="http://localhost:5000"
````

## Ejecución
### Ejecución del backend
El servicio postgresql debe estar activo.
````
cd backend

flask run
````
### Ejecución del frontend
````
cd frontend

npm start
````

### Añadir datos al árbol
Hay un fichero csv en el backend que contiene conocimientos de ejemplo "backend/static/conocimientosLKS.csv"

Se pueden añadir directamente ejecutando una petición a la api del backend: 
````
localhost:5000/api/add_csv
````
Esto añadirá unos 500 conocimientos de ejemplo.

Puede tardar varios minutos, ya que por cada nodo se genera y almacena un embedding con la ruta del nodo.

> En caso de eliminar el nodo raíz, añadir otra raíz que no tenga el identificador '1' podría dar problemas. Se pueden reiniciar los identificadores desde el cliente de la base de datos.
# Funcionalidades
## Gestión de usuarios
Para poder utilizar las funcionalidades de la aplicación el usuario debe autenticarse mediante su cuenta de Google.

Al iniciar sesión, se guardará su correo electrónico en la base de datos. Tras esto, el usuario podrá añadir conocimientos a su cuenta, ya sea manualmente o subiendo su currículum.

La sesión se gestiona con un token de sesión http-only JWT, con una duración máxima de 2 horas.

Tras iniciar sesión, el usuario podrá acceder a tres secciones: 

- Arbol
- Personal
- Home

## Arbol general
En esta sección se muestra el árbol de conocimientos de la empresa.

Se pueden añadir / eliminar / modificar los nombres de los conocimientos. También se pueden cambiar de lugar arrastrándolos desde la parte izquierda.

También se pueden buscar los nodos por nombre, se tienen en cuenta las máyúsculas.

## Arbol personal
En esta sección se muestra un subárbol que representa el conocimiento del usuario.

Se puede mostrar de dos formas: 

- Switch desactivado: Se muestran únicamente los conocimientos que el usuario tiene, solo se pueden eliminar los nodos.
- Switch activado: Se muestran todos los conocimientos de la empresa, pero los del usuario están resaltados. En esta sección se pueden eliminar y añadir nodos, haciendo click en estos.

Los nodos que se añaden o eliminan en esta sección se modificarán solo en el subárbol del usuario, sin afectar el árbol general. De esta forma se podrían añadir requerimientos de privilegios para poder acceder al árbol general en un futuro, con diferentes roles de usuarios.

## Home
En esta sección se puede subir el currículum del usuario para extraer sus conocimientos.

Tras cargar el CV en forma de texto  o PDF, se le manda el currículum a un modelo de lenguaje, quien determina cuáles de los conocimientos de la empresa tiene el usuario. Después se añaden los conociemientos al subárbol del usuario.

En el directorio "backend\static\CV" hay varios currículums generados por ChatGPT para hacer pruebas.

## Grafos LangGraph

Se ha creado un grafo en LangGraph para crear una propuesta de proyecto automáticamente a partir de una licitación utilizando los conocimientos de la empresa. Tras esto, se ha creado otro grafo que dada una propuesta de proyecto elige los usuarios de la empresa considerados más adecuados para trabajar en este proyecto.

Para probar esta funcionalidad se ha creado una ruta http: "llm/test_licitacion_equipo_graph" que se define en el directorio "backend/LLM/llm_routes.py" y utiliza el grafo "backend/LLM/licitacion_equipo_graph"

> Este grafo puede llegar a tardar 1-5 minutos para generar una solución, limitado en gran medida por el paso del agente LATS. Se ha probado sobre todo con proyectos de desarrollo de aplicaciones web, pero el objetivo es que se pueda utilizar con diferentes tipos de proyectos software.

> El grafo se suele interrumpir para validar añadir conocimientos nuevos por consola. También se debe interactuar por consola para aprobar el proyecto, añadir feedback al proyecto y especificar la cantidad de usuarios.

Este grafo combina los dos grafos mencionados, obteniendo los usuarios propuestos a partir de la licitación.

La ejecución de este grafo se muestra por consola.

Para utilizar el grafo se han generado licitaciones de ejemplo usando ChatGPT, se pueden encontrar en el directorio "backend/static/licitacion"

También se puede consultar el mapa creado en Excalidraw para ver todas sus partes de forma visual.

Los diferentes agentes utilizados en este grafo (Zero Shot, Few Shots, ReAct, LATS, CRAG) son conocidos y han sido explicados en profundidad por diferentes estudios. Los agentes utilizados se han creado a partir de una base explicada en la documentación de LangGraph: https://langchain-ai.github.io/langgraph/
Además, en el mapa de Excalidraw se incluye los enlaces a la documentación para cada agente.
Los agentes Zero Shot y Few Shots no se incluyen en esta documentación, ya que son muy simples (el primero es un prompt sin ejemplos y el segundo es un prompt con ejemplos)

La selección de agentes puede no haber sido la más efectiva, por ejemplo, el grafo LATS es muy costoso y quizás sería de más utilidad en un caso en el que se requiera un contenido más abstracto con mayores posibilidades. De todas formas, estas estrategias tienen la capacidad de mejorar los resultados de los modelos de lenguaje, expandiendo aún más su potencial. En la web y en la documentación mencionada se pueden encontrar más estrategias para diferentes casos de uso.
### Grafo licitación
**Licitación -> propuesta de proyecto**

Se puede probar este grafo individualmente utilizando la ruta http: "llm/test_graph"

El funcionamiento abstracto del grafo es el siguiente: 

- Dados los datos de la licitación y unos requerimientos adicionales, genera con un agente Few Shots la descripción del proyecto que será de ayuda para crear una propuesta más detallada. 
- Genera las etapas técnicas del proyecto con un agente Reflection. Este agente genera una solución, critica esta solución y busca información adicional en la web. Con la crítica y la información adicional mejora esta solución.
- Genera los conocimientos/tecnologías abstractas (herramientas) para cada etapa utilizando un agente ReAct. Por ejemplo, 'Framework frontenda' sería una herramienta y 'Angular' sería una tecnología que se le podría asignar a esta herramienta. Este agente primero genera una solución inicial, y después decide si buscar en la web información adicional, modificar esta solución o marcarla como solución final. Además, utiliza la estrategia CoT (Chain of Thought) en cada llamada.
- Finalmente, se utiliza un subgrafo LATS (Language Agent Tree Search) para generar los candidatos de tecnologías para cada herramienta y elegir la tecnología propuesta. El subgrafo LATS intenta mejorar una solución inicial criticándola y utilizando el algoritmo de Montecarlo. Dentro de cada nodo de este algoritmo, se encuentra el siguiente subgrafo: 
- Subgrafo CRAG. Dadas las propuestas de herramientas que el agente ReAct ha generado, este subgrafo genera candidatos de tecnologías a partir del árbol de la empresa. Para ello, primero se buscan con una búsqueda semántica los 10 nodos del árbol de conocimientos más parecidos a la herramienta necesaria. Es por esto que cada nodo tiene un embedding en la base de datos que representa la ruta del nodo en forma de vector. Tras la búsqueda, un agente Zero Shot determina si el conocimiento es válido para esta herramienta, si existe alguna tecnología válida el subgrafo las devuelve. De no existir, se reintenta reescribiendo la herramienta con otro agente. Si sigue sin encontrarse ninguna tecnología válida, un agente Zero Shot propone una tecnología para suplir esta herramienta, se pausa el grafo y se espera a que el usuario valide la tecnología por consola. Si se valida la tecnología, un agente Zero Shot decide donde añadir el nodo.
Tras tener las propuestas de tecnologías, un agente Zero Shot elige una por cada herramienta, quedando así una propuesta de proyecto Software.
- En el último paso se imprime la propuesta de proyecto por consola y se le pide al usuario que valide el resultado. Si el usuario no lo valida, este tendrá que proporcionar feedback, reiniciando así el grafo. El grafo podrá volver a tres etapas dependiendo del feedback obtenido. Un agente Few Shots decidirá los siguientes tres casos: reiniciar todo el grafo, volver a definir las herramientas de cada etapa o volver a definir las tecnologías de cada herramienta de una etapa. En caso de volver a los dos últimos casos, el grafo modificará solo la etapa que el agente decida, con el objetivo de modificar únicamente lo que el usuario ha especificado.

### Grafo equipo
**propuesta de proyecto-> propuesta de equipo**

Se puede probar este grafo individualmente utilizando la ruta http: "llm/test_equipo_graph"

El funcionamiento abstracto del grafo es el siguiente: 

- Pide al usuario que introduzca la cantidad de trabajadores necesarios para el proyecto. 
- Dada la propuesta software y la cantidad de trabajadores, un agente Zero Shot genera unos puestos de trabajo (roles) para completar este proyecto.
- Otro agente Zero Shot clasifica los conocimientos del proyecto para cada puesto (un conocimiento puede aparecer en varios puestos)
- Finalmente, se realiza un problema de optimización para maximizar la cantidad de conocimientos suplidos por los usuarios. Teniendo por un lado los usuarios, con una lista de conocimientos cada uno, y por otro lado los puestos, con una lista de conocimientos también, se utiliza la función "linear_sum_assignment" de la librería "scipy.optimize" para maximizar el objetivo mencionado y elegir los usuarios.
- ## Bases de datos vectoriales
Se ha creado una llamada a modelos de lenguaje para ver la utilidad de la estrategia RAG en la gestión del conocimiento.

Es posible utilizar Milvus o Chroma para esto. En caso de utilizar Milvus, la aplicación escuchará a la base de datos en el puerto 19530, mientras que en el caso de Chroma en el 8000. Las pruebas se han realizado lanzando las bases de datos en Docker. Para cambiar de base de datos hay que indicar en el constructor de "backend/LLM/DB/modelTools.py" la variable vectorDB a chromaTools() o milvusTools(), para las funcionalidades desarrolladas cambiar de base de datos no tiene ninguna diferencia.

Con la petición http "llm/add_vector_files" se cargan algunos datos de ejemplo en la base de datos. Los ficheros embebidos son Jsons que representan una métrica para medir el conocimiento de un usuario en una escala del 1 al 5. Se cargan en chunks por conocimiento. El fichero con los datos de ejemplo se encuentra en "backend/static/data/0/proficency.json"

Con la petición http "llm/get_knowledge_level/<cv_file>/<skills_file>" se puede obtener el nivel de conocimiento estimado de un usuario en los conocimientos proporcionados basándose en el currículum proporcionado y en las métricas disponibles en la base de datos. Como enviar una métrica por conocimiento sería restrictivamente caro, se realiza una búsqueda semántica del currículum en la base de datos, obteniendo así las métricas más importantes para el curriculum proporcionado. Con estas métricas un modelo de lenguaje valora el nivel de los skills proporcionados.

Un ejemplo sería: "localhost:5000/llm/get_knowledge_level/cv1/skills2", que utiliza cv1.txt y skills2.json del directorio static.

Adicionalmente se ha creado la ruta http "llm/handle_knowledge_metric_reaact/<input_data>" que utilizando un agente ReAct (explicado en la sección de LangGraph) prefabricado de LangChain genera una métrica parecida a las añadidas a la base de datos para el conocimiento indicado. De esta forma, si queremos una métrica para AWS, podríamos ejecutar: 
""localhost:5000/llm/handle_knowledge_metric_reaact/AWS"

Por lo tanto, sería posible automatizar la creación de métricas y valoración de conocimientos encadenando las estrategias comentadas.

