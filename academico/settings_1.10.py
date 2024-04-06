# Django settings for AOK project.
import os
import datetime
import django
import djcelery
from decimal import getcontext, ROUND_HALF_UP
getcontext().rounding = ROUND_HALF_UP
djcelery.setup_loader()
# from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

DEBUG = True
# TEMPLATE_DEBUG = DEBUG

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'sga.unemi.edu.ec', 'sagest.unemi.edu.ec', '192.168.61.96', '192.168.3.175', '192.168.3.136']
ALLOWED_HOSTS = ['*']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(os.path.realpath("settings.py"))
# SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))

# NOMBRE INSTITUCION
NOMBRE_INSTITUCION = "Universidad Estatal de Milagro"
CONTACTO_EMAIL = "informacion@unemi.edu.ec"

# CLAVE POR DEFECTO
DEFAULT_PASSWORD = 'unemi'


# ADMINISTRADOR
ADMINS = (
    ('administrador', 'sistemas@unemi.edu.ec'),
    ('michaeloc_20', 'sistemas@unemi.edu.ec'),
    ('kpalaciosz', 'sistemas@unemi.edu.ec'),
    ('crodriguezn', 'sistemas@unemi.edu.ec'),
)

MANAGERS = ADMINS


DATABASES = {
    'default': { #ACADEMICO LOCALHOST
        'ENGINE': 'django.db.backends.postgresql_psycopg2',     # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sga2',                                         # Or path to database file if using sqlite3.
        'USER': 'postgres',                                     # Not used with sqlite3.
        'PASSWORD': 'M1ch3ll3A2020**',                          # Not used with sqlite3.
        'HOST': '127.0.0.1',                                    # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5433',                                         # Set to empty string for default. Not used with sqlite3.
    },
    # 'backup': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',     # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    #     'NAME': 'sga_27052021',                                          # Or path to database file if using sqlite3.
    #     'USER': 'postgres',                                     # Not used with sqlite3.
    #     'PASSWORD': 'M1ch3ll3A2020**',                          # Not used with sqlite3.
    #     'HOST': '127.0.0.1',                                    # Set to empty string for localhost. Not used with sqlite3.
    #     'PORT': '5432',                                         # Set to empty string for default. Not used with sqlite3.
    # },
    'sga_select': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        # 'NAME': 'unemi',                      # Or path to database file if using sqlite3.
        'NAME': 'sga2',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'M1ch3ll3A2020**',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5433',                      # Set to empty string for default. Not used with sqlite3.
    },
    'moodle_db': { #MOODLE DE PREGRADO
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        # 'NAME': 'unemi',                      # Or path to database file if using sqlite3.
        'NAME': 'moocunemi',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'M1ch3ll3A2020**',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5433',                      # Set to empty string for default. Not used with sqlite3.
    },
    # 'moodle_db_prueba': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    #     'NAME': 'moocdos',                      # Or path to database file if using sqlite3.
    #     'USER': 'moocfepo',                      # Not used with sqlite3.
    #     'PASSWORD': 'F3po03?*FA',                  # Not used with sqlite3.
    #     'HOST': '10.10.100.174',                      # Set to empty string for localhost. Not used with sqlite3.
    #     'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    # },

    #CAMPUS VIRTUAL ADMISION
    'db_moodle_virtual': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        # 'NAME': 'unemi',                      # Or path to database file if using sqlite3.
        'NAME': 'moocunemi',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'M1ch3ll3A2020**',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5433',                      # Set to empty string for default. Not used with sqlite3.
    },
    # consultas al esclavo
    # 'db_moodle_virtual_select': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    #     # 'NAME': 'unemi',                      # Or path to database file if using sqlite3.
    #     'NAME': 'moodleunemi',                      # Or path to database file if using sqlite3.
    #     'USER': 'moocweb',                      # Not used with sqlite3.
    #     'PASSWORD': 'Un3M12o18?m00C',                  # Not used with sqlite3.
    #     'HOST': '10.10.100.147',                      # Set to empty string for localhost. Not used with sqlite3.
    #     'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    # },
    # consultas al esclavo
    # 'db_moodle_semestre': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    #     # 'NAME': 'unemi',                      # Or path to database file if using sqlite3.
    #     'NAME': 'moocunemi',                      # Or path to database file if using sqlite3.
    #     'USER': 'moocunemiweb',                      # Not used with sqlite3.
    #     'PASSWORD': 'Un3M12o19?mooC',                  # Not used with sqlite3.
    #     'HOST': '10.10.100.129',                      # Set to empty string for localhost. Not used with sqlite3.
    #     'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    # },
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Guayaquil'
USE_TZ = False
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-EC'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

DECIMAL_SEPARATOR = '.'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

# STATIC_ROOT = os.path.join(SITE_ROOT, 'staticfiles/')
# STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #"C:/proyectos/aok/static",
    os.path.join(SITE_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '04m76#%5&*fg8^6677d%8lv0+2t$hkjw=8emvaed(an118!y6a'



AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware', # """NUEVO APLICAR 29/05/2021"""
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware', # """NUEVO APLICAR 29/05/2021"""
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware', # """NUEVO APLICAR 22/02/2022"""
    # 'django.middleware.cache.CacheMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middle.xframeoptions.XFrameOptionsMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddlewareUnemi',
    'oauth2_provider.middleware.OAuth2TokenMiddleware', #"""NUEVO APLICAR 29/05/2021"""
)


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
TEST_RUNNER = 'django.test.runner.DiscoverRunner'  # If you wish to delay updates to your test suite
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_CACHE_ALIAS = "default"

# CACHE_MIDDLEWARE_SECONDS = 60 * 15
# CACHE_MIDDLEWARE_KEY_PREFIX = 'web1'

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         #'LOCATION': '10.10.100.174:11211',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

ROOT_URLCONF = 'urls'


REST_FRAMEWORK = {
    'DATETIME_INPUT_FORMATS': ['%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S'],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_INPUT_FORMATS': ['%Y-%m-%d', '%d-%m-%Y'],
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_INPUT_FORMATS': ['%H:%M:%S', '%I:%M:%S'],
    'TIME_FORMAT': '%H:%M:%S',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_METADATA_CLASS': (
        'rest_framework.metadata.SimpleMetadata'
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #"""NUEVO APLICAR 29/05/2021"""
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',

    ),
    'DEFAULT_PERMISSIONS_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.postgres',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'preventconcurrentlogins',
    # 'db_defaults',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'sga',
    'sagest',
    'balcon',
    'med',
    'bib',
    'socioecon',
    'mobile',
    'ckeditor_uploader',
    'moodle',
    'rest_framework',
    # 'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'posgrado',
    'helpdesk',
    'investigacion',
    'admision',
    #desde aqui
    'djcelery',
    'clrncelery',
    #'celery_progress',
    'corsheaders', #"""NUEVO APLICAR 29/05/2021"""
    'inno',
    'bd',
    'django_select2',
    'oauth2_provider', #"""NUEVO APLICAR 29/05/2021"""
    'api', #"""NUEVO APLICAR 29/05/2021"""
    #'oauth2', #"""NUEVO APLICAR 29/05/2021"""
    'crispy_forms', #"""NUEVO APLICAR 29/05/2021"""
    'certi',
    'elfinderfs',
    'voto',
    'even',
    'matricula',
    'soap',
    'evath',
    'pdip',
    'postulaciondip',
    'webpush',
    'wpush',
    'pwa',
    'postulate'
    #'channels',
    #'ws',

)

SESSION_EXPIRE_AT_BROWSER_CLOSE =True


# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
# #     'django.template.loaders.eggs.Loader',
# )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SITE_ROOT, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DB_DEFAULTS_ENABLE_ALL_MODELS = True
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler'
#         }
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     }
# }

WSGI_APPLICATION = 'apache.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# CONFIGURACION DEL THIRD PARTY RUNJASPERREPORTS
JR_RUN = os.path.join(SITE_ROOT, 'thirdparty', 'lib')
JR_JAVA_COMMAND = 'java'
JR_REPORTS_FOLDER = os.path.join(SITE_ROOT, 'media', 'reports')
JR_USEROUTPUT_FOLDER = os.path.join(SITE_ROOT, 'media', 'documentos', 'userreports')
JR_DB_TYPE = 'postgresql'
SITE_STORAGE = "D://UNEMI/svn/academico/"
# SUBREPOTRS_FOLDER = "/".join([os.path.join(SITE_STORAGE, 'media', 'reportes', 'encabezados_pies', '')])
SUBREPOTRS_FOLDER = SITE_STORAGE + "/".join(['media', 'reportes', 'encabezados_pies', ''])

# CONFIGURACION DE CORREO
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# In-memory backend (locmem)
# EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
# Dummy backend (---)
# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_ACTIVE = True
EMAIL_HOST = 'smtp-relay.gmail.com' # 'smtp-relay.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'sga2@unemi.edu.ec'
EMAIL_HOST_PASSWORD = 'sga_ticsun3M1*?2016'
EMAIL_USE_TLS = True
EMAIL_DOMAIN = 'unemi.edu.ec'
ENVIO_SOLO_CORREO_INSTITUCIONAL = True




# #EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_ACTIVE = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'clockem@unemi.edu.ec'
# EMAIL_HOST_PASSWORD = 'carlos_locke20'
# EMAIL_USE_TLS = True
# EMAIL_DOMAIN = 'unemi.edu.ec'
# #DEFAULT_FROM_EMAIL = '<sga_tics@unemi.edu.ec>'
# ENVIO_SOLO_CORREO_INSTITUCIONAL = True

# CONFIGURACION DE CORREO
#ENVIO_SOLO_CORREO_INSTITUCIONAL = False
#EMAIL_ACTIVE = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'sgaunemi@gmail.com'
#EMAIL_HOST_PASSWORD = 'un3m12016'
#EMAIL_USE_TLS = True
#EMAIL_DOMAIN = ''


# CONFIGURACIONES ESPECIFICAS DE INSTITUTO
CLASES_HORARIO_ESTRICTO = True      # Horario estricto de apertura/cierre de clases
CLASES_APERTURA_ANTES = 15          # Minutos de apertura antes de inicio
CLASES_APERTURA_DESPUES = 45        # Minutos de apertura despues de inicio
CLASES_CIERRE_ANTES = 1             # Minutos de cierre antes de terminacion
CLASES_CONTINUAS_AUTOMATICAS = True
PERMITE_ABRIR_MATERIAS_ENFECHA = True

# PARA EL CONTROL DE ALUMNOS EN EL IAVQ (LLENAR DATOS PERSONALES Y QUE HAYA PAGADO MATRICULA)
PAGO_ESTRICTO = False            # Pago estricto, no permite acciones de asistencia y evaluaciones si no se ha pagado la matricula.
DATOS_ESTRICTO = False           # Datos de Cuenta de alumnos, no permite acciones de asistencia y evaluacion si no ha llenado los datos personales
DATOS_OBLIGATORIOS = False

# UBICACION DE FICHEROS
BANCA_OUTPUT_PICHINCHA = os.path.join(SITE_ROOT, 'media', 'documentos', 'bancaonline_pichincha')
BANCA_OUTPUT_GUAYAQUIL = os.path.join(SITE_ROOT, 'media', 'documentos', 'bancaonline_guayaquil')
COOPERATIVA_OUTPUT_JEP = os.path.join(SITE_ROOT, 'media', 'documentos', 'cooponline_jep')

# TIPOS DE ARCHIVOS / SYLLABUS O DEBER / GENERALES
ARCHIVO_TIPO_SYLLABUS = 8
ARCHIVO_TIPO_DEBERES = 7
ARCHIVO_TIPO_GENERAL = 9
ARCHIVO_TIPO_MICRO = 10
ARCHIVO_TIPO_COBROS = 12
ARCHIVO_TIPO_NOTAS = 13
ARCHIVO_TIPO_MANUALES = 14

# ID_BANCOS
ID_BANCO_PICHINCHA = 2
ID_CUENTA_BANCO_PICHINCHA = 2

# CORREO OBLIGATOTIO
CORREO_OBLIGATORIO = False

# PREGUNTAS INSCRIPCION
PREGUNTAS_INSCRIPCION = False

# DEFINE SI SE UTILIZAN GRUPOS DE ALUMNOS
UTILIZA_GRUPOS_ALUMNOS = False

# MATRICULACION (True - MATRICULACION X MATERIA, False - MATRICULACION X NIVEL)
MATRICULACION_LIBRE = True


# SOLICITUDES EN SECRETARIA
SOLICITUD_NUMERO_AUTOMATICO = True
PERMITE_ALUMNO_REGISTRAR = False

# ESTADO DE LA MATERIA
NOTA_ESTADO_APROBADO = 1
NOTA_ESTADO_REPROBADO = 2
NOTA_ESTADO_EN_CURSO = 3
NOTA_ESTADO_SUPLETORIO = 4

# TIPOS DE MATRICULAS
MATRICULA_REGULAR_ID = 1
MATRICULA_ESPECIAL_ID = 2
MATRICULA_EXTRAORDINARIA_ID = 3
MATRICULA_OTRAS_ID = 4

# BIBLIOTECA
DOCUMENTOS_COLECCION = True
DOCUMENTOS_AUTONUMERACION = True
DOCUMENTOS_COLECCION_AUTONUMERACION = False

# FOTOS DE CUENTA
GENERAR_TUMBAIL = True
ACTUALIZAR_FOTO_ALUMNOS = False
ACTUALIZAR_FOTO_ADMINISTRATIVOS = False
CONTROL_UNICO_CREDENCIALES = True

# TIPO RESPUESTA EVALUACIONES (1-(MAL--EXCELENTE(1-5)) 2-(MAL--EXCELENTE(1-10)) 3-(SI-AVECES-NO(1-3)))
TIPO_RESPUESTA_EVALUACION = 3

# CHEQUE SI TIENE CONFLICTO DE HORARIO AL MATRICULARSE
CHEQUEAR_CONFLICTO_HORARIO = True

# CANTIDAD DE MATRICULAS MAXIMAS X MATERIA
CANTIDAD_MATRICULAS_MAXIMAS = 3

#CANTIDAD MAXIMA DE HORAS JUSTIFICADAS
CANTIDAD_HORAS_JUSTIFICACION_ASISTENCIAS = 120
CANTIDAD_DIAS_APERTURAR_CLASE = 150
PORCIENTO_RECUPERACION_FALTAS = 1
LIMITE_HORAS_JUSTIFICAR = True

# MATRICULACION X NIVEL O POR GRUPO
MATRICULACION_POR_NIVEL = False

# NOMBRE NIVEL AUTOMATICO
NOMBRE_NIVEL_AUTOMATICO = True

# HORARIO
HORARIO_RESUMIDO = True
VERIFICAR_CONFLICTO_DOCENTE = True

# GRATUIDAD UNIVERSIDADES
UTILIZA_GRATUIDADES = True
PORCIENTO_PERDIDA_PARCIAL_GRATUIDAD = 60  # Valor minimo de porciento para perdida de gratuidad parcial (en funcion de las materias a seleccionar en el periodo)
PORCIENTO_PERDIDA_TOTAL_GRATUIDAD = 30    # Valor minimo de porciento para perdida de gratuidad total (en funcion de las horas de materias reprobadas / total horas malla)

# TIPOS DE INSCRIPCIONES
USA_TIPOS_INSCRIPCIONES = True
TIPO_INSCRIPCION_INICIAL = 1

# PLANIFICACION DOCENTE
USA_PLANIFICACION = True


# APLICACIONES MOVILES
URL_APLICACION_ESTUDIANTE_ANDROID = "https://play.google.com/store/apps/details?id=com.oksoftwr.academicok.unemi"
URL_APLICACION_ESTUDIANTE_IOS = ""
URL_APLICACION_PROFESOR_ANDROID = ""

# PERMITE MATRICULAR CON DEUDA
MATRICULAR_CON_DEUDA = True

# CEDULA COMO CLAVE DE USUARIO
CLAVE_USUARIO_CEDULA = True

# CUPO X MATERIAS O CAPACIDAD DE AULA
CUPO_POR_MATERIA = True
CAPACIDAD_MATERIA_INICIAL = 30

# NOTIFICACIONES EMAIL
NOTIFICA_ELIMINACION_MATERIA = False

# VALIDA INGRESO DE CALIFICACIONES

# ID ALTERNATIVAS
ALTERNATIVA_RECUPERACION_ID = 21
ALTERNATIVA_MEJORAMIENTO_ID = 22

DOCENCIA_ACTIVIDAD_ID = 3

SUBTIPO_COMPONENTE_HETEROEVALUACION_ID = 4
SUBTIPO_COMPONENTE_AUTOEVALUACION_ID = 1
SUBTIPO_COMPONENTE_COEVALUACION_PARES_ID = 3
SUBTIPO_COMPONENTE_COEVALUACION_DIRECTIVOS_ID = 2

USA_EVALUACION_INTEGRAL = True
MODULO_EVALUACION_PARESDIRECTIVOS_ID = 91

# TUTORIAS Y PROYECTOS DE GRADO
PREPROYECTO_ESTADO_PENDIENTE_ID = 1
PREPROYECTO_ESTADO_APROBADO_ID = 2
PREPROYECTO_ESTADO_RECHAZADO_ID = 3

PREPROYECTO_CAMBIOTUTOR_ID = 1
PREPROYECTO_CAMBIOTITULO_ID = 2
PREPROYECTO_CAMBIOINTEGRANTE_ID = 3

SOLICITUD_PREPROYECTO_ESTADO_PENDIENTE_ID = 1
SOLICITUD_PREPROYECTO_ESTADO_APROBADO_ID = 2
SOLICITUD_PREPROYECTO_ESTADO_RECHAZADO_ID = 3

TIPO_TRABAJOTITULACION_TESIS_ID = 1

# CHEQUEO DE CORREO
CHEQUEAR_CORREO = False

# MODULO DE FINANZAS
GENERAR_RUBRO_DERECHO = False

# FORMAS DE PAGO
FORMA_PAGO_EFECTIVO = 1
FORMA_PAGO_CHEQUE = 2
FORMA_PAGO_TARJETA = 3
FORMA_PAGO_DEPOSITO = 4
FORMA_PAGO_TRANSFERENCIA = 5
FORMA_PAGO_ELECTRONICO = 6
FORMA_PAGO_CUENTA_PORCOBRAR = 7

# TIPOS DE OTROS RUBROS
TIPO_OTRO_RUBRO = 0
TIPO_MORA_RUBRO = 0
VALOR_MORA_RUBRO = 0
GENERAR_RUBRO_MORA = False
GENERAR_RUBRO_MORA_CUOTA = False
GENERAR_RUBRO_MORA_MATRICULA = False
VALOR_DERECHOEXAMEN_RUBRO = 0
VALOR_DERECHOEXAMEN_EXTRAORDINARIO_RUBRO = 0

# BECAS
BECA_MODELO_NUEVO = False

SEXO_FEMENINO = 1
SEXO_MASCULINO = 2

# Define si utiliza nivel 0 (propedeutico)
UTILIZA_NIVEL0_PROPEDEUTICO = False
TIPO_PERIODO_PROPEDEUTICO = 1
TIPO_PERIODO_REGULAR = 2
NIVEL_MALLA_CERO = 0
NIVEL_MALLA_UNO = 1
MALLA_MATERIAS_OPTATIVAS_OBLIGATORIAS = False
MALLA_MATERIAS_LIBRE_OPCION_OBLIGATORIAS = False

# Tipos de Modelo de Evaluaciones

EVALUACION_IAVQ = 1
EVALUACION_ITB = 2
EVALUACION_ITS = 3
EVALUACION_TES = 4
EVALUACION_IGAD = 5
EVALUACION_LEXA = 6
EVALUACION_LIBERTAD = 7
EVALUACION_IBARRA = 8
EVALUACION_LICEOADUANERO = 9
EVALUACION_ITSEI = 10
EVALUACION_ISAC = 11
EVALUACION_UNEMI = 12
EVALUACION_GENERICA = 13
MODELO_EVALUACION = EVALUACION_UNEMI

#Para los Roles de Pago a Docentes
COEFICIENTE_PORCIENTO_IESS = 0.0935
COEFICIENTE_RETENCION = 0.08

# Si usa o no la Ficha Medica y el Dpto Medico
UTILIZA_FICHA_MEDICA = False
FICHA_MEDICA_ESTRICTA = False

# Si usa la Biblioteca Virtual
UTILIZA_MODULO_BIBLIOTECA = True


# rubros inscripcion
RUBRO_TIPO_OTRO_CD = 0

UTILIZA_MODULO_ENCUESTAS = True

ALLOWED_IPS_FOR_INHOUSE = ['*']

MODELO_IMPRESION_NUEVO = False
TIEMPO_CIERRE_SESION = 1800

NOTIFICACION_DEBERES = False

MAXIMO_ACTIVIDADES_EXTRAS = 0

MAXIMO_MATERIA_ONLINE = 10

MALLA_OPTATIVAS = 4
MALLA_LIBRE_OPCION = 5

CONTROL_UNICO_PAGOS = False
CALCULO_POR_CREDITO = True

HOMITIRCAPACIDADHORARIO = False

EVALUACION_DOCENTE_POR_MATERIA = False
IVA = 0.14

HORAS_EXTRA_LIDER_PROYECTO = 5

RECARGO_MATRICULACION_EXT = False

MAXIMO_ADJUNTO_ENVIO = 5

EMAIL_INSTITUCIONAL_AUTOMATICO = True

PAGO_OBLIGATORIO_PRIMERACUOTA = False

AUTOREGISTRO_EMPRESA = True

AUTOREGISTRO_EMPRESA_AUTORIZAR = True

VER_FOTO_LECCION = True

MODALIDAD_DISTANCIA = 0

MATRICULA_ONLINE_SOLODISTANCIA = False

SUBIR_SILABO_DOCENTE = False

ARRASTRES_MAXIMOS = 3

PRACTICAS_PREPROFESIONALES_ACTIVAS = True

ABRIR_CLASES_ATRASADAS = False


# APLICAR DESCUENTOS EN FACTURAS
DESCUENTOS_EN_FACTURAS = False


PORCIENTO_CUMPLIMIENTO_MALLA_ANTEPROYECTO = 80

PIE_PAGINA_CREATIVE_COMMON_LICENCE = True

VER_EVALUACION_DOCENTE_FINANZAS = False

APROBACION_DISTRIBUTIVO = True

HORAS_AUTORIZADO_EVALUACION_DOCENTE = 48

MATRICULAS_SOLO_TERCERAS = False

COSTO_EN_MALLA = False

DIAS_MATRICULA_EXPIRA = 0

CALCULO_NIVEL_POR_CREDITOS = True

#TIPO_DOCENTE
TIPO_DOCENTE_TEORIA = 1
TIPO_DOCENTE_PRACTICA = 2
TIPO_DOCENTE_FIRMA = 3

APLICAR_BECA_RUBROS_PAGADOS= False

USA_RETIRO_MATRICULA = True
USA_RETIRO_MATERIA = True
ASISTENCIA_EN_GRUPO = False

#ESTADO SOLICITUDES DE APERTURA DE CLASES
SOLICITUD_APERTURACLASE_PENDIENTE_ID = 1
SOLICITUD_APERTURACLASE_APROBADA_ID = 2
SOLICITUD_APERTURACLASE_RECHAZADA_ID = 3
USA_PORCIENTO_APERTURACLASE = True
PORCIENTO_APERTURACLASE = 60

PERSONA_ESTADO_CIVIL_ID = 1

CRITERIO_HORAS_CLASE_TIEMPO_COMPLETO_ID = 15
CRITERIO_HORAS_CLASE_MEDIO_TIEMPO_ID = 16
CRITERIO_HORAS_CLASE_PARCIAL_ID = 21
CRITERIO_HORAS_CLASE_PRACTICA = 20

TIEMPO_DEDICACION_TIEMPO_COMPLETO_ID = 1
TIEMPO_DEDICACION_MEDIO_TIEMPO_ID = 2
TIEMPO_DEDICACION_PARCIAL_ID = 3

MAXIMO_HORAS_DOCENCIA_TIEMPO_COMPLETO = 26
MAXIMO_HORAS_DOCENCIA_MEDIO_TIEMPO = 12
MAXIMO_HORAS_DOCENCIA_PRACTICA = 36

ABRIR_CLASES_DISPOSITIVO_MOVIL = False
TIPO_MATRICULA_RUBRO = 0
TIPO_CUOTA_RUBRO = 0
PERSONA_ELABORA_POA = 26500
PERSONA_APRUEBA_POA = 28773
COPIA_POA = [PERSONA_ELABORA_POA, PERSONA_APRUEBA_POA, 27984]

METODO_INVENTARIO = 1
VALIDATE_IPS = False

VER_SILABO_MALLA = False
VER_PLAN_ESTUDIO = False


RESPONSABLE_BIENES_ID = 2421
ASISTENTE_BODEGA_ID = 25925
ANALISTA_PRESUPUESTO_ID = 26018

AUDITAR_USUARIO = []
CORREO_AUDITOR = []

DECLARACION_SGA = True
DECLARACION_SAGEST = True

TESORERO_ID = 2570
DIAS_MODIFICAR_ACTIVOS = 30
ACUMULAR_DOS_MESES = False

TIPO_AMBIENTE_FACTURACION = 2

PASSSWORD_SIGNCLI = 'Bruna2015'
SERVER_URL_SIGNCLI = "http://sagest.unemi.edu.ec"
SERVER_USER_SIGNCLI = 'root'
SERVER_PASS_SIGNCLI = 'magic.number.82'
ONLINE = 2
URL_SERVICIO_ENVIO_SRI_PRUEBAS = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl' if ONLINE == 1 else 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl'
URL_SERVICIO_AUTORIZACION_SRI_PRUEBAS = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl' if ONLINE == 1 else 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'

URL_SERVICIO_ENVIO_SRI_PRODUCCION = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl' if ONLINE == 1 else 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl'
URL_SERVICIO_AUTORIZACION_SRI_PRODUCCION = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl' if ONLINE == 1 else 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'

JR_RUN_SING_SIGNCLI = os.path.join(SITE_ROOT, 'thirdparty', 'signcli')

BANCO_PACIFICO_ID = 19
COMISION_BANCO_PACIFICO = 0.25
VENTA_BASE_ID = 2762
PUESTO_ACTIVO_ID = 1
RUBRO_SOLICITUD_SECRETARIA_ID = 1

TIPO_DOCENTE_AYUDANTIA = 5
MAXIMO_HORAS_DOCENCIA_AYUDANTIA = 40
CRITERIO_HORAS_CLASE_AYUDANTIA = 19
PERSONA_AUTORIZA_COMPROBANTE_INGRESO_ID = 4988
PERSONA_AUTORIZA_COMPROBANTE_EGRESO_ID = 1
ADMINISTRADOR_ID = 1

PDF_GET_EJECUTABLE='/usr/local/bin/wkhtmltopdf'

PDF_GET_FACTURA='http://sagest.unemi.edu.ec/show_factura/'
PDF_GET_NOTACREDITO='http://sagest.unemi.edu.ec/show_notacredito/'

PORCENTAJE_SEGURO = 0.1145

NOMINA_RUBRO_INGRESOS_ID = [44, 45, 72, 3, 12, 13, 60, 2617, 2621, 2636, 2637, 2638, 2639, 133, 2654]
NOMINA_RUBRO_RENTA_ID = [33, 136]
NOMINA_RUBRO_EXTRA_ID = [2624, 2626, 2627, 2628, 2629, 2630, 28, 139, 47]
NOMINA_RUBRO_SEGURO_ID = [31]

TIPOS_RUBROS_BANCO = [2845]

NOMINA_RUBRO_SUELDOS = [44]
NOMINA_RUBRO_SOBRESUELDOS = [45,2624,72,3,12,13,60,2617,2621,2636,2637,2638,2639,2626,2627.2628,2629,2630,47,28,139]
NOMINA_RUBRO_DECIMOTERCER = [24]
NOMINA_RUBRO_DECIMOCUARTO = [23]
NOMINA_RUBRO_FONDORESERVA = [124, 143]
CLASES_CIERRE_AUTOMATICA = True
HILOS_MAXIMOS = 4
DIAS_INGRESO_POA = 7
DIAS_VALIDEZ_RECIBO_COBRO = 8

CARRERAS_ADMISION = [47,48,49,50,51,52,53,54,55,56,57,64,65,66]
COMISION_BANCO_RUBRO_ID = 239
PORCENTAJE_ASEGURADO = 5
TIPO_TRAMITE_VERIFICAR_ID = [11, 13]

CUENTA_ACREEDORA_ID = 12
FICHA_SITUACIONALOBLIGATORIO = False
PRESUPUESTO_ID = 2393

RUBRO_MATRICULA = 2924
RUBRO_ARANCEL = 2923
PORCENTAJE_MULTA = 25

PANTALLA_PREINSCRIPCION = False

PERIODO_ELIMINA_MATRICULA = [11]
HORAS_VIGENCIA = 24


#ANTEPROYECTO
MAX_CALIFICADORES=3

#ANTEPROYECTO -CALIFICACION
MAX_NOTA=100
MIN_PROMEDIO_APROBACION=70

#TIPO DE PROFESOR
TITULAR_ID=1
OCASIONAL_ID=2
HONORARIO_ID=3
INVITADO_ID=4

#ESTADO DEL PROYECTO
PROYECTO_EN_TUTORIA=1
PROYECTO_SUSPENDIDO=2

#DIAS LIMITES DE PROYECTO DE GRADO son 18 meses
DIAS_LIMITES_PROYECTO_GRADO=546
DIAS_LIMITES_SUBIR_PROYECTO_GRADO_COMPLETO=7

#BLOQUEOS DE APERTURA  DE GRUPO DE TITULACION
MODULO_INGLES_ID=6
POSGRADO_EDUCACION_ID=7
MODULOS_COMPUTACION_ID =8
ADMISION_ID=9

#TIPO DE TITULACION
PROYECTOS_TITULACION_ID=1
EXAMEN_COMPLEXIVO_ID=2

#CANTIDAD DE CUPO PARA CADA ALTERNATIVA
CUPO_POR_ALTERNATIVATITULACION=900


#CANTIDAD MINIMA DE PRACTICAS PROFESSIONALES
HORAS_MIN_PRACTICAS_PREPROFESIONALES=224
REPORTE_PDF_FACTURA_ID = 1
REPORTE_PDF_NOTACREDITO_ID = 1
ESTADO_GESTACION = 1
SERVER_RESPONSE = '211'
TIPO_TRAMITE_PAGO_ROL = 0
BENEFICIARIO_UNEMI = 0

COBRA_COMISION_BANCO = False

# GRUPOS
PROFESORES_GROUP_ID = 1
ALUMNOS_GROUP_ID = 2
RECTORADO_GROUP_ID = 5
SISTEMAS_GROUP_ID = 3
FINANCIERO_GROUP_ID = 9
SECRETARIA_GROUP_ID = 4
ASISTENTES_SECRETARIA_GROUP_ID = 14
EMPLEADORES_GRUPO_ID = 17
VINCULACION_GROUP_ID = 20
BIBLIOTECA_GRUPO_ID = 15
ADMISIONES_GROUP_ID = 12
SOPORTE_GROUP_ID = 36

SECRETARIA_CCAA_GROUP_ID = 29
SECRETARIA_CCEE_GROUP_ID = 32
SECRETARIA_CCES_GROUP_ID = 33
SECRETARIA_CCII_GROUP_ID = 30
SECRETARIA_CCSS_GROUP_ID = 31
SECRETARIA_CCLE_GROUP_ID = 34
SECRETARIA_EDUCON_GROUP_ID = 44

COORDINACION_CCAA_GROUP_ID = 26
COORDINACION_CCEE_GROUP_ID = 24
COORDINACION_CCES_GROUP_ID = 27
COORDINACION_CCII_GROUP_ID = 23
COORDINACION_CCSS_GROUP_ID = 25
COORDINACION_CCLE_GROUP_ID = 28

# GRUPOS DE CORREOS
SISTEMAS_EMAIL = []
CALLCENTER_CONTACTO = []
FINANCIERO_EMAIL = []
REGISTRO_NUEVOS_ESTUDIANTES = []

# if DEBUG:
#     INTERNAL_IPS = ('127.0.0.1',)
#     MIDDLEWARE += (
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     )
#
#     INSTALLED_APPS += (
#         'debug_toolbar',
#     )
#
#     DEBUG_TOOLBAR_PANELS = [
#         'debug_toolbar.panels.versions.VersionsPanel',
#         'debug_toolbar.panels.timer.TimerPanel',
#         # 'debug_toolbar.panels.settings.SettingsPanel',
#         'debug_toolbar.panels.headers.HeadersPanel',
#         'debug_toolbar.panels.request.RequestPanel',
#         'debug_toolbar.panels.sql.SQLPanel',
#         # 'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#         # 'debug_toolbar.panels.templates.TemplatesPanel',
#         'debug_toolbar.panels.cache.CachePanel',
#         'debug_toolbar.panels.signals.SignalsPanel',
#         # 'debug_toolbar.panels.logging.LoggingPanel',
#         # 'debug_toolbar.panels.redirects.RedirectsPanel',
#     ]
#
#     DEBUG_TOOLBAR_CONFIG = {
#         'INTERCEPT_REDIRECTS': False,
#     }




CKEDITOR_CONFIGS = {
    'awesome_ckeditor': {
        'toolbar': 'Basic',
    },
    'default': {
        'skin': 'moono',
        'height': 300,
        'width': '100%',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'NewPage', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'SelectAll']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['ShowBlocks']},
            {'name': 'yourcustomtools', 'items': [
                'Maximize',
            ]},
        ],
        "language": "es-EC",
        'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'toolbar': 'YourCustomToolbarConfig',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}
CKEDITOR_JQUERY_URL = os.path.join(STATIC_URL, 'js/jquery.min.js')
CKEDITOR_MEDIA_PREFIX = "/static/ckeditor/"
CKEDITOR_UPLOAD_PATH = "ckeditor/"
CKEDITOR_RESTRICT_BY_USER = 'True'
THUMBNAIL_HIGH_RESOLUTION = True
CONN_MAX_AGE = 40


#CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://127.0.0.1:6379/0")
#CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'

REDIS_HOST = '127.0.0.1'
REDIS_PASSWORD = ''
REDIS_PORT = 6379
REDIS_BD = 0
BROKER_URL = 'redis://127.0.0.1:6379/0'
#CELERY_RESULT_BACKEND = 'redis://localhost:6379'
#BROKER_URL = 'redis://user:un3m1.redis.2021@10.10.100.140:6379/0'
CELERY_RESULT_BACKEND = "djcelery.backends.database:DatabaseBackend"
CELERY_TIMEZONE = "America/Guayaquil"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYD_CONCURRENCY = 10
CELERYD_MAX_TASKS_PER_CHILD = 1
#Cada trabajador ejecuta como máximo 1 tarea y será destruido, lo que puede evitar pérdidas de memoria.

#FILE_FIREBIASE_JSON = os.path.join(SITE_ROOT, 'serviceAccountKey.json')

#"""NUEVO APLICAR 29/05/2021"""
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
# https://github.com/adamchainz/django-cors-headers
# preflight options en rest_framework django
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'http://127.0.0.1:81',
    'https://aulagrado.unemi.edu.ec',
    'https://aulanivelacion.unemi.edu.ec',
    'https://posgrado.unemi.edu.ec',
    'https://sagest.epunemi.gob.ec',
    'http://190.15.128.134',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    'http://127.0.0.1:3000',
]

CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:3000',
]

#"""NUEVO APLICAR 22/02/2022"""
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

#"""NUEVO APLICAR 22/02/2022"""
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8080',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:81',
]
#"""NUEVO APLICAR 22/02/2022"""
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# JWT_AUTH = {
#     'JWT_ENCODE_HANDLER':
#         'rest_framework_jwt.utils.jwt_encode_handler',
#     'JWT_DECODE_HANDLER':
#         'rest_framework_jwt.utils.jwt_decode_handler',
#     'JWT_PAYLOAD_HANDLER':
#         'rest_framework_jwt.utils.jwt_payload_handler',
#     'JWT_PAYLOAD_GET_USER_ID_HANDLER':
#         'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',
#     'JWT_RESPONSE_PAYLOAD_HANDLER':
#         'rest_framework_jwt.utils.jwt_response_payload_handler',
#     'JWT_SECRET_KEY': SECRET_KEY,
#     'JWT_GET_USER_SECRET_KEY': None,
#     'JWT_PUBLIC_KEY': None,
#     'JWT_PRIVATE_KEY': None,
#     'JWT_ALGORITHM': 'HS256',
#     'JWT_VERIFY': True,
#     'JWT_VERIFY_EXPIRATION': True,
#     'JWT_LEEWAY': 0,
#     'JWT_EXPIRATION_DELTA': datetime.timedelta(minutes=5),
#     'JWT_AUDIENCE': None,
#     'JWT_ISSUER': None,
#     'JWT_ALLOW_REFRESH': True,
#     'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=1),
#     'JWT_AUTH_HEADER_PREFIX': 'Bearer',
#     'JWT_AUTH_COOKIE': None,
#
# }

#"""NUEVO APLICAR 22/02/2022"""
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(minutes=60),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': datetime.timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': datetime.timedelta(days=1),
}


#WKHTMLTOPDF_URL = 'C://Program Files//wkhtmltopdf//bin//wkhtmltopdf.exe'

LOGIN_URL = '/api/1.0/oauth/2/login'


OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope',
               'write': 'Write scope',
               'groups': 'Access to your groups',
               'CLIENT_ID_GENERATOR_CLASS': 'oauth2_provider.generators.ClientIdGenerator',
               }
}

TMP_ROOT = os.path.join(SITE_ROOT, 'tmp')
TMP_URL = 'tmp'

ELFINDERFS = {
    'roots': {
        'Media': {
            'url': MEDIA_URL,
            'root': MEDIA_ROOT,
            'thumbnails_prefix': '.thumbnails',
        },
        'TMP': {
            'url': TMP_URL,
            'root': TMP_ROOT,
            'thumbnails_prefix': '.thumbnails',
        },
    },
    'default_root': 'Media',
}

SITE_POPPLER = "C:\\poppler\\21.10.0\\Library\\bin\\"

# SITE_ID = 1


# NOTIFICACIONES WEB
# PWA
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'academico/templates/serviceworker.js')
PWA_APP_NAME = 'UNEMI'
PWA_APP_SHORT_NAME = 'UNEMI'
PWA_APP_DESCRIPTION = "UNIVERSIDAD ESTATAL DE MILAGRO"
PWA_APP_THEME_COLOR = '#012e46'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'portrait'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        "src": "/static/pwalogo/72x72.png",
        "sizes": "72x72",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/96x96.png",
        "sizes": "96x96",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/128x128.png",
        "sizes": "128x128",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/144x144.png",
        "sizes": "144x144",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/152x152.png",
        "sizes": "152x152",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/192x192.png",
        "sizes": "192x192",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/384x384.png",
        "sizes": "384x384",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/512x512.png",
        "sizes": "512x512",
        "type": "image/png"
    }]
PWA_APP_ICONS_APPLE = [
    {
        "src": "/static/pwalogo/72x72.png",
        "sizes": "72x72",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/96x96.png",
        "sizes": "96x96",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/128x128.png",
        "sizes": "128x128",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/144x144.png",
        "sizes": "144x144",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/152x152.png",
        "sizes": "152x152",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/192x192.png",
        "sizes": "192x192",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/384x384.png",
        "sizes": "384x384",
        "type": "image/png"
    },
    {
        "src": "/static/pwalogo/512x512.png",
        "sizes": "512x512",
        "type": "image/png"
    }]
PWA_APP_SPLASH_SCREEN = [{'src': '/static/pwalogo/640x1136.png', 'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'}]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'es-ec'
PWA_APP_DEBUG_MODE = False

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "BByk6uECEJsxL4xO5rqAghWY1PV_5c9V6JuOHnRo5o9jWQRr-ciEP9uUvtMNgRhcBm0zBNm0Hq_ukRrTm4V5_0k",
    "VAPID_PRIVATE_KEY": "sxSmEpzixxbx6WBV34FCtMmkwXMQXHNrzRnRf_JohYE",
    "VAPID_ADMIN_EMAIL": "hllerenaa@unemi.edu.ec"
}

DATABASES_MONGO = {
    'default': {
        'NAME': 'sga',
        'USER': 'admin',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': 27017,
    },
}

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'asgi_redis.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')],
#         },
#         'ROUTING': 'ws.routing.channel_routing',
#     },
# }

#ASGI_APPLICATION = "ws.asgi.channel_layer"
