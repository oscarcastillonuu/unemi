import os
import sys

YOUR_PATH = os.path.dirname(os.path.realpath(__file__))
# print(f"YOUR_PATH: {YOUR_PATH}")
SITE_ROOT = os.path.dirname(os.path.dirname(YOUR_PATH))
SITE_ROOT = os.path.join(SITE_ROOT, '')
# print(f"SITE_ROOT: {SITE_ROOT}")
your_djangoproject_home = os.path.split(SITE_ROOT)[0]
sys.path.append(your_djangoproject_home)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
application = get_wsgi_application()
from sga.models import *
from sagest.models import *
from settings import MATRICULACION_LIBRE, UTILIZA_GRUPOS_ALUMNOS, NOMBRE_NIVEL_AUTOMATICO, MATRICULACION_POR_NIVEL, \
    CAPACIDAD_MATERIA_INICIAL, CUPO_POR_MATERIA, APROBACION_DISTRIBUTIVO, USA_EVALUACION_INTEGRAL, \
    TIPO_DOCENTE_TEORIA, TIPO_DOCENTE_PRACTICA, VERIFICAR_CONFLICTO_DOCENTE, TIPO_CUOTA_RUBRO, SITE_STORAGE
from sga.funcionesxhtml2pdf import conviert_html_to_pdfsaveqrcertificadoscongresoinscritoturistica
from django.db.models import F, Value
from django.db.models.functions import Concat
from bd.models import InventarioOpcionSistema
from settings import MEDIA_ROOT, BASE_DIR
import requests

def descargar_imagenes_opciones_originales():
    print('Descargando imágenes')
    grupo_id = 1
    list_modulos = Modulo.objects.filter(modulogrupo__grupos__id=grupo_id, status=True).values_list('id', flat=True)
    opciones = InventarioOpcionSistema.objects.filter(
        status=True,
        preguntauxplora__isnull=False,
        preguntauxplora__gt='',
        archivo__isnull=False,
        modulo_id__in=list_modulos
    ).order_by('nombre')

    for indice, opcion in enumerate(opciones):
        nombre_carpeta = opcion.nombre.replace('.', '')
        nombre_carpeta = f'{indice+1} - {nombre_carpeta}'
        nombreimagen = opcion.nombre.replace('.', '')
        nombreimagen = f'{opcion.descripcion}'
        imagen_url = 'https://sga.unemi.edu.ec' + opcion.archivo.url

        carpeta_destino = os.path.join(settings.MEDIA_ROOT, 'imagenes_opcion_original', nombre_carpeta)
        os.makedirs(carpeta_destino, exist_ok=True)

        try:
            response = requests.get(imagen_url)
            response.raise_for_status()

            nombre_archivo = os.path.join(carpeta_destino, f"{nombreimagen}.png")
            # Guardar la imagen en el directorio de destino
            with open(nombre_archivo, 'wb') as archivo_destino:
                archivo_destino.write(response.content)
            print(f"Imagen guardada: {nombre_archivo}")

        except Exception as e:
            print(f"Error al guardar la imagen: {e}")



descargar_imagenes_opciones_originales()