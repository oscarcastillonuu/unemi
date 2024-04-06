# SISTEMA DE GESTIÓN ACADÉMICA - ESTUDIANTE

Este sistema solo permitira perfiles estudiantes (admisión, pregrado y posgrado)

## Creación del proyecto.

Para iniciar el proyecto debes de introductir:

### Pre requisitos

Debes de tener instalado NODE

```bash
# Ingresar al sigueinte enlace: https://nodejs.org/es/download/
# Comprobar node instalado
npm -v
```

### Instalar requisitos del proyecto

```bash
# Comando permitira la instalación de requerimientos
npm install
```

### Post Instalación

```bash
# Comando permitira copiar archivos de instalación de requerimientos a la carpeta static
npm run postinstall
```

Si estás viendo esto, probablemente ya hayas hecho este paso. ¡Felicitaciones!

> **Nota:** Localmente se creara la carpeta `node_modules`  
> **Nota:** Se debe contar con el archivo .env con la siguiente estructura - Consulta el tema ***"Cómo manipular el archivo de variables de entorno .env"*** dentro de este documento

```bash
VITE_BASE_API_URI_DEV=http://127.0.0.1:8000/api/1.0/jwt
VITE_BASE_API_URI_PROD=http://127.0.0.1:8000/api/1.0/jwt
VITE_BASE_API_STATIC_DEV=http://127.0.0.1:8000/static
VITE_BASE_API_STATIC_PROD=http://127.0.0.1:8000/static
VITE_BASE_API_DEV=http://127.0.0.1:8000
VITE_BASE_API_PROD=http://127.0.0.1:8000
VITE_BASE_WS_DEV=ws://127.0.0.1:8000
VITE_BASE_WS_PROD=ws://127.0.0.1:8000
VITE_CONTACT_EMAIL="tic@unemi.edu.ec"
VITE_FACEBOOK_PAGE="UNEMIEcuador"
VITE_LINKEDIN_PROFILE="unemiecuador"
VITE_TWITTER_USERNAME="UNEMIEcuador"
VITE_DOMAIN="unemi.edu.ec/"
VITE_SITE_URL="https://www.unemi.edu.ec/"
```

## Cómo manipular el archivo de variables de entorno `.env`

> **Nota:** El archivo `environments.enc` es el que contiene las variables de entorno, se tiene que realizar una **desencriptación** para obtener el archivo de variables de entorno `.env`.

> **Nota:** Para realizar la **desencriptación/encriptación** se requiere tener `gcloud cli`.

### Instalar e iniciar el sdk
> **Nota:** Si ya se tiene `gcloud` configurado, no es necesario realizar estos pasos.

1. Instalar el `SDK` - [¿Cómo instalar gcloud?](https://cloud.google.com/sdk/docs/install)

2. Iniciar el `SDK` con el proyecto `sga-instance-group` - [¿Cómo iniciar gcloud?](https://cloud.google.com/sdk/docs/initializing)

### **Desencriptar** el archivo .env

> **¡Importante!** Sustituir los valores de ***KEYRING*** y ***KEY*** en la última línea antes de correr el comando para `desencripción`.  
> Los valores se encuentran en una tabla de contenido en GCP [sga-instance-group](https://console.cloud.google.com/security/kms/key/manage/us-east1/sga/sgaest;tab=overview?project=sga-instance-group) (***KEYRING***=Key ring y ***KEY***=Name).

```bash
gcloud kms decrypt \
--ciphertext-file=environments.enc \
--plaintext-file=.env \
--location=us-east1 \
--keyring=KEYRING --key=KEY
```
- Esta acción nos creará el archivo `.env` con las variables de entorno que contiene el archivo `environments.enc` dentro del directorio raíz del proyecto

### **Encriptar** el archivo .env

Si se requiere ***cambiar o agregar*** nuevas variables de entorno, es necesario volver a encriptar el archivo `.env` con las mismas llaves para el correcto funcionamiento de la aplicación en ambiente productivo.

> **¡Importante!** Sustituir los valores de ***KEYRING*** y ***KEY*** en la última línea antes de correr el comando para `encriptación`.  
> Los valores se encuentran en una tabla de contenido en GCP [sga-instance-group](https://console.cloud.google.com/security/kms/key/manage/us-east1/sga/sgaest;tab=overview?project=sga-instance-group) (***KEYRING***=Key ring y ***KEY***=Name).

```bash
gcloud kms encrypt \
--ciphertext-file=environments.enc \
--plaintext-file=.env \
--location=us-east1 \
--keyring=KEYRING --key=KEY
```
- Esta acción nos reconstruye el archivo `environments.enc` con los cambios realizados dentro del archivo `.env`

## Desarrollo

Una vez que haya creado un proyecto e instalado las dependencias con `npm install` (o `pnpm install` o `yarn`), inicie un servidor de desarrollo:

```bash
npm run dev
```
O inicie el servidor y abra la aplicación en una nueva pestaña del navegador
```bash
npm run dev -- --open
```

## Producción
> La gestión para el despliegue a `producción`, está manejada por ***Cloud Build***.  

> **¡Importante!**   Para desplegar una versión de `producción` de su aplicación, cualquier ***TAG*** con ***commit*** que se empujen al repositorio de ***GitHub*** realizará la activación del despliegue a `producción` automáticamente.

#### Para obtener una vista previa de lo que se despliega a producción:
Compilar la aplicación.

```bash
npm run build
```

Visualización de la compilación.
```bash
npm run preview
```
