# Guía de instalación

Este documento contiene los pasos necesarios para ejecutar localmente la aplicación web.

El Backend está compuesto por Flask y una base de datos PostgreSQL.

El Frontend utiliza Astro como Framework principal, combinado con componentes de React.

Adicionalmente el backend puede acceder a las bases de datos vectoriales Chroma o Milvus.

  

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
