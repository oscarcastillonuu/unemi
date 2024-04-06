Sistema de Gestión Académica
===

## Requisitos

- Python v3.9.10

- Django 4.0.3

- Apache Server

- PostgreSQL 12

- Redis

```sh
# Ejemplo con Fedora
# Python está por defecto en Centos 9
sudo dnf install httpd httpd-devel redis
```

En producción se corre CentOS 9, el Dockerfile contiene las dependencias
necesarias para ese sistema operativo. Una alternativa a esto es correr los
requisitos externos dentro de contenedores. Para esto, requiere tener instalado
[Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/).

## Desarrollo

Hay tres opciones para correr el SGA en tu maquina de desarrollo. Se puede
correr con la instalación de Python global, dentro de un ambiente virtual
(virtualenv), o con Docker Compose. Se recomienda el ambiente virtual para
asegurar las versiones correctas de Python y sus librerias.

### Virtualenv

1. Debe asegurar de que tiene instalados los requisitos del proyecto y que sean
   accesibles. Esto incluye los IPs de la base de datos y cachés.

2. Instalar las dependencias de la aplicación. En caso de utilizar un ambiente
   virtual, crear el virtualenv con Python 3.6.

  ```sh
  # (Opcional) Crear y activar un nuevo virtualenv
  python -m venv venv
  source venv/bin/activate

  # Instalar dependencias dentro del virtualenv
  pip install --upgrade pip
  ```

3. Definir valores de ambiente con los IP de los requisitos externos.

  ```sh
  # Crear copia local de archivo de variables de entorno
  cp .env.example .env

  # Abre el archivo .env y llena con los valores para su ambiente
  ```

4. Correr el servidor local

### Docker Compose

TODO: Documentar `docker-compose.venv.yml`

```sh
# Crear los directorios de datos de las bases de datos
mkdir -p data/admision_db data/posgrado_db data/pregrado_db sga_admision_db sga_default_db sga_epunemi_db

# Crear el contenedor de la aplicación
docker-compose build

# Correr el contenedor y sus dependencias
docker-compose up
```

#### Errores de stat

```sh
error checking context: 'can't stat '/home/me/dev/academico/data/admision_db''.
```

Estos errores se dan cuando el usuario no es miembro del grupo de Docker. Se
puede [agregar el UID y GID del usuario](https://dev.to/acro5piano/specifying-user-and-group-in-docker-i2e
), o se puede cambiar el dueño del directorio de datos:

```sh
# Dentro del directorio del proyecto
sudo chown -R $USER data
```


#### Requerimientos

```sh
pip install -r requirements.txt
```

Intalar los requerimientos para el correcto funcionamiento con, pip install -r requirements.txt

```sh
absl-py==1.0.0
amqp==5.1.0
anyjson==0.2.5
arabic-reshaper==2.1.3
asgiref==3.4.1
astunparse==1.6.3
async-timeout==4.0.2
attrs==21.4.0
billiard==3.6.4.0
cached-property==1.5.2
cachetools==4.2.4
celery==5.2.3
certifi==2021.10.8
cffi==1.15.0
chardet==3.0.4
charset-normalizer==2.0.12
clang==5.0
click==8.0.4
click-didyoumean==0.3.0
click-plugins==1.1.1
click-repl==0.2.0
code128==0.3
colorama==0.4.4
contextvars==2.4
coreapi==2.3.3
coreschema==0.0.4
cryptography==36.0.1
cssselect2==0.5.0
Deprecated==1.2.13
Django==4.0.3
django-appconf==1.0.5
django-celery==3.1.17
django-ckeditor==6.2.0
django-cors-headers==3.11.0
django-crispy-forms==1.14.0
django-debug-toolbar==3.2.4
django-js-asset==2.0.0
django-mobi==0.1.7
django-oauth-toolkit==1.7.0
django-pwa==1.0.10
django-qrcode==0.3
django-select2==7.10.0
django-sendgrid-v5==1.2.0
django-stubs==1.9.0
django-stubs-ext==0.3.1
django-webpush==0.3.4
djangorestframework==3.13.1
djangorestframework-simplejwt==5.1.0
docutils==0.18.1
et-xmlfile==1.1.0
future==0.18.2
googletrans==3.0.0
h11==0.9.0
h2==3.2.0
hiredis==2.0.0
hpack==3.0.0
hstspreload==2021.12.1
html2image==2.0.1
html5lib==1.1
http-ece==1.1.0
httpcore==0.9.1
httpx==0.13.3
hyperframe==5.2.0
idna==2.10
immutables==0.16
isodate==0.6.1
itypes==1.2.0
Jinja2==3.0.3
jwcrypto==1.0
kombu==5.2.4
lxml==4.8.0
MarkupSafe==2.1.1
mypy==0.941
mypy-extensions==0.4.3
oauthlib==3.2.0
openpyxl==3.0.9
packaging==21.3
pdf2image==1.16.0
Pillow==9.0.1
platformdirs==2.5.1
prompt-toolkit==3.0.28
psycopg2==2.9.3
py-vapid==1.8.2
pycparser==2.21
PyJWT==2.3.0
pyparsing==3.0.7
PyPDF2==1.26.0
PyPDF3==1.0.6
PyQRCode==1.2.1
python-bidi==0.4.2
python-dateutil==2.8.2
python-docx==0.8.11
python-http-client==3.3.7
pytz==2022.1
pywebpush==1.9.4
redis==4.2.0
reportlab==3.6.8
requests==2.27.1
requests-file==1.5.1
requests-toolbelt==0.9.1
rfc3986==1.5.0
sendgrid==6.9.7
six==1.16.0
sniffio==1.2.0
spyne==2.14.0
sqlparse==0.4.2
starkbank-ecdsa==2.0.3
svglib==1.2.1
tinycss2==1.1.1
toml==0.10.2
tomli==2.0.1
tqdm==4.63.0
types-pytz==2021.3.6
types-PyYAML==6.0.5
typing_extensions==4.1.1
tzdata==2022.1
uritemplate==4.1.1
urllib3==1.26.9
vine==5.0.0
wcwidth==0.2.5
webencodings==0.5.1
wrapt==1.14.0
xhtml2pdf==0.2.6
xlrd==2.0.1
XlsxWriter==3.0.3
xlwt==1.3.0
zeep==4.1.0
endesive==0.2.0
qrcode==7.3.1
```
#### PWA cambiar URL por RE_PATH
.\site-packages\pwa\urls.py

```sh
from django.urls import re_path

from .views import manifest, service_worker, offline

# Serve up serviceworker.js and manifest.json at the root
urlpatterns = [
    re_path(r'^serviceworker\.js$', service_worker, name='serviceworker'),
    re_path(r'^manifest\.json$', manifest, name='manifest'),
    re_path('^offline/$', offline, name='offline')
]
```
