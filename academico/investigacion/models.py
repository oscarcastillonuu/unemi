import os
from datetime import datetime, timedelta, date
from decimal import Decimal

from investigacion.funciones import diff_month, diff_hours
from sga.funciones import ModeloBase, null_to_decimal
from django.db import models
from django.db.models.query_utils import Q
from django.db.models import Sum, Count, F
from django.db.models.aggregates import Count, Max
from sga.models import Externo, Profesor, ProyectoInvestigacionExterno, Titulacion, AreaConocimientoTitulacion, \
    SubAreaConocimientoTitulacion, SubAreaEspecificaConocimientoTitulacion, LineaInvestigacion, SubLineaInvestigacion, \
    Provincia, Canton, ArticuloInvestigacion, PonenciasInvestigacion, LibroInvestigacion, CapituloLibroInvestigacion, \
    ParticipantesMatrices, \
    ArticuloPersonaExterna, PonenciaPersonaExterna, LibroPersonaExterna, ProyectoInvestigacionPersonaExterna, \
    ProgramasInvestigacion, Coordinacion, PlanificarPonencias, Periodo, ESTADO_APROBACION_EVIDENCIA, ClaseActividad, \
    EvidenciaActividadDetalleDistributivo, DetalleDistributivo

unicode = str

VALOR_SI_NO = (
    ('', u'---------'),
    (1, u'SI'),
    (2, u'NO')
)

CATEGORIA_PROYECTO = (
    ('', u'---------'),
    (1, u'INNOVACIÓN TECNOLÓGICA'),
    (2, u'DESARROLLO TECNOLÓGICO'),
    (3, u'INVESTIGACIÓN SOCIAL'),
    (4, u'INVESTIGACIÓN CIENTÍFICA')
)

TIPO_EQUIPAMIENTO = (
    ('', u'---------'),
    (1, u'EQUIPOS MAYORES - PROYECTOS TIPO A'),
    (2, u'EQUIPOS MENORES - PROYECTOS TIPO B'),
    (3, u'NO - PROYECTOS TIPO C'),
    (4, u'PROYECTOS TECNOLÓGICOS - PROYECTOS TIPO D')
)

MONTO_PROYECTO = (
    ('', u'---------'),
    (1, u'PROYECTOS TIPO A'),
    (2, u'PROYECTOS TIPO B'),
    (3, u'PROYECTOS TIPO C'),
    (4, u'PROYECTOS TIPO D')
)

TIPO_PROYECTO = (
    (1, u'TIPO A'),
    (2, u'TIPO B'),
    (3, u'TIPO C'),
    (4, u'TIPO D')
)

TIPO_PROYECTO_EVALUACION = (
    (1, u'PROPUESTA'),
    (2, u'FINALIZADO'),
)

TIPO_INDUSTRIA_PRIORIZADA = (
    (1, u'BIENES'),
    (2, u'SERVICIOS')
)

TIPO_UNIDAD_PERIODO = (
    (1, u'DIAS'),
    (2, u'MESES'),
    (3, u'AÑOS')
)

TIPO_COBERTURA_EJECUCION = (
    ('', u'---------'),
    (1, u'INTERNACIONAL'),
    (2, u'NACIONAL'),
    (3, u'ZONAL'),
    (4, u'PROVINCIAL'),
    (5, u'LOCAL')
)

TIPO_INSTITUCION_PARTICIPANTE = (
    (1, u'EJECUTORA'),
    (2, u'CO-EJECUTORA')
)

TIPO_PORCENTAJE_EQUIPOS = (
    (1, u'MÍNIMO'),
    (2, u'MÁXIMO'),
    (3, u'NINGUNO')
)

FUNCION_INTEGRANTE = (
    ('', u'--------'),
    (1, u'DIRECTOR'),
    (2, u'CO-DIRECTOR'),
    (3, u'INVESTIGADOR ASOCIADO'),
    (4, u'AYUDANTE DE INVESTIGACIÓN'),
    (5, u'INVESTIGADOR COLABORADOR')
)

FUNCION_INTEGRANTE_GRUPO_INVESTIGACION = (
    ('', u'--------'),
    (1, u'DIRECTOR'),
    (2, u'CO-DIRECTOR'),
    (3, u'INVESTIGADOR')
)

TIPO_INTEGRANTE = (
    (1, u'PROFESOR'),
    (2, u'ESTUDIANTE'),
    (3, u'ADMINISTRATIVO'),
    (4, u'EXTERNO')
)

TIPO_REGISTRO_INTEGRANTE = (
    (1, u'INTEGRANTE INICIAL'),
    (2, u'REEMPLAZADO'),
    (3, u'REEMPLAZO'),
    (4, u'AGREGADO'),
    (5, u'EXCLUIDO')
)

TIPO_EVALUADOR_PROYECTO = (
    (1, u'PROFESOR'),
    (4, u'EXTERNO')
)

ESTADO_INVESTIGADOR_ACREDITADO = (
    (1, u'POR VERIFICAR'),
    (2, u'VALIDADO'),
    (3, u'RECHAZADO'),
    (4, u'NO APLICA')
)

TIPO_PASAJE_AEREO = (
    (1, u'INTERNACIONAL'),
    (2, u'NACIONAL'),
    (3, u'GENERAL')
)

TIPO_VIATICO = (
    (1, u'INTERNACIONAL'),
    (2, u'NACIONAL'),
    (3, u'GENERAL')
)

TIPO_MOVILIZACION = (
    (1, u'INTERNACIONAL'),
    (2, u'NACIONAL'),
    (3, u'GENERAL')
)

CUMPLE_PORCENTAJE_COMPRA_EQUIPO = (
    (1, u'NO APLICA'),
    (2, u'SI'),
    (3, u'NO')
)

ESTADO_CUMPLIMIENTO_OBJETIVO = (
    (1, u'PENDIENTE'),
    (2, u'CUMPLIDO'),
    (3, u'INCUMPLIDO')
)

ESTADO_ACTIVIDAD = (
    (1, u'POR INICIAR'),
    (2, u'EN EJECUCIÓN'),
    (3, u'FINALIZADA'),
    (4, u'PENDIENTE')
)

TIPO_EVALUADOR = (
    (1, u'INTERNO'),
    (2, u'EXTERNO')
)

TIPO_EVALUACION = (
    (1, u'INTERNA'),
    (2, u'EXTERNA')
)

ESTADO_EVALUACION_INTERNA_EXTERNA = (
    (1, u'ACEPTADO Y NO REQUIERE MODIFICACIONES'),
    (2, u'SERÁ ACEPTADO LUEGO DE MODIFICACIONES MENORES'),
    (3, u'DEBE SER PRESENTADO NUEVAMENTE LUEGO DE MODIFICACIONES MAYORES'),
    (4, u'RECHAZADO'),
    (5, u'EN PROCESO DE EVALUACIÓN')
)

ESTADO_EVALUACION = (
    (1, u'EN CURSO'),
    (2, u'CONFIRMADA'),
    (3, u'ACTA GENERADA'),
    (4, u'ACTA SUBIDA'),
    (5, u'CERRADA'),
    (6, u'NOVEDAD')
)

ESTADO_EVALUACION_OBRA = (
    (1, u'EN CURSO'),
    (2, u'ACTA GENERADA'),
    (3, u'ACTA FIRMADA'),
    (4, u'ACTA SUBIDA'),
    (5, u'CONFIRMADA'),
    (6, u'CERRADA'),
    (7, u'NOVEDAD')
)

TIPO_REVISOR = (
    (1, u'EVIDENCIA'),
    (2, u'BITACORA')
)

TIPO_ROL = (
    (1, 'VALIDADOR'),
    (2, 'APROBADOR')
)

TIPO_ARCHIVO = (
    (1, u'PROYECTO CONTENIDO'),
    (2, u'DOCUMENTO CONCATENADO'),
    (3, u'NOVEDADES REVISIÓN'),
    (4, u'RESOLUCION OCAS'),
    (5, u'CONTRATO DE EJECUCIÓN'),
    (6, u'INFORME DE AVANCE'),
    (7, u'INFORME FINAL'),
    (8, u'INSCRIPCIÓN PROYECTO'),
    (9, u'INSCRIPCIÓN PROYECTO MODIFICACIONES MENORES'),
    (10, u'INSCRIPCIÓN PROYECTO MODIFICACIONES MAYORES'),
    (11, u'INSCRIPCIÓN PROYECTO FIRMADO'),
    (12, u'INSCRIPCIÓN PROYECTO MODIFICACIONES MENORES FIRMADO'),
    (13, u'INSCRIPCIÓN PROYECTO MODIFICACIONES MAYORES FIRMADO'),
    (14, u'INSCRIPCIÓN PROYECTO GENERADO POR COORDINACIÓN DE INVESTIGACIÓN')
)

ESTADO_ARCHIVO_EVIDENCIA = (
    (1, u"CARGADO"),
    (2, u"VALIDADO"),
    (3, u"RECHAZADO"),
    (4, u"NOVEDAD"),
    (5, u"EN REVISIÓN")
)

ESTADO_INFORME = (
    (1, u'POR GENERAR'),
    (2, u"EN ELABORACIÓN"),
    (3, u"ELABORADO"),
    (4, u"CARGADO"),
    (5, u"VERIFICADO"),
    (6, u"P.NOVEDADES"),
    (7, u"APROBADO"),
    (8, u"P.NOVEDADES A"),
    (9, u"RECHAZADO A"),
    (10, u"A.VALIDADO"),
    (11, u"A.NOVEDAD")
)

TRIMESTRE_PROGRAMACION_GASTO = (
    (1, u'ENE-MAR'),
    (2, u'ABR-JUN'),
    (3, u'JUL-SEP'),
    (4, u'OCT-DIC')
)

TIPO_INFORME = (
    (1, u'AVANCE'),
    (2, u'FINAL')
)

TIPO_OBRA_RELEVANCIA = (
    ('', u'---------'),
    (1, u'LIBRO'),
    (2, u'CAPÍTULO')
)

TIPO_FILIACION = (
    ('', u'---------'),
    (1, u'INTERNA'),
    (2, u'EXTERNA')
)

TIPO_PARTICIPANTE = (
    (1, u'AUTOR'),
    (2, u'COAUTOR')
)

ESTADO_CRONOGRAMA = (
    (1, u"EN EDICIÓN"),
    (2, u"CONFIRMADO"),
    (3, u"VALIDADO"),
    (4, u"NOVEDAD")
)

TIPO_RESOLUCION_GRUPO = (
    (1, u'CONSEJO FACULTAD'),
    (2, u'OCS')
)

ESTADO_INFORME_GRUPO = (
    (1, u'ELABORADO'),
    (2, u"VALIDADO"),
    (3, u"NOVEDAD"),
    (4, u"FIRMADO"),
)

TIPO_CUMPLIMIENTO_INFORME = (
    (1, u'OBJETIVO'),
    (2, u'RESULTADO')
)

TIPO_CAMBIO_INFORME = (
    (1, u'CAMBIO'),
    (2, u'PROBLEMA')
)

TIPO_CRITERIO_EVALUACION_PCIENTIFICA = (
    (1, u'ACP'),
    (2, u'ACA'),
    (3, u'BAC'),
    (4, u'PON'),
    (5, u'PRO'),
    (6, u'DTE'),
    (7, u'REV'),
    (8, u'GIE')
)

TIPO_PERSONA_PUBLICACION_F = [
    {"id": 1, "descripcion": "PROFESOR"},
    {"id": 2, "descripcion": "ADMINISTRATIVO"},
    {"id": 3, "descripcion": "ESTUDIANTE"}
]

TIPO_INTEGRANTE_PUBLICACION_F = [
    {"id": 1, "descripcion": "AUTOR"},
    {"id": 2, "descripcion": "COAUTOR"}
]

TIPO_FILIACION_PUBLICACION_F = [
    {"id": 1, "descripcion": "INTERNA"},
    {"id": 2, "descripcion": "EXTERNA"}
]

TIPO_PERSONA_GRUPO_INVESTIGACION_F = [
    {"id": 1, "descripcion": "PROFESOR"},
    {"id": 2, "descripcion": "ESTUDIANTE"},
    {"id": 4, "descripcion": "EXTERNO"}
]

ESTADO_APROBACION = (
    (1, u"PENDIENTE"),
    (2, u'APROBADO'),
    (3, u'RECHAZADO'),
)

ESTADO_REVISION = (
    (1, u"PENDIENTE"),
    (2, u'SOLICITADO'),
    (3, u'REVISADO'),
)


# --------------------------> MANTENIMIENTOS <-----------------------------

class InvImpacto(ModeloBase):
    descripcion = models.TextField(default='', verbose_name=u"Detalle")
    rangoinicio = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'Rango Inicio')
    rangofin = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'Rango Fin')

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(InvImpacto, self).save(*args, **kwargs)

    def __str__(self):
        return u"%s" % self.descripcion + ' (Desde %' + str(self.rangoinicio) + ' Hasta %' + str(self.rangofin) + ')'


class InvCausa(ModeloBase):
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u"Detalle")

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(InvCausa, self).save(*args, **kwargs)

    def flexbox_repr(self):
        profe = ""
        if self.descripcion():
            profe = "CAUSA"
        return self.descripcion + profe

    def __str__(self):
        return u"%s" % self.descripcion


class InvEfecto(ModeloBase):
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u"Detalle")

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(InvEfecto, self).save(*args, **kwargs)

    def __str__(self):
        return u"%s" % self.descripcion


class InvRoles(ModeloBase):
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u"Detalle")
    unico = models.BooleanField(default=False, verbose_name=u"Puesto Único")

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(InvRoles, self).save(*args, **kwargs)

    def __str__(self):
        return u"%s" % self.descripcion


ESTADOS_AREA = (
    (1, u'PENDIENTE'),
    (2, u'PREAPROBADO'),
    (3, u'APROBADO'),
    (4, u'RECHAZADO')
)


# --------------------> COMISION <----------------------------------------

class InvCabComision(ModeloBase):
    nombre = models.CharField(default='', max_length=50, verbose_name=u'Nombre')
    estadocomision = models.IntegerField(choices=ESTADOS_AREA, blank=True, null=True, verbose_name=u'Estados')
    estadoareas = models.IntegerField(choices=ESTADOS_AREA, blank=True, null=True, verbose_name=u'Estados')
    archivoaprobado = models.FileField(upload_to='investigacion/informe', blank=True, null=True,
                                       verbose_name=u'Archivo Informe pdf')
    fecha_numresolucion = models.DateTimeField(blank=True, null=True)
    numresolucion = models.CharField(default='', max_length=100, blank=True, null=True, verbose_name=u'Número de Resolución')
    archivoresolucionpdf = models.FileField(upload_to='investigacion/resolucion', blank=True, null=True,
                                            verbose_name=u'Archivo Resolución pdf')

    def download_archivoaprobadopdf(self):
        if self.archivoaprobado:
            regreso = self.archivoaprobado.url
        else:
            regreso = ''
        return regreso

    def download_archivoresolucionpdf(self):
        if self.archivoresolucionpdf:
            regreso = self.archivoresolucionpdf.url
        else:
            regreso = ''
        return regreso

    def observaciones(self):
        observaciones = InvDetObservacion.objects.filter(cabcom_id=self.pk, status=True).count()
        return observaciones

    def participantes(self):
        participantes = InvDetComisionParticipantes.objects.filter(cabcom_id=self.pk, status=True).count()
        return participantes

    def areas(self):
        areas = InvCabAreas.objects.filter(cabcom_id=self.pk, status=True).count()
        return areas

    def __str__(self):
        return u"%s" % self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(InvCabComision, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Investigación Comisión"
        verbose_name_plural = u"Investigación Comisiones"
        ordering = ['nombre']


class InvDetObservacion(ModeloBase):
    cabcom = models.ForeignKey(InvCabComision, on_delete=models.CASCADE, verbose_name=u"Comisión")
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u"Detalle")

    def flexbox_repr(self):
        return self.cabcom.nombre

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(InvDetObservacion, self).save(*args, **kwargs)


class InvDetComisionParticipantes(ModeloBase):
    cabcom = models.ForeignKey(InvCabComision, on_delete=models.CASCADE, verbose_name=u"Comisión")
    persona = models.ForeignKey('sga.Persona', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona")
    rol = models.ForeignKey(InvRoles, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Cargos")

    def flexbox_repr(self):
        return self.persona

    def institucionlaboral(self):
        if self.persona.es_externo():
            lab = Externo.objects.get(persona=self.persona, status=True)
            institucion = lab.institucionlabora
        else:
            from sagest.models import DistributivoPersona
            dis = DistributivoPersona.objects.filter(persona=self.persona, status=True, estadopuesto=1).count()
            if dis != 0:
                institucion = 'UNEMI'
            else:
                institucion = 'SIN REGISTRAR'
        return institucion

    def hojadevidaexterno(self):
        if self.persona.es_externo():
            lab = Externo.objects.get(persona=self.persona, status=True)
            if lab.hojadevida:
                hv = lab.hojadevida.url
            else:
                hv = ''

        return hv

    def experiencia(self):
        exp = ProyectoInvestigacionExterno.objects.filter(persona=self.persona, status=True)
        return exp

    def tituloalto(self):
        t3 = Titulacion.objects.filter(persona=self.persona, titulo__nivel__nombre='TERCER NIVEL', status=True).order_by('-pk')
        t4 = Titulacion.objects.filter(persona=self.persona, titulo__nivel__nombre='CUARTO NIVEL', status=True).order_by('-pk')
        lista = []

        if t3.count() > 0 and t4.count() == 0:
            lista.append(t3[0])
        elif t3.count() > 0 and t4.count() > 0:
            lista.append(t4[0])
        else:
            lista.append('Sin titulos registrados')
        return lista

    def titulos3nivel(self):
        t3 = Titulacion.objects.filter(persona=self.persona, titulo__nivel__nombre='TERCER NIVEL', status=True)
        return t3

    def titulos4nivel(self):
        t4 = Titulacion.objects.filter(persona=self.persona, titulo__nivel__nombre='CUARTO NIVEL', status=True)
        return t4


class InvComisionHistorialEstados(ModeloBase):
    cabcom = models.ForeignKey(InvCabComision, on_delete=models.CASCADE, verbose_name=u"Comisión")
    descripcion = models.CharField(default='', max_length=200, blank=True, null=True, verbose_name=u'Observación')
    estado = models.TextField(default='', blank=True, null=True, verbose_name=u"Estado Detalle")
    aprobadopor = models.ForeignKey('sga.Persona', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona")

    def flexbox_repr(self):
        return self.cabcom.nombre


# --------------------> CAMPOS DE ACCIÓN <----------------------------------------

class InvCabAreas(ModeloBase):
    cabcom = models.ForeignKey(InvCabComision, on_delete=models.CASCADE, verbose_name=u"Comisión")
    nombre = models.CharField(default='', max_length=50, blank=True, null=True, verbose_name=u'Nombre')
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u'Descripción')
    impacto = models.ForeignKey(InvImpacto, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Impacto")
    numinforme = models.CharField(default='', max_length=100, blank=True, null=True, verbose_name=u'Número de Informe')
    archivoinformepdf = models.FileField(upload_to='investigacion/informe', blank=True, null=True,
                                         verbose_name=u'Archivo Informe pdf')
    aprobadopor = models.ForeignKey('sga.Persona', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona")
    estadoarea = models.IntegerField(choices=ESTADOS_AREA, blank=True, null=True, verbose_name=u'Estados')

    def objetivos(self):
        objetivos = InvDetAreasProblemas.objects.filter(cabareas_id=self.pk, status=True).count()
        return objetivos

    def verobjetivos(self):
        verobjetivos = InvDetAreasProblemas.objects.filter(cabareas_id=self.pk, status=True)
        return verobjetivos

    def download_archivoinformepdf(self):
        if self.archivoinformepdf:
            regreso = self.archivoinformepdf.url
        else:
            regreso = ''
        return regreso

    def __str__(self):
        return u"%s" % self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.descripcion = self.descripcion.upper()
        super(InvCabAreas, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Investigación Areas"
        verbose_name_plural = u"Investigación Areas"
        ordering = ['nombre']


class InvDetAreasProblemas(ModeloBase):
    cabareas = models.ForeignKey(InvCabAreas, on_delete=models.CASCADE, verbose_name=u"Impacto")
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u"Detalle")

    def causas(self):
        causas = InvDetAreasCausas.objects.filter(cabproblemas_id=self.pk, status=True).order_by('pk')
        return causas

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(InvDetAreasProblemas, self).save(*args, **kwargs)

    def __str__(self):
        return u"%s" % self.cabareas.nombre


class InvDetAreasCausas(ModeloBase):
    cabproblemas = models.ForeignKey(InvDetAreasProblemas, on_delete=models.CASCADE, verbose_name=u"Impacto")
    causas = models.ForeignKey(InvCausa, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Impacto")

    def efectos(self):
        efectos = InvDetAreasCausasEfecto.objects.filter(cabareascausa_id=self.pk, status=True).order_by('pk')
        return efectos


class InvDetAreasCausasEfecto(ModeloBase):
    cabareascausa = models.ForeignKey(InvDetAreasCausas, on_delete=models.CASCADE, verbose_name=u"Impacto")
    efecto = models.ForeignKey(InvEfecto, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Efecto")


class InvCabAreasHistorialEstados(ModeloBase):
    cabarea = models.ForeignKey(InvCabAreas, on_delete=models.CASCADE, verbose_name=u"Comisión")
    descripcion = models.CharField(default='', max_length=200, blank=True, null=True, verbose_name=u'Observación')
    estado = models.TextField(default='', blank=True, null=True, verbose_name=u"Estado Detalle")
    aprobadopor = models.ForeignKey('sga.Persona', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona")

    def flexbox_repr(self):
        return self.cabarea \
            .nombre


class InvCabAreasHistorialInforme(ModeloBase):
    cabarea = models.ForeignKey(InvCabAreas, on_delete=models.CASCADE, verbose_name=u"Comisión")
    archivoinformepdf = models.FileField(upload_to='investigacion/informehistorial', blank=True, null=True,
                                         verbose_name=u'Archivo Informe pdf')
    realizadopor = models.ForeignKey('sga.Persona', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona")

    def flexbox_repr(self):
        return self.cabarea \
            .nombre

    def download_archivoinformepdf(self):
        if self.archivoinformepdf:
            regreso = self.archivoinformepdf.url
        else:
            regreso = ''
        return regreso


# --------------------> LINEAS DE INVESTIGACIÓN  <----------------------------------------

class AreaUnesco(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre')

    def subareas(self):
        return SubAreaUnesco.objects.filter(cabarea_id=self.pk).order_by('pk')

    def __str__(self):
        return u"%s" % self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(AreaUnesco, self).save(*args, **kwargs)


class SubAreaUnesco(ModeloBase):
    cabarea = models.ForeignKey(AreaUnesco, on_delete=models.CASCADE, verbose_name=u"Area")
    nombre = models.CharField(default='', max_length=200, verbose_name=u'Nombre')

    def __str__(self):
        return u"%s" % self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(SubAreaUnesco, self).save(*args, **kwargs)


class IndustriaPriorizada(ModeloBase):
    tipo = models.IntegerField(choices=TIPO_INDUSTRIA_PRIORIZADA, default=1, verbose_name=u'Tipo de industria')
    nombre = models.CharField(default='', max_length=250, verbose_name=u'Nombre')
    orden = models.IntegerField(default=0, verbose_name=u'Orden')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Industria Priorizada"
        verbose_name_plural = u"Industrias Priorizadas"
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        super(IndustriaPriorizada, self).save(*args, **kwargs)


class ZonaPlanificacion(ModeloBase):
    numero = models.IntegerField(default=0, verbose_name=u'Número')
    nombre = models.CharField(max_length=50, verbose_name=u'Nombre')
    miembroszona = models.CharField(max_length=250, default='', verbose_name=u'Miembros integrantes de la zona')

    def __str__(self):
        return u'%s ( %s )' % (self.nombre, self.miembroszona)

    class Meta:
        verbose_name = u"Zona de Planificación"
        verbose_name_plural = u"Zonas de Planificación"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        self.miembroszona = self.miembroszona.upper().strip()
        super(ZonaPlanificacion, self).save(*args, **kwargs)


class TipoRecursoPresupuesto(ModeloBase):
    descripcion = models.CharField(max_length=150, default='', verbose_name=u'Descripción')
    orden = models.IntegerField(default=0, verbose_name=u'Orden')
    abreviatura = models.CharField(max_length=50, default='', verbose_name=u'Abreviatura')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')

    def __str__(self):
        return u'%s - %s' % (self.descripcion, self.orden)

    class Meta:
        verbose_name = u"Tipo de Recurso de Presupuesto"
        verbose_name_plural = u"Tipos de Recurso de Presupuesto"
        ordering = ['descripcion']

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper().strip()
        super(TipoRecursoPresupuesto, self).save(*args, **kwargs)


class Periodocidad(ModeloBase):
    descripcion = models.CharField(max_length=150, default='', verbose_name=u'Descripción')
    valor = models.IntegerField(default=0, verbose_name=u'Valor')
    tipo = models.IntegerField(choices=TIPO_UNIDAD_PERIODO, default=1, verbose_name=u'Tipo de periodo')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')

    def __str__(self):
        return u'%s' % (self.descripcion)

    class Meta:
        verbose_name = u"Periodocidad de tiempo"
        verbose_name_plural = u"Periodocidades de tiempo"
        ordering = ['descripcion']
        unique_together = ('descripcion',)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper().strip()
        super(Periodocidad, self).save(*args, **kwargs)


class Categoria(ModeloBase):
    descripcion = models.CharField(max_length=150, default='', verbose_name=u'Descripción')
    numero = models.IntegerField(default=0, verbose_name=u'Número')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')
    compraequipo = models.IntegerField(choices=VALOR_SI_NO, blank=True, null=True, verbose_name=u'Contempla compra equipos')

    def __str__(self):
        return u'%s' % (self.descripcion)

    class Meta:
        verbose_name = u"Categoría de proyecto"
        verbose_name_plural = u"Categorías de proyectos"
        ordering = ['descripcion']
        unique_together = ('descripcion',)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper().strip()
        super(Categoria, self).save(*args, **kwargs)


class GrupoInvestigacionRequisitoIntegrante(ModeloBase):
    numero = models.IntegerField(default=0, verbose_name=u'Número de requisito')
    descripcion = models.TextField(default='', verbose_name=u'Descripción')
    observacion = models.CharField(max_length=500, default='', verbose_name=u'Observación')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')

    def __str__(self):
        return u'%s - %s' % (self.numero, self.descripcion)

    class Meta:
        verbose_name = u"Requisito para ser Director del grupo de investigación"
        verbose_name_plural = u"Requisitos para ser Director del grupo de investigación"


class GrupoInvestigacion(ModeloBase):
    numero = models.IntegerField(blank=True, null=True, verbose_name=u'Número de solicitud')
    fechasolicitud = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de solicitud de creación de grupo')
    solicitudvigente = models.BooleanField(default=False, verbose_name=u'Solicitud vigente')
    solicitado = models.BooleanField(default=False, verbose_name=u'Solicitud enviada a decano')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Periodo académico')
    coordinacion = models.ForeignKey(Coordinacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Facultad pertenece grupo')
    profesor = models.ForeignKey("sga.Profesor", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Profesor solicitante')
    nombre = models.TextField(default='', verbose_name=u'Nombre')
    acronimo = models.CharField(default='', max_length=50, verbose_name=u'Acrónimo')
    descripcion = models.TextField(default='', verbose_name=u'Descripción')
    objetivogeneral = models.TextField(default='', verbose_name=u'Objetivo general')
    lineainvestigacion = models.ManyToManyField(LineaInvestigacion, verbose_name=u'líneas de investigación')
    colaboracion = models.TextField(default='', verbose_name=u'Colaboración con otros grupos de Investigación del director')
    logotipo = models.FileField(upload_to='grupoinvestigacion/logo/%Y/%m/%d', blank=True, null=True, verbose_name=u'Logotipo')
    aprobadocoord = models.BooleanField(default=True, verbose_name=u'Aprobado por facultad')
    informegen = models.BooleanField(default=False, verbose_name=u'Informe técnico generado')
    aprobadoocs = models.BooleanField(default=True, verbose_name=u'Aprobado por OCS')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    estado = models.ForeignKey("sagest.EstadoSolicitud", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Estado asignado')

    def __str__(self):
        return u'%s' % (self.nombre)

    class Meta:
        verbose_name = u"Grupo de investigación"
        verbose_name_plural = u"Grupos de investigación"
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        self.acronimo = self.acronimo.upper().strip()
        super(GrupoInvestigacion, self).save(*args, **kwargs)

    def director(self):
        if self.grupoinvestigacionintegrante_set.filter(funcion=1, status=True).exists():
            return self.grupoinvestigacionintegrante_set.filter(funcion=1, status=True)[0]
        else:
            return None

    def icono_vigente(self):
        return 'fa fa-check-circle text-success' if self.vigente else 'fa fa-times-circle text-error'

    def integrantes(self):
        return self.grupoinvestigacionintegrante_set.filter(status=True).order_by('id')

    def puede_eliminar(self):
        if ProyectoInvestigacion.objects.values("id").filter(status=True, grupoinvestigacion=self).count() == 0:
            if PlanificarPonencias.objects.values("id").filter(status=True, grupoinvestigacion=self).count() == 0:
                return True

        return False

    def carrera_grupo(self):
        return self.grupoinvestigacionintegrante_set.filter(status=True, funcion=1)[0].carrera.nombre

    def recorrido(self):
        return self.grupoinvestigacionrecorrido_set.filter(status=True).order_by('id')

    def puede_editar_solicitud(self):
        return self.estado.valor in [1, 6, 12]

    def puede_eliminar_solicitud(self):
        return self.estado.valor in [1, 6, 12]

    def puede_confirmar_solicitud(self):
        return self.estado.valor == 1

    def puede_revisar_solicitud(self):
        return self.estado.valor in [2, 4, 6]

    def puede_subir_resolucion_facultad(self):
        return self.estado.valor in [4, 5]

    def puede_reasignar_a_coordinador(self):
        return self.estado.valor == 5

    def puede_reasignar_a_analista(self):
        return self.estado.valor == 7

    def puede_validar_solicitud(self):
        return self.estado.valor in [8, 9, 10]

    def puede_devolver_a_vicerrector(self):
        return self.estado.valor == 10

    def puede_devolver_a_solicitante(self):
        return self.estado.valor == 11

    def puede_subir_resolucion_ocs(self):
        return self.estado.valor in [20, 21]

    def tiene_observaciones(self):
        return self.estado.valor in [6, 12]

    def objetivos_especificos(self):
        return self.grupoinvestigacionobjetivo_set.filter(status=True).order_by('id')

    def tecnologias(self):
        return self.grupoinvestigaciontecnologia_set.filter(status=True).order_by('id')

    def requisitos_director(self):
        return GrupoInvestigacionIntegranteRequisito.objects.filter(status=True, integrante__funcion=1, integrante__grupo=self).order_by('id')

    def lineas_grupo(self):
        return self.lineainvestigacion.all()

    def resolucion_facultad(self):
        if self.grupoinvestigacionresolucion_set.values("id").filter(status=True, vigente=True, tipo=1).exists():
            return self.grupoinvestigacionresolucion_set.filter(status=True, vigente=True, tipo=1)[0]
        return None

    def resolucion_ocs(self):
        if self.grupoinvestigacionresolucion_set.values("id").filter(status=True, vigente=True, tipo=2).exists():
            return self.grupoinvestigacionresolucion_set.filter(status=True, vigente=True, tipo=2)[0]
        return None

    def puede_agregar_editar_informe(self):
        return self.estado.valor in [9, 13, 14, 17]

    def tiene_informe(self):
        return False

    def informe(self):
        if self.grupoinvestigacioninforme_set.values("id").filter(status=True).exists():
            return self.grupoinvestigacioninforme_set.filter(status=True)[0]
        return None

    def puede_imprimir_informe(self):
        return self.estado.valor in [13, 14]

    def puede_firmar_informe(self):
        if self.puede_imprimir_informe():
            return self.informe().impreso
        return False

    def puede_validar_informe(self):
        return self.estado.valor in [14, 15, 16, 17]

    def puede_firmar_informe_experto(self):
        return self.estado.valor in [15, 16]

    def puede_firmar_informe_coordinador(self):
        return self.estado.valor in [16, 18, 19]

    def revisado_decano(self):
        return self.grupoinvestigacionrecorrido_set.values("id").filter(status=True, estado__valor__in=[4, 5, 6])

    def revisado_analista(self):
        return self.grupoinvestigacionrecorrido_set.values("id").filter(status=True, estado__valor__in=[9, 10])

    def resolucion_memorando(self):
        documentos = []

        resolucion = self.resolucion_facultad()
        documentos.append({
            "descripcion": "Resolución " + resolucion.numero,
            "fecha": resolucion.fecha,
            "numeropagina": resolucion.numeropagina,
            "archivo": resolucion.archivo
        })

        return documentos


class GrupoInvestigacionObjetivo(ModeloBase):
    grupo = models.ForeignKey(GrupoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Grupo de Investigación')
    descripcion = models.TextField(default='', verbose_name=u'Descripción del objetivo')

    def __str__(self):
        return '%s - %s' % (self.grupo, self.descripcion)

    class Meta:
        verbose_name = u"Objetivo específico del grupo de investigación"
        verbose_name_plural = u"Objetivos específicos del grupo de investigación"

    def save(self, *args, **kwargs):
        super(GrupoInvestigacionObjetivo, self).save(*args, **kwargs)


class GrupoInvestigacionTecnologia(ModeloBase):
    grupo = models.ForeignKey(GrupoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Grupo de Investigación')
    descripcion = models.TextField(default='', verbose_name=u'Descripción de la tecnología que domina')

    def __str__(self):
        return '%s - %s' % (self.grupo, self.descripcion)

    class Meta:
        verbose_name = u"Tecnología que domoina el grupo de investigación"
        verbose_name_plural = u"Tecnologías que domina el grupo de investigación"

    def save(self, *args, **kwargs):
        super(GrupoInvestigacionTecnologia, self).save(*args, **kwargs)


class GrupoInvestigacionIntegrante(ModeloBase):
    grupo = models.ForeignKey(GrupoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Grupo de Investigación')
    tipo = models.IntegerField(choices=TIPO_INTEGRANTE, default=1, verbose_name=u'Tipo de integrante')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, verbose_name=u'Persona')
    coordinacion = models.ForeignKey("sga.Coordinacion", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Facultad pertenece persona')
    carrera = models.ForeignKey("sga.Carrera", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Carrera pertenece persona')
    tipodocente = models.ForeignKey("sga.ProfesorTipo", blank=True, null=True, on_delete=models.CASCADE, verbose_name=u"Tipo (profesores)")
    dedicacion = models.ForeignKey("sga.TiempoDedicacionDocente", blank=True, null=True, on_delete=models.CASCADE, verbose_name=u"Dedicación (profesores)")
    filiacion = models.IntegerField(choices=TIPO_FILIACION, default=1, verbose_name=u'Tipo de filiación')
    funcion = models.IntegerField(choices=FUNCION_INTEGRANTE_GRUPO_INVESTIGACION, default=3, verbose_name=u'Función del integrante')
    cantidadhora = models.DecimalField(default=0, max_digits=30, decimal_places=2, blank=True, null=True, verbose_name=u'Cantidad de horas dedicación al grupo')
    trayectoriaprevia = models.TextField(default='', verbose_name=u'Trayectoria previa en las líneas de investigación propuestas')
    justificacion = models.TextField(default='', verbose_name=u'Justificación de participación en más de 2 grupos vigentes a la vez')

    def __str__(self):
        return u'%s - %s' % (self.persona, self.get_funcion_display())

    class Meta:
        verbose_name = u"Integrante del grupo de investigación"
        verbose_name_plural = u"Integrantes del grupo de investigación"

    def save(self, *args, **kwargs):
        super(GrupoInvestigacionIntegrante, self).save(*args, **kwargs)


class GrupoInvestigacionIntegranteRequisito(ModeloBase):
    integrante = models.ForeignKey(GrupoInvestigacionIntegrante, on_delete=models.CASCADE, verbose_name=u'Integrante de Grupo de Investigación')
    requisito = models.ForeignKey(GrupoInvestigacionRequisitoIntegrante, on_delete=models.CASCADE, verbose_name=u'Requisito')
    cumpledir = models.BooleanField(default=False, verbose_name=u'Estado cumplimiento asignado por director de grupo')
    cumpledec = models.BooleanField(default=False, verbose_name=u'Estado cumplimiento asignado por decano de facultad')
    cumpleanl = models.BooleanField(default=False, verbose_name=u'Estado cumplimiento asignado por analista de investigación')

    def __str__(self):
        return u'%s - %s' % (self.integrante, self.requisito)

    class Meta:
        verbose_name = u"Requisito del integrante del grupo de investigación"
        verbose_name_plural = u"Requisitos de los integrantes del grupo de investigación"

    def save(self, *args, **kwargs):
        super(GrupoInvestigacionIntegranteRequisito, self).save(*args, **kwargs)


class GrupoInvestigacionRecorrido(ModeloBase):
    grupo = models.ForeignKey(GrupoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Grupo de Investigación')
    fecha = models.DateField(verbose_name=u'Fecha recorrido')
    observacion = models.TextField(verbose_name=u'Observación del recorrido')
    estado = models.ForeignKey("sagest.EstadoSolicitud", on_delete=models.CASCADE, verbose_name=u"Estado asignado")

    def __str__(self):
        return u'%s - %s - %s' % (self.grupo, self.fecha, self.estado.descripcion)

    class Meta:
        verbose_name = u"Grupo de Investigación Recorrido"
        verbose_name_plural = u"Grupos de Investigación Recorrido"


class GrupoInvestigacionResolucion(ModeloBase):
    grupo = models.ForeignKey(GrupoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Grupo de Investigación')
    tipo = models.IntegerField(choices=TIPO_RESOLUCION_GRUPO, default=1, verbose_name=u'Tipo de resolución')
    numero = models.CharField(max_length=150, verbose_name=u'Número de resolución')
    fecha = models.DateField(verbose_name=u'Fecha resolución')
    resuelve = models.TextField(default='', verbose_name=u'Resuelve')
    archivo = models.FileField(upload_to='grupoinvestigacion/resolucion/%Y/%m/%d', verbose_name=u'Archivo resolución')
    numeropagina = models.IntegerField(default=0, verbose_name=u'Número de páginas')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')

    def __str__(self):
        return u'%s - %s - %s' % (self.grupo, self.fecha, self.numero)

    class Meta:
        verbose_name = u"Resolución de Grupo de Investigación"
        verbose_name_plural = u"Resoluciones de Grupos de Investigación"


class GrupoInvestigacionInforme(ModeloBase):
    grupo = models.ForeignKey(GrupoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Grupo de Investigación')
    secuencia = models.IntegerField(default=0, verbose_name=u'Secuencia informe')
    fecha = models.DateTimeField(verbose_name=u'Fecha del informe')
    numero = models.CharField(default='', max_length=150, verbose_name=u'Número')
    remitente = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, verbose_name=u"Persona que elabora el informe")
    cargoremitente = models.ForeignKey("sagest.DenominacionPuesto", on_delete=models.CASCADE, verbose_name=u"Cargo de quién elabora el informe")
    destinatario = models.ForeignKey("sga.Persona", related_name="+", on_delete=models.CASCADE, verbose_name=u"Persona a quién va dirigido el informe")
    cargodestinatario = models.ForeignKey("sagest.DenominacionPuesto", related_name="+", on_delete=models.CASCADE, verbose_name=u"Cargo de a quién va drigido el informe")
    objeto = models.TextField(default='', verbose_name=u'Objeto')
    antecedente = models.TextField(default='', verbose_name=u'Antecedentes')
    motivaciontecnica = models.TextField(default='', verbose_name=u'Motivación técnica')
    conclusion = models.TextField(default='', verbose_name=u'Conclusiones')
    recomendacion = models.TextField(default='', verbose_name=u'Recomendaciones')
    impreso = models.BooleanField(default=False, verbose_name=u'Informe impreso')
    archivo = models.FileField(upload_to='grupoinvestigacion/informe/generado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo del informe')
    archivofirmado = models.FileField(upload_to='grupoinvestigacion/informe/firmado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo del informe con firmas')
    observacion = models.TextField(default='', verbose_name=u'Observación de la revisión')
    elabora = models.ForeignKey("sga.Persona", related_name="+", on_delete=models.CASCADE, verbose_name=u"Persona que elabora el informe")
    cargoelabora = models.ForeignKey("sagest.DenominacionPuesto", related_name="+", on_delete=models.CASCADE, verbose_name=u"Cargo de quién elabora el informe")
    verifica = models.ForeignKey("sga.Persona", related_name="+", blank=True, null=True, on_delete=models.CASCADE, verbose_name=u"Persona que verifica el informe")
    cargoverifica = models.ForeignKey("sagest.DenominacionPuesto", related_name="+", blank=True, null=True, on_delete=models.CASCADE, verbose_name=u"Cargo de quién verifica el informe")
    aprueba = models.ForeignKey("sga.Persona", related_name="+", on_delete=models.CASCADE, verbose_name=u"Persona que aprueba el informe")
    cargoaprueba = models.ForeignKey("sagest.DenominacionPuesto", related_name="+", on_delete=models.CASCADE, verbose_name=u"Cargo de quién aprueba el informe")
    firmaelabora = models.BooleanField(default=False, verbose_name=u'Firmado por persona que elabora')
    firmaverifica = models.BooleanField(default=False, verbose_name=u'Firmado por persona que verifica')
    firmaaprueba = models.BooleanField(default=False, verbose_name=u'Firmado por persona que aprueba')
    remitidocga = models.BooleanField(default=False, verbose_name=u'Informe Remitido a CGA')
    estado = models.IntegerField(choices=ESTADO_INFORME_GRUPO, default=1, verbose_name=u'Estado')

    def __str__(self):
        return u'%s - %s - %s' % (self.grupo, self.numero, self.get_estado_display())

    class Meta:
        verbose_name = u"Informe Técnico de Grupo de Investigación"
        verbose_name_plural = u"Informes Técnicos de Grupos de Investigación"

    def anexos(self):
        return self.grupoinvestigacioninformeanexo_set.filter(status=True).order_by('id')


class GrupoInvestigacionInformeAnexo(ModeloBase):
    informe = models.ForeignKey(GrupoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Grupo de Investigación')
    descripcion = models.CharField(max_length=250, default='', verbose_name=u'Descripción')
    fecha = models.DateField(verbose_name=u'Fecha generación de la evidencia')
    numeropagina = models.IntegerField(default=1, verbose_name=u'Número de páginas')
    archivo = models.FileField(upload_to='grupoinvestigacion/anexoinforme/%Y/%m/%d', verbose_name=u'Archivo del anexo')

    def __str__(self):
        return u'%s - %s' % (self.informe, self.descripcion)

    class Meta:
        verbose_name = u"Anexo del Informe Técnico de Grupo de Investigación"
        verbose_name_plural = u"Anexos del Informe Técnico de Grupo de Investigación"


class ConvocatoriaProyecto(ModeloBase):
    descripcion = models.CharField(max_length=150, verbose_name=u'Descripción')
    apertura = models.DateField(verbose_name=u'Fecha apertura de convocatoria')
    cierre = models.DateField(verbose_name=u'Fecha cierre de convocatoria')
    inicioevalint = models.DateField(verbose_name=u'Fecha inicio evaluación interna')
    finevalint = models.DateField(verbose_name=u'Fecha fin evaluación interna')
    inicioreevalint = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio reevaluación interna')
    finreevalint = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin reevaluación interna')
    inicioevalext = models.DateField(verbose_name=u'Fecha inicio evaluación externa')
    finevalext = models.DateField(verbose_name=u'Fecha fin evaluación externa')
    inicioreevalext = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio reevaluación externa')
    finreevalext = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin reevaluación externa')
    vigente = models.BooleanField(default=True, verbose_name=u'Convocatoria vigente')
    minimoaprobacion = models.IntegerField(default=0, verbose_name=u'Puntaje mínimo aprobación evaluación')
    periodocidad = models.ForeignKey(Periodocidad, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Periodocidad para elaboración de informes')
    archivoresolucion = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo resolución ocas')
    archivoformatopresupuesto = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo formato presupuesto')
    archivoconvocatoria = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de las bases de la convocatoria')
    minintegranteu = models.IntegerField(default=0, verbose_name=u'Número mínimo integrantes UNEMI')
    maxintegranteu = models.IntegerField(default=0, verbose_name=u'Número máximo integrantes UNEMI')
    minintegrantee = models.IntegerField(default=0, verbose_name=u'Número mínimo integrantes EXTERNOS')
    maxintegrantee = models.IntegerField(default=0, verbose_name=u'Número máximo integrantes EXTERNOS')
    visible = models.BooleanField(default=True, verbose_name=u'Mostrar en pantalla')

    def __str__(self):
        return u'%s - %s - %s' % (self.descripcion, self.apertura, self.cierre)

    class Meta:
        verbose_name = u"Convocatoria Proyecto de Investigación"
        verbose_name_plural = u"Convocatorias Proyectos de Investigación"

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.strip().upper()
        super(ConvocatoriaProyecto, self).save(*args, **kwargs)

    def esta_abierta(self):
        fechaactual = datetime.now().date()
        return self.cierre >= fechaactual >= self.apertura

    def evaluacion_interna_abierta(self):
        fechaactual = datetime.now().date()
        return self.inicioevalint <= fechaactual <= self.finevalint

    def reevaluacion_interna_abierta(self):
        fechaactual = datetime.now().date()
        return self.inicioreevalint <= fechaactual <= self.finreevalint

    def evaluacion_externa_abierta(self):
        fechaactual = datetime.now().date()
        return self.inicioevalext <= fechaactual <= self.finevalext

    def reevaluacion_externa_abierta(self):
        fechaactual = datetime.now().date()
        return self.inicioreevalext <= fechaactual <= self.finreevalext

    def total_proyectos(self):
        return self.proyectoinvestigacion_set.filter(status=True).count()

    def total_proyectos_director(self, persona):
        return self.proyectoinvestigacion_set.values('id').filter(status=True, profesor__persona=persona).count()

    def total_proyectos_como_participante(self, persona):
        return self.proyectoinvestigacion_set.values('id').filter(status=True, proyectoinvestigacionintegrante__persona=persona, proyectoinvestigacionintegrante__status=True, proyectoinvestigacionintegrante__tiporegistro__in=[1, 3, 4],
                                                                  proyectoinvestigacionintegrante__funcion__in=[2, 3, 4, 5]).count()

    def es_evaluador_proyecto_finalizado(self, persona):
        return self.proyectoinvestigacion_set.values('id').filter(proyectoinvestigacionevaluador__persona=persona, proyectoinvestigacionevaluador__tipo=1, proyectoinvestigacionevaluador__tipoproyecto=2, proyectoinvestigacionevaluador__status=True).exists()

    def es_integrante_externo(self, persona):
        return self.proyectoinvestigacion_set.values('id').filter(status=True, proyectoinvestigacionintegrante__persona=persona, proyectoinvestigacionintegrante__status=True, proyectoinvestigacionintegrante__tipo=4).count()

    def totales_propuestas_proyectos_evaluar(self, persona):
        evaluados = pendientes = encurso = 0
        # asignados = self.proyectoinvestigacion_set.values('id').filter(proyectoinvestigacionevaluador__persona=persona, proyectoinvestigacionevaluador__tipo=2, proyectoinvestigacionevaluador__tipoproyecto=1, proyectoinvestigacionevaluador__status=True).count()
        asignados = self.proyectoinvestigacion_set.values('id').filter(proyectoinvestigacionevaluador__persona=persona, proyectoinvestigacionevaluador__tipoproyecto=1, proyectoinvestigacionevaluador__status=True, proyectoinvestigacionevaluador__reevaluacion=False).count()
        if asignados > 0:
            # evaluaciones = EvaluacionProyecto.objects.filter(status=True, tipo=2, adicional=False, proyecto__convocatoria=self, evaluador__persona=persona)
            evaluaciones = EvaluacionProyecto.objects.filter(status=True, adicional=False, proyecto__convocatoria=self, evaluador__persona=persona)
            # evaluados = evaluaciones.filter(estadoregistro=5).count()
            evaluados = evaluaciones.filter(estadoregistro__in=[2, 5, 6]).count()
            encurso = evaluaciones.count() - evaluados
            pendientes = asignados - evaluaciones.count()

        return {"asignados": asignados, "evaluados": evaluados, "encurso": encurso, "pendientes": pendientes}

    def totales_propuestas_proyectos_reevaluar(self, persona):
        evaluados = pendientes = encurso = 0
        # asignados = self.proyectoinvestigacion_set.values('id').filter(proyectoinvestigacionevaluador__persona=persona, proyectoinvestigacionevaluador__tipo=2, proyectoinvestigacionevaluador__tipoproyecto=1, proyectoinvestigacionevaluador__status=True).count()
        asignados = self.proyectoinvestigacion_set.values('id').filter(proyectoinvestigacionevaluador__persona=persona, proyectoinvestigacionevaluador__tipoproyecto=1, proyectoinvestigacionevaluador__status=True, proyectoinvestigacionevaluador__reevaluacion=True).count()
        if asignados > 0:
            # evaluaciones = EvaluacionProyecto.objects.filter(status=True, tipo=2, adicional=False, proyecto__convocatoria=self, evaluador__persona=persona)
            evaluaciones = EvaluacionProyecto.objects.filter(status=True, adicional=True, proyecto__convocatoria=self, evaluador__persona=persona)
            # evaluados = evaluaciones.filter(estadoregistro=5).count()
            evaluados = evaluaciones.filter(estadoregistro__in=[2, 5, 6]).count()
            encurso = evaluaciones.count() - evaluados
            pendientes = asignados - evaluaciones.count()

        return {"asignados": asignados, "evaluados": evaluados, "encurso": encurso, "pendientes": pendientes}

    def rubricas_evaluacion(self):
        return self.rubricaevaluacion_set.filter(status=True).order_by('numero')

    def total_valoracion_rubricas(self):
        if self.rubricaevaluacion_set.filter(status=True).exists():
            return self.rubricaevaluacion_set.filter(status=True).aggregate(total=Sum('valoracion'))['total']
        return 0

    def lista_ids_montofinanciamiento(self):
        return self.convocatoriamontofinanciamiento_set.values_list('tipoproyecto', flat=True).filter(status=True).order_by('id')

    def lista_ids_programasinvestigacion(self):
        return self.convocatoriaprogramainvestigacion_set.values_list('programainvestigacion_id', flat=True).filter(status=True).order_by('id')

    def tiene_resolucion_aprobacion(self):
        return self.resolucion_aprobacion()

    def archivo_resolucion_aprobacion(self):
        return self.resolucion_aprobacion()[0].archivo

    def resolucion_aprobacion(self):
        return self.convocatoriaresolucionaprobacionproyecto_set.filter(status=True).order_by('fecha')

    def tipos_recursos_presupuesto(self):
        return self.convocatoriatiporecurso_set.filter(status=True).order_by('secuencia')


class ConvocatoriaMontoFinanciamiento(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaProyecto, on_delete=models.CASCADE, verbose_name=u'Convocatoria de Proyectos', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Categoría de proyectos')
    tipoproyecto = models.IntegerField(choices=TIPO_PROYECTO, blank=True, null=True, verbose_name=u'Tipo de proyecto')
    tipoequipamiento = models.IntegerField(choices=TIPO_EQUIPAMIENTO, blank=True, null=True, verbose_name=u'Contempla compra de equipamiento')
    minimo = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u'Monto mínimo')
    maximo = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u'Monto máximo')
    porcentajecompra = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% para compra de equipo')
    tipoporcentaje = models.IntegerField(default=0, choices=TIPO_PORCENTAJE_EQUIPOS, verbose_name=u'Tipo de porcentaje')

    def __str__(self):
        return u'%s - %s - %s - %s' % (self.convocatoria.descripcion, self.get_tipoproyecto_display(), self.get_tipoequipamiento_display(), self.maximo)

    class Meta:
        verbose_name = u"Monto de Financiamiento de Convocatoria Proyecto"
        verbose_name_plural = u"Montos de Financiamiento de Convocatorias Proyectos"

    def tipo_equipamiento(self):
        if self.tipoequipamiento == 1:
            return 'EQUIPOS MAYORES'
        elif self.tipoequipamiento == 2:
            return 'EQUIPOS MENORES'
        elif self.tipoequipamiento == 4:
            return 'PROYECTOS TECNOLÓGICOS'
        else:
            return 'NO'


class ConvocatoriaProgramaInvestigacion(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaProyecto, on_delete=models.CASCADE, verbose_name=u'Convocatoria de Proyectos', blank=True, null=True)
    programainvestigacion = models.ForeignKey(ProgramasInvestigacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Programa de investigación')

    def __str__(self):
        return u'%s - %s' % (self.convocatoria.descripcion, self.programainvestigacion.nombre)

    class Meta:
        verbose_name = u"Programa de investigación de Convocatoria Proyecto"
        verbose_name_plural = u"Programas de investigación de Convocatorias Proyectos"

    def en_uso(self):
        return ProyectoInvestigacion.objects.values('id').filter(status=True, programainvestigacion=self.programainvestigacion, convocatoria=self.convocatoria).exists()


class ConvocatoriaTipoRecurso(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaProyecto, on_delete=models.CASCADE, verbose_name=u'Convocatoria de Proyectos')
    tiporecurso = models.ForeignKey(TipoRecursoPresupuesto, on_delete=models.CASCADE, verbose_name=u'Requisito')
    secuencia = models.IntegerField(default=0, verbose_name=u'Número de orden en el que se listan')

    def __str__(self):
        return u'%s - %s - %s' % (self.convocatoria.descripcion, self.tiporecurso.descripcion, self.secuencia)

    class Meta:
        verbose_name = u"Tipo de Recurso de la convocatoria"
        verbose_name_plural = u"Tipos de Recursos de las convocatorias"


class TipoResultadoCompromiso(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaProyecto, on_delete=models.CASCADE, verbose_name=u'Convocatoria de Proyectos', blank=True, null=True)
    descripcion = models.CharField(max_length=250, default='', verbose_name=u'Descripción')
    numero = models.IntegerField(default=0, verbose_name=u'Número')
    fijo = models.BooleanField(default=False, verbose_name=u'Fijo')
    obligatorio = models.BooleanField(default=False, verbose_name=u'Obligatorio')

    def __str__(self):
        return u'%s - %s' % (self.descripcion, self.numero)

    class Meta:
        verbose_name = u"Tipo de Resultado/Compromiso"
        verbose_name_plural = u"Tipos de Resultado/Compromiso"
        ordering = ['descripcion']

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.strip()
        super(TipoResultadoCompromiso, self).save(*args, **kwargs)


class ConvocatoriaResolucionAprobacionProyecto(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaProyecto, on_delete=models.CASCADE, verbose_name=u'Convocatoria de Proyectos', blank=True, null=True)
    fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha de resolución')
    numero = models.CharField(max_length=250, blank=True, null=True, verbose_name=u'Número')
    archivo = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo')
    resuelve = models.TextField(default='', verbose_name=u'Texto Resuelve')
    fechanotificaaprobacion = models.DateField(blank=True, null=True, verbose_name=u'Fecha de notificación de proyectos aprobados')

    def __str__(self):
        return u'%s - %s - %s' % (self.convocatoria.descripcion, self.fecha, self.numero)

    class Meta:
        verbose_name = u"Resolución de aprobación de proyectos de la Convocatoria"
        verbose_name_plural = u"Resoluciones de aprobación de proyectos de la Convocatoria"

    def save(self, *args, **kwargs):
        self.numero = self.numero.upper().strip()
        super(ConvocatoriaResolucionAprobacionProyecto, self).save(*args, **kwargs)


class ProyectoInvestigacion(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaProyecto, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Convocatoria de proyectos')
    profesor = models.ForeignKey("sga.Profesor", blank=True, null=True, on_delete=models.CASCADE, verbose_name=u'Profesor solicitante - Director del proyecto')
    categoria = models.IntegerField(choices=CATEGORIA_PROYECTO, blank=True, null=True, verbose_name=u'Categoría de proyecto')
    categoria2 = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Categoría de proyectos')
    codigo = models.CharField(max_length=250, blank=True, null=True, verbose_name=u'Código del proyecto')
    secuencia = models.IntegerField(blank=True, null=True, verbose_name=u'Secuencia para código del proyecto')
    titulo = models.TextField(verbose_name=u"Título del proyecto")
    fechainicio = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio')
    fechafinplaneado = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin planeado')
    fechafinreal = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin real')
    fechacierre = models.DateField(blank=True, null=True, verbose_name=u'Fecha cierre')
    areaconocimiento = models.ForeignKey(AreaConocimientoTitulacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Área de conocimiento')
    subareaconocimiento = models.ForeignKey(SubAreaConocimientoTitulacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Sub-área de conocimiento')
    subareaespecificaconocimiento = models.ForeignKey(SubAreaEspecificaConocimientoTitulacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Sub-área específica de conocimiento')
    lineainvestigacion = models.ForeignKey(LineaInvestigacion, on_delete=models.CASCADE, verbose_name=u'Línea de investigación')
    sublineainvestigacion = models.ManyToManyField(SubLineaInvestigacion, verbose_name=u'Sub-líneas de investigación')
    programainvestigacion = models.ForeignKey(ProgramasInvestigacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Programa de investigación')
    # Borrar el campo coordinacion cuando los docentes actualicen.
    coordinacion = models.ForeignKey(Coordinacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Facultad')
    coordinaciones = models.ManyToManyField(Coordinacion, related_name='+', verbose_name=u'Facultades')
    grupoinvestigacion = models.ForeignKey(GrupoInvestigacion, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Grupo de investigación')
    industriapriorizada = models.ForeignKey(IndustriaPriorizada, on_delete=models.CASCADE, verbose_name=u'Área o industria priorizada')
    requiereconvenio = models.BooleanField(default=False, verbose_name=u'Requiere convenio')
    especificaconvenio = models.TextField(blank=True, null=True, verbose_name=u'Especificación del convenio')
    requierepermiso = models.BooleanField(default=False, verbose_name=u'La ejecución requiere de permisos de investigación')
    especificapermiso = models.TextField(blank=True, null=True, verbose_name=u'Especificación del permiso')
    tiempomes = models.IntegerField(default=0, verbose_name=u'Tiempo de duración en meses')
    compraequipo = models.IntegerField(choices=TIPO_EQUIPAMIENTO, blank=True, null=True, verbose_name=u'Contempla compra de equipamiento')
    montototal = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Monto total del financiamiento")
    montounemi = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Monto del financiamiento de Unemi")
    montootrafuente = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Monto del financiamiento de otras fuentes")
    presupuesto = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Monto presupuesto del proyecto")
    cumpleporcentajeequipo = models.IntegerField(choices=CUMPLE_PORCENTAJE_COMPRA_EQUIPO, default=1, verbose_name=u'Cumple con porcentaje de compra de equipos')
    tipocobertura = models.IntegerField(choices=TIPO_COBERTURA_EJECUCION, verbose_name=u'Tipo de cobertura de ejecución del proyecto')
    zonas = models.ManyToManyField(ZonaPlanificacion, verbose_name=u'Zonas para ejecucion tipo ZONAL')
    provincias = models.ManyToManyField(Provincia, verbose_name=u'Provincias para ejecucion tipo PROVINCIAL')
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='+', blank=True, null=True, verbose_name=u'Provincia para ejecucion tipo LOCAL')
    canton = models.ManyToManyField(Canton, verbose_name=u'Cantones para ejecucion tipo LOCAL')
    requiereparroquia = models.BooleanField(default=False, verbose_name=u'Ingresar nombre de parroquia')
    parroquia = models.TextField(blank=True, null=True, verbose_name=u'Nombre de la o las parroquias')
    resumenpropuesta = models.TextField(default='', verbose_name=u'Resumen de la propuesta')
    formulacionproblema = models.TextField(default='', verbose_name=u'Formulación del problema')
    objetivogeneral = models.TextField(default='', verbose_name=u'Objetivos generales')
    justificacion = models.TextField(default='', verbose_name=u'Justificación')
    estadoarte = models.TextField(default='', verbose_name=u'Estado del arte')
    metodologia = models.TextField(default='', verbose_name=u'Metodología')
    impactosocial = models.TextField(default='', verbose_name=u'Impacto social')
    impactocientifico = models.TextField(default='', verbose_name=u'Impacto científico')
    impactoeconomico = models.TextField(default='', verbose_name=u'Impacto económico')
    impactopolitico = models.TextField(default='', verbose_name=u'Impacto político')
    otroimpacto = models.TextField(default='', verbose_name=u'Otro impacto')
    archivoproyecto = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo del proyecto')
    documentogenerado = models.BooleanField(default=False, verbose_name=u'Documento único generado')
    archivodocumento = models.FileField(upload_to='proyectoinvestigacion/documentos', blank=True, null=True, verbose_name=u'Archivo del documento formulario generado')
    archivodocumentosindatint = models.FileField(upload_to='proyectoinvestigacion/documentos', blank=True, null=True, verbose_name=u'Archivo del documento formulario generado sin datos de los integrantes')
    archivodocumentofirmado = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo formulario de inscripción firmado')
    archivopresupuesto = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo del presupuesto final')
    estadodocumentofirmado = models.IntegerField(choices=ESTADO_ARCHIVO_EVIDENCIA, default=1, verbose_name=u'Estado formulario de inscripción firmado')
    observaciondocumentofirmado = models.TextField(default='', verbose_name=u'Observación de formulario de inscripción firmado')
    archivonovedad = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de novedades de verificaicón')
    archivoresolucionocas = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de resolución de Ocas')
    archivocontratoejecucion = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de contrato de ejecucion')
    tipo = models.IntegerField(choices=TIPO_PROYECTO, blank=True, null=True, verbose_name=u'Tipo de proyecto')
    fechaverirequi = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha verificación de requisitos')
    resolucionaprobacion = models.ForeignKey(ConvocatoriaResolucionAprobacionProyecto, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Resolucion de aprobación de ocas')
    fechaaprobacion = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha aprobación de proyecto')
    estadocronograma = models.IntegerField(choices=ESTADO_CRONOGRAMA, blank=True, null=True, verbose_name=u'Estado del cronograma')
    registrado = models.BooleanField(default=False, verbose_name=u'Registrado por docente')
    cambiomenor = models.BooleanField(default=False, verbose_name=u'Cambios menores solicitados')
    cambiomayor = models.BooleanField(default=False, verbose_name=u'Cambios mayores solicitados')
    verificado = models.IntegerField(choices=VALOR_SI_NO, blank=True, null=True, verbose_name=u'Verificado o Presenta novedad')
    aprobado = models.IntegerField(choices=VALOR_SI_NO, blank=True, null=True, verbose_name=u'Aprobado o descartado por ocas')
    ejecucion = models.IntegerField(choices=VALOR_SI_NO, blank=True, null=True, verbose_name=u'En ejecución o finalizado')
    cerrado = models.IntegerField(choices=VALOR_SI_NO, blank=True, null=True, verbose_name=u'Cerrado')
    puntajeevalint = models.IntegerField(default=0, verbose_name=u'Puntaje evaluación interna')
    puntajeevalext = models.IntegerField(default=0, verbose_name=u'Puntaje evaluación externa')
    verificainforme = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, related_name="+", blank=True, null=True, verbose_name=u"Persona verifica informes")
    apruebainforme = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, related_name="+", blank=True, null=True, verbose_name=u"Persona aprueba informes")
    archivoanulacion = models.FileField(upload_to='proyectoinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo anulación de proyecto')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    presupactualizado = models.BooleanField(default=False, verbose_name=u'Documento Presupuesto actualizado por Coordinación de Investigación')
    estado = models.ForeignKey("sagest.EstadoSolicitud", on_delete=models.CASCADE, default=1, verbose_name=u"Estado del registro")

    def __str__(self):
        return u'%s - %s - %s' % (self.categoria2.descripcion, self.profesor, self.titulo)

    class Meta:
        verbose_name = u"Proyecto de Investigación"
        verbose_name_plural = u"Proyectos de Investigación"

    def save(self, *args, **kwargs):
        self.parroquia = self.parroquia.strip().upper() if self.parroquia else ''
        super(ProyectoInvestigacion, self).save(*args, **kwargs)

    def monto_minimo_equipos(self):
        if self.compraequipo == 3:
            montominimoequipos = 0
        else:
            if self.compraequipo:
                regfin = ConvocatoriaMontoFinanciamiento.objects.get(convocatoria=self.convocatoria, tipoequipamiento=self.compraequipo)
            else:
                regfin = ConvocatoriaMontoFinanciamiento.objects.get(convocatoria=self.convocatoria, categoria=self.categoria2)

            montominimoequipos = Decimal(self.montounemi * (regfin.porcentajecompra) / 100).quantize(Decimal('.01'))

        return montominimoequipos

    def presupuesto_excede_montoproyecto(self):
        if self.presupuesto > 0:
            if self.montototal < self.presupuesto:
                dif = abs(self.montototal - self.presupuesto)
                if self.convocatoria.apertura.year < 2021:
                    return dif > 1000
                else:
                    return dif > 0.05
            else:
                return False
        return False

    def rol_participante(self, persona):
        participante = self.proyectoinvestigacionintegrante_set.filter(status=True, tiporegistro__in=[1, 3, 4], persona=persona)[0]
        datos = {"id": participante.funcion, "descripcion": participante.get_funcion_display()}
        return datos

    def integrantes_proyecto(self):
        return self.proyectoinvestigacionintegrante_set.filter(status=True, tiporegistro__in=[1, 3, 4]).order_by('funcion', 'persona__apellido1', 'persona__apellido2', 'persona__nombres')

    def integrantes_director_codirector(self):
        return self.integrantes_proyecto().filter(funcion__in=[1, 2])

    def integrantes_director_codirector_novedad(self):
        return self.integrantes_director_codirector().filter(estadoacreditado=3)

    def cantidad_integrantes_unemi(self):
        return self.integrantes_proyecto().filter(funcion__in=[1, 2, 3]).count()

    def cantidad_integrantes_externos(self):
        return self.integrantes_proyecto().filter(funcion=5).count()

    def integrantes_proyecto_informe(self):
        return self.proyectoinvestigacionintegrante_set.filter(status=True, tiporegistro__in=[1, 3, 4]).order_by('funcion', 'id')

    def integrantes_completos(self):
        convocatoria = self.convocatoria
        maximou = convocatoria.maxintegranteu
        maximoe = convocatoria.maxintegrantee
        registradosu = self.cantidad_integrantes_unemi()
        registradose = self.cantidad_integrantes_externos()
        return (registradosu + registradose) < (maximou + maximoe)

    def instituciones_proyecto(self):
        return self.proyectoinvestigacioninstitucion_set.filter(status=True).order_by('id')

    def nombre_director_proyecto(self):
        director = self.proyectoinvestigacionintegrante_set.filter(status=True, funcion=1)[0]
        return director.profesor.persona.nombre_completo()

    def nombre_director_proyecto_inverso(self):
        director = self.proyectoinvestigacionintegrante_set.filter(status=True, funcion=1)[0]
        return director.profesor.persona.nombre_completo_inverso()

    def prespuesto_asignado(self):
        return self.proyectoinvestigacionitempresupuesto_set.filter(status=True).exists()

    def presupuesto_asignado_equipos(self):
        return self.proyectoinvestigacionitempresupuesto_set.filter(status=True, tiporecurso__abreviatura='EQP').exists()

    def presupuesto_grupo_totales(self):
        return TipoRecursoPresupuesto.objects.values('id', 'descripcion').filter(proyectoinvestigacionitempresupuesto__proyecto=self, proyectoinvestigacionitempresupuesto__status=True).annotate(totalgrupo=Sum('proyectoinvestigacionitempresupuesto__valortotal')).order_by('orden', 'id')

    def presupuesto_detalle_tiporecurso(self, tiporecursoid):
        return self.proyectoinvestigacionitempresupuesto_set.filter(status=True, tiporecurso_id=tiporecursoid).order_by('id')

    def totales_detalle_tiporecurso(self, tiporecursoid):
        if self.proyectoinvestigacionitempresupuesto_set.values("id").filter(status=True, tiporecurso_id=tiporecursoid).exists():
            totales = self.proyectoinvestigacionitempresupuesto_set.values("tiporecurso_id").filter(status=True, tiporecurso_id=tiporecursoid).annotate(sumaitems=Sum('valortotal')).annotate(totalitems=Count('valortotal'))[0]
            return {"totalitems": totales["totalitems"], "totaldetalle": totales["sumaitems"]}
        else:
            return {"totalitems": 0, "totaldetalle": 0}

    def totales_detalle_equipos(self):
        if self.proyectoinvestigacionitempresupuesto_set.values("id").filter(status=True, tiporecurso__abreviatura='EQP').exists():
            totales = self.proyectoinvestigacionitempresupuesto_set.values("tiporecurso_id").filter(status=True, tiporecurso__abreviatura='EQP').annotate(sumaitems=Sum('valortotal')).annotate(totalitems=Count('valortotal'))[0]
            return {"totalitems": totales["totalitems"], "totaldetalle": totales["sumaitems"]}
        else:
            return {"totalitems": 0, "totaldetalle": 0}

    def total_general_detalle_presupuesto(self):
        if self.proyectoinvestigacionitempresupuesto_set.values("proyecto_id").filter(status=True).exists():
            totales = self.proyectoinvestigacionitempresupuesto_set.values("proyecto_id").filter(status=True).annotate(sumaitems=Sum('valortotal'))[0]
            return totales["sumaitems"]
        else:
            return 0

    def presupuesto_detallado(self):
        return self.proyectoinvestigacionitempresupuesto_set.filter(status=True).order_by('id')

    def cronograma_asignado(self):
        return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, objetivo__proyecto=self).exists()

    def cronograma_objetivo_totales(self):
        return self.proyectoinvestigacionobjetivo_set.values('id', 'descripcion').filter(status=True, proyectoinvestigacioncronogramaactividad__status=True).annotate(totalactividades=Count('proyectoinvestigacioncronogramaactividad__id')).annotate(
            totalponderacion=Sum('proyectoinvestigacioncronogramaactividad__ponderacion')).order_by('id')

    def cronograma_objetivo(self):
        return self.proyectoinvestigacionobjetivo_set.filter(status=True).order_by('id')

    def porcentaje_avance_ejecucion(self):
        return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, objetivo__proyecto=self).aggregate(totalejecutado=Sum('porcentajeejecucion'))['totalejecutado']

    def porcentaje_avance_esperado(self):
        return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, objetivo__proyecto=self, estado__in=[2, 3]).aggregate(totalesperado=Sum('ponderacion'))['totalesperado']

    def cronograma_detallado_objetivo(self, objetivoid):
        return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, objetivo_id=objetivoid, objetivo__proyecto=self).order_by('objetivo_id', 'id')

    def totales_detalle_objetivo(self, objetivoid):
        if ProyectoInvestigacionCronogramaActividad.objects.values("id").filter(status=True, objetivo_id=objetivoid, objetivo__proyecto=self).exists():
            totales = ProyectoInvestigacionCronogramaActividad.objects.values("objetivo_id").filter(status=True, objetivo_id=objetivoid, objetivo__proyecto=self).annotate(totalponderacion=Sum('ponderacion')).annotate(totalactividades=Count('id'))[0]
            return {"totalactividades": totales["totalactividades"], "totalponderacion": totales["totalponderacion"]}
        else:
            return {"totalactividades": 0, "totalponderacion": 0}

    def cronograma_detallado_objetivo_ejecucion_finalizada(self, objetivoid):
        return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, estado__in=[2, 3], objetivo_id=objetivoid, objetivo__proyecto=self).order_by('objetivo_id', 'id')

    def cronograma_detallado(self):
        return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, objetivo__proyecto=self).order_by('objetivo_id', 'id')

    def puede_generar_documento(self):
        if self.estado.valor in [1, 28, 29, 40, 41]:
            ponderacion = self.total_ponderacion_actividades()
            dif = abs(self.montototal - self.presupuesto)
            mesesactividades = self.total_meses_actividades()
            difmeses = self.tiempomes - mesesactividades if self.tiempomes >= mesesactividades else 0
            cantidadintegrantes = self.cantidad_integrantes_unemi()

            # if ponderacion != 100 or dif > 0.05 or mesesactividades < self.tiempomes or cantidadintegrantes < self.convocatoria.minintegranteu or not self.archivopresupuesto:
            # if ponderacion != 100 or dif > 0.05 or mesesactividades < self.tiempomes or cantidadintegrantes < self.convocatoria.minintegranteu:
            if ponderacion != 100 or dif > 0.05 or difmeses > 1 or cantidadintegrantes < self.convocatoria.minintegranteu:
                return False
            elif self.integrantes_director_codirector_novedad():
                return False
            else:
                return True
        else:
            return False

    def puede_subir_documento(self):
        return self.estado.valor in [1, 28, 29, 40, 41]

    def advertencias_generar_documento(self):
        advertencias = []

        ponderacion = self.total_ponderacion_actividades()
        dif = abs(self.montototal - self.presupuesto)
        mesesactividades = self.total_meses_actividades()
        cantidadintegrantes = self.cantidad_integrantes_unemi()
        novedaddircor = self.integrantes_director_codirector_novedad()

        if cantidadintegrantes < self.convocatoria.minintegranteu:
            msg = {"mensaje": "La cantidad de integrantes UNEMI requerida para el proyecto es <strong>%s</strong> y usted tiene registrado <strong>%s</strong>" % (self.convocatoria.minintegranteu, cantidadintegrantes)}
            advertencias.append(msg)
        if self.montototal != self.presupuesto:
            msg = {"mensaje": "El valor del monto de financiamiento del proyecto debe ser igual al total del presupuesto. Monto Financiamiento: <strong>%s</strong>, Total Presupuesto: <strong>%s</strong>" % (self.montototal, self.presupuesto)}
            advertencias.append(msg)
        if ponderacion != 100:
            msg = {"mensaje": "El porcentaje de ponderación del cronograma de actividades del proyecto debe ser <strong>100.00 %</strong>, usted tiene registrado <strong>" + str(ponderacion) + " %</strong>"}
            advertencias.append(msg)
        if mesesactividades < self.tiempomes:
            if self.tiempomes - mesesactividades > 1:
                msg = {"mensaje": "La cantidad de meses acumulada del cronograma de actividades del proyecto debe ser igual al tiempo de ejecución registrado. Cantidad meses cronograma: <strong>%s</strong>, Tiempo de ejecución registrado: <strong>%s</strong>" % (mesesactividades, self.tiempomes)}
                advertencias.append(msg)
        if novedaddircor:
            msg = {"mensaje": "Existen novedades con los registros de los integrantes <strong>DIRECTOR / CO-DIRECTOR</strong>"}
            advertencias.append(msg)

        return advertencias

    def presupuesto_completo(self):
        dif = abs(self.montototal - self.presupuesto)
        if self.convocatoria.apertura.year < 2021:
            return dif <= 1000
            # if dif <= 1000:
            #     return True
            # else:
            #     return False
        else:
            return dif <= 0.05
            # if dif <= 0.05:
            #     return True
            # else:
            #     return False

    def total_meses_actividades(self):
        fechainiciomin = None
        fechafinmax = None

        for actividad in self.cronograma_detallado():
            if fechainiciomin is None:
                fechainiciomin = actividad.fechainicio

            if fechafinmax is None:
                fechafinmax = actividad.fechafin

            if actividad.fechainicio < fechainiciomin:
                fechainiciomin = actividad.fechainicio

            if actividad.fechafin > fechafinmax:
                fechafinmax = actividad.fechafin

        mesesactividad = diff_month(fechainiciomin, fechafinmax)
        return mesesactividad

    def total_ponderacion_actividades(self):
        if ProyectoInvestigacionCronogramaActividad.objects.values("id").filter(status=True, objetivo__proyecto=self).exists():
            return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, objetivo__proyecto=self).aggregate(totalponderacion=Sum('ponderacion'))['totalponderacion']
        else:
            return 0

    def valores_avance(self):
        if self.proyectoinvestigacioninforme_set.values("id").filter(status=True, estado=10).exists():
            cumplimiento = self.proyectoinvestigacioninforme_set.filter(status=True, estado=10).order_by('-id')[0].porcentajeejecucion
            return {"cumplimiento": cumplimiento, "porcumplir": 100 - cumplimiento}
        else:
            return {"cumplimiento": 0, "porcumplir": 100}

    def resultados_compromisos(self):
        return self.proyectoinvestigacionresultado_set.filter(status=True).order_by('id')

    def objetivos_especificos(self):
        return self.proyectoinvestigacionobjetivo_set.filter(status=True).order_by('id')

    def cronograma_actividades(self):
        return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, objetivo__proyecto=self).order_by('id')

    def cronograma_actividades_pendientes(self):
        return ProyectoInvestigacionCronogramaActividad.objects.filter(status=True, estado__in=[1, 2, 4], objetivo__proyecto=self).order_by('fechainicio', 'fechafin')

    def entregables_actividades_completos(self):
        completos = True
        for actividad in self.cronograma_actividades():
            if not actividad.entregable and not actividad.lista_entregables():
                completos = False
                break

        return completos

    def referencias_bibliograficas(self):
        return self.proyectoinvestigacionreferenciabibliografica_set.filter(status=True).order_by('id')

    def puede_editar(self):
        return self.estado.valor in [1, 4, 15, 28, 38, 40]

    def puede_verificar(self):
        if self.estado.valor in [2, 3, 4, 5]:
            # actual = datetime.strptime('2022-08-19 23:00:00', '%Y-%m-%d %H:%M:%S')
            # if diff_hours(self.fecha_modificacion, actual) < 24:
            # if diff_hours(self.fecha_modificacion, datetime.now()) > 12: #24
            return True
            # else:
            #     return False
        else:
            return False

    def puede_asignar_evaluadores(self):
        # return self.estado.valor not in [1, 2, 4, 5] and self.convocatoria.total_valoracion_rubricas() == 100 and self.convocatoria.minimoaprobacion > 0 and self.puntajeevalint == 0 and self.puntajeevalext == 0
        return self.estado.valor not in [1, 2, 4, 5] and self.convocatoria.total_valoracion_rubricas() == 100 and self.convocatoria.minimoaprobacion > 0  # and self.puntajeevalint == 0 and self.puntajeevalext == 0

    def puede_evaluar_interna(self):
        return self.estado.valor in [6, 7, 9] and self.tiene_asignado_evaluadores_propuesta_proyecto() and self.convocatoria.apertura.year < 2022

    def tiene_asignado_evaluadores_propuesta_proyecto(self):
        return self.proyectoinvestigacionevaluador_set.values('id').filter(status=True, tipo=1, tipoproyecto=1).exists() and self.proyectoinvestigacionevaluador_set.values('id').filter(status=True, tipo=2, tipoproyecto=1).exists()

    def puede_evaluar_externa(self):
        return self.estado.valor in [8, 10, 12, 33, 35, 37]

    def puede_revisar_evaluacion(self):
        return self.evaluacionproyecto_set.values('id').filter(status=True, tipo=1).exists() and self.evaluacionproyecto_set.values('id').filter(status=True, tipo=2).exists()

    def tiene_evaluaciones(self):
        return self.evaluacionproyecto_set.values('id').filter(status=True).exists()

    def tiene_evaluaciones_cerradas(self):
        return self.evaluacionproyecto_set.values('id').filter(status=True, estadoregistro=5).exists()

    def falta_cerrar_evaluaciones(self):
        if self.convocatoria.apertura.year >= 2022:
            if self.tiene_evaluaciones():
                evaluaciones = self.evaluaciones()
                return evaluaciones.values("id").filter(estadoregistro=2).exists()
            else:
                return False
        else:
            return False

    def faltan_archivos_evaluacion(self):
        if self.convocatoria.apertura.year < 2022:
            if self.tiene_evaluaciones():
                evaluaciones = self.evaluaciones()
                x = evaluaciones.values("id").count()
                y = evaluaciones.values("id").filter(~Q(archivoevaluacion='')).count()
                return evaluaciones.count() != evaluaciones.filter(~Q(archivoevaluacion='')).count()
            else:
                return False
        else:
            return False

    def evaluaciones_internas_completas(self):
        if self.evaluacionproyecto_set.filter(status=True, tipo=1).count() > 0:
            if not self.proyectoinvestigacionrecorrido_set.filter(status=True, estado__valor=8).exists():
                return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=False, estadoregistro=2).count() == self.evaluadores_internos().filter(reevaluacion=False).count()
            else:
                return True
        return False

    def evaluacion_interna_encurso(self):
        if self.estado.valor == 9:
            return True
        else:
            return self.estado.valor == 7 and not self.evaluaciones_internas_completas_cerradas()

    def evaluaciones_internas_completas_cerradas(self):
        if self.evaluacionproyecto_set.filter(status=True, tipo=1).count() > 0:
            if not self.proyectoinvestigacionrecorrido_set.filter(status=True, estado__valor=8).exists():
                return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=False, estadoregistro=5).count() == self.evaluadores_internos().filter(reevaluacion=False).count()
            else:
                return True
        return False

    def reevaluaciones_internas_completas_cerradas(self):
        if self.evaluacionproyecto_set.filter(status=True, tipo=1).count() > 0:
            if not self.proyectoinvestigacionrecorrido_set.filter(status=True, estado__valor=8).exists():
                return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True, estadoregistro=5).count() == self.evaluadores_internos().filter(reevaluacion=True).count()
            else:
                return True
        return False

    def requiere_evaluacion_interna_adicional(self):
        return self.estado.valor == 9
        # if self.evaluacionproyecto_set.filter(status=True, tipo=1).count() > 0:
        #     return self.evaluacionproyecto_set.filter(status=True, tipo=1, estado=3).exists()
        # return False

    def evaluaciones_externas_completas(self):
        if self.evaluacionproyecto_set.filter(status=True, tipo=2).count() > 0:
            if not self.proyectoinvestigacionrecorrido_set.filter(status=True, estado__valor=11).exists():
                return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=False).count() == self.evaluadores_externos().count()
            else:
                return True
        return False

    def evaluaciones_externas_completas_cerradas(self):
        if self.evaluacionproyecto_set.filter(status=True, tipo=2).count() > 0:
            if not self.proyectoinvestigacionrecorrido_set.filter(status=True, estado__valor=11).exists():
                return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=False, estadoregistro=5).count() == self.evaluadores_externos().filter(reevaluacion=False).count()
            else:
                return True
        return False

    def reevaluaciones_externas_completas_cerradas(self):
        if self.evaluacionproyecto_set.filter(status=True, tipo=2).count() > 0:
            if not self.proyectoinvestigacionrecorrido_set.filter(status=True, estado__valor=13).exists():
                return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True, estadoregistro=5).count() == self.evaluadores_externos().filter(reevaluacion=True).count()
            else:
                return True
        return False

    def requiere_evaluacion_externa_adicional(self):
        return self.estado.valor == 12
        # if self.evaluacionproyecto_set.filter(status=True, tipo=1).count() > 0:
        #     return self.evaluacionproyecto_set.filter(status=True, tipo=2, estado=3).exists()
        # return False

    def evaluaciones(self):
        return self.evaluacionproyecto_set.filter(status=True).order_by('tipo', 'fecha_creacion')

    def evaluaciones_internas(self):
        return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=False).order_by('tipo', 'fecha_creacion')

    def evaluaciones_internas_correo(self):
        if not self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).exists():
            return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=False).order_by('id')
        elif self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).count() == 3:
            return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).order_by('-id')[:1]
        else:
            return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).order_by('id')

    def evaluacion_interna_adicional(self):
        return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).order_by('tipo', 'fecha_creacion')

    def evaluacion_interna_adicional_2(self):
        return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).order_by('-id')[0]

    def evaluaciones_externas(self):
        return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=False).order_by('tipo', 'fecha_creacion')

    def evaluacion_externa_adicional(self):
        return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).order_by('tipo', 'fecha_creacion')

    def evaluacion_externa_adicional_2(self):
        return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).order_by('-id')[0]

    def evaluaciones_externas_correo(self):
        if not self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).exists():
            return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=False).order_by('id')
        elif self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).count() == 3:
            return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).order_by('-id')[:1]
        else:
            return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).order_by('id')

    def puntaje_final_evaluacion_interna(self):
        # Si no hay reevaluaciones internas
        if not self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).exists():
            return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=False).order_by('-puntajetotal')[0].puntajetotal
        else:
            # Si existen 3 reevaluaciones, selecciono la nota del último registro
            if self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).count() == 3:
                return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).order_by('-id')[0].puntajetotal
            else:
                return self.evaluacionproyecto_set.filter(status=True, tipo=1, adicional=True).order_by('-puntajetotal')[0].puntajetotal

    def puntaje_final_evaluacion_externa(self):
        # Si no hay reevaluaciones internas
        if not self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).exists():
            return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=False).order_by('-puntajetotal')[0].puntajetotal
        else:
            # Si existen 3 reevaluaciones, selecciono la nota del último registro
            if self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).count() == 3:
                return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).order_by('-id')[0].puntajetotal
            else:
                return self.evaluacionproyecto_set.filter(status=True, tipo=2, adicional=True).order_by('-puntajetotal')[0].puntajetotal

    def puede_actualizar_presupuesto(self):
        return self.estado.valor == 13 and self.convocatoria.apertura.year == 2022

    def puede_generar_documento_investigacion(self):
        if self.convocatoria.apertura.year >= 2023:
            return self.estado.valor == 13
        elif self.convocatoria.apertura.year == 2022:
            if self.profesor:
                return self.presupactualizado or not self.documentogenerado
            else:
                return False
        else:
            return False

    def puede_subir_documento_investigacion(self):
        if self.presupactualizado:
            return self.presupactualizado and self.documentogenerado
        else:
            return self.documentogenerado

    def puede_aprobar(self):
        if self.convocatoria.tiene_resolucion_aprobacion():
            if not self.presupactualizado:
                return self.estado.valor in [13, 18, 19]
            else:
                return self.estado.valor in [13, 18, 19] and self.documentogenerado is True and self.archivodocumentofirmado.name != ''
        else:
            return False

    def puede_ver_evidencias(self):
        return self.estado.valor == 20

    def tiene_evidencias_subidas(self):
        return ProyectoInvestigacionActividadEvidencia.objects.values('id').filter(status=True, entregable__actividad__objetivo__proyecto=self).exists()

    def tiene_conflicto_fecha_cronograma(self):
        return self.cronograma_detallado().values('id').filter(fechainicio__lt=self.fechainicio).exists()

    def tiene_conflicto_fechas_iniciofin_actividades(self):
        return self.cronograma_detallado().values('id').filter(fechainicio__gt=F('fechafin')).exists()

    def evaluadores_internos(self):
        return self.proyectoinvestigacionevaluador_set.filter(status=True, tipo=1, tipoproyecto=1).order_by('id')

    def evaluadores_externos(self):
        return self.proyectoinvestigacionevaluador_set.filter(status=True, tipo=2, tipoproyecto=1).order_by('id')

    def evaluadores_internos_porevaluar(self):
        return self.proyectoinvestigacionevaluador_set.filter(status=True, tipo=1, tipoproyecto=1, evaluacionproyecto__isnull=True).order_by('id')

    def evaluadores_internos_evaluaron(self):
        return self.proyectoinvestigacionevaluador_set.filter(status=True, tipo=1, tipoproyecto=1, evaluacionproyecto__isnull=False).order_by('id')

    def evaluadores_externos_porevaluar(self):
        return self.proyectoinvestigacionevaluador_set.filter(status=True, tipo=2, tipoproyecto=1, evaluacionproyecto__isnull=True).order_by('id')

    def evaluadores_externos_evaluaron(self):
        return self.proyectoinvestigacionevaluador_set.filter(status=True, tipo=2, tipoproyecto=1, evaluacionproyecto__isnull=False).order_by('id')

    def evaluadores_proyecto_finalizado(self):
        return self.proyectoinvestigacionevaluador_set.filter(status=True, tipo=1, tipoproyecto=2).order_by('id')

    def secuencia_informe_avance(self):
        reg = self.proyectoinvestigacioninforme_set.filter(status=True).aggregate(secuencia=Max('secuencia') + 1)
        if reg['secuencia'] is None:
            secuencia = 1
        else:
            secuencia = reg['secuencia']
        return secuencia

    def informes_tecnicos(self):
        if self.convocatoria.apertura.year > 2020:
            return self.proyectoinvestigacioninforme_set.filter(status=True).order_by('id')
        else:
            return self.proyectoinvestigacioninforme_set.filter(status=True, tipo=2).order_by('id')

    def total_informes(self):
        return self.informes_tecnicos().count()

    def puede_asignar_revisor_informes(self, persona):
        if self.estado.valor == 20:
            if persona.es_coordinador_investigacion():
                return True
            elif persona.id == 126172:
                return True
            else:
                return False
        else:
            return False

    def cronograma_objetivo_enejecucion_finalizada(self):
        return self.proyectoinvestigacionobjetivo_set.filter(status=True, proyectoinvestigacioncronogramaactividad__status=True, proyectoinvestigacioncronogramaactividad__estado__in=[2, 3]).distinct().order_by('id')

    def evidencias_subidas_validadas(self):
        return ProyectoInvestigacionActividadEvidencia.objects.filter(status=True, estado=2, entregable__actividad__objetivo__proyecto=self).order_by('fecha_creacion')

    def cantidad_evidencias_subidas_validadas(self):
        return self.evidencias_subidas_validadas().count()

    def evaluaciones_proyectofinalizado_completas(self):
        return False

    def tiene_asignado_evaluadores_proyecto_finalizado(self):
        return self.proyectoinvestigacionevaluador_set.values('id').filter(status=True, tipo=1, tipoproyecto=2).exists()

    def evaluacion_proyecto_finalizado_evaluador(self, persona):
        return None

    def evaluacion_propuesta_proyecto(self, persona, tipoevaluacion, reevaluacion):
        if self.evaluacionproyecto_set.values("id").filter(status=True, tipo=tipoevaluacion, evaluador__persona=persona, adicional=reevaluacion).exists():
            return self.evaluacionproyecto_set.filter(status=True, tipo=tipoevaluacion, evaluador__persona=persona, adicional=reevaluacion)[0]
        return None

    def puede_agregar_informe(self):
        if self.convocatoria.apertura.year > 2020:
            if ProyectoInvestigacionInforme.objects.values("id").filter(status=True, proyecto=self, estado__in=[1, 2, 3, 5, 6, 8]).exists():
                return False
            else:
                return not ProyectoInvestigacionInforme.objects.values("id").filter(status=True, proyecto=self, estado=7, archivo='').exists()
        else:
            if ProyectoInvestigacionInforme.objects.values("id").filter(status=True, proyecto=self, tipo=2, estado__in=[1, 2, 3, 5, 6, 8]).exists():
                return False
            else:
                return not ProyectoInvestigacionInforme.objects.values("id").filter(status=True, proyecto=self, tipo=2, estado=7, archivo='').exists()

    def puede_agregar_informe_director(self):
        return not ProyectoInvestigacionInforme.objects.values("id").filter(status=True, proyecto=self, aprobado=False).exists()

    def novedades_evaluaciones(self):
        if self.estado.valor == 7:
            if self.evaluaciones_internas_completas():
                # Obtengo los estados asignados en cada evaluación
                estados = [evaluacion.estado for evaluacion in self.evaluaciones_internas() if evaluacion.estadoregistro in [2, 5, 6]]
                # if self.estado.valor != 9:
                #     estados = [evaluacion.estado for evaluacion in self.evaluaciones_internas() if evaluacion.estadoregistro in [2, 5, 6]]
                # else:
                #     estados = [evaluacion.estado for evaluacion in self.evaluacion_interna_adicional() if evaluacion.estadoregistro in [2, 5, 6]]

                # Verifico si hay un estado diferente: si los estados son iguales la longitud del conjunto debe ser 1
                iguales = len(set(estados)) == 1

                evaluaciones = self.evaluaciones_internas()

                if iguales:
                    # Si tiene estado MODIFICACIONES MAYORES
                    if evaluaciones.values('id').filter(estado=3):
                        return {"novedad": True, "mensaje": "Los resultados de las evaluaciones internas son DEBE SER PRESENTADO NUEVAMENTE LUEGO DE MODIFICACIONES MAYORES por lo que es necesario una EVALUACIÓN INTERNA ADICIONAL"}
                    else:
                        return {"novedad": False}
                else:
                    # evaluaciones = self.evaluaciones_internas()
                    if evaluaciones.values('id').filter(estado=1) and evaluaciones.values('id').filter(estado=2):
                        return {"novedad": False}
                    else:
                        return {"novedad": True, "mensaje": "Los resultados de las evaluaciones internas son diferentes por lo que es necesario una EVALUACIÓN INTERNA ADICIONAL"}
            else:
                return {"novedad": False}
        elif self.estado.valor == 32:
            if self.reevaluaciones_internas_completas_cerradas():
                # Obtengo los estados asignados en cada evaluación
                estados = [evaluacion.estado for evaluacion in self.evaluacion_interna_adicional() if evaluacion.estadoregistro in [2, 5, 6]]
                # if self.estado.valor != 9:
                #     estados = [evaluacion.estado for evaluacion in self.evaluaciones_internas() if evaluacion.estadoregistro in [2, 5, 6]]
                # else:
                #     estados = [evaluacion.estado for evaluacion in self.evaluacion_interna_adicional() if evaluacion.estadoregistro in [2, 5, 6]]

                # Verifico si hay un estado diferente: si los estados son iguales la longitud del conjunto debe ser 1
                iguales = len(set(estados)) == 1

                if iguales:
                    return {"novedad": False}
                else:
                    evaluaciones = self.evaluacion_interna_adicional()
                    if evaluaciones.values('id').filter(estado=1) and evaluaciones.values('id').filter(estado=2):
                        return {"novedad": False}
                    else:
                        return {"novedad": True, "mensaje": "Los resultados de las evaluaciones internas son diferentes por lo que es necesario una EVALUACIÓN INTERNA ADICIONAL"}
            else:
                return {"novedad": False}
        else:
            return {"novedad": False}

    def puede_subir_archivo_presupuesto(self):
        # return self.estado.valor in [1, 15, 16, 28, 29]
        return self.estado.valor in [1, 15, 16, 28, 29, 38, 39, 40, 41, 42, 43]

    def formulario_inscripcion_anterior(self):
        return self.proyectoinvestigacionhistorialarchivo_set.filter(status=True, tipo=11).order_by('-id')[0]

    def puede_editar_cronograma(self):
        if self.estado.valor in [1, 4, 15, 16, 28, 29, 38, 39, 40, 41]:
            return True
        elif self.estado.valor == 18 and self.estadocronograma in [1, 4]:
            return True
        else:
            return False

    def color_estado_cronograma(self):
        if self.estadocronograma == 1:
            return 'warning'
        elif self.estadocronograma == 2:
            return 'info'
        elif self.estadocronograma == 3:
            return 'success'
        else:
            return 'important'

    def fase_aprobacion_superada(self):
        return self.estado.valor in [20, 21]

    def contempla_compra_equipos(self):
        return self.proyectoinvestigacionitempresupuesto_set.values("id").filter(status=True, tiporecurso__abreviatura='EQP').exists()


class ProyectoInvestigacionRecorrido(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    fecha = models.DateField(verbose_name=u'Fecha')
    observacion = models.TextField(verbose_name=u'Observación del recorrido')
    estado = models.ForeignKey("sagest.EstadoSolicitud", on_delete=models.CASCADE, verbose_name=u"Estado de la solicitud")

    def __str__(self):
        return u'%s - %s - %s' % (self.proyecto, self.fecha, self.estado.descripcion)

    class Meta:
        verbose_name = u"Proyecto de Investigación Recorrido"
        verbose_name_plural = u"Proyectos de Investigación Recorrido"


class ProyectoInvestigacionHistorialArchivo(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    tipo = models.IntegerField(choices=TIPO_ARCHIVO, verbose_name=u'Tipo de archivo')
    archivo = models.CharField(max_length=250, verbose_name=u'Nombre del archivo')

    def __str__(self):
        return u'%s - %s - %s' % (self.proyecto, self.tipo, self.archivo)

    class Meta:
        verbose_name = u"Proyecto de Investigación Historial archivo"
        verbose_name_plural = u"Proyectos de Investigación historial archivos"


class ProyectoInvestigacionInstitucion(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    tipo = models.IntegerField(choices=TIPO_INSTITUCION_PARTICIPANTE, verbose_name=u'Tipo de institución participante')
    nombre = models.CharField(max_length=250, verbose_name=u'Nombre de la institución')
    representante = models.CharField(max_length=250, verbose_name=u'Nombres y Apellidos del representante legal')
    cedula = models.CharField(max_length=20, verbose_name=u'Identificación del representante legal')
    telefono = models.CharField(default='', max_length=100, verbose_name=u'Número de teléfono/celular')
    fax = models.CharField(default='', max_length=100, verbose_name=u'Número de fax')
    email = models.CharField(default='', max_length=100, verbose_name=u'Dirección de e-mail')
    direccion = models.CharField(default='', max_length=250, verbose_name=u'Dirección de domicilio')
    paginaweb = models.CharField(default='', max_length=100, verbose_name=u'Página web')

    def __str__(self):
        return u'%s - %s - %s' % (self.proyecto, self.get_tipo_display(), self.representante)

    class Meta:
        verbose_name = u"Institución Participante del proyecto"
        verbose_name_plural = u"Instituciones Participantes del proyecto"

    def save(self, *args, **kwargs):
        self.representante = self.representante.strip().upper()
        self.email = self.email.strip().lower()
        self.direccion = self.direccion.strip().upper()
        self.paginaweb = self.paginaweb.strip().lower()
        self.nombre = self.nombre.strip().upper()
        super(ProyectoInvestigacionInstitucion, self).save(*args, **kwargs)


class ProyectoInvestigacionObjetivo(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    numero = models.IntegerField(blank=True, null=True, verbose_name=u'Número de objetivo')
    descripcion = models.TextField(default='', verbose_name=u'Descripción del objetivo')
    estadocumplimiento = models.IntegerField(choices=ESTADO_CUMPLIMIENTO_OBJETIVO, verbose_name=u'Estado de cumplimiento')

    def __str__(self):
        return '%s - %s' % (self.proyecto, self.descripcion)

    class Meta:
        verbose_name = u"Objetivo específico del proyecto"
        verbose_name_plural = u"Objetivos específicos del proyecto"

    def save(self, *args, **kwargs):
        super(ProyectoInvestigacionObjetivo, self).save(*args, **kwargs)

    def tiene_cronograma_actividades(self):
        return self.proyectoinvestigacioncronogramaactividad_set.filter(status=True).exists()

    def cronograma_actividades(self):
        return self.proyectoinvestigacioncronogramaactividad_set.filter(status=True).order_by('id')

    def total_actividades(self):
        return self.proyectoinvestigacioncronogramaactividad_set.filter(status=True).aggregate(totalactividades=Count('id'))['totalactividades']

    def total_ponderaciones(self):
        return self.proyectoinvestigacioncronogramaactividad_set.filter(status=True).aggregate(totalponderacion=Sum('ponderacion'))['totalponderacion']

    def cronograma_actividades_ejecucion_finalizada(self):
        return self.proyectoinvestigacioncronogramaactividad_set.filter(status=True, estado__in=[2, 3]).order_by('id')


class ProyectoInvestigacionResultado(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    resultado = models.ForeignKey(TipoResultadoCompromiso, on_delete=models.CASCADE, verbose_name=u'Tipo de Resultado o compromiso')
    marcado = models.BooleanField(default=False, verbose_name=u'Marcado')

    def __str__(self):
        return '%s - %s' % (self.proyecto, self.resultado.descripcion)

    class Meta:
        verbose_name = u"Resultado o Compromiso del proyecto"
        verbose_name_plural = u"Resultados o compromisos del proyecto"

    def save(self, *args, **kwargs):
        super(ProyectoInvestigacionResultado, self).save(*args, **kwargs)


class ProyectoInvestigacionReferenciaBibliografica(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    descripcion = models.TextField(default='', verbose_name=u'Descripción de la referencia')

    def __str__(self):
        return '%s - %s' % (self.proyecto, self.descripcion)

    class Meta:
        verbose_name = u"Referencia bibliográfica del proyecto"
        verbose_name_plural = u"Referencias bibliográficas del proyecto"

    def save(self, *args, **kwargs):
        super(ProyectoInvestigacionReferenciaBibliografica, self).save(*args, **kwargs)


class ProyectoInvestigacionIntegrante(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    tipo = models.IntegerField(choices=TIPO_INTEGRANTE, verbose_name=u'Tipo de integrante')
    funcion = models.IntegerField(choices=FUNCION_INTEGRANTE, verbose_name=u'Función del integrante')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Persona')
    profesor = models.ForeignKey("sga.Profesor", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Profesor')
    inscripcion = models.ForeignKey("sga.Inscripcion", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Alumno')
    administrativo = models.ForeignKey("sga.Administrativo", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Administrativo')
    externo = models.ForeignKey("sga.Externo", blank=True, on_delete=models.CASCADE, null=True, verbose_name=u'Externo')
    tiporegistro = models.IntegerField(choices=TIPO_REGISTRO_INTEGRANTE, default=1, verbose_name=u'Tipo de registro')
    personareemplazo = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, related_name="+", blank=True, null=True, verbose_name=u'Persona quién le reemplaza')
    archivo = models.FileField(upload_to='soporteintegrante/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de soporte')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    estadoacreditado = models.IntegerField(choices=ESTADO_INVESTIGADOR_ACREDITADO, default=1, verbose_name=u'Estado de investigador acreditado')
    archivoacreditado = models.FileField(upload_to='investigadoracreditado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de soporte de investigador acreditado')

    def __str__(self):
        return u'%s - %s' % (self.persona, self.get_funcion_display())

    class Meta:
        verbose_name = u"Integrante del proyecto"
        verbose_name_plural = u"Integrantes del proyecto"

    def save(self, *args, **kwargs):
        super(ProyectoInvestigacionIntegrante, self).save(*args, **kwargs)

    def puede_eliminar(self, proyecto):
        asignadocronograma = ProyectoInvestigacionCronogramaResponsable.objects.values("id").filter(status=True, persona=self.persona, actividad__objetivo__proyecto=proyecto).exists()
        asignadopasaje = ProyectoInvestigacionPasajeIntegrante.objects.values("id").filter(status=True, persona=self.persona, proyecto=proyecto).exists()
        if asignadocronograma is False and asignadopasaje is False:
            return True
        else:
            return False

    def datos_integrante(self):
        return None
        # if self.tipo == 1:
        #     return self.profesor
        # elif self.tipo == 2:
        #     return self.inscripcion
        # elif self.tipo == 3:
        #     return self.administrativo
        # else:
        #     return self.externo

    def formacion_academica(self):
        return self.persona.titulacion_set.filter(status=True, titulo__nivel__rango__in=[5, 6]).order_by('-fechaobtencion', '-titulo__nivel__rango')

    def experiencia_laboral(self):
        return self.persona.mis_experienciaslaborales().filter(status=True).order_by('-fechafin', '-fechainicio')

    def experiencia_laboral_unemi(self):
        lista_cargos = []
        cargos = self.persona.distributivopersonahistorial_set.values('denominacionpuesto_id').filter(status=True).distinct()
        for cargo in cargos:
            c = self.persona.distributivopersonahistorial_set.filter(status=True, denominacionpuesto_id=cargo['denominacionpuesto_id']).order_by('fecha_creacion')[0]
            datocargo = {"cargo": c.denominacionpuesto.descripcion,
                         "fechainicio": c.fecha_creacion}
            lista_cargos.append(datocargo)

        ordenados = sorted(lista_cargos, key=lambda dato: dato['fechainicio'], reverse=True)

        return ordenados

    def articulos_publicados(self):
        persona = self.persona
        articulos = ArticuloInvestigacion.objects.select_related().filter((Q(participantesarticulos__profesor__persona=persona) | Q(participantesarticulos__administrativo__persona=persona)), status=True, aprobado=True, participantesarticulos__status=True).order_by('-fechapublicacion')
        return articulos

    def articulos_publicados_persona_externa(self):
        articulos = ArticuloPersonaExterna.objects.filter(status=True, externo=self.externo).order_by('-fechapublicacion')
        return articulos

    def ponencias_publicadas(self):
        persona = self.persona
        ponencias = PonenciasInvestigacion.objects.select_related().filter((Q(participanteponencias__profesor__persona=persona) | Q(participanteponencias__administrativo__persona=persona)), status=True, participanteponencias__status=True).order_by('-fechapublicacion')
        return ponencias

    def ponencias_publicadas_persona_externa(self):
        ponencias = PonenciaPersonaExterna.objects.filter(status=True, externo=self.externo).order_by('-fechafin', '-fechainicio')
        return ponencias

    def libros_publicados(self):
        persona = self.persona
        libros = LibroInvestigacion.objects.select_related().filter((Q(participantelibros__profesor__persona=persona) | Q(participantelibros__profesor__persona=persona)), status=True, participantelibros__status=True).order_by('-fechapublicacion')
        return libros

    def libros_publicados_persona_externa(self):
        libros = LibroPersonaExterna.objects.filter(status=True, externo=self.externo, tipo=1).order_by('-fechapublicacion')
        return libros

    def capitulos_libro_publicados(self):
        persona = self.persona
        capitulos = CapituloLibroInvestigacion.objects.select_related().filter((Q(participantecapitulolibros__profesor__persona=persona) | Q(participantecapitulolibros__profesor__persona=persona)), status=True, participantecapitulolibros__status=True).order_by('-fechapublicacion')
        return capitulos

    def capitulos_libro_publicados_persona_externa(self):
        capitulos = LibroPersonaExterna.objects.filter(status=True, externo=self.externo, tipo=2).order_by('-fechapublicacion')
        return capitulos

    def proyectos_investigacion_unemi(self):
        # integrante = self.datos_integrante()
        # persona = integrante.persona

        if self.tipo == 1:
            proyectosunemi = ParticipantesMatrices.objects.filter(status=True, profesor=self.profesor, proyecto__tipo=2, matrizevidencia_id=2, proyecto__status=True)
        elif self.tipo == 2:
            proyectosunemi = ParticipantesMatrices.objects.filter(status=True, inscripcion=self.inscripcion, proyecto__tipo=2, matrizevidencia_id=2, proyecto__status=True)
        elif self.tipo == 3:
            proyectosunemi = ParticipantesMatrices.objects.filter(status=True, administrativo=self.administrativo, proyecto__tipo=2, matrizevidencia_id=2, proyecto__status=True)
        else:
            proyectosunemi = None

        return proyectosunemi

    def proyectos_investigacion_externo(self):
        persona = self.persona
        proyectosexternos = ProyectoInvestigacionExterno.objects.filter(persona=persona, status=True)
        return proyectosexternos

    def proyectos_investigacion_persona_externa(self):
        proyectos = ProyectoInvestigacionPersonaExterna.objects.filter(status=True, externo=self.externo).order_by('-fechafin', '-fechainicio')
        return proyectos

    def tiene_formacion_academica(self):
        formacion = self.formacion_academica()
        if formacion:
            return True
        else:
            return False

    def tiene_experiencia(self):
        experiencia = self.experiencia_laboral()
        experiencia_unemi = self.experiencia_laboral_unemi()
        if experiencia or experiencia_unemi:
            return True
        else:
            return False

    def tiene_produccion_cientifica(self):
        if self.tipo != 4:
            articulos = self.articulos_publicados()
            ponencias = self.ponencias_publicadas()
            libros = self.libros_publicados()
            capitulos = self.capitulos_libro_publicados()
            if articulos or ponencias or libros or capitulos:
                return True
            else:
                return False
        else:
            articulos = self.articulos_publicados_persona_externa()
            ponencias = self.ponencias_publicadas_persona_externa()
            libros = self.libros_publicados_persona_externa()
            capitulos = self.capitulos_libro_publicados_persona_externa()
            if articulos or ponencias or libros or capitulos:
                return True
            else:
                return False

    def tiene_proyectos_investigacion(self):
        if self.tipo != 4:
            proyectosi = self.proyectos_investigacion_unemi()
            proyectose = self.proyectos_investigacion_externo()
            if proyectose or proyectosi:
                return True
            else:
                return False
        else:
            proyectos = self.proyectos_investigacion_persona_externa()
            if proyectos:
                return True
            else:
                return False

    def color_tipo_registro(self):
        if self.tiporegistro == 1:
            return 'success'
        elif self.tiporegistro == 2:
            return 'important'
        elif self.tiporegistro == 3:
            return 'info'
        elif self.tiporegistro == 4:
            return 'inverse'
        else:
            return 'warning'

    def color_estado_acreditado(self):
        if self.estadoacreditado == 1:
            return 'warning'
        elif self.estadoacreditado == 2:
            return 'success'
        elif self.estadoacreditado == 3:
            return 'important'
        else:
            return 'inverse'


class ProyectoInvestigacionCronogramaActividad(ModeloBase):
    objetivo = models.ForeignKey(ProyectoInvestigacionObjetivo, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Objetivo de proyecto de Investigación')
    actividad = models.TextField(default='', verbose_name=u'Descripción de la actividad')
    ponderacion = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% ponderación')
    fechainicio = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio')
    fechafin = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin')
    entregable = models.TextField(default='', verbose_name=u'Entregable')
    subirevidenciaretraso = models.BooleanField(default=False, verbose_name=u'Permiso para subir evidencias con retraso')
    porcentajeejecucion = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% ejecución')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    observacioninv = models.TextField(default='', verbose_name=u'Observación de investigación')
    estado = models.IntegerField(choices=ESTADO_ACTIVIDAD, default=1, verbose_name=u'Estado')

    def __str__(self):
        return u'%s - [ %s a %s ] - %s' % (self.actividad, self.fechainicio, self.fechafin, self.get_estado_display())

    class Meta:
        verbose_name = u"Cronograma de actividades del proyecto"
        verbose_name_plural = u"Cronogramas de actividades del proyecto"

    def save(self, *args, **kwargs):
        super(ProyectoInvestigacionCronogramaActividad, self).save(*args, **kwargs)

    def lista_responsables(self):
        return self.proyectoinvestigacioncronogramaresponsable_set.filter(status=True).order_by('id')

    def responsables(self):
        return ",".join(e.persona.nombre_completo_inverso() for e in self.lista_responsables())

    def lista_ids_responsables(self):
        return self.proyectoinvestigacioncronogramaresponsable_set.values_list('persona_id', flat=True).filter(status=True).order_by('id')

    def lista_html_nombres_responsables(self):
        listahtml = "<ul>"
        for responsable in self.lista_responsables():
            listahtml = listahtml + "<li>" + responsable.persona.nombre_completo_inverso() + "</li>"
        listahtml = listahtml + "</ul>"
        return listahtml

    def lista_entregables(self):
        return self.proyectoinvestigacioncronogramaentregable_set.filter(status=True).order_by('id')

    def entregables(self):
        return ",".join(e.entregable for e in self.lista_entregables())

    def lista_ids_entregables(self):
        return self.proyectoinvestigacioncronogramaentregable_set.values_list('id', flat=True).filter(status=True).order_by('id')

    def lista_html_entregables(self):
        if self.lista_entregables():
            listahtml = "<ul>"
            for entregable in self.lista_entregables():
                listahtml = listahtml + "<li>" + entregable.entregable + "</li>"
            listahtml = listahtml + "</ul>"
            return listahtml
        return ''

    def evidencias(self):
        return ProyectoInvestigacionActividadEvidencia.objects.filter(status=True, entregable__actividad=self).order_by('entregable_id', 'id')
        # return self.proyectoinvestigacioncronogramaentregable_set.filter(proyectoinvestigacionactividadevidencia__isnull=False).order_by('id')

    def total_evidencias(self):
        evidencias = self.evidencias()
        if evidencias:
            return evidencias.count()
        else:
            return 0

    def total_evidencias_por_revisar(self):
        return self.evidencias().filter(estado=1).count()

    def total_evidencias_por_confirmar_revision(self):
        return self.evidencias().filter(estado=5).count()

    def puede_subir_evidencias(self):
        return self.estado == 2 or self.estado == 4

    def puede_subir_evidencias_retraso(self):
        return self.estado == 3 and self.subirevidenciaretraso

    def color_estado(self):
        if self.estado == 1:
            return 'warning'
        elif self.estado == 2:
            return 'info'
        elif self.estado == 3:
            return 'success'
        else:
            return 'important'

    def puede_revisar_evidencia(self):
        return self.evidencias().filter(estado=1).count() > 0 and self.ultima_revision_esta_confirmada()

    def evidencias_por_revisar(self):
        return self.evidencias().filter(estado=1).order_by('id')

    def puede_confirmar_ultima_revision(self):
        if self.ultima_revision():
            return not self.ultima_revision().confirmada
        return False

    def ultima_revision(self):
        if self.proyectoinvestigacionrevisionactividad_set.filter(status=True).exists():
            return self.proyectoinvestigacionrevisionactividad_set.filter(status=True).order_by('-id')[0]
        return None

    def ultima_revision_esta_confirmada(self):
        if self.ultima_revision():
            return self.ultima_revision().confirmada
        return True

    def ultima_revision_confirmada(self):
        if self.proyectoinvestigacionrevisionactividad_set.filter(status=True, confirmada=True).exists():
            return self.proyectoinvestigacionrevisionactividad_set.filter(status=True, confirmada=True).order_by('-id')[0]
        return None

    def ultimo_porcentaje_ejecucion_asignado(self):
        if self.proyectoinvestigacioninformeactividad_set.filter(status=True, aprobado=True).exists():
            return self.proyectoinvestigacioninformeactividad_set.filter(status=True, aprobado=True).order_by('-id')[0].porcentajeejecucion
        return 0


class ProyectoInvestigacionCronogramaResponsable(ModeloBase):
    actividad = models.ForeignKey(ProyectoInvestigacionCronogramaActividad, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Actividad del cronograma')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona responsable")

    def __str__(self):
        return u'%s - %s' % (self.actividad, self.persona)

    class Meta:
        verbose_name = u"Responsable de la actividad"
        verbose_name_plural = u"Responsables de las actividades"


class ProyectoInvestigacionCronogramaEntregable(ModeloBase):
    actividad = models.ForeignKey(ProyectoInvestigacionCronogramaActividad, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Actividad del cronograma')
    entregable = models.TextField(default='', verbose_name=u'Entregable de la actividad')

    def __str__(self):
        return u'%s - %s' % (self.actividad, self.entregable)

    class Meta:
        verbose_name = u"Entregable de la actividad"
        verbose_name_plural = u"Entregables de las actividades"

    def total_evidencias(self):
        return self.proyectoinvestigacionactividadevidencia_set.filter(status=True).count()


class ProyectoInvestigacionActividadEvidencia(ModeloBase):
    entregable = models.ForeignKey(ProyectoInvestigacionCronogramaEntregable, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Entregable de la actividad')
    fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha')
    descripcion = models.TextField(default='', verbose_name=u'Descripción')
    archivo = models.FileField(upload_to='evidenciaproyinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evidencia')
    retraso = models.BooleanField(default=False, verbose_name=u'Subida con retraso')
    personarevisa = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona revisa")
    fecharevisa = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha revisión')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    estado = models.IntegerField(choices=ESTADO_ARCHIVO_EVIDENCIA, default=1, verbose_name=u'Estado')

    def __str__(self):
        return u'%s - %s' % (self.entregable, self.descripcion)

    class Meta:
        verbose_name = u"Evidencia de la actividad"
        verbose_name_plural = u"Evidencias de las actividades"

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.strip().upper()
        super(ProyectoInvestigacionActividadEvidencia, self).save(*args, **kwargs)

    def color_estado(self):
        if self.estado == 1:
            return 'info'
        elif self.estado == 2:
            return 'success'
        elif self.estado == 3:
            return 'important'
        else:
            return 'warning'

    def nombre_archivo(self):
        return os.path.split(str(self.archivo))[1]


class ProyectoInvestigacionHistorialActividadEvidencia(ModeloBase):
    entregable = models.ForeignKey(ProyectoInvestigacionCronogramaEntregable, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Entregable de la actividad')
    fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha')
    descripcion = models.TextField(default='', verbose_name=u'Descripción')
    archivo = models.CharField(max_length=250, verbose_name=u'Nombre del archivo')

    def __str__(self):
        return u'%s - %s - %s' % (self.entregable, self.archivo)

    class Meta:
        verbose_name = u"Proyecto de Investigación Historial actividad evidencia"
        verbose_name_plural = u"Proyectos de Investigación historial actividad evidencias"


class ProyectoInvestigacionItemPresupuesto(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    tiporecurso = models.ForeignKey(TipoRecursoPresupuesto, on_delete=models.CASCADE, verbose_name=u'Tipo de recurso')
    recurso = models.TextField(default='', verbose_name=u"Recurso")
    descripcion = models.TextField(default='', verbose_name=u"Descripción del recurso")
    unidadmedida = models.ForeignKey("sagest.UnidadMedida", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Unidad de medida")
    cantidad = models.IntegerField(default=0, verbose_name=u'Cantidad')
    valorunitario = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor unitario")
    calculaiva = models.BooleanField(default=False, verbose_name=u'Calcular iva')
    valoriva = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor del iva")
    valortotal = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor total")
    observacion = models.TextField(default='', verbose_name=u'Observaciones')

    def __str__(self):
        return u'%s - %s - %s' % (self.proyecto, self.tiporecurso.descripcion, self.recurso)

    class Meta:
        verbose_name = u"Presupuesto del proyecto"
        verbose_name_plural = u"Presupuesto del proyecto"

    def save(self, *args, **kwargs):
        super(ProyectoInvestigacionItemPresupuesto, self).save(*args, **kwargs)


class ProyectoInvestigacionPresupuestoProgramacionGasto(ModeloBase):
    itempresupuesto = models.ForeignKey(ProyectoInvestigacionItemPresupuesto, on_delete=models.CASCADE, verbose_name=u'Presupuesto')
    numeroanio = models.IntegerField(default=0, verbose_name=u'Número año')
    trimestre = models.IntegerField(choices=TRIMESTRE_PROGRAMACION_GASTO, verbose_name=u'Trimestre')
    valor = models.FloatField(default=0, verbose_name=u"Valor Gasto")

    def __str__(self):
        return u'%s - %s - %s - %s' % (self.itempresupuesto, self.numeroanio, self.get_trimestre_display(), self.valor)

    class Meta:
        verbose_name = u"Programación del gasto del presupuesto"
        verbose_name_plural = u"Programaciones del gasto del presupuesto"


class ProyectoInvestigacionPasajeIntegrante(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    itempresupuesto = models.ForeignKey(ProyectoInvestigacionItemPresupuesto, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Item presupuesto')
    persona = models.ForeignKey("sga.Persona", blank=True, null=True, on_delete=models.CASCADE, verbose_name=u"Persona responsable")
    itinerario = models.TextField(default='', verbose_name=u"Itinerario")
    fechasalida = models.DateField(blank=True, null=True, verbose_name=u'Fecha de salida')
    fecharetorno = models.DateField(blank=True, null=True, verbose_name=u'Fecha de retorno')
    actividad = models.TextField(default='', verbose_name=u"Actividad a desarrollar")
    cantidad = models.IntegerField(default=0, verbose_name=u'Cantidad pasajes')
    valorunitario = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor unitario")
    calculaiva = models.BooleanField(default=False, verbose_name=u'Calcular iva')
    valoriva = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor del iva")
    valortotal = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor total")
    observacion = models.TextField(default='', verbose_name=u'Observaciones')
    tipopasaje = models.IntegerField(default=1, choices=TIPO_PASAJE_AEREO, verbose_name=u'Tipo pasaje aéreo')

    def __str__(self):
        return u'%s - %s - %s - %s' % (self.persona, self.itinerario, self.fechasalida, self.fecharetorno)

    class Meta:
        verbose_name = u"Pasaje del integrante del proyecto"
        verbose_name_plural = u"Pasajes del integrante del proyecto"

    def save(self, *args, **kwargs):
        self.itinerario = self.itinerario.strip().upper()
        self.actividad = self.actividad.strip().upper()
        self.observacion = self.observacion.strip().upper()
        super(ProyectoInvestigacionPasajeIntegrante, self).save(*args, **kwargs)


class ProyectoInvestigacionViaticoIntegrante(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    pasajeintegrante = models.ForeignKey(ProyectoInvestigacionPasajeIntegrante, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Pasaje de integrante')
    itempresupuesto = models.ForeignKey(ProyectoInvestigacionItemPresupuesto, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Item presupuesto')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona responsable")
    nocheestancia = models.IntegerField(default=0, verbose_name=u'Noches estancia')
    valor = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor")
    calculaiva = models.BooleanField(default=False, verbose_name=u'Calcular iva')
    valoriva = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor del iva")
    valortotal = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor total")
    observacion = models.TextField(default='', verbose_name=u'Observaciones')
    tipoviatico = models.IntegerField(default=1, choices=TIPO_VIATICO, verbose_name=u'Tipo viático')

    def __str__(self):
        return u'%s - %s - %s' % (self.persona, self.nocheestancia, self.valortotal)

    class Meta:
        verbose_name = u"Viático del integrante del proyecto"
        verbose_name_plural = u"Viáticos del integrante del proyecto"

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.strip().upper()
        super(ProyectoInvestigacionViaticoIntegrante, self).save(*args, **kwargs)


class ProyectoInvestigacionMovilizacionIntegrante(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    pasajeintegrante = models.ForeignKey(ProyectoInvestigacionPasajeIntegrante, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Pasaje de integrante')
    itempresupuesto = models.ForeignKey(ProyectoInvestigacionItemPresupuesto, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Item presupuesto')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona responsable")
    ciudad = models.TextField(default='', verbose_name=u"Ciudades movilización")
    cantidaddia = models.IntegerField(default=0, verbose_name=u'Número de días')
    valor = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor")
    calculaiva = models.BooleanField(default=False, verbose_name=u'Calcular iva')
    valoriva = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor del iva")
    valortotal = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Valor total")
    observacion = models.TextField(default='', verbose_name=u'Observaciones')
    tipomovilizacion = models.IntegerField(default=1, choices=TIPO_MOVILIZACION, verbose_name=u'Tipo movilización')

    def __str__(self):
        return u'%s - %s - %s' % (self.persona, self.cantidaddia, self.valortotal)

    class Meta:
        verbose_name = u"Movilización del integrante del proyecto"
        verbose_name_plural = u"Movilizaciones del integrante del proyecto"

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.strip().upper()
        super(ProyectoInvestigacionMovilizacionIntegrante, self).save(*args, **kwargs)


class ProyectoInvestigacionEvaluador(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Evaluador")
    tipo = models.IntegerField(choices=TIPO_EVALUADOR, verbose_name=u'Tipo de evaluador')
    tipoproyecto = models.IntegerField(choices=TIPO_PROYECTO_EVALUACION, default=1, verbose_name=u'Tipo de proyecto')
    inicioevaluacion = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio para evaluar')
    finevaluacion = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin para evaluar')
    notificado = models.BooleanField(default=False, verbose_name=u'Notificado cómo evaluador de proyecto')
    reevaluacion = models.BooleanField(default=False, verbose_name=u'Asignado para reevaluación')

    def __str__(self):
        return u'%s - %s - %s - %s' % (self.proyecto, self.persona, self.get_tipo_display(), self.get_tipoproyecto_display())

    class Meta:
        verbose_name = u"Evaluador del proyecto"
        verbose_name_plural = u"Evaluadores del proyecto"

    def id_registro_profesor_o_externo(self):
        if self.tipo == 1:
            return Profesor.objects.get(persona=self.persona, status=True).id
        else:
            return Externo.objects.get(persona=self.persona, status=True).id

    def tiene_registro_evaluacion(self):
        return self.evaluacionproyecto_set.filter(status=True).exists()


class RubricaEvaluacion(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaProyecto, on_delete=models.CASCADE, verbose_name=u'Convocatoria de Proyectos')
    categoria = models.CharField(default='', max_length=150, verbose_name=u'Categoría')
    numero = models.IntegerField(default=0, verbose_name=u'Número orden')
    descripcion = models.TextField(default='', verbose_name=u"Descripción")
    valoracion = models.IntegerField(default=0, verbose_name=u'Valoración de la categoría')

    def __str__(self):
        return u'%s - %s - %s' % (self.convocatoria, self.categoria, self.valoracion)

    class Meta:
        verbose_name = u"Rúbrica de Evaluación de la convocatoria"
        verbose_name_plural = u"Rúbricas de Evaluación de la convocatoria"

    def items_rubrica(self):
        return self.rubricaevaluacionitem_set.filter(status=True).order_by('id')

    def total_items_rubrica(self):
        return self.items_rubrica().count()

    def en_uso(self):
        return EvaluacionProyectoDetalle.objects.values('id').filter(status=True, rubricaitem__rubrica=self).exists()


class RubricaEvaluacionItem(ModeloBase):
    rubrica = models.ForeignKey(RubricaEvaluacion, on_delete=models.CASCADE, verbose_name=u'Rúbrica de Evaluación')
    item = models.TextField(default='', verbose_name=u"Item")
    puntajemaximo = models.IntegerField(default=0, verbose_name=u'Puntaje máximo')

    def __str__(self):
        return u'%s - %s - %s' % (self.rubrica.categoria, self.item, self.puntajemaximo)

    class Meta:
        verbose_name = u"Item de la Rúbrica de Evaluación de la convocatoria"
        verbose_name_plural = u"Items de las Rúbricas de Evaluación de la convocatoria"


class EvaluacionProyecto(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha de evaluación')
    fechaconfirma = models.DateField(blank=True, null=True, verbose_name=u'Fecha confirmación')
    tipo = models.IntegerField(default=1, choices=TIPO_EVALUACION, verbose_name=u'Tipo de evaluación')
    evaluador = models.ForeignKey(ProyectoInvestigacionEvaluador, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona evaluador")
    puntajetotal = models.IntegerField(default=0, verbose_name=u'Puntaje total de evaluación')
    observacion = models.TextField(default='', verbose_name=u'Observaciones')
    archivo = models.FileField(upload_to='evaluacionproyinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de novedades de evaluación')
    archivoevaluacion = models.FileField(upload_to='evaluacionproyinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evaluación')
    archivoevaluacionfirmada = models.FileField(upload_to='evaluacionproyinvestigacion/firmado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evaluación firmada')
    estado = models.IntegerField(default=1, choices=ESTADO_EVALUACION_INTERNA_EXTERNA, verbose_name=u'Estado')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona revisa resultados")
    fecharevision = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha revisión')
    revisado = models.BooleanField(default=False, verbose_name=u'Revisado por coordinación investigación')
    observacionrevision = models.TextField(default='', verbose_name=u'Observaciones por coordinacio investigación')
    adicional = models.BooleanField(default=False, verbose_name=u'Evaluación adicional')
    estadoregistro = models.IntegerField(default=5, choices=ESTADO_EVALUACION, verbose_name=u'Estado del registro')

    def __str__(self):
        return u'%s - %s - %s - %s' % (self.proyecto.titulo, self.puntajetotal, self.get_estado_display(), self.get_estadoregistro_display())

    class Meta:
        verbose_name = u"Evaluación de Proyectos de investigación"
        verbose_name_plural = u"Evaluaciones de Proyectos de investigación"

    def detalle_evaluacion_items_rubrica(self, rubrica):
        return self.evaluacionproyectodetalle_set.filter(status=True, rubricaitem__rubrica=rubrica).order_by('id')

    def total_obtenido_detalle_evaluacion_rubrica(self, rubrica):
        return self.evaluacionproyectodetalle_set.filter(status=True, rubricaitem__rubrica=rubrica).aggregate(total=Sum('puntaje'))['total']

    def color_estado_registro(self):
        if self.estadoregistro == 1:
            return 'inverse'
        elif self.estadoregistro == 2:
            return 'info'
        elif self.estadoregistro == 3:
            return 'default'
        elif self.estadoregistro == 4:
            return 'warning'
        elif self.estadoregistro == 5:
            return 'success'
        else:
            return 'important'

    def observacion_estado_registro(self):
        if self.estadoregistro == 1:
            return 'Evaluación en curso'
        elif self.estadoregistro == 2:
            return 'Evaluación confirmada'
        elif self.estadoregistro == 3:
            return 'Acta de evaluación generada'
        elif self.estadoregistro == 4:
            return 'Acta de evaluación subida'
        elif self.estadoregistro == 5:
            return 'Evaluación Cerrada'
        else:
            return 'Acta de evaluación con novedades'


class EvaluacionProyectoDetalle(ModeloBase):
    evaluacion = models.ForeignKey(EvaluacionProyecto, on_delete=models.CASCADE, verbose_name=u'Evaluación de proyecto')
    numero = models.IntegerField(default=0, verbose_name=u'Número orden')
    rubricaitem = models.ForeignKey(RubricaEvaluacionItem, on_delete=models.CASCADE, verbose_name=u'Criterio o item de rúbrica de evaluación')
    puntaje = models.IntegerField(default=0, verbose_name=u'Puntaje asignado')

    def __str__(self):
        return u'%s - %s - %s' % (self.evaluacion, self.rubricaitem.item, self.puntaje)

    class Meta:
        verbose_name = u"Detalle de Evaluación de Proyectos de investigación"
        verbose_name_plural = u"Detalles Evaluación de Proyectos de investigación"


class ProyectoInvestigacionRevisionActividad(ModeloBase):
    actividad = models.ForeignKey(ProyectoInvestigacionCronogramaActividad, on_delete=models.CASCADE, verbose_name=u'Actividad del cronograma')
    fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha de revisión')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona revisa")
    porcentaje = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% ejecución')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    confirmada = models.BooleanField(default=False, verbose_name=u'Revisión confirmada')

    def __str__(self):
        return u'%s - %s - %s - %s' % (self.actividad.actividad, self.persona, self.porcentaje, self.fecha)

    class Meta:
        verbose_name = u"Revisión de actividad de Proyectos de investigación"
        verbose_name_plural = u"Revisiones de actividades de Proyectos de investigación"

    def detalle_revision(self):
        return self.proyectoinvestigacionrevisionactividaddetalle_set.filter(status=True).order_by('id')


class ProyectoInvestigacionRevisionActividadDetalle(ModeloBase):
    revisionactividad = models.ForeignKey(ProyectoInvestigacionRevisionActividad, on_delete=models.CASCADE, verbose_name=u'Revisión actividad')
    evidencia = models.ForeignKey(ProyectoInvestigacionActividadEvidencia, on_delete=models.CASCADE, verbose_name=u'Evidencia')
    estado = models.IntegerField(choices=ESTADO_ARCHIVO_EVIDENCIA, default=1, verbose_name=u'Estado')
    observacion = models.TextField(default='', verbose_name=u'Observación')

    def __str__(self):
        return u'%s - %s' % (self.evidencia, self.get_estado_display())

    class Meta:
        verbose_name = u"Revisión de detalle de actividad de Proyectos de investigación"
        verbose_name_plural = u"Revisiones de detalles de actividades de Proyectos de investigación"


class ProyectoInvestigacionInforme(ModeloBase):
    proyecto = models.ForeignKey(ProyectoInvestigacion, on_delete=models.CASCADE, verbose_name=u'Proyecto de Investigación')
    periodo = models.ForeignKey("sga.Periodo", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Periodo académico')
    tipo = models.IntegerField(choices=TIPO_INFORME, default=1, verbose_name=u'Tipo de informe')
    secuencia = models.IntegerField(default=0, verbose_name=u'Secuencia informe')
    fechainicio = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio para generar')
    fechafin = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin para generar')
    generado = models.BooleanField(default=False, verbose_name=u'Informe generado')
    fecha = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha del informe')
    numero = models.CharField(default='', max_length=150, verbose_name=u'Número')
    adenda = models.BooleanField(default=False, verbose_name=u'¿Solicitó adenda contrato?')
    prorroga = models.BooleanField(default=False, verbose_name=u'¿Solicitó prórroga?')
    mesprorroga = models.IntegerField(default=0, verbose_name=u'Meses prórroga')
    fechafinproyecto = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin de proyecto (incluyendo prórroga)')
    montoejecutado = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Monto ejecutado del presupuesto")
    porcentajepresup = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% ejecución presupuestaria')
    aplicacapacitacion = models.BooleanField(default=False, verbose_name=u'¿Aplica entrenamiento y capacitación?')
    capacitacion = models.TextField(default='', verbose_name=u'Detalle de la capacitación')
    aplicadisemresultado = models.BooleanField(default=False, verbose_name=u'¿Aplica diseminación de resultados?')
    disemresultado = models.TextField(default='', verbose_name=u'Detalle diseminación de resultados')
    obtuvoproductopat = models.BooleanField(default=False, verbose_name=u'¿Se obtuvo algún producto patentable?')
    productopatentable = models.TextField(default='', verbose_name=u'Detalle de producto patentable')
    conclusion = models.TextField(default='', verbose_name=u'Conclusiones')
    continuacion = models.TextField(default='', verbose_name=u'Continuación del proyecto')
    lineabase = models.TextField(default='', verbose_name=u'Línea base')
    indicadorgeneral = models.TextField(default='', verbose_name=u'Descripción del Indicador')
    fuentedatosgeneral = models.TextField(default='', verbose_name=u'Fuente de datos')
    lineabasegeneral = models.TextField(default='', verbose_name=u'Datos de Línea base')
    recomendacion = models.TextField(default='', verbose_name=u'Recomendaciones')
    archivogenerado = models.FileField(upload_to='proyectoinvestigacion/informes', blank=True, null=True, verbose_name=u'Archivo del informe generado con evidencias')
    archivo = models.FileField(upload_to='informeproyinvestigacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo del informe con firmas')
    personaverifica = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona verifica")
    fechaverificacion = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha verificación')
    observacionverificacion = models.TextField(blank=True, null=True, verbose_name=u'Observación de la verificación')
    personaaprueba = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, related_name="+", blank=True, null=True, verbose_name=u"Persona aprueba")
    fechaaprobacion = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha aprobación')
    observacionaprobacion = models.TextField(blank=True, null=True, verbose_name=u'Observación de la aprobación')
    fechavalidacion = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha validación informe firmado')
    observacionvalidacion = models.TextField(blank=True, null=True, verbose_name=u'Observación de la validación informe firmado')
    avanceesperado = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2, verbose_name=u'% de avance esperado del proyecto')
    porcentajeejecucion = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% ejecución real del proyecto')
    aprobado = models.BooleanField(default=False, verbose_name=u'Informe aprobado')
    firmaelabora = models.BooleanField(default=False, verbose_name=u'Firmado por persona que elabora')
    firmaverifica = models.BooleanField(default=False, verbose_name=u'Firmado por persona que verifica')
    firmaaprueba = models.BooleanField(default=False, verbose_name=u'Firmado por persona que aprueba')
    estado = models.IntegerField(choices=ESTADO_INFORME, default=1, verbose_name=u'Estado')

    def __str__(self):
        return u'%s - %s - %s' % (self.numero, self.proyecto.titulo, self.get_estado_display())

    class Meta:
        verbose_name = u"Informe de Proyecto de investigación"
        verbose_name_plural = u"Informes de Proyectos de investigación"

    def puede_agregar(self):
        return True

        # if self.estado == 1 and self.proyecto.verificainforme is not None and self.proyecto.cantidad_evidencias_subidas_validadas() > 0:
        #     # return self.fechainicio <= datetime.now().date() <= self.fechafin
        #     enfecha = self.fechainicio <= datetime.now().date()
        #     if enfecha:
        #         pendienteanterior = ProyectoInvestigacionInforme.objects.values("id").filter(status=True, proyecto=self.proyecto, pk__lt=self.id).exclude(estado=4).exists()
        #         return not pendienteanterior
        #     return False
        # return False

    def puede_agregar_con_retraso(self):
        return self.estado == 2

    def color_estado(self):
        if self.estado in [1, 2]:
            return 'warning'
        elif self.estado in [6, 8]:
            return 'important'
        elif self.estado == 3:
            return 'inverse'
        elif self.estado == 4:
            return 'default'
        elif self.estado == 5:
            return 'info'
        else:
            return 'success'

    def puede_revisar_aprobar(self):
        return self.estado in [3, 4, 5, 6, 7, 8]

    def objetivos_especificos_cronograma_informe(self):
        return self.proyecto.proyectoinvestigacionobjetivo_set.filter(proyectoinvestigacioncronogramaactividad__proyectoinvestigacioninformeactividad__status=True, proyectoinvestigacioncronogramaactividad__proyectoinvestigacioninformeactividad__informe=self).distinct().order_by('id')

    def actividades_objetivo_especifico(self, objetivoid):
        return self.proyectoinvestigacioninformeactividad_set.filter(status=True, actividad__objetivo_id=objetivoid).order_by('id')

    def actividades(self):
        return self.proyectoinvestigacioninformeactividad_set.filter(status=True).order_by('actividad_id')

    def total_actividades(self):
        return self.actividades().count()

    def evidencias(self):
        return self.proyectoinvestigacioninformeanexo_set.filter(status=True).order_by('id')

    def total_evidencias(self):
        if self.tipo == 1:
            return self.evidencias().count()
        else:
            return self.total_evidencias_informe_final()

    def total_evidencias_informe_final(self):
        return len(self.evidencias_informe_final())

    def evidencias_informe_final(self):
        lista_evidencias = []
        for reg in self.ejecucion_financiera():
            evidencia = {
                'tipo': 'Ejecución Prespuesto',
                'descripcion': reg.descripcion,
                'archivo': reg.archivo
            }
            lista_evidencias.append(evidencia)

        for reg in self.capacitaciones_realizadas():
            evidencia = {
                'tipo': 'Capacitaciones ejecutadas',
                'descripcion': reg.tema,
                'archivo': reg.archivo
            }
            lista_evidencias.append(evidencia)

        for reg in self.publicaciones():
            evidencia = {
                'tipo': 'Publicaciones realizadas',
                'descripcion': reg.titulo,
                'archivo': reg.archivo
            }
            lista_evidencias.append(evidencia)

        for reg in self.eventos_cientificos():
            evidencia = {
                'tipo': 'Eventos científicos',
                'descripcion': reg.nombre,
                'archivo': reg.archivo
            }
            lista_evidencias.append(evidencia)

        return lista_evidencias

    def ejecucion_tecnica(self):
        return self.proyectoinvestigacioninformeejecucionobjetivo_set.filter(status=True).order_by('id')

    def ejecucion_financiera(self):
        return self.proyectoinvestigacioninformeevideciapresupuesto_set.filter(status=True).order_by('id')

    def objetivos_cumpliento(self):
        return self.proyectoinvestigacioninformeobjetivoresultado_set.filter(status=True, tipo=1).order_by('id')

    def resultados_significativos(self):
        return self.proyectoinvestigacioninformeobjetivoresultado_set.filter(status=True, tipo=2).order_by('id')

    def capacitaciones_realizadas(self):
        return self.proyectoinvestigacioninformecapacitacion_set.filter(status=True).order_by('id')

    def publicaciones(self):
        return self.proyectoinvestigacioninformepublicacion_set.filter(status=True).order_by('id')

    def eventos_cientificos(self):
        return self.proyectoinvestigacioninformeevento_set.filter(status=True).order_by('id')

    def otros_productos(self):
        return self.proyectoinvestigacioninformeotroproducto_set.filter(status=True).order_by('id')

    def personas_participantes(self):
        return self.proyectoinvestigacioninformeparticipante_set.filter(status=True).order_by('id')

    def instituciones_participantes(self):
        return self.proyectoinvestigacioninformeinstitucion_set.filter(status=True).order_by('id')

    def cambios(self):
        return self.proyectoinvestigacioninformecambioproblema_set.filter(status=True, tipo=1).order_by('id')

    def problemas(self):
        return self.proyectoinvestigacioninformecambioproblema_set.filter(status=True, tipo=2).order_by('id')

    def equipamiento(self):
        return self.proyectoinvestigacioninformeequipamiento_set.filter(status=True).order_by('id')

    def indicadores(self):
        return self.proyectoinvestigacioninformeindicador_set.filter(status=True).order_by('id')

    def informacion_completa(self):
        # Verificar que la información del informe esté completa
        valido = True
        mensajes = ""

        if not self.ejecucion_financiera():
            valido = False
            mensajes = "<br><b>- </b>Faltan detalles de evidencias ejecución del presupuesto. <b>[E.2 Ejecución Financiera]</b>"

        if self.objetivos_cumpliento().filter(detalle='').exists():
            valido = False
            mensajes = mensajes + "<br><b>- </b>Los detalles de cumplimiento de los objetivos deben estar completos. <b>[F. Objetivos General y Específicos]</b>"

        if self.resultados_significativos().filter(detalle='').exists():
            valido = False
            mensajes = mensajes + "<br><b>- </b>Las descripciones de resultados deben estar completas. <b>[G.1 Resultados significativos]</b>"

        if self.aplicacapacitacion:
            if not self.capacitaciones_realizadas():
                valido = False
                mensajes = mensajes + "<br><b>- </b>Ingrese mínimo un registro de jornadas de capacitaciones realizadas. <b>[G.2 Oportunidades de entrenamiento]</b>"

        if not self.publicaciones():
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese mínimo un registro de publicaciones realizadas. <b>[H.1 Publicaciones]</b>"

        if not self.eventos_cientificos():
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese mínimo un registro de participación en eventos científicos. <b>[I. Participación en Eventos Científicos]</b>"

        if not self.cambios():
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese mínimo un registro de cambios realizados. <b>[K.1 Cambios]</b>"

        if not self.problemas():
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese mínimo un registro de problemas presentados. <b>[K.2 Problemas Técnicos y Financieros]</b>"

        if not self.conclusion:
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese las conclusiones. <b>[M. Conclusiones]</b>"

        if not self.continuacion:
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese la continuación del proyecto. <b>[N. Continuación del Proyecto]</b>"

        if not self.lineabase:
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese la línea base. <b>[O.1 Línea base]</b>"

        if not self.indicadorgeneral:
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese la descripción del indicador. <b>[O.2 Metodología]</b>"

        if not self.fuentedatosgeneral:
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese la fuente de datos. <b>[O.2 Metodología]</b>"

        if not self.lineabasegeneral:
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese datos de línea base. <b>[O.2 Metodología]</b>"

        if not self.indicadores():
            valido = False
            mensajes = mensajes + "<br><b>- </b>Ingrese mínimo un indicador (Causa, problema efecto). <b>[O.2 Metodología]</b>"

        return {
            "valido": valido,
            "mensajes": mensajes
        }


class ProyectoInvestigacionInformeActividad(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    actividad = models.ForeignKey(ProyectoInvestigacionCronogramaActividad, on_delete=models.CASCADE, verbose_name=u'Actividad del cronograma')
    responsable = models.ManyToManyField("sga.Persona", verbose_name=u'Responsables')
    entregable = models.TextField(default='', verbose_name=u'Entregable')
    fechainicio = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio')
    fechafin = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin')
    cantidadhora = models.IntegerField(blank=True, null=True, verbose_name=u'Cantidad de horas')
    porcentajeejecucion = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% ejecución')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    estado = models.IntegerField(choices=ESTADO_ACTIVIDAD, default=1, verbose_name=u'Estado')
    aprobado = models.BooleanField(default=False, verbose_name=u'Actividad aprobada en el informe')

    def __str__(self):
        return u'%s - %s' % (self.informe, self.actividad.actividad)

    class Meta:
        verbose_name = u"Proyecto de Investigación actividad del informe"
        verbose_name_plural = u"Proyectos de Investigación actividades de los informes"


class ProyectoInvestigacionInformeAnexo(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    # evidencia = models.ForeignKey(ProyectoInvestigacionActividadEvidencia, on_delete=models.CASCADE, verbose_name=u'Evidencia del entregable de la actividad del proyecto')
    descripcion = models.CharField(max_length=250, default='', verbose_name=u'Descripción')
    fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha generación de la evidencia')
    numeropagina = models.CharField(blank=True, null=True, max_length=150, verbose_name=u'Número de páginas')
    archivo = models.FileField(upload_to='evidenciainformeproyinv/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evidencia')

    def __str__(self):
        return u'%s - %s' % (self.informe, self.descripcion)

    class Meta:
        verbose_name = u"Proyecto de Investigación anexo del informe"
        verbose_name_plural = u"Proyectos de Investigación anexos de los informes"


class ProyectoInvestigacionInformeEjecucionObjetivo(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    objetivo = models.ForeignKey(ProyectoInvestigacionObjetivo, on_delete=models.CASCADE, verbose_name=u'Objetivo de proyecto de Investigación')
    porcentajeejecucion = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% ejecución del objetivo')

    def __str__(self):
        return '{} - {} - {:.2f}%'.format(self.informe.numero, self.objetivo.descripcion, self.porcentajeejecucion)

    class Meta:
        verbose_name = u"Ejecución objetivo específico de Informe de Proyecto de investigación"
        verbose_name_plural = u"Ejecucipon objetivos específicos de Informes de Proyectos de investigación"


class ProyectoInvestigacionInformeEvideciaPresupuesto(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    descripcion = models.CharField(max_length=250, default='', verbose_name=u'Descripción')
    archivo = models.FileField(upload_to='evidenciainformeproyinv/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evidencia')

    def __str__(self):
        return '{} - {}'.format(self.informe.numero, self.descripcion)

    class Meta:
        verbose_name = u"Evidencia de ejecución del presupuesto para el informe"
        verbose_name_plural = u"Evidencias de ejecución del presupuesto para el informe"


class ProyectoInvestigacionInformeObjetivoResultado(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    descripcion = models.TextField(default='', verbose_name=u'Descripción del objetivo o resultado')
    detalle = models.TextField(default='', verbose_name=u'Detalle de cumplimiento del objetivo o de resultado')
    tipo = models.IntegerField(choices=TIPO_CUMPLIMIENTO_INFORME, default=1, verbose_name=u'Tipo de registro')
    agregado = models.BooleanField(default=False, verbose_name=u'Resultado agregado')

    def __str__(self):
        return '{} - {} - {}'.format(self.informe.numero, self.get_tipo_display(), self.descripcion)

    class Meta:
        verbose_name = u"Cumplimiento de objetivo/resultado para el informe"
        verbose_name_plural = u"Cumplimiento de objetivos/resultados para el informe"


class ProyectoInvestigacionInformeCapacitacion(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    tema = models.CharField(max_length=250, default='', verbose_name=u'Tema de la capacitación')
    fechainicio = models.DateField(verbose_name=u'Fecha inicio')
    fechafin = models.DateField(verbose_name=u'Fecha de fin')
    lugar = models.CharField(max_length=250, default='', verbose_name=u'Lugar de la capacitación')
    personacapacitada = models.IntegerField(default=1, verbose_name=u'Número de personas capacitadas')
    archivo = models.FileField(upload_to='evidenciainformeproyinv/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evidencia')

    def __str__(self):
        return '{} - {}'.format(self.informe.numero, self.tema)

    class Meta:
        verbose_name = u"Detalle de capacitación del informe"
        verbose_name_plural = u"Detalles de capacitaciones de los informes"


class ProyectoInvestigacionInformePublicacion(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    titulo = models.CharField(max_length=250, default='', verbose_name=u'Título')
    revista = models.CharField(max_length=250, default='', verbose_name=u'Revista/Libro')
    issn = models.CharField(max_length=100, default='', verbose_name=u'ISSN')
    indexacion = models.CharField(max_length=250, default='', verbose_name=u'Indexación')
    fechaenvio = models.DateField(verbose_name=u'Fecha de envío')
    fechaaceptacion = models.DateField(verbose_name=u'Fecha de aceptación')
    archivo = models.FileField(upload_to='evidenciainformeproyinv/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evidencia')

    def __str__(self):
        return '{} - {}'.format(self.informe.numero, self.titulo)

    class Meta:
        verbose_name = u"Detalle de publicación del informe"
        verbose_name_plural = u"Detalles de publicaciones de los informes"


class ProyectoInvestigacionInformeEvento(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    nombre = models.CharField(max_length=250, default='', verbose_name=u'Nombre del evento')
    lugar = models.CharField(max_length=250, default='', verbose_name=u'Lugar del evento')
    fecha = models.DateField(verbose_name=u'Fecha del evento')
    titulo = models.CharField(max_length=250, default='', verbose_name=u'Título del trabajo')
    archivo = models.FileField(upload_to='evidenciainformeproyinv/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evidencia')

    def __str__(self):
        return '{} - {}'.format(self.informe.numero, self.nombre)

    class Meta:
        verbose_name = u"Detalle de participación en evento científico del informe"
        verbose_name_plural = u"Detalles de participaciones en eventos científicos de los informes"


class ProyectoInvestigacionInformeOtroProducto(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    descripcion = models.CharField(max_length=250, default='', verbose_name=u'Nombre del evento')

    def __str__(self):
        return '{} - {}'.format(self.informe.numero, self.descripcion)

    class Meta:
        verbose_name = u"Detalle de otro producto del informe"
        verbose_name_plural = u"Detalles de otros productos de los informes"


class ProyectoInvestigacionInformeParticipante(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    nombre = models.CharField(max_length=250, default='', verbose_name=u'Nombres')
    apellido = models.CharField(max_length=250, default='', verbose_name=u'Apellidos')
    funcion = models.IntegerField(default=1, choices=FUNCION_INTEGRANTE, verbose_name=u'Función o rol del participante')
    entidad = models.CharField(max_length=250, default='', verbose_name=u'Entidad o institución')
    email = models.CharField(max_length=250, default='', verbose_name=u'Dirección de e-mail')
    objetivo = models.ManyToManyField(ProyectoInvestigacionObjetivo, verbose_name=u'Objetivos en los que participó')

    def __str__(self):
        return '{} - {} {} - {}'.format(self.informe.numero, self.nombre, self.apellido, self.get_funcion_display())

    class Meta:
        verbose_name = u"Detalle de persona participante del proyecto para el informe"
        verbose_name_plural = u"Detalles de personas participantes de los proyectos para los informes"

    def ids_objetivos_participacion(self):
        ids = ",".join(str(o.id) for o in self.objetivo.all())
        numeros = ", ".join(str(o.numero) for o in self.objetivo.all())

        ids_objetivos = {
            "ids": ids,
            "numeros": numeros
        }
        return ids_objetivos


class ProyectoInvestigacionInformeInstitucion(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    nombre = models.CharField(max_length=250, default='', verbose_name=u'Nombre de la institución')
    actividad = models.CharField(max_length=250, default='', verbose_name=u'Actividades en las que participó')

    def __str__(self):
        return '{} - {}'.format(self.informe.numero, self.nombre)

    class Meta:
        verbose_name = u"Detalle de institución participante del proyecto para el informe"
        verbose_name_plural = u"Detalles de instituciones participantes de los proyectos para los informes"


class ProyectoInvestigacionInformeCambioProblema(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    detalle = models.CharField(max_length=250, default='', verbose_name=u'Detalle del cambio o problema')
    tipo = models.IntegerField(default=1, choices=TIPO_CAMBIO_INFORME, verbose_name=u'Tipo de registro')

    def __str__(self):
        return '{} - {} - {}'.format(self.informe.numero, self.detalle, self.get_tipo_display())

    class Meta:
        verbose_name = u"Detalle de cambio/problema para el informe"
        verbose_name_plural = u"Detalles de cambios/problemas para los informes"


class ProyectoInvestigacionInformeEquipamiento(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    codigo = models.CharField(max_length=20, default='', verbose_name=u'Código de barra')
    equipo = models.CharField(max_length=250, default='', verbose_name=u'Equipo')
    descripcion = models.CharField(max_length=250, default='', verbose_name=u'Descripción')
    objetivo = models.ManyToManyField(ProyectoInvestigacionObjetivo, verbose_name=u'Objetivos en los que se utilizó')
    ubicacion = models.CharField(max_length=250, default='', verbose_name=u'Ubicación')
    custodio = models.CharField(max_length=250, default='', verbose_name=u'Personal custodio')

    def __str__(self):
        return '{} - {} - {}'.format(self.informe.numero, self.equipo, self.ubicacion)

    class Meta:
        verbose_name = u"Detalle de equipamiento del proyecto para el informe"
        verbose_name_plural = u"Detalles de equipamientos de los proyectos para los informes"

    def ids_objetivos_participacion(self):
        ids = ",".join(str(o.id) for o in self.objetivo.all())
        numeros = ", ".join(str(o.numero) for o in self.objetivo.all())

        ids_objetivos = {
            "ids": ids,
            "numeros": numeros
        }
        return ids_objetivos


class ProyectoInvestigacionInformeIndicador(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    indicador = models.TextField(default='', verbose_name=u'Indicador')
    descripcion = models.TextField(default='', verbose_name=u'Descripción')
    fuentedato = models.TextField(default='', verbose_name=u'Fuente de datos')
    lineabase = models.TextField(default='', verbose_name=u'Datos de la línea base')

    def __str__(self):
        return '{} - {}'.format(self.informe.numero, self.indicador)

    class Meta:
        verbose_name = u"Detalle de indicador para el informe"
        verbose_name_plural = u"Detalles de indicadores para los informes"


class ProyectoInvestigacionHistorialInforme(ModeloBase):
    informe = models.ForeignKey(ProyectoInvestigacionInforme, on_delete=models.CASCADE, verbose_name=u'Informe de Proyecto de Investigación')
    conclusion = models.TextField(default='', verbose_name=u'Conclusiones')
    recomendacion = models.TextField(default='', verbose_name=u'Recomendaciones')
    archivo = models.CharField(default='', max_length=250, verbose_name=u'Nombre del archivo')

    def __str__(self):
        return u'%s - %s' % (self.informe, self.archivo)

    class Meta:
        verbose_name = u"Proyecto de Investigación Historial informe"
        verbose_name_plural = u"Proyectos de Investigación historial informes"


class EvaluadorProyecto(ModeloBase):
    tipo = models.IntegerField(choices=TIPO_EVALUADOR, verbose_name=u'Tipo de evaluador')
    tipopersona = models.IntegerField(choices=TIPO_INTEGRANTE, verbose_name=u'Tipo de persona')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona")
    profesor = models.ForeignKey("sga.Profesor", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Profesor')
    inscripcion = models.ForeignKey("sga.Inscripcion", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Alumno')
    administrativo = models.ForeignKey("sga.Administrativo", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Administrativo')
    externo = models.ForeignKey("sga.Externo", blank=True, on_delete=models.CASCADE, null=True, verbose_name=u'Externo')
    propuestaproyecto = models.BooleanField(default=False, verbose_name=u'Habilitado para propuestas de proyecto')
    proyectofinalizado = models.BooleanField(default=False, verbose_name=u'Habilitado para proyectos finalizados')
    obrarelevancia = models.BooleanField(default=False, verbose_name=u'Habilitado para obras de relevancia')
    activo = models.BooleanField(default=True, verbose_name=u'Activo/Inactivo')

    def __str__(self):
        return u'%s - %s' % (self.persona, self.get_tipo_display())

    class Meta:
        verbose_name = u"Evaluador de proyectos"
        verbose_name_plural = u"Evaluadores de proyectos"

    def puede_eliminar(self):
        return not ProyectoInvestigacionEvaluador.objects.values("id").filter(status=True, persona=self.persona).exists()

    def formacion_academica(self):
        return self.persona.titulacion_set.filter(status=True, titulo__nivel__rango__in=[5, 6]).order_by('-fechaobtencion', '-titulo__nivel__rango')

    def experiencia_laboral(self):
        return self.persona.mis_experienciaslaborales().filter(status=True).order_by('-fechafin', '-fechainicio')

    def articulos_publicados_persona_externa(self):
        articulos = ArticuloPersonaExterna.objects.filter(status=True, externo=self.externo).order_by('-fechapublicacion')
        return articulos

    def ponencias_publicadas_persona_externa(self):
        ponencias = PonenciaPersonaExterna.objects.filter(status=True, externo=self.externo).order_by('-fechafin', '-fechainicio')
        return ponencias

    def libros_publicados_persona_externa(self):
        libros = LibroPersonaExterna.objects.filter(status=True, externo=self.externo, tipo=1).order_by('-fechapublicacion')
        return libros

    def capitulos_libro_publicados_persona_externa(self):
        capitulos = LibroPersonaExterna.objects.filter(status=True, externo=self.externo, tipo=2).order_by('-fechapublicacion')
        return capitulos

    def proyectos_investigacion_persona_externa(self):
        proyectos = ProyectoInvestigacionPersonaExterna.objects.filter(status=True, externo=self.externo).order_by('-fechafin', '-fechainicio')
        return proyectos

    def externo_tiene_otros_perfiles(self):
        return self.persona.perfilusuario_set.values("id").filter(
            Q(administrativo__isnull=False) | Q(profesor__isnull=False) | Q(empleador__isnull=False) | Q(instructor__isnull=False) | Q(inscripcion__isnull=False) | Q(inscripcionaspirante__isnull=False) | Q(inscripcionpostulante__isnull=False)).exists()

    def total_proyectos_asignados(self):
        return ProyectoInvestigacionEvaluador.objects.values("id").filter(status=True, persona=self.persona).count()

    def total_obras_asignadas(self):
        return ObraRelevanciaEvaluador.objects.values("id").filter(status=True, persona=self.persona).count()


class PublicacionOrcid(ModeloBase):
    redpersona = models.ForeignKey("sga.RedPersona", on_delete=models.PROTECT, verbose_name=u"Persona")
    codigo = models.IntegerField(default=0, verbose_name=u'Código o ID publicación')
    fechacrea = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha creación')
    fechaedita = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha edición')
    titulo = models.TextField(blank=True, null=True, verbose_name=u'Título')
    subtitulo = models.TextField(blank=True, null=True, verbose_name=u'Sub-Título')
    titulorevista = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'Título de la revista')
    descripcion = models.TextField(blank=True, null=True, verbose_name=u'Descripción corta')
    tipo = models.CharField(blank=True, null=True, max_length=150, verbose_name=u'Tipo')
    anio = models.IntegerField(blank=True, null=True, verbose_name=u'Año de publicación')
    mes = models.IntegerField(blank=True, null=True, verbose_name=u'Mes de publicación')
    dia = models.IntegerField(blank=True, null=True, verbose_name=u'Día de publicación')
    url = models.TextField(blank=True, null=True, verbose_name=u'Url de publicación')
    colaborador = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'Colaboradores')
    procesada = models.BooleanField(default=False, verbose_name=u'Procesada')

    def __str__(self):
        return u'%s - %s - %s' % (self.redpersona.str_red_persona(), self.codigo, self.titulo)

    class Meta:
        verbose_name = u"Publicación del personal en ORCID"
        verbose_name_plural = u"Publicaciones del personal en ORCID"


class PublicacionScopus(ModeloBase):
    perfilacademico = models.ForeignKey("sga.RedPersona", on_delete=models.PROTECT, verbose_name=u"Perfil académico Scopus")
    codigo = models.BigIntegerField(default=0, verbose_name=u'Código o ID publicación')
    url = models.TextField(blank=True, null=True, verbose_name=u'Url de publicación')
    eid = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'ID electrónico')
    titulo = models.TextField(blank=True, null=True, verbose_name=u'Título')
    autor = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'Primer autor')
    titulofuente = models.TextField(blank=True, null=True, verbose_name=u'Título de la fuente')
    issn = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'Identificador ISSN')
    eissn = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'Identificador eISSN')
    isbn = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'Identificador ISBN')
    volumen = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'Volumen')
    pagina = models.CharField(blank=True, null=True, max_length=250, verbose_name=u'Número de páginas')
    fechapublica = models.DateField(blank=True, null=True, verbose_name=u'Fecha de publicación')
    fechaportada = models.CharField(blank=True, null=True, max_length=50, verbose_name=u'Fecha de visualización en portada')
    doi = models.CharField(blank=True, null=True, max_length=100, verbose_name=u'Identificador de objeto de documento DOI')
    ccita = models.IntegerField(default=0, verbose_name=u'Cantidad de veces citada')
    tipofuente = models.CharField(blank=True, null=True, max_length=150, verbose_name=u'Tipo de fuente')
    codigotipo = models.CharField(blank=True, null=True, max_length=50, verbose_name=u'Código tipo documento')
    descripciontipo = models.CharField(blank=True, null=True, max_length=50, verbose_name=u'Descripión tipo documento')
    procesada = models.BooleanField(default=False, verbose_name=u'Procesada')

    def __str__(self):
        return u'%s - %s - %s' % (self.perfilacademico.str_red_persona(), self.codigo, self.titulo)

    class Meta:
        verbose_name = u"Publicación del personal en SCOPUS"
        verbose_name_plural = u"Publicaciones del personal en SCOPUS"


class ConvocatoriaObraRelevancia(ModeloBase):
    descripcion = models.CharField(max_length=150, default='', verbose_name=u'Descripción')
    iniciopos = models.DateField(verbose_name=u'Fecha inicio de postulación')
    finpos = models.DateField(verbose_name=u'Fecha fin de postulación')
    inicioevalint = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio evaluación interna')
    finevalint = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin evaluación interna')
    inicioevalext = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio evaluación externa')
    finevalext = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin evaluación externa')
    archivo = models.FileField(upload_to='obrarelevancia/convocatoria/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la convocatoria')
    archivocga = models.FileField(upload_to='obrarelevancia/convocatoria/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de resolución comisión gestión académica')
    publicada = models.BooleanField(default=False, verbose_name=u'Convocatoria publicada')
    estado = models.ForeignKey("sagest.EstadoSolicitud", on_delete=models.CASCADE, verbose_name=u"Estado asignado")

    def __str__(self):
        return u'%s - %s - %s' % (self.descripcion, self.iniciopos, self.finpos)

    class Meta:
        verbose_name = u"Convocatoria para obras de relevancia"
        verbose_name_plural = u"Convocatorias para obras de relevancia"

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.strip().upper()
        super(ConvocatoriaObraRelevancia, self).save(*args, **kwargs)

    def puede_postular(self):
        # Verifico que el periodo de postulación esté vigente
        if self.iniciopos <= datetime.now().date() <= self.finpos and self.estado.valor == 2:
            return True
        else:
            return False

    def evaluacion_interna_abierta(self):
        fechaactual = datetime.now().date()
        return self.inicioevalint <= fechaactual <= self.finevalint

    def evaluacion_externa_abierta(self):
        fechaactual = datetime.now().date()
        return self.inicioevalext <= fechaactual <= self.finevalext

    def totales_obras_relevancia_evaluacion(self, persona, tipoevaluacion):
        evaluados = encurso = 0
        pendientes = asignados = self.obrarelevancia_set.values('id').filter(obrarelevanciaevaluador__persona=persona, obrarelevanciaevaluador__tipo=tipoevaluacion, obrarelevanciaevaluador__status=True).count()
        evaluaciones = EvaluacionObraRelevancia.objects.filter(status=True, obrarelevancia__convocatoria=self, evaluador=persona, tipo=tipoevaluacion)
        if evaluaciones:
            evaluados = evaluaciones.filter(estado__in=[2, 5, 6]).count()
            encurso = evaluaciones.count() - evaluados
            pendientes = asignados - evaluaciones.count()

        return {"asignados": asignados, "evaluados": evaluados, "encurso": encurso, "pendientes": pendientes}

    def rubricas_evaluacion(self):
        return self.rubricaobrarelevanciaconvocatoria_set.filter(status=True).order_by('secuencia')


class ObraRelevancia(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Convocatoria')
    profesor = models.ForeignKey("sga.Profesor", on_delete=models.CASCADE, verbose_name=u'Profesor')
    tipo = models.IntegerField(choices=TIPO_OBRA_RELEVANCIA, default=1, verbose_name=u'Tipo de obra')
    titulolibro = models.TextField(default='', verbose_name=u'Título del libro')
    titulocapitulo = models.TextField(default='', verbose_name=u'Título del capítulo de libro')
    isbn = models.CharField(max_length=150, default='', verbose_name=u'Identificador ISBN')
    aniopublicacion = models.IntegerField(verbose_name=u'Año de publicación')
    editorial = models.CharField(max_length=250, default='', verbose_name=u'Nombre de la editorial')
    areaconocimiento = models.ForeignKey("sga.AreaConocimientoTitulacion", on_delete=models.CASCADE, verbose_name=u'Área de conocimiento')
    subareaconocimiento = models.ForeignKey("sga.SubAreaConocimientoTitulacion", on_delete=models.CASCADE, verbose_name=u'Sub-área de conocimiento')
    subareaespecificaconocimiento = models.ForeignKey("sga.SubAreaEspecificaConocimientoTitulacion", on_delete=models.CASCADE, verbose_name=u'Sub-área específica de conocimiento')
    lineainvestigacion = models.ForeignKey("sga.LineaInvestigacion", on_delete=models.CASCADE, verbose_name=u'Línea de investigación')
    archivolibro = models.FileField(upload_to='obrarelevancia/obra/%Y/%m/%d', verbose_name=u'Archivo del libro')
    archivocapitulo = models.FileField(upload_to='obrarelevancia/obra/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo del capítulo de libro')
    archivoeditorial = models.FileField(upload_to='obrarelevancia/obra/%Y/%m/%d', verbose_name=u'Archivo del certificado de la editorial')
    archivoinforme = models.FileField(upload_to='obrarelevancia/obra/%Y/%m/%d', verbose_name=u'Archivo del informe de revisión por pares')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    estado = models.ForeignKey("sagest.EstadoSolicitud", on_delete=models.CASCADE, verbose_name=u'Estado asignado')

    def __str__(self):
        return u'%s - %s - %s' % (self.convocatoria.descripcion, self.profesor, self.titulolibro)

    class Meta:
        verbose_name = u"Obra de Relevancia"
        verbose_name_plural = u"Obras de Relevancia"

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.strip().upper()
        super(ObraRelevancia, self).save(*args, **kwargs)

    def puede_editar(self):
        return self.estado.valor in [1, 4]

    def puede_confirmar(self):
        return self.estado.valor == 1

    def puede_eliminar(self):
        return self.estado.valor in [1, 4]

    def puede_habilitar_edicion(self):
        return self.estado.valor == 2

    def participantes(self):
        return self.obrarelevanciaparticipante_set.filter(status=True).order_by('id')

    def listado_participantes_agrupado(self):
        return ",".join(e.persona.nombre_completo_inverso() for e in self.participantes())

    def listado_participantes_acta_evaluacion(self):
        MAXIMO = 9
        participantes = self.participantes()
        listado = []
        for participante in participantes:
            listado.append({
                "nombres": participante.persona.nombre_completo_inverso(),
                "filiacion": participante.get_filiacion_display()
            })

        for n in range(0, MAXIMO - len(participantes)):
            listado.append({
                "nombres": "&nbsp;",
                "filiacion": "&nbsp;"
            })

        return listado

    def evaluacion(self, persona, tipoevaluacion):
        if self.evaluacionobrarelevancia_set.values("id").filter(status=True, tipo=tipoevaluacion, evaluador=persona).exists():
            return self.evaluacionobrarelevancia_set.filter(status=True, tipo=tipoevaluacion, evaluador=persona)[0]
        return None

    def evidencias(self):
        documentos = []

        documento = {"id": 1, "descripcion": "Libro", "archivo": self.archivolibro}
        documentos.append(documento)

        if self.archivocapitulo:
            documento = {"id": 2, "descripcion": "Capítulo de libro", "archivo": self.archivocapitulo}
            documentos.append(documento)

        documento = {"id": 3, "descripcion": "Certificado editorial", "archivo": self.archivoeditorial}
        documentos.append(documento)

        documento = {"id": 4, "descripcion": "Informe de revisión pares", "archivo": self.archivoinforme}
        documentos.append(documento)

        return documentos

    def puede_asignar_evaluadores(self):
        return self.estado.valor in [2, 3, 6, 7, 8, 10, 13, 14]

    def total_evaluadores(self):
        return self.evaluadores_internos().count() + self.evaluadores_externos().count()

    def evaluadores_internos(self):
        return self.obrarelevanciaevaluador_set.filter(status=True, tipo=1).order_by('id')

    def evaluadores_externos(self):
        return self.obrarelevanciaevaluador_set.filter(status=True, tipo=2).order_by('id')

    def tiene_asignado_evaluadores(self):
        return self.obrarelevanciaevaluador_set.filter(status=True).exists()

    def tiene_evaluaciones(self):
        return self.evaluacionobrarelevancia_set.filter(status=True).exists()

    def evaluaciones_internas_completas(self):
        if self.evaluacionobrarelevancia_set.filter(status=True, tipo=1).count() > 0:
            if not self.obrarelevanciarecorrido_set.filter(status=True, estado__valor=8).exists():
                return self.evaluacionobrarelevancia_set.filter(status=True, tipo=1).count() == self.evaluadores_internos().count()
            else:
                return True
        return False

    def evaluaciones_cerradas(self):
        if self.evaluacionobrarelevancia_set.filter(status=True).exists():
            return self.evaluacionobrarelevancia_set.filter(status=True, estado=6).count() == self.total_evaluadores()
        return False

    def evaluaciones_internas_cerradas(self):
        if self.evaluacionobrarelevancia_set.filter(status=True, tipo=1).exists():
            if not self.obrarelevanciarecorrido_set.filter(status=True, estado__valor=8).exists():
                return self.evaluacionobrarelevancia_set.filter(status=True, tipo=1, estado=6).count() == self.evaluadores_internos().count()
            else:
                return True
        return False

    def evaluaciones(self):
        return self.evaluacionobrarelevancia_set.filter(status=True).order_by('id')

    def evaluaciones_internas(self):
        return self.evaluacionobrarelevancia_set.filter(status=True, tipo=1).order_by('id')

    def evaluaciones_externas(self):
        return self.evaluacionobrarelevancia_set.filter(status=True, tipo=2).order_by('id')

    def falta_cerrar_evaluaciones(self):
        if self.tiene_evaluaciones():
            evaluaciones = self.evaluaciones()
            return evaluaciones.values("id").filter(estado=5).exists()
        else:
            return False

    def evaluaciones_externas_completas(self):
        if self.evaluacionobrarelevancia_set.filter(status=True, tipo=2).count() > 0:
            if not self.obrarelevanciarecorrido_set.filter(status=True, estado__valor=11).exists():
                return self.evaluacionobrarelevancia_set.filter(status=True, tipo=2).count() == self.evaluadores_externos().count()
            else:
                return True
        return False

    def puede_evaluar_externo(self):
        if self.estado.valor == 8:
            return {"resultado": True, "mensaje": "Pendiente de Evaluar", "abrev": "PENDIENTE", "color": "warning"}
        elif self.estado.valor == 6:
            return {"resultado": False, "mensaje": "Evaluación Interna Pendiente", "abrev": "E.INTERNA P", "color": "warning"}
        elif self.estado.valor == 7:
            return {"resultado": False, "mensaje": "Evaluación Interna en Curso", "abrev": "E.INTERNA", "color": "info"}
        else:
            return {"resultado": False, "mensaje": "Evaluación Interna No superada", "abrev": "E.INTERNA NS", "color": "important"}


class ObraRelevanciaParticipante(ModeloBase):
    obrarelevancia = models.ForeignKey(ObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Obra de relevancia')
    filiacion = models.IntegerField(choices=TIPO_FILIACION, default=1, verbose_name=u'Tipo de filiación')
    tipo = models.IntegerField(choices=TIPO_PARTICIPANTE, default=1, verbose_name=u'Tipo de participante')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, verbose_name=u'Persona')

    def __str__(self):
        return u'%s - %s - %s' % (self.obrarelavancia.titulolibro, self.persona, self.get_filiacion_display())

    class Meta:
        verbose_name = u"Participante de Obra de Relevancia"
        verbose_name_plural = u"Participantes de Obras de Relevancia"


class ObraRelevanciaRecorrido(ModeloBase):
    obrarelevancia = models.ForeignKey(ObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Obra de relevancia')
    fecha = models.DateField(verbose_name=u'Fecha recorrido')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, verbose_name=u"Persona")
    observacion = models.TextField(default='', verbose_name=u'Observación del recorrido')
    estado = models.ForeignKey("sagest.EstadoSolicitud", on_delete=models.CASCADE, verbose_name=u'Estado asignado')

    def __str__(self):
        return u'%s - %s - %s' % (self.obrarelevancia, self.fecha, self.estado.descripcion)

    class Meta:
        verbose_name = u"Recorrido de obra de relevancia"
        verbose_name_plural = u"Recorridos de obra de relevancia"

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.strip().upper()
        super(ObraRelevanciaRecorrido, self).save(*args, **kwargs)


class RubricaObraRelevancia(ModeloBase):
    numero = models.IntegerField(default=0, verbose_name=u'Número de requisito')
    descripcion = models.TextField(default='', verbose_name=u'Descripción')
    observacion = models.CharField(max_length=500, default='', verbose_name=u'Observación')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')

    def __str__(self):
        return u'%s' % (self.descripcion)

    class Meta:
        verbose_name = u"Rúbrica general para Evaluación de Obra de Relevancia"
        verbose_name_plural = u"Rúbricas generales para Evaluaciones de Obras de Relevancia"


class RubricaObraRelevanciaConvocatoria(ModeloBase):
    convocatoria = models.ForeignKey(ConvocatoriaObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Convocatoria')
    rubrica = models.ForeignKey(RubricaObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Rúbrica de Evaluación')
    secuencia = models.IntegerField(default=1, verbose_name=u'Número de orden en el que se listan')

    def __str__(self):
        return u'%s - %s - %s' % (self.convocatoria.descripcion, self.rubrica.descripcion, self.secuencia)

    class Meta:
        verbose_name = u"Rúbrica de Evaluación Obras Relevancia de la convocatoria"
        verbose_name_plural = u"Rúbricas de Evaluación Obras Relevancia de las convocatorias"


class ObraRelevanciaEvaluador(ModeloBase):
    obrarelevancia = models.ForeignKey(ObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Obra de Relevancia')
    persona = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, verbose_name=u"Evaluador")
    tipo = models.IntegerField(default=1, choices=TIPO_EVALUADOR, verbose_name=u'Tipo de evaluador')
    notificado = models.BooleanField(default=False, verbose_name=u'Notificado cómo evaluador')

    def __str__(self):
        return u'%s - %s - %s' % (self.obrarelevancia, self.persona, self.get_tipo_display())

    class Meta:
        verbose_name = u"Evaluador de Obra de Relevancia"
        verbose_name_plural = u"Evaluadores de Obras de Relevancia"


class EvaluacionObraRelevancia(ModeloBase):
    obrarelevancia = models.ForeignKey(ObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Obra de Relevancia')
    fecha = models.DateField(verbose_name=u'Fecha de evaluación')
    fechaconfirma = models.DateField(blank=True, null=True, verbose_name=u'Fecha confirmación del evaluador')
    tipo = models.IntegerField(default=1, choices=TIPO_EVALUACION, verbose_name=u'Tipo de evaluación')
    evaluador = models.ForeignKey("sga.Persona", on_delete=models.CASCADE, verbose_name=u"Persona evaluador")
    titulo = models.ForeignKey("sga.Titulacion", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Título académico del evaluador")
    cumplerequisito = models.BooleanField(default=False, verbose_name=u'Cumple los requisitos para ser declarada obra relevante')
    observacion = models.TextField(default='', verbose_name=u'Observaciones')
    archivo = models.FileField(upload_to='obrarelevancia/evaluacion/generado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evaluación')
    archivofirmado = models.FileField(upload_to='obrarelevancia/evaluacion/firmado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de la evaluación firmada')
    revisor = models.ForeignKey("sga.Persona", related_name="+", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona que revisa documento firmado")
    fecharevision = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha revisión')
    revisado = models.BooleanField(default=False, verbose_name=u'Revisado por Coordinación investigación')
    observacionrevision = models.TextField(default='', verbose_name=u'Observaciones por Coordinación de investigación')
    estado = models.IntegerField(default=1, choices=ESTADO_EVALUACION_OBRA, verbose_name=u'Estado de la evaluación')

    def __str__(self):
        return u'%s - %s - %s' % (self.obrarelevancia.titulolibro, self.cumplerequisito, self.get_estado_display())

    class Meta:
        verbose_name = u"Evaluación de Obras de Relevancia"
        verbose_name_plural = u"Evaluaciones de Obras de Relevancia"

    def color_estado(self):
        if self.estado == 1:
            return 'inverse'
        elif self.estado == 2:
            return 'info'
        elif self.estado == 3:
            return 'default'
        elif self.estado == 4:
            return 'info'
        elif self.estado == 5:
            return 'warning'
        elif self.estado == 6:
            return 'success'
        else:
            return 'important'

    def observacion_estado(self):
        if self.estado == 1:
            return 'Evaluación en curso'
        elif self.estado == 2:
            return 'Acta de evaluación generada'
        elif self.estado == 3:
            return 'Acta de evaluación firmada'
        elif self.estado == 4:
            return 'Acta de evaluación subida'
        elif self.estado == 5:
            return 'Evaluación confirmada'
        elif self.estado == 6:
            return 'Evaluación Cerrada'
        else:
            return 'Acta de evaluación con novedades'

    def detalle_rubricas(self):
        return self.evaluacionobrarelevanciadetalle_set.filter(status=True).order_by('id')

    def direcciones_email_evaluador(self):
        direccionesemail = ""
        if self.evaluador.lista_emails():
            direccionesemail = ", ".join(self.evaluador.lista_emails())
        return direccionesemail

    def telefonos_contacto_evaluador(self):
        telefonos = ""
        if self.evaluador.lista_telefonos():
            telefonos = ", ".join(self.evaluador.lista_telefonos())
        return telefonos

    def puede_subir_actafirmada(self):
        return self.tipo == 2 and self.estado in [2, 3, 4]

    def puede_confirmar(self):
        return self.estado == 3

    def puede_cerrar(self):
        return self.estado in [5, 6, 7]


class EvaluacionObraRelevanciaDetalle(ModeloBase):
    evaluacion = models.ForeignKey(EvaluacionObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Evaluación de Obra de Relevancia')
    numero = models.IntegerField(default=1, verbose_name=u'Número orden / secuencia')
    rubrica = models.ForeignKey(RubricaObraRelevancia, on_delete=models.CASCADE, verbose_name=u'Rúbrica de Evaluación')
    cumple = models.BooleanField(default=False, verbose_name=u'Cumple con rúbrica')
    observacion = models.TextField(default='', verbose_name=u'Observaciones')

    def __str__(self):
        return u'%s - %s - %s' % (self.evaluacion, self.rubrica.descripcion, self.cumple)

    class Meta:
        verbose_name = u"Detalle de Evaluación de Obras de Relevancia"
        verbose_name_plural = u"Detalles Evaluación de Obras de Relevancia"


class CriterioEvaluacionInvestigacion(ModeloBase):
    numero = models.IntegerField(default=0, verbose_name=u'Número')
    descripcion = models.CharField(max_length=250, default='', verbose_name=u'Descripción')
    medioverificacion = models.CharField(max_length=250, default='', verbose_name=u'Medio de verificación')
    tipo = models.IntegerField(choices=TIPO_CRITERIO_EVALUACION_PCIENTIFICA, default=1, verbose_name=u'Tipo de criterio')
    vigente = models.BooleanField(default=True, verbose_name=u'Vigente')

    def __str__(self):
        return '{} - {} - {}'.format(self.numero, self.descripcion, self.medioverificacion)

    class Meta:
        verbose_name = u"Criterio de Evaluación de Investigación"
        verbose_name_plural = u"Criterios de Evaluación de Investigación"


class PeriodoEvaluacionInvestigacion(ModeloBase):
    descripcion = models.CharField(max_length=150, default='', verbose_name=u'Descripción')
    inicio = models.DateField(verbose_name=u'Fecha inicio de evaluación')
    fin = models.DateField(verbose_name=u'Fecha fin de evaluación')
    instructivo = models.FileField(upload_to='evaluacioninvestigacion/periodo/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo del instructivo')

    def __str__(self):
        return '{} - {} - {}'.format(self.descripcion, self.inicio, self.fin)

    class Meta:
        verbose_name = u"Periodo de Evaluación de Investigación"
        verbose_name_plural = u"Periodos de Evaluación de Investigación"


class CriterioPeriodoEvaluacionInvestigacion(ModeloBase):
    periodo = models.ForeignKey(PeriodoEvaluacionInvestigacion, on_delete=models.CASCADE, verbose_name=u'Periodo de Evaluación de Investigación')
    criterio = models.ForeignKey(CriterioEvaluacionInvestigacion, on_delete=models.CASCADE, verbose_name=u'Criterio de Evaluación de Investigación')
    porcentaje = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name=u'% calificación')

    def __str__(self):
        return '{} - {} - {}'.format(self.periodo.descripcion, self.criterio.descripcion, self.porcentaje)

    class Meta:
        verbose_name = u"Criterio del Periodo de Evaluación de Investigación"
        verbose_name_plural = u"Criterios del Periodo de Evaluación de Investigación"


class UserCriterioRevisor(ModeloBase):
    persona = models.ForeignKey('sga.Persona', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona")
    criteriodocenciaperiodo = models.ForeignKey('sga.CriterioDocenciaPeriodo', blank=True, null=True, on_delete=models.CASCADE)
    criterioinvestigacionperiodo = models.ForeignKey('sga.CriterioInvestigacionPeriodo', blank=True, null=True, on_delete=models.CASCADE)
    criteriogestionperiodo = models.ForeignKey('sga.CriterioGestionPeriodo', blank=True, null=True, on_delete=models.CASCADE)
    tiporevisor = models.IntegerField(default=1, choices=TIPO_REVISOR, verbose_name=u'Tipo de usuario revisor')
    rol = models.IntegerField(default=1, choices=TIPO_ROL, verbose_name=u'Tipo de usuario revisor')

    def __str__(self):
        return u'%s' % (self.persona)

    def get_gruporevision(self):
        return self.usercriteriorevisorintegrantes_set.filter(status=True)


class BitacoraActividadDocente(ModeloBase):
    profesor = models.ForeignKey('sga.Profesor', blank=True, null=True, verbose_name=u'Profesor', on_delete=models.CASCADE)
    criterio = models.ForeignKey('sga.DetalleDistributivo', blank=True, null=True, verbose_name=u'Criterio', on_delete=models.CASCADE)
    nombre = models.TextField(default='', blank=True, null=True, verbose_name=u'Nombre mes de bitacora')
    fechaini = models.DateTimeField(verbose_name=u'Fecha inicio', blank=True, null=True)
    fechafin = models.DateTimeField(verbose_name=u'Fecha fin', blank=True, null=True)
    estadorevision = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u"Estado de revisión")
    registrotardio = models.BooleanField(default=False, verbose_name=u'Registro tardío', blank=True, null=True)

    # horasplanificadas = models.IntegerField(default=0, verbose_name=u"Horas planificadas", blank=True, null=True)

    def __str__(self):
        return u'%s - %s' % (self.profesor, self.criterio)

    def pendientes_revision(self):
        return self.detallebitacoradocente_set.filter(estadoaprobacion=1, status=True).count()

    def get_detallebitacora(self):
        return self.detallebitacoradocente_set.filter(status=True)

    def actualizar_horas_planificadas(self):
        try:
            inicio, fin = self.criterio.distributivo.periodo.inicio, self.criterio.distributivo.periodo.fin
            if actividad := self.criterio.actividaddetalledistributivo_set.filter(status=True).first():
                inicio, fin = actividad.desde, actividad.hasta

            claseactividad = ClaseActividad.objects.filter(detalledistributivo=self.criterio, detalledistributivo__distributivo__profesor=self.profesor, status=True).values_list('dia', 'turno_id').order_by('inicio', 'dia', 'turno__comienza')
            dt, end, step = self.fechaini, self.fechafin, timedelta(days=1)
            result = []
            while dt <= end:
                if inicio <= dt.date() <= fin:
                    # Excluye el feriado por examenes
                    exclude = 0  # if not (self.criterio.criteriogestionperiodo and self.criterio.criteriogestionperiodo.criterio.id == 220) else 2
                    if not self.criterio.distributivo.periodo.diasnolaborable_set.values('id').filter(status=True, fecha=dt, activo=True).exclude(motivo=exclude):
                        result += [dt.strftime('%Y-%m-%d') for dclase in claseactividad if dt.isocalendar()[2] == dclase[0]]
                dt += step
            # self.horasplanificadas = result.__len__()
            # self.save()
            return result.__len__()
        except Exception as ex:
            ...

    def horas_planificadas(self):
        # if not self.horasplanificadas:
        #     self.actualizar_horas_planificadas()

        return self.actualizar_horas_planificadas()

    def get_porcentaje_cumplimiento(self):
        try:
            from django.db.models import Sum, F, ExpressionWrapper, TimeField

            hp, hr, ha = self.horas_planificadas(), 0, 0

            _get_horas_minutos = lambda th: (th.total_seconds() / 3600).__str__().split('.')
            detallebitacora = self.detallebitacoradocente_set.filter(status=True).annotate(diferencia=ExpressionWrapper(F('horafin') - F('horainicio'), output_field=TimeField())).order_by('fecha', 'horainicio', 'horafin')

            if th := detallebitacora.aggregate(total=Sum('diferencia'))['total']:
                h, m = _get_horas_minutos(th)
                hr = float("%s.%s" % (h, round(float('0.' + m) * 60)))

            if self.estadorevision == 3:
                if th := detallebitacora.filter(estadoaprobacion=2).aggregate(total=Sum('diferencia'))['total']:
                    h, m = _get_horas_minutos(th)
                    ha = float("%s.%s" % (h, round(float('0.' + m) * 60)))

            if hp:
                return r if (r := (((ha if ha else hr) / hp) * 100)) <= 100 else 100

            return 0
        except Exception as ex:
            ...

    def get_historial(self):
        return self.historialbitacoraactividaddocente_set.filter(status=True)


class HistorialBitacoraActividadDocente(ModeloBase):
    bitacora = models.ForeignKey(BitacoraActividadDocente, blank=True, null=True, verbose_name=u'Bitácora', on_delete=models.CASCADE)
    estadorevision = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u"Estado de revisión")
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Persona aprueba/valida', on_delete=models.CASCADE)
    fecharegistrotardio = models.DateField(verbose_name=u'Fecha del registro tardío', blank=True, null=True)

    def __str__(self):
        criterio = ''
        if d := self.bitacora.criterio.criteriodocenciaperiodo:
            criterio = d.criterio.nombre
        if i := self.bitacora.criterio.criterioinvestigacionperiodo:
            criterio = i.criterio.nombre
        if g := self.bitacora.criterio.criteriogestionperiodo:
            criterio = g.criterio.nombre

        return f"{self.persona} - {criterio}"

    class Meta:
        verbose_name = u"Historial de bitácora de actividades"
        verbose_name_plural = u"Historiales de bitácora de actividades"


class DetalleBitacoraDocente(ModeloBase):
    bitacoradocente = models.ForeignKey(BitacoraActividadDocente, blank=True, null=True, verbose_name=u'Bitacora docente', on_delete=models.CASCADE)
    titulo = models.TextField(default='', blank=True, null=True, verbose_name=u'Titulo')
    fecha = models.DateTimeField(verbose_name=u'Fecha', blank=True, null=True)
    horainicio = models.TimeField(verbose_name=u'Hora Inicio', blank=True, null=True)
    horafin = models.TimeField(verbose_name=u'Hora Fin', blank=True, null=True)
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u'Descripción')
    link = models.TextField(default='', blank=True, null=True, verbose_name=u'Link')
    archivo = models.FileField(upload_to='bitacoraactividad/%Y/%m/%d', blank=True, null=True, verbose_name=u'archivo de actividad')
    estadoaprobacion = models.IntegerField(choices=ESTADO_APROBACION, default=1, verbose_name=u"Estado de aprobación")
    observacion = models.TextField(default='', blank=True, null=True, verbose_name=u'Observación')

    def __str__(self):
        return u'%s - %s' % (self.bitacoradocente, self.descripcion)

    def download_link(self):
        return self.archivo.url

    class Meta:
        verbose_name = u"Detalle de Bitácora del Docente"
        verbose_name_plural = u"Detalles de Bitácora del Docente"
        ordering = ['fecha']


class DepartamentoBitacora(ModeloBase):
    detallebitacora = models.ForeignKey(DetalleBitacoraDocente, on_delete=models.CASCADE, verbose_name=u'Bitacora')
    departamento = models.ForeignKey('sagest.Departamento', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Departamento")

    def __str__(self):
        return u'%s' % (self.detallebitacora)


class PersonaBitacora(ModeloBase):
    detallebitacora = models.ForeignKey(DetalleBitacoraDocente, on_delete=models.CASCADE, verbose_name=u'Bitacora')
    persona = models.ForeignKey('sga.Persona', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Persona")

    def __str__(self):
        return u'%s' % (self.detallebitacora)
