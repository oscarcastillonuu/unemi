# -*- coding: UTF-8 -*-
import json
import operator
import os
import random
import time
import sys
from datetime import datetime, timedelta, date
from decimal import Decimal
import PyPDF2

from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models import Sum

from sga.funciones import ModeloBase, null_to_decimal, variable_valor, null_to_numeric
from django.contrib.contenttypes.models import ContentType
from sga.models import Administrativo, Matricula, Persona, TIPO_ARCHIVO_PORSGRADO
from django.db.models import Q
unicode = str

ESTADO_REVISION = (
    (1, u"PENDIENTE"),
    (2, u"APROBADO"),
    (3, u"RECHAZADO"),
)


CONTACTO_MAESTRIA = (
    (1, u"Facebook"),
    (2, u"Instagram"),
    (3, u"LinkedIn"),
    (4, u"Mail"),
    (5, u"WhatsApp"),
    (6, u"Referido por un amigo"),
    (7, u"Otro"),
)

TIPO_COBRO = (
    (1, u"SIN RUBRO"),
    (2, u"MATRICULA"),
    (3, u"COSTO TOTAL"),
)

TIPO_ARCHIVO = (
    (1, u"PDF"),
    (2, u"IMG"),
)

ESTADO_REVISION_APROBAR = (
    (2, u"APROBADO"),
    (3, u"RECHAZADO"),
)


ESTADO_SOLICITUD_MATRICULA = (
    (1, u"SOLICITADO"),
    (2, u"APROBADO"),
    (3, u"RECHAZADO"),
)

ESTADO_EXAMEN_MSC = (
    (1, u'PENDIENTE'),
    (2, u'APROBADO'),
    (3, u'RECHAZADO')
)

ESTADO_ENTREVISTA_MSC = (
    (1, u'APROBADO'),
    (2, u'RECHAZADO')
)

ESTADO_ASESOR_COMERCIAL = (
    (1, u"PENDIENTE"),
    (2, u"ASIGNADO"),
)

ESTADO_FORMA_PAGO = (
    (1, u"PENDIENTE"),
    (2, u"APROBADO"),
    (3, u"RECHAZADO"),
)

ESTADO_CONTRATO = (
    (1, u"PENDIENTE"),
    (2, u"APROBADO"),
    (3, u"RECHAZADO"),
    (4, u"EN PROCESO DE ANULACIÓN"),
    (5, u"ANULADO"),
    (6, u"OFICIO RECHAZADO"),
)

ESTADO_META = (
    (1, u"NO CUMPLIDA"),
    (2, u"CUMPLIDA"),
)

GRUPO_ROL = (
    (1, u"SIN ASIGNAR"),
    (2, u"TERRITORIO 1"),
    (3, u"TERRITORIO 2"),
    (4, u"EJECUTIVO"),
)

MOTIVO_OFICIO = (
    (0, u'---------'),
    (1, u"CAMBIO DE COHORTE"),
    (2, u"CAMBIO DE MODALIDAD DE PAGO"),
    (3, u"CAMBIO DE TABLA DE AMORTIZACIÓN"),
    (4, u"CAMBIO DE MAESTRÍA"),
    (5, u"CAMBIO DE MENCIÓN"),
)

ITINERARIO_ASIGNATURA_MALLA = (
    (0, u'---------'),
    (1, u'1'),
    (2, u'2'),
    (3, u'3')
)

ESTADO_ATENDIDO = (
    (1, u"POR ATENDER"),
    (2, u"ATENDIDO"),
)

#REVISION DE INFORME TITULACION POSGRADO
TIPO_PREGUNTA = (
(1, u"SI_NO"),
)

TIPO_INFORME = (
(1, u"INFORME DE REVISIÓN DEL TRABAJO DE TITULACIÓN"),
)

ESTADO_DICTAMEN = (
(1, u"EN REVISIÓN"),
(2, u"ACEPTADO SIN OBSERVACIONES, PROCEDE A SUSTENTACIÓN"),
(3, u"ACEPTADO CON MODIFICACIONES MENORES, PROCEDE A SUSTENTACIÓN"),
(4, u"DENEGADO, CON OBSERVACIONES MAYORES"),
(5, u"REPROBADO, NO CUMPLE CON LOS PARÁMETROS ESTABLECIDOS"),
)

class MaestriasAdmision(ModeloBase):
    carrera = models.ForeignKey('sga.Carrera', null=True, blank=True, verbose_name=u'Carrera', on_delete=models.CASCADE)
    descripcion = models.CharField(default='', max_length=200, verbose_name=u"Descripcion")
    enlace = models.CharField(default='https://www.unemi.edu.ec/index.php/maestrias/', max_length=500, verbose_name=u'URL de la maestria')
    cuposlibres = models.IntegerField(default=0, verbose_name=u'Cupos a vender de la maestría')


    def __str__(self):
        # return u'%s - %s' % (self.carrera, self.descripcion)
        return self.descripcion

    def en_uso(self):
        return self.cohortemaestria_set.exists()

    def nombre_corto(self):
        return self.carrera.nombre[11:] if self.carrera.nombre[:6] == 'MAESTR' else self.carrera.nombre

    def cohortes_maestria(self):
        return CohorteMaestria.objects.filter(status=True, maestriaadmision=self).order_by('-id')

    def cohortes_maestria_abiertas(self):
        return CohorteMaestria.objects.filter(status=True, maestriaadmision=self, procesoabierto=True).order_by('-id')

    def cohortes_maestria_cerradas(self):
        return CohorteMaestria.objects.filter(status=True, maestriaadmision=self, procesoabierto=False).order_by('-id')

    def cantidad_asesores_asignados(self):
        metas = 0
        if AsesorMeta.objects.filter(status=True, maestria=self).exists():
            metas = AsesorMeta.objects.filter(status=True, maestria=self).values_list('asesor__id').order_by('asesor__id').distinct().count()
        return metas

    def cant_metas_mes(self, anio, mes):
        metas = 0
        if AsesorMeta.objects.filter(status=True, maestria=self, asesor__activo=True).exists():
            idmetas = AsesorMeta.objects.filter(status=True, maestria=self, asesor__activo=True).values_list('id', flat=True).order_by('id').distinct()
            if DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).exists():
                metas = DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).distinct().count()
        return metas

    def cant_sin_metas_mes(self, anio, mes):
        asig = self.cantidad_asesores_asignados()
        metas = 0
        if AsesorMeta.objects.filter(status=True, maestria=self, asesor__activo=True).exists():
            idmetas = AsesorMeta.objects.filter(status=True, maestria=self, asesor__activo=True).values_list('id', flat=True).order_by('id').distinct()
            if DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).exists():
                metas = DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).distinct().count()
        return asig - metas

    def lista_asesores_asignados(self):
        lista = None
        if AsesorMeta.objects.filter(status=True, maestria=self).exists():
            idase = AsesorMeta.objects.filter(status=True, maestria=self).values_list('asesor__id').order_by('asesor__id').distinct()
            lista = AsesorComercial.objects.filter(status=True, id__in=idase)
        return lista

    def ventas_maestrias_validas(self, anio, mes):
        ventas = VentasProgramaMaestria.objects.filter(status=True, inscripcioncohorte__cohortes__maestriaadmision=self, valida=True, fecha__month=mes, fecha__year=anio).count()
        return ventas

    def ventas_validas_asesor(self, anio, mes, asesor):
        ventas = VentasProgramaMaestria.objects.filter(status=True, asesor=asesor,
                                                       inscripcioncohorte__cohortes__maestriaadmision=self, valida=True, fecha__month=mes,
                                                       fecha__year=anio).count()
        return ventas

    def recaudado_maestria_format(self, anio, mes):
        from sagest.models import Rubro, Pago
        ventas = 0
        idins = VentasProgramaMaestria.objects.filter(status=True, inscripcioncohorte__cohortes__maestriaadmision=self, valida=True, fecha__month=mes, fecha__year=anio).values_list('inscripcioncohorte__id', flat=True)
        idr = Rubro.objects.filter(status=True, inscripcion__id__in=idins, inscripcion__cohortes__maestriaadmision=self).values_list('id', flat=True)
        if len(idr) > 0:
            ventas = Decimal(null_to_decimal(Pago.objects.filter(status=True, rubro__id__in=idr).aggregate(total=Sum('valortotal'))['total'], 2)).quantize(Decimal('.01'))
        return f"{ventas:,.2f}"

    def recaudado_asesor(self, anio, mes, asesor):
        from sagest.models import Rubro, Pago
        ventas = 0
        idins = VentasProgramaMaestria.objects.filter(status=True, asesor=asesor,
                                                      inscripcioncohorte__cohortes__maestriaadmision=self, valida=True, fecha__month=mes,
                                                      fecha__year=anio).values_list('inscripcioncohorte__id', flat=True)
        idr = Rubro.objects.filter(status=True, inscripcion__id__in=idins, inscripcion__cohortes__maestriaadmision=self).values_list('id', flat=True)
        if len(idr) > 0:
            ventas = Decimal(null_to_decimal(Pago.objects.filter(status=True, rubro__id__in=idr).aggregate(total=Sum('valortotal'))['total'], 2)).quantize(Decimal('.01'))
        return ventas

    def recaudado_asesor_real(self, anio, mes, asesor):
        from sagest.models import Rubro, Pago
        ventas = self.ventas_validas_asesor(anio, mes, asesor)
        valormaestria = 1
        if CohorteMaestria.objects.filter(status=True, maestriaadmision=self, valorprogramacertificado__gt=0):
            valormaestria = CohorteMaestria.objects.filter(status=True, maestriaadmision=self, valorprogramacertificado__gt=0).order_by('id').first().valorprogramacertificado
        idins = VentasProgramaMaestria.objects.filter(status=True, asesor=asesor,
                                                      inscripcioncohorte__cohortes__maestriaadmision=self, valida=True, fecha__month=mes,
                                                      fecha__year=anio).values_list('inscripcioncohorte__id', flat=True)
        idr = Rubro.objects.filter(status=True, inscripcion__id__in=idins, inscripcion__cohortes__maestriaadmision=self).values_list('id', flat=True)
        ventas = Decimal(null_to_decimal(ventas * valormaestria)).quantize(Decimal('.01'))
        return ventas

    def recaudado_maestria(self, anio, mes):
        from sagest.models import Rubro, Pago
        ventas = 0
        idins = VentasProgramaMaestria.objects.filter(status=True,
                                                      inscripcioncohorte__cohortes__maestriaadmision=self, valida=True, fecha__month=mes,
                                                      fecha__year=anio).values_list('inscripcioncohorte__id', flat=True)
        idr = Rubro.objects.filter(status=True, inscripcion__id__in=idins, inscripcion__cohortes__maestriaadmision=self).values_list('id', flat=True)
        if len(idr) > 0:
            ventas = Decimal(null_to_decimal(Pago.objects.filter(status=True, rubro__id__in=idr).aggregate(total=Sum('valortotal'))['total'], 2)).quantize(Decimal('.01'))
        return ventas

    def recaudado_maestria_real(self, anio, mes):
        from sagest.models import Rubro, Pago
        ventas = self.ventas_maestrias_validas(anio, mes)
        valormaestria = 1
        if CohorteMaestria.objects.filter(status=True, maestriaadmision=self, valorprogramacertificado__gt=0):
            valormaestria = CohorteMaestria.objects.filter(status=True, maestriaadmision=self, valorprogramacertificado__gt=0).order_by('id').first().valorprogramacertificado
        idins = VentasProgramaMaestria.objects.filter(status=True,
                                                      inscripcioncohorte__cohortes__maestriaadmision=self, valida=True, fecha__month=mes,
                                                      fecha__year=anio).values_list('inscripcioncohorte__id', flat=True)
        idr = Rubro.objects.filter(status=True, inscripcion__id__in=idins, inscripcion__cohortes__maestriaadmision=self).values_list('id', flat=True)
        ventas = Decimal(null_to_decimal(ventas * valormaestria)).quantize(Decimal('.01'))
        return ventas

    def porcentaje_cumplimiento(self, anio, mes, asesor):
        from sagest.models import Rubro, Pago
        porcentaje = 0
        ventas = self.ventas_validas_asesor(anio, mes, asesor)


        metas = DetalleAsesorMeta.objects.filter(status=True, inicio__month=mes, inicio__year=anio,
                                                 asesormeta__maestria=self, asesormeta__asesor=asesor).first().cantidad

        if ventas > 0 and metas > 0:
            # if ventas > metas:
            #     porcentaje = 100
            # else:
            tot = (ventas/metas) * 100
            porcentaje = Decimal(null_to_decimal(tot)).quantize(Decimal('.01'))
        else:
            porcentaje = 0
        return porcentaje

    def porcentaje_cumplimiento_maes(self, anio, mes):
        from sagest.models import Rubro, Pago
        porcentaje = 0
        ventas = self.ventas_maestrias_validas(anio, mes)

        metas = DetalleAsesorMeta.objects.filter(status=True, inicio__month=mes, inicio__year=anio, asesormeta__maestria=self).aggregate(total=Sum('cantidad'))['total']

        if ventas > 0 and metas > 0:
            # if ventas > metas:
            #     porcentaje = 100
            # else:
            tot = (ventas/metas) * 100
            porcentaje = Decimal(null_to_decimal(tot)).quantize(Decimal('.01'))
        else:
            porcentaje = 0
        return porcentaje

    def tiene_metas_mes(self, anio, mes):
        estado = False
        if AsesorMeta.objects.filter(status=True, maestria=self).exists():
            idmetas = AsesorMeta.objects.filter(status=True, maestria=self).values_list('id', flat=True).order_by('id').distinct()
            if DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).exists():
                estado = True
        return estado

    def ids_cabecerameta(self):
        try:
            lista = None
            if AsesorMeta.objects.filter(status=True, maestria=self).exists():
                lista = AsesorMeta.objects.filter(status=True, maestria=self).values_list('id', flat=True).order_by('id').distinct()
            return list(lista) if lista != None else lista
        except Exception as ex:
            pass

    def total_metas(self):
        deta = 0
        if AsesorMeta.objects.filter(status=True, maestria=self).exists():
            lista = AsesorMeta.objects.filter(status=True, maestria=self).values_list('id', flat=True).order_by('id').distinct()
            deta = DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=lista).aggregate(total=Sum('cantidad'))['total']
        return deta

    def total_metas_mes(self, mes, anio):
        deta = 0
        if DetalleAsesorMeta.objects.filter(status=True, inicio__month=mes, inicio__year=anio, asesormeta__maestria=self).exists():
            deta = DetalleAsesorMeta.objects.filter(status=True, inicio__month=mes, inicio__year=anio, asesormeta__maestria=self).aggregate(total=Sum('cantidad'))['total']
        return deta

    def sobrante(self, mes, anio):
        cupos = CuposMaestriaMes.objects.get(status=True, maestria=self, inicio__month=mes, inicio__year=anio)
        result = cupos.cuposlibres - self.total_metas_mes(mes, anio)
        return result

    def ofertada(self):
        hoy = datetime.now().date()
        estado = False
        if CohorteMaestria.objects.values('id').filter(maestriaadmision=self, fechainicioinsp__lte=hoy,
                                                       fechafininsp__gte=hoy, activo=True, status=True).exists():
            estado = True

        elif CohorteMaestria.objects.values('id').filter(maestriaadmision=self, fechainiciorequisito__lte=hoy,
                                                        fechafinrequisito__gte=hoy, activo=True, status=True).exists():
            estado = True

        elif CohorteMaestria.objects.values('id').filter(maestriaadmision=self, fechainiciocohorte__lte=hoy,
                                                        fechafincohorte__gte=hoy, activo=True, status=True).exists():
            estado = False
        return estado

    def menciones(self):
        from sga.models import ItinerarioMallaEspecilidad
        malla = self.carrera.malla()
        return ItinerarioMallaEspecilidad.objects.filter(malla=malla, status=True)

    def tiene_requisitos_homologacion(self):
        return True if RequisitosMaestria.objects.filter(status=True, maestria=self) else False

    class Meta:
        verbose_name = u"MaestriasAdmisiones"
        verbose_name_plural = u"MaestriasAdmision"
        ordering = ['descripcion']
        unique_together = ('descripcion',)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(MaestriasAdmision, self).save(*args, **kwargs)

class TablaEntrevistaMaestria(ModeloBase):
    nombre = models.CharField(default='', max_length=250, verbose_name=u'Nombre de tabla')
    estado = models.BooleanField(default=True, verbose_name=u'Estado')

    def __str__(self):
        return u'%s' % self.nombre

    def mi_detalle(self):
        if self.estadoentrevista_set.filter(status=True).exists():
            return self.estadoentrevista_set.filter(status=True)
        return None

    def tabla_seleccionada(self, cohorte):
        return True if self.cohortemaestria_set.filter(status=True, pk=int(cohorte)).exists() else False

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(TablaEntrevistaMaestria, self).save(*args, **kwargs)


class EstadoEntrevista(ModeloBase):
    tablaentrevista = models.ForeignKey(TablaEntrevistaMaestria, blank=True, null=True, verbose_name=u'Tabla', on_delete=models.CASCADE)
    observacion = models.TextField(default='', verbose_name=u'Observación')
    ponderacion = models.FloatField(blank=True, null=True, verbose_name=u'Ponderación')
    # estado = models.IntegerField(choices=ESTADO_ENTREVISTA_MSC, default=1, verbose_name=u'Estado')

    def __str__(self):
        return u'%s' % self.observacion

    def esta_uso(self):
        return True if self.integrantegrupoentrevitamsc_set.all().exists() else False

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.upper()
        super(EstadoEntrevista, self).save(*args, **kwargs)

TIPO_COHORTE = (
    (1, "EXAMEN Y ENTREVISTA"),
    (2, "EXAMEN"),
    (3, "APROBACIÓN DE REQUISITOS"),
)


class CohorteMaestria(ModeloBase):
    descripcion = models.CharField(default='', max_length=200, verbose_name=u"Nombre")
    maestriaadmision = models.ForeignKey(MaestriasAdmision, null=True, blank=True, verbose_name=u'Materia', on_delete=models.CASCADE)
    modalidad = models.ForeignKey('sga.Modalidad', null=True, blank=True, verbose_name=u'Modalidad', on_delete=models.CASCADE)
    tablaentrevista = models.ForeignKey(TablaEntrevistaMaestria, null=True, blank=True, verbose_name=u'Tabla ponderacion entrevista', on_delete=models.CASCADE)
    alias = models.CharField(default='', max_length=100, verbose_name=u"Alias")
    numerochorte = models.IntegerField(default=0, verbose_name=u'Numero de cohorte')
    cupodisponible = models.IntegerField(default=0, verbose_name=u'cupos disponibles de ingreso')
    cantidadgruposexamen = models.IntegerField(default=0, verbose_name=u'Numero de grupos de examen')
    fechainiciocohorte = models.DateField(verbose_name=u"Fecha Inicio cohorte", null=True, blank=True)
    fechafincohorte = models.DateField(verbose_name=u"Fecha Fin cohorte", null=True, blank=True)
    fechainicioinsp = models.DateField(verbose_name=u"Fecha Inicio de cohorte", null=True, blank=True)
    fechafininsp = models.DateField(verbose_name=u"Fecha Fin de cohorte", null=True, blank=True)
    fechainicioextraordinariainsp = models.DateField(verbose_name=u"Fecha inicio extraordinaria de cohorte", null=True, blank=True)
    fechafinextraordinariainsp = models.DateField(verbose_name=u"Fecha Fin extraordinaria de cohorte", null=True, blank=True)
    fechainiciorequisito = models.DateField(verbose_name=u"Fecha Inicio Requisito", null=True, blank=True)
    fechafinrequisito = models.DateField(verbose_name=u"Fecha Fin Requisito", null=True, blank=True)
    fechafinrequisitobeca = models.DateField(verbose_name=u'Fecha fin requisitos de beca', blank=True, null=True)
    fechainicioexamen = models.DateField(verbose_name=u"Fecha inicio examen", null=True, blank=True)
    fechafinexamen = models.DateField(verbose_name=u"Fecha fin examen", null=True, blank=True)
    notaminimaexa = models.FloatField(default=0, verbose_name=u'Nota minima de examen')
    notamaximaexa = models.FloatField(default=0, verbose_name=u'Nota maxima de examen')
    notaminimatest = models.FloatField(default=0, verbose_name=u'Nota minima de test')
    notamaximatest = models.FloatField(default=0, verbose_name=u'Nota maxima test')
    ponderacionminimaentrevista = models.FloatField(default=0, verbose_name=u'Ponderación minima de la entrevista')
    ponderacionmaximaentrevista = models.FloatField(default=0, verbose_name=u'Ponderación maxima de la entrevista')
    tienecostoexamen = models.BooleanField(default=False, verbose_name=u"Tiene costo el examen")
    valorexamen = models.FloatField(default=0, verbose_name=u'Valor del exámen')
    tienecostomatricula = models.BooleanField(default=False, verbose_name=u"Tiene costo la matricula")
    valormatricula = models.FloatField(null=True, blank=True, verbose_name=u'Valor del mátricula')
    tienecuota = models.BooleanField(default=False, verbose_name=u"Tiene cuotas")
    numerocuota = models.IntegerField(null=True, blank=True, verbose_name=u'Numero de cuotas de la maestria')
    valorcuota = models.FloatField(null=True, blank=True, verbose_name=u'Valor de la cuota de la maestria')
    activo = models.BooleanField(default=True, verbose_name=u"Activo")
    tienecostotramite = models.BooleanField(default=False, verbose_name=u"Tiene costo trámite")
    valortramite = models.FloatField(null=True, blank=True, verbose_name=u'Valor del trámite')
    cantidadgruposentrevista = models.IntegerField(default=0,null=True, blank=True, verbose_name=u'Numero de grupos de entrevista')
    minutosrango = models.IntegerField(default=0, verbose_name=u'Cada cuanto minutos son de entrevista por entrevistado')
    archivomatriz = models.FileField(upload_to='archivomatriz/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo')
    totaladmitidoscohorte = models.IntegerField(default=0, verbose_name=u'Total admitidos por cohorte')
    coordinador = models.ForeignKey('sga.Persona', null=True, blank=True, verbose_name=u'Persona', on_delete=models.CASCADE)
    urlmoodle = models.CharField(default='https://aulaposgrado.unemi.edu.ec/', max_length=500, verbose_name=u'url moodle pregrado presencial y virtual')
    keymoodle = models.CharField(default='1823dd47f3c35c924e066289aae91360', max_length=500, verbose_name=u'key moodle')
    procesoabierto = models.BooleanField(default=True, verbose_name=u"Si el proceso esta abierto o no")
    tienecostototal = models.BooleanField(default=False, verbose_name=u"Cuando se genera el rubro total del valor completo para la maestría y no tienen valor de matrícula")
    valorprograma = models.FloatField(default=0, verbose_name=u'Valor total del programa')
    tiporubro = models.ForeignKey('sagest.TipoOtroRubro', blank=True, null=True, verbose_name=u"Tipo", on_delete=models.CASCADE)
    fechavencerubro = models.DateField(verbose_name=u"Fecha vence  rubro", null=True, blank=True)
    observacionrubro = models.TextField(blank=True, null=True, verbose_name=u"Observación rubro")
    fechainiordinaria = models.DateField(verbose_name=u"Fecha inicio matricula ordinaria", null=True, blank=True)
    fechafinordinaria = models.DateField(verbose_name=u"Fecha fin matricula ordinaria", null=True, blank=True)
    fechainiextraordinaria = models.DateField(verbose_name=u"Fecha inicio matricula extraordinaria", null=True, blank=True)
    fechafinextraordinaria = models.DateField(verbose_name=u"Fecha fin matricula extraordinaria", null=True, blank=True)
    valorprogramacertificado = models.FloatField(default=0, verbose_name=u'Valor total del programa para certificado')
    presupuestobeca = models.FloatField(default=0, verbose_name=u'Monto presupuesto para becas')
    tipo = models.IntegerField(choices=TIPO_COHORTE, default=1, verbose_name=u'Estado Email evidencia')
    cuposlibres = models.IntegerField(default=0, verbose_name=u'Cupos libres de la cohorte')
    periodoacademico = models.ForeignKey('sga.Periodo', verbose_name=u'Periodo académico', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return u'%s - %s' % (self.maestriaadmision.descripcion, self.descripcion)

    def en_uso(self):
        return self.requisitosmaestria_set.exists()

    def idnumber(self):
        anoini = self.fechainiciocohorte.year
        anofin = self.fechafincohorte.year
        if anoini != anofin:
            ano = '%s-%s' % (anoini, anofin)
        else:
            ano = '%s' % anoini
        return u'COHORTE%s-%s' % (self.id, ano)

    def puederevisar(self):
        hoy = datetime.now().date()
        if hoy > self.fechafinrequisito:
            return True
        else:
            return False

    def listadorequisitocohorte(self):
        return self.requisitosmaestria_set.filter(status=True).order_by('id')

    def tiene_gruporequisitos(self):
        return self.gruporequisitocohorte_set.filter(status=True)

    def existe_sinproceso(self):
        return self.integrantegrupoentrevitamsc_set.filter(status=True).exists()

    def gruporequisitos(self):
        return self.gruporequisitocohorte_set.filter(status=True)

    def tiene_requisitos(self):
        return self.requisitosmaestria_set.filter(status=True)

    def total_inscritos(self):
        return self.inscripcioncohorte_set.values('id').filter(status=True).count()

    def total_inscritossinnotificar(self):
        return self.inscripcioncohorte_set.values('id').filter(estado_emailevidencia=1, status=True).count()

    def listapreguntas(self,tipo):
        return self.preguntamaestria_set.filter(pregunta__tipopregunta=tipo,status=True)

    def total_preguntas(self):
        return self.preguntamaestria_set.values('id').filter(status=True).count()

    def total_requisitos(self):
        return self.requisitosmaestria_set.values('id').filter(status=True).count()

    def costo_maestria(self):
        if self.tienecuota:
            return null_to_decimal((self.numerocuota * self.valorcuota),2)
        return None

    def totalcosto_maestria(self):
        if self.tienecuota:
            return null_to_decimal((self.numerocuota * self.valorcuota + self.valorexamen + self.valormatricula),2)
        return None

    def puede_subir_requisitos(self):
        fecha = datetime.now().date()
        return True if CohorteMaestria.objects.filter(status=True, pk=self.id, fechainiciorequisito__lte=fecha, fechafinrequisito__gte=fecha).exists() else False

    def total_evidencia_cohorte(self):
        return self.requisitosmaestria_set.values('id').filter(status=True).count()

    def tiene_grupoexamen(self):
        return self.grupoexamenmsc_set.filter(status=True)

    def cant_requisitos(self):
        return self.requisitosmaestria_set.values('id').filter(status=True).count()

    def puede_editar_prespuestobecas(self):
        return not self.inscripcioncohorte_set.values('id').filter(status=True, tipobeca__isnull=False, descuentoposgradomatricula__estado__in=[2, 4]).exists()

    def valor_utilizado_presupuestobecas(self):
        from sga.models import DescuentoPosgradoMatricula
        utilizado = null_to_decimal(DescuentoPosgradoMatricula.objects.filter(inscripcioncohorte__cohortes=self, status=True, estado__in=[2, 4, 8, 10]).aggregate(totalutilizado=Sum('valordescuento'))['totalutilizado'], 2)
        return utilizado

    def saldo_disponible_presupuestobecas(self):
        # from sga.models import DescuentoPosgradoMatricula
        # utilizado = null_to_decimal(DescuentoPosgradoMatricula.objects.filter(inscripcioncohorte__cohortes=self, status=True, estado__in=[2, 4]).aggregate(totalutilizado=Sum('valordescuento'))['totalutilizado'], 2)
        # return Decimal(self.presupuestobeca).quantize(Decimal('.01')) - utilizado
        return self.presupuestobeca - self.valor_utilizado_presupuestobecas()

    def total_recaudado_maestria(self, anio):
        from sagest.models import Rubro, Pago
        try:
            total_recaudado = 0
            listado_admitidos_pagos = []

            idadmitidos = InscripcionCohorte.objects.filter(status=True, cohortes__id=self.id).values_list('id', flat=True)

            for idadmitido in idadmitidos:
                if Rubro.objects.filter(inscripcion__id=idadmitido, status=True).exists():
                    admitido = InscripcionCohorte.objects.get(pk=idadmitido)
                    rubrocohorte = Rubro.objects.get(inscripcion=admitido)
                    costomaestria = admitido.cohortes.valorprogramacertificado

                    cantinscripciones = InscripcionCohorte.objects.filter(inscripcionaspirante__id=admitido.inscripcionaspirante.id).count()

                    if costomaestria > 0:
                        diezporciento = costomaestria * 0.10

                        if costomaestria == rubrocohorte.valor:
                            valorpagado = admitido.total_pagado_cohorte()
                        else:
                            if cantinscripciones > 1:
                                valorpagado = admitido.total_pagado_cohorte()
                            else:
                                valorpagado = admitido.inscripcionaspirante.persona.total_pagado_maestria()

                        if valorpagado >= diezporciento:
                            if anio != 0:
                                if Pago.objects.filter(rubro__inscripcion__id=admitido.id, fecha__year=anio).order_by('id').exists():
                                    pago = Pago.objects.filter(rubro__inscripcion__id=admitido.id, fecha__year=anio).order_by('id').first()
                                    listado_admitidos_pagos.append(pago.rubro.inscripcion.id)
                            else:
                                listado_admitidos_pagos.append(admitido.id)

            ventas = Rubro.objects.filter(status=True, inscripcion_id__in=listado_admitidos_pagos)

            for venta in ventas:
                if venta.matricula:
                    tot_venta = venta.matricula.total_pagado_alumno_rubro_maestria()
                else:
                    tot_venta = null_to_numeric(
                        Pago.objects.filter(rubro__persona=venta.persona, status=True, rubro__tipo__tiporubro=1).exclude(pagoliquidacion__isnull=False).exclude(
                            factura__valida=False).aggregate(valor=Sum('valortotal'))['valor'])

                total_recaudado += tot_venta

            return total_recaudado
        except Exception as ex:
            pass

    def total_por_recaudar_maestria(self, anio):
        from sagest.models import Pago, Rubro
        try:
            total_maestria = 0
            listado_admitidos_pagos = []

            idadmitidos = InscripcionCohorte.objects.filter(status=True, cohortes__id=self.id).values_list('id', flat=True)

            for idadmitido in idadmitidos:
                if Rubro.objects.filter(inscripcion__id=idadmitido, status=True).exists():
                    admitido = InscripcionCohorte.objects.get(pk=idadmitido)
                    rubrocohorte = Rubro.objects.get(inscripcion=admitido)
                    costomaestria = admitido.cohortes.valorprogramacertificado

                    cantinscripciones = InscripcionCohorte.objects.filter(inscripcionaspirante__id=admitido.inscripcionaspirante.id).count()

                    if costomaestria > 0:
                        diezporciento = costomaestria * 0.10

                        if costomaestria == rubrocohorte.valor:
                            valorpagado = admitido.total_pagado_cohorte()
                        else:
                            if cantinscripciones > 1:
                                valorpagado = admitido.total_pagado_cohorte()
                            else:
                                valorpagado = admitido.inscripcionaspirante.persona.total_pagado_maestria()

                        if valorpagado >= diezporciento:
                            if anio != 0:
                                if Pago.objects.filter(rubro__inscripcion__id=admitido.id, fecha__year=anio).order_by('id').exists():
                                    pago = Pago.objects.filter(rubro__inscripcion__id=admitido.id, fecha__year=anio).order_by('id').first()
                                    listado_admitidos_pagos.append(pago.rubro.inscripcion.id)
                            else:
                                listado_admitidos_pagos.append(admitido.id)

            ventas = Rubro.objects.filter(status=True, inscripcion_id__in=listado_admitidos_pagos)

            for venta in ventas:
                tot_venta = venta.inscripcion.cohortes.valorprogramacertificado

                total_maestria += tot_venta

            por_recaudar =  total_maestria - float(self.total_recaudado_maestria(anio))

            return por_recaudar
        except Exception as ex:
            pass

    def total_admitidos_maestria(self):
        from sagest.models import Rubro

        idadmitidos = InscripcionCohorte.objects.filter(status=True, cohortes__id=self.id).values_list('id', flat=True)

        admitidos = Rubro.objects.filter(status=True, admisionposgradotipo__in=[2, 3],
                                                          inscripcion_id__in=idadmitidos).count()

        return admitidos

    def total_maestrantes(self):
        from sagest.models import Rubro

        listado_admitidos_pagos = []
        idadmitidos = InscripcionCohorte.objects.filter(status=True, cohortes__id=self.id).values_list('id', flat=True)

        for idadmitido in idadmitidos:
            if Rubro.objects.filter(inscripcion__id=idadmitido, status=True).exists():
                admitido = InscripcionCohorte.objects.get(pk=idadmitido)
                rubrocohorte = Rubro.objects.get(inscripcion=admitido)
                costomaestria = admitido.cohortes.valorprogramacertificado

                cantinscripciones = InscripcionCohorte.objects.filter(inscripcionaspirante__id=admitido.inscripcionaspirante.id).count()

                if costomaestria > 0:
                    diezporciento = costomaestria * 0.10

                    if costomaestria == rubrocohorte.valor:
                        valorpagado = admitido.total_pagado_cohorte()
                    else:
                        if cantinscripciones > 1:
                            valorpagado = admitido.total_pagado_cohorte()
                        else:
                            valorpagado = admitido.inscripcionaspirante.persona.total_pagado_maestria()

                    if valorpagado >= diezporciento:
                        listado_admitidos_pagos.append(admitido.id)

        maestrantes = Rubro.objects.filter(status=True, admisionposgradotipo__in=[2, 3],
                                                          inscripcion_id__in=listado_admitidos_pagos).count()

        return maestrantes

    def total_registrados(self):
        return InscripcionCohorte.objects.filter(status=True, cohortes=self).count()

    def tiene_requisitos_comercializacion(self):
        return True if RequisitosMaestria.objects.filter(status=True, cohorte=self, obligatorio=True, requisito__claserequisito__clasificacion__id=3).exists() else False

    def ventas_cohortes_facturadas(self, desde, hasta):
        ventas = VentasProgramaMaestria.objects.filter(status=True, inscripcioncohorte__cohortes=self, facturado=True, fecha__range=(desde, hasta)).count()
        return ventas

    def ventas_cohortes_reportadas(self, desde, hasta):
        ventas = VentasProgramaMaestria.objects.filter(status=True, inscripcioncohorte__cohortes=self, facturado=False, fecha__range=(desde, hasta)).count()
        return ventas

    def ventas_cohortes_rechazadas(self, desde, hasta):
        ventas = VentasProgramaMaestria.objects.filter(status=True, inscripcioncohorte__cohortes=self, valida=False, fecha__range=(desde, hasta)).count()
        return ventas

    def ventas_cohortes_validas(self, desde, hasta):
        ventas = VentasProgramaMaestria.objects.filter(status=True, inscripcioncohorte__cohortes=self, valida=True, fecha__range=(desde, hasta)).count()
        return ventas

    def cantidad_asesores_asignados(self):
        metas = 0
        if AsesorMeta.objects.filter(status=True, cohorte=self).exists():
            metas = AsesorMeta.objects.filter(status=True, cohorte=self).values_list('asesor__id').order_by('asesor__id').distinct().count()
        return metas

    def cantidad_asesores_asignados_ina(self):
        metas = 0
        if AsesorMeta.objects.filter(status=True, cohorte=self, asesor__activo=False).exists():
            metas = AsesorMeta.objects.filter(status=True, cohorte=self, asesor__activo=False).values_list('asesor__id', flat=True).order_by('asesor__id').distinct().count()
        return metas

    def cantidad_asesores_asignados_act(self):
        metas = 0
        if AsesorMeta.objects.filter(status=True, cohorte=self, asesor__activo=True).exists():
            metas = AsesorMeta.objects.filter(status=True, cohorte=self, asesor__activo=True).values_list('asesor__id', flat=True).order_by('asesor__id').distinct().count()
        return metas

    def cant_metas_mes(self, anio, mes):
        metas = 0
        if AsesorMeta.objects.filter(status=True, cohorte=self, asesor__activo=True).exists():
            idmetas = AsesorMeta.objects.filter(status=True, cohorte=self, asesor__activo=True).values_list('id', flat=True).order_by('id').distinct()
            if DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).exists():
                metas = DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).distinct().count()
        return metas

    def cant_sin_metas_mes(self, anio, mes):
        asig = self.cantidad_asesores_asignados()
        metas = 0
        if AsesorMeta.objects.filter(status=True, cohorte=self, asesor__activo=True).exists():
            idmetas = AsesorMeta.objects.filter(status=True, cohorte=self, asesor__activo=True).values_list('id', flat=True).order_by('id').distinct()
            if DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).exists():
                metas = DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).distinct().count()
        return asig - metas

    def tiene_metas_mes(self, anio, mes):
        estado = False
        if AsesorMeta.objects.filter(status=True, cohorte=self).exists():
            idmetas = AsesorMeta.objects.filter(status=True, cohorte=self).values_list('id', flat=True).order_by('id').distinct()
            if DetalleAsesorMeta.objects.filter(status=True, asesormeta__id__in=idmetas, inicio__month=mes, inicio__year=anio).exists():
                estado = True
        return estado

    class Meta:
        verbose_name = u"CohorteMaestria"
        verbose_name_plural = u"CohorteMaestriaes"
        ordering = ['maestriaadmision']

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        self.alias = self.alias.upper()
        super(CohorteMaestria, self).save(*args, **kwargs)


class InscripcionAspirante(ModeloBase):
    persona = models.ForeignKey('sga.Persona', verbose_name=u'Persona', on_delete=models.CASCADE)
    cohortes = models.ForeignKey(CohorteMaestria, blank=True, null=True, verbose_name=u'Maestria periodo', on_delete=models.CASCADE)
    titulograduado = models.CharField(default='', max_length=500, verbose_name=u'Titulo graduado')
    titulouniversidad = models.CharField(default='', max_length=500, verbose_name=u'Como se informo')
    activo = models.BooleanField(default=True, verbose_name=u"Activo")

    def __str__(self):
        return u'%s' % self.persona

    def segunda_inscripcion(self):
        return True if InscripcionCohorte.objects.filter(status=True, inscripcionaspirante=self, doblepostulacion=True).exists() else False

class ConfigFinanciamientoCohorte(ModeloBase):
    descripcion = models.TextField(blank=True, null=True, verbose_name=u"Descripción")
    cohorte = models.ForeignKey(CohorteMaestria, null=True, blank=True, verbose_name=u'Cohorte Maestria', on_delete=models.CASCADE)
    valormatricula = models.FloatField(default=0, blank=True, null=True, verbose_name=u'Valor Matricula')
    valorarancel = models.FloatField(default=0, blank=True, null=True, verbose_name=u'Valor Arancel')
    valortotalprograma = models.FloatField(default=0, blank=True, null=True, verbose_name=u'Valor total del programa')
    porcentajeminpagomatricula = models.FloatField(default=0, blank=True, null=True, verbose_name=u'Porcentaje mín pago matrícula')
    maxnumcuota = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'Máx número de cuotas')
    fecha = models.DateField(verbose_name=u"Fecha corte de cuotas", null=True, blank=True)

    def __str__(self):
        return f'{self.descripcion} - {self.porcentajeminpagomatricula}% - {self.maxnumcuota} cuotas'
        # return u'%s - %s - %s' % (self.descripcion, str(self.porcentajeminpagomatricula), str(self.maxnumcuota))
        # return u'%s' % self.descripcion

    class Meta:
        verbose_name = u'Configuración Financiamiento Cohorte'
        verbose_name_plural = u'Configuraciones Financiamiento Cohorte'
        ordering = ('id',)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(ConfigFinanciamientoCohorte,self).save(*args, **kwargs)

    def tablaamortizacioncohortemaestria(self, insc, hoy):
        tablaamortizacion = []
        maxnumcuota = self.maxnumcuota
        valortotalprograma = Decimal(null_to_decimal(self.valortotalprograma, 2)).quantize(Decimal('.01'))
        porcentajemae = Decimal(null_to_decimal(self.porcentajeminpagomatricula, 2)).quantize(Decimal('.01'))
        valormatricula = Decimal(null_to_decimal((valortotalprograma * porcentajemae) / 100, 2)).quantize(Decimal('.01'))
        valorarancel = valortotalprograma - valormatricula
        fechainiciopago = hoy
        fechavence = self.fecha

        # Registro de pago inicial, matricula
        tablaamortizacion += [('', '', '', valormatricula, valorarancel)]

        # Generacion de cuotas convertir la fecha
        dia = int(fechavence.day)
        mes = int(fechavence.month)
        anio = int(fechavence.year)
        bandera = 0
        valorcuota = 0
        valordescontado = 0
        valorpendiente = 0
        ultimo_dia = int(fechavence.day)

        # Generacion de la primera cuota aplicando porcentaje de la cuota inicial
        for n in range(maxnumcuota):
            if bandera == 0:
                fechavence = date(anio, mes, dia)
                valorcuota = Decimal(null_to_decimal(valorarancel / maxnumcuota)).quantize(Decimal('.01'))
                valorpendiente = valorarancel - valorcuota
                tablaamortizacion += [(n+1, fechainiciopago, fechavence, valorcuota, valorpendiente)]
                valordescontado = valorcuota + valorcuota
                valorpendiente = valorarancel - valordescontado
                bandera = 1
                mes += 1
                if mes == 13:
                    mes = 1
                    anio += 1
            else:
                salio = True
                d = 0
                while salio:
                    try:
                        fechavence = date(anio, mes, dia - d)
                        salio = False
                    except:
                        salio = True
                    d += 1
                mes += 1
                if mes == 13:
                    mes = 1
                    anio += 1
                if n == maxnumcuota-1:
                    # Generacion de cuota final para evitar perder decimales(centavo$)
                    valorfinal = Decimal(null_to_decimal(valorarancel)).quantize(Decimal('.01')) - (valorcuota * (maxnumcuota - 1))
                    valordescontado = valordescontado + valorfinal - valorcuota
                    valorpendiente = valorarancel - valordescontado
                    tablaamortizacion += [(maxnumcuota, fechainiciopago, fechavence, valorfinal, valorpendiente)]
                else:
                    tablaamortizacion += [(n + 1, fechainiciopago, fechavence, valorcuota, valorpendiente)]
                    valordescontado = valordescontado + valorcuota
                    valorpendiente = valorarancel - valordescontado
        return tablaamortizacion

class GrupoRequisitoCohorte(ModeloBase):
    observacion = models.TextField(blank=True, null=True, verbose_name=u"Observación")
    cohorte = models.ForeignKey(CohorteMaestria, null=True, blank=True, verbose_name=u'Cohorte Maestria', on_delete=models.CASCADE)
    orden = models.IntegerField(blank=True, null=True, verbose_name=u'Orden nivel')

    def __str__(self):
        return u'%s' % self.observacion

    def mis_requisitosgrupos(self):
        return self.requisitosgrupocohorte_set.filter(status=True)

class RolAsesor(ModeloBase):
    descripcion = models.TextField(default='', verbose_name=u'Descripcion')

    def __str__(self):
        return u'%s' % self.descripcion

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(RolAsesor,self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Rol Asesor"
        verbose_name_plural = u"Roles Asesores"
        ordering = ['id']


class AsesorComercial(ModeloBase):
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Asesor Comercial', on_delete=models.CASCADE)
    rol = models.ForeignKey(RolAsesor, blank=True, null=True, verbose_name=u'Rol del Asesor', on_delete=models.CASCADE)
    fecha_desde = models.DateTimeField(blank=True, null=True, verbose_name=u'Vigencia Asesor Desde')
    fecha_hasta = models.DateTimeField(blank=True, null=True, verbose_name=u'Vigencia Asesor Hasta')
    telefono = models.CharField(default='', max_length=50, verbose_name=u"Telefono de trabajo")
    activo = models.BooleanField(blank=True, null=True, default=True, verbose_name=u"Activo")
    rolgrupo = models.IntegerField(choices=GRUPO_ROL, default=1, verbose_name=u'Grupo Territorio')

    def __str__(self):
        return u'%s' % self.persona

    def cohortesasignadas(self):
        return AsesorMeta.objects.filter(asesor_id=self.id, status=True).distinct().order_by('-id')

    def cantidad_reservaciones_pendientes(self):
        return HistorialReservacionProspecto.objects.filter(persona=self.persona, status=True, estado_asesor=1).count()

    def asignados(self):
        aa = datetime.now().date().year
        asi =aa + 1
        return InscripcionCohorte.objects.filter(status=True, asesor=self, fecha_creacion__year__in=[aa, asi]).count()

    def atendidos(self):
        aa = datetime.now().date().year
        asi =aa + 1
        return InscripcionCohorte.objects.filter(status=True, asesor=self, tiporespuesta__isnull=False, fecha_creacion__year__in=[aa, asi]).count()

    def no_atendidos(self):
        aa = datetime.now().date().year
        asi =aa + 1
        return InscripcionCohorte.objects.filter(status=True, asesor=self, tiporespuesta__isnull=True, fecha_creacion__year__in=[aa, asi]).count()

    def ventas_obtenidas(self):
        aa = datetime.now().date().year
        asi =aa + 1
        return VentasProgramaMaestria.objects.filter(status=True, asesor=self, valida=True, fecha__year__in=[aa, asi]).count()

    def ventas_obtenidas_fecha(self, lista):
        return VentasProgramaMaestria.objects.filter(status=True, asesor=self, valida=True, inscripcioncohorte__id__in=lista).count()

    def tiene_meta_cohorte(self, idc):
        return True if AsesorMeta.objects.filter(asesor_id=self.id, status=True, cohorte__id=idc) else False

    def perfil_administrativo(self):
        from sga.models import PerfilUsuario, Administrativo
        if Administrativo.objects.filter(status=True, persona=self.persona).exists():
            admin = Administrativo.objects.filter(status=True, persona=self.persona).first()
            if PerfilUsuario.objects.filter(status=True, persona=self.persona, administrativo=admin).exists():
                perfil = PerfilUsuario.objects.filter(status=True, persona=self.persona, administrativo=admin).first()
                return perfil
            else:
                return None
        else:
            return None

    def territorios(self):
        return AsesorTerritorio.objects.filter(status=True, asesor=self)

    class Meta:
        verbose_name = u"Asesor Comercial"
        verbose_name_plural = u"Asesores Comerciales"
        ordering = ['id']


class AsesorMeta(ModeloBase):
    asesor = models.ForeignKey(AsesorComercial, blank=True, null=True, verbose_name=u'Asesor Comercial', on_delete=models.CASCADE)
    fecha_inicio_meta = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de Inicio Meta')
    fecha_fin_meta = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de Fin Meta')
    meta = models.IntegerField(blank=True, null=True, verbose_name=u'Meta')
    cohorte = models.ForeignKey(CohorteMaestria, null=True, blank=True, verbose_name=u'Cohorte Maestria', on_delete=models.CASCADE)
    maestria = models.ForeignKey(MaestriasAdmision, null=True, blank=True, verbose_name=u'Maestria asignada', on_delete=models.CASCADE)
    estado = models.IntegerField(choices=ESTADO_META, default=1, verbose_name=u'Estado de la meta')

    def __str__(self):
        return u'%s' % self.asesor

    def total_ventas_reportadas(self):
        try:
            return VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesor, inscripcioncohorte__cohortes=self.cohorte, facturado=False).count()
        except Exception as ex:
            pass

    def total_ventas_facturadas(self):
        try:
            return VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesor, inscripcioncohorte__cohortes=self.cohorte, facturado=True).count()
        except Exception as ex:
            pass

    def total_ventas_validas(self):
        try:
            return VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesor, inscripcioncohorte__cohortes=self.cohorte, valida=True).count()
        except Exception as ex:
            pass

    def total_ventas_rechazadas(self):
        try:
            return VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesor, inscripcioncohorte__cohortes=self.cohorte, valida=False).count()
        except Exception as ex:
            pass

    def metas_pendientes(self):
        return self.meta - self.total_ventas_validas()

    def estado_meta(self):
        estado = False
        if self.total_ventas_validas() > self.meta:
            estado = True
        return estado

    def listado_maestrantes(self):
        from sagest.models import Rubro

        listado_ventas = []

        idadmitidos = InscripcionCohorte.objects.filter(cohortes=self.cohorte,
                                                        status=True,
                                                        asesor = self.asesor).values_list('id', flat=True)

        for idadmitido in idadmitidos:
            if Rubro.objects.filter(inscripcion__id=idadmitido).exists():
                admitido = InscripcionCohorte.objects.get(pk=idadmitido)
                rubrocohorte = Rubro.objects.get(inscripcion=admitido)
                costomaestria = admitido.cohortes.valorprogramacertificado
                diezporciento = costomaestria * 0.10

                if costomaestria == rubrocohorte.valor:
                    valorpagado = admitido.total_pagado_cohorte()
                else:
                    valorpagado = admitido.inscripcionaspirante.persona.total_pagado_maestria()

                if valorpagado >= diezporciento:
                    listado_ventas.append(admitido.id)

        return Rubro.objects.filter(status=True, admisionposgradotipo__in=[2, 3], inscripcion_id__in=listado_ventas)

    def cant_vent_ase(self, anio, mes):
        metas = 0
        if VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.maestria, fecha__year=anio, fecha__month=mes, valida=True).exists():
            metas = VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.maestria, fecha__year=anio, fecha__month=mes, valida=True).count()
        return metas

    class Meta:
        verbose_name = u"Asesor Meta"
        verbose_name_plural = u"Asesores Metas"
        ordering = ['id']

class DetalleAsesorMeta(ModeloBase):
    asesormeta = models.ForeignKey(AsesorMeta, blank=True, null=True, verbose_name=u'Cabecera meta', on_delete=models.CASCADE)
    inicio = models.DateField(blank=True, null=True, verbose_name=u'Inicio de meta')
    fin = models.DateField(blank=True, null=True, verbose_name=u'Fin de meta')
    cantidad = models.IntegerField(blank=True, null=True, default=0, verbose_name=u'Cantidad de ventas a conseguir')
    estado = models.IntegerField(choices=ESTADO_META, default=1, verbose_name=u'Estado de la meta')

    def __str__(self):
        return u'%s - %s' % (self.asesormeta.asesor, self.cantidad)

    def cant_vent_rep(self):
        metas = 0
        anio = self.inicio.year
        mes = self.inicio.month
        if VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesormeta.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.asesormeta.maestria, fecha__year=anio, fecha__month=mes, facturado=False).exists():
            metas = VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesormeta.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.asesormeta.maestria, fecha__year=anio, fecha__month=mes, facturado=False).count()
        return metas

    def cant_vent_fac(self):
        metas = 0
        anio = self.inicio.year
        mes = self.inicio.month
        if VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesormeta.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.asesormeta.maestria, fecha__year=anio, fecha__month=mes, facturado=True).exists():
            metas = VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesormeta.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.asesormeta.maestria, fecha__year=anio, fecha__month=mes, facturado=True).count()
        return metas

    def cant_vent_val(self):
        metas = 0
        anio = self.inicio.year
        mes = self.inicio.month
        if VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesormeta.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.asesormeta.maestria, fecha__year=anio, fecha__month=mes, valida=True).exists():
            metas = VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesormeta.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.asesormeta.maestria, fecha__year=anio, fecha__month=mes, valida=True).count()
        return metas

    def cant_vent_rec(self):
        metas = 0
        anio = self.inicio.year
        mes = self.inicio.month
        if VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesormeta.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.asesormeta.maestria, fecha__year=anio, fecha__month=mes, valida=False).exists():
            metas = VentasProgramaMaestria.objects.filter(status=True, asesor=self.asesormeta.asesor, inscripcioncohorte__cohortes__maestriaadmision=self.asesormeta.maestria, fecha__year=anio, fecha__month=mes, valida=False).count()
        return metas

    def metas_pendientes(self):
        if self.cant_vent_val() > self.cantidad:
            tot = 0
        else:
            tot = self.cantidad - self.cant_vent_val()
        return tot

    def estado_meta(self):
        estado = False
        if self.cant_vent_val() >= self.cantidad:
            estado = True
        return estado

    def mesmeta(self):
        return int(self.inicio.month)

    def porcentaje_cumplimiento(self):
        from sagest.models import Rubro, Pago
        porcentaje = 0
        ventas = self.cant_vent_val()


        metas = self.cantidad

        if ventas > 0 and metas > 0:
            tot = (ventas/metas) * 100
            porcentaje = Decimal(null_to_decimal(tot)).quantize(Decimal('.01'))
        else:
            porcentaje = 0
        return porcentaje

    class Meta:
        verbose_name = u"Detalle de metas"
        verbose_name_plural = u"Detalle de metas mensuales"
        ordering = ['id']

class CuposMaestriaMes(ModeloBase):
    maestria = models.ForeignKey(MaestriasAdmision, null=True, blank=True, verbose_name=u'Maestria', on_delete=models.CASCADE)
    inicio = models.DateField(blank=True, null=True, verbose_name=u'Inicio de meta')
    fin = models.DateField(blank=True, null=True, verbose_name=u'Fin de meta')
    cuposlibres = models.IntegerField(default=0, verbose_name=u'Cupos a vender de la maestría')
    estado = models.IntegerField(choices=ESTADO_META, default=1, verbose_name=u'Estado de la meta mensual')

    def __str__(self):
        return u'%s - %s - %s' % (self.maestria, self.inicio, self.fin)

    class Meta:
        verbose_name = u"Cupo maestría mensual"
        verbose_name_plural = u"Cupos maestría mensuales"
        ordering = ['-id']

class AsesorTerritorio(ModeloBase):
    asesor = models.ForeignKey(AsesorComercial, blank=True, null=True, verbose_name=u'Asesor Comercial', on_delete=models.CASCADE)
    canton = models.ForeignKey('sga.Canton', blank=True, null=True, verbose_name=u'Territorio asignado', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s - %s' % (self.asesor, self.canton.nombre)

    class Meta:
        verbose_name = u"Asesor Territorio"
        verbose_name_plural = u"Asesores de Territorio"
        ordering = ['-id']

class TipoRespuestaProspecto(ModeloBase):
    descripcion = models.CharField(default='', blank=True, null=True, max_length=300, verbose_name=u"Descripción")

    def __str__(self):
        return u"%s" % self.descripcion

    class Meta:
        verbose_name = u'Tipo de Respuesta de Prospecto'
        verbose_name_plural = u'Tipos de Respuesta de Prospecto'
        ordering = ['descripcion']

class CanalInformacionMaestria(ModeloBase):
    descripcion = models.CharField(default='', blank=True, null=True, max_length=300, verbose_name=u"Descripción")
    valido_form = models.BooleanField(default=False, verbose_name=u"Para presentar en formulario externo")

    def __str__(self):
        return u"%s" % self.descripcion

    class Meta:
        verbose_name = u'Canal de Información'
        verbose_name_plural = u'Canales de Información'
        ordering = ['descripcion']

class InscripcionCohorte(ModeloBase):
    inscripcionaspirante = models.ForeignKey(InscripcionAspirante, verbose_name=u'Inscripcion Aspirante', on_delete=models.CASCADE)
    cohortes = models.ForeignKey(CohorteMaestria, blank=True, null=True, verbose_name=u'Programa de maestría', on_delete=models.CASCADE)
    activo = models.BooleanField(default=True, verbose_name=u"Activo")
    aproboproceso = models.BooleanField(default=False, verbose_name=u"Aprobó proceso de maestria")
    fecharecibo = models.DateField(blank=True, null=True, verbose_name=u'fecha de recibo')
    grupo = models.ForeignKey(GrupoRequisitoCohorte, blank=True, null=True, verbose_name=u'Programa de maestría', on_delete=models.CASCADE)
    estado_emailevidencia = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u'Estado Email evidencia')
    fecha_emailevidencia = models.DateTimeField(blank=True, null=True)
    persona_emailevidencia = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Quien aprueba o rechaza evidencias', on_delete=models.CASCADE)
    estado_aprobador = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u'Estado Email evidencia')
    fecha_aprobador = models.DateTimeField(blank=True, null=True)
    persona_aprobador = models.ForeignKey('sga.Persona', blank=True, null=True,related_name='+', verbose_name=u'Quien aprueba o rechaza evidencias', on_delete=models.CASCADE)
    persona_permisosubir = models.ForeignKey('sga.Persona', blank=True, null=True,related_name='+', verbose_name=u'Quien aprueba o rechaza evidencias', on_delete=models.CASCADE)
    fecha_permisosubir = models.DateTimeField(blank=True, null=True)
    envioemailrecordatorio = models.BooleanField(default=False, verbose_name=u"Envió email recordatorio")
    fecha_envioemailrecordatorio = models.DateTimeField(blank=True, null=True)
    tipobeca = models.ForeignKey('sga.DetalleConfiguracionDescuentoPosgrado', blank=True, null=True, verbose_name=u'Tipo de beca', on_delete=models.CASCADE)
    contactomaestria = models.IntegerField(choices=CONTACTO_MAESTRIA, blank=True, null=True, verbose_name=u'Contacto maestria')
    inscripcion = models.ForeignKey('sga.Inscripcion', blank=True, null=True, verbose_name=u'Inscripción', on_delete=models.CASCADE)
    tipocobro = models.IntegerField(choices=TIPO_COBRO, default=1, verbose_name=u'tipo de cobro')
    tipo = models.ForeignKey('sagest.TipoOtroRubro', blank=True, null=True, verbose_name=u"Tipo", on_delete=models.CASCADE)
    codigoqr = models.BooleanField(default=False, verbose_name=u"Admitidos generado con código QR")
    asesor = models.ForeignKey(AsesorComercial, blank=True, null=True, verbose_name=u'Asesor Comercial', on_delete=models.CASCADE)
    estado_asesor = models.IntegerField(choices=ESTADO_ASESOR_COMERCIAL, default=1, verbose_name=u'Estado aprobacion Lead')
    tiulacionaspirante = models.ForeignKey('sga.Titulacion', null=True, blank=True, verbose_name=u'Titulacion', on_delete=models.SET_NULL)
    cantexperiencia = models.FloatField(default=0, verbose_name=u'Años de experiencia')
    formapagopac = models.ForeignKey('inno.TipoFormaPagoPac', blank=True, null=True, verbose_name=u'Forma de Pago', on_delete=models.CASCADE)
    estadoformapago = models.IntegerField(choices=ESTADO_FORMA_PAGO, default=1, verbose_name=u'Estado de forma de pago')
    numcuotaspago = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'Número de cuotas')
    tiporespuesta = models.ForeignKey(TipoRespuestaProspecto, blank=True, null=True, verbose_name=u'Respuesta del Prospecto', on_delete=models.CASCADE)
    itinerario = models.IntegerField(choices=ITINERARIO_ASIGNATURA_MALLA, default=0, blank=True, null=True, verbose_name=u'Itinerario')
    Configfinanciamientocohorte = models.ForeignKey(ConfigFinanciamientoCohorte, blank=True, null=True, verbose_name=u'Configuración financiamiento cohorte', on_delete=models.CASCADE)
    atencion_financiamiento = models.IntegerField(choices=ESTADO_ATENDIDO, default=1, verbose_name=u'Estado atención financiamiento')
    doblepostulacion = models.BooleanField(default=False, verbose_name=u'Verfica si el postulante va cursar dos maestrias')
    subirrequisitogarante = models.BooleanField(default=True, verbose_name=u'Verfica si el postulante debe subir requisistos de garante')
    canal = models.ForeignKey(CanalInformacionMaestria, blank=True, null=True, verbose_name=u'Canal de Informacion', on_delete=models.CASCADE)
    preaprobado = models.BooleanField(default=False, verbose_name=u'Verfica si el postulante cumple con sus requisitos de admision')
    todosubido = models.BooleanField(default=False, verbose_name=u'Verfica si el postulante tiene todas sus evidencias de admisión subidas')
    tienerechazo = models.BooleanField(default=False, verbose_name=u'Verifica si el postulante tiene alguna evidencia rechazada')
    vendido = models.BooleanField(default=False, verbose_name=u'Verifica si el postulante es una venta para el asesor')
    todosubidofi = models.BooleanField(default=False, verbose_name=u'Verifica si el tiene subido todos los requisitos de financiamiento')
    tienerechazofi = models.BooleanField(default=False, verbose_name=u'Verifica si el postulante tiene alguna evidencia de financiamiento rechazada')
    aceptado = models.BooleanField(default=False, verbose_name=u'Verifica si el postulante aceptó su modalidad de pago')
    puedeeditarmp = models.BooleanField(default=True, verbose_name=u'Puede editar modalidad de pago')
    puedesubiroficio = models.BooleanField(default=False, verbose_name=u'Puede subir oficio de terminación de contrato')
    leaddezona = models.BooleanField(default=False, verbose_name=u'Lead contactado por asesor de zona')
    es_becado = models.BooleanField(default=False, verbose_name=u'Verifica si el postulante tiene beca')
    convenio = models.ForeignKey('posgrado.Convenio', blank=True, null=True, verbose_name=u'Convenio de posgrado', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s - %s' % (self.inscripcionaspirante, self.cohortes)

    class Meta:
        verbose_name = u"Inscripción cohorte"
        verbose_name_plural = u"Inscripciones cohortes"
        ordering = ['id']

    def cambioadmitido(self):
        if CambioAdmitidoCohorteInscripcion.objects.filter(status=True,inscripcionCohorte=self).exists():
            return CambioAdmitidoCohorteInscripcion.objects.filter(status=True,inscripcionCohorte=self).order_by('-id').first()
        return None

    def esta_inscrito(self):
        from sga.models import Inscripcion
        x = Inscripcion.objects.filter(persona=self.inscripcionaspirante.persona, carrera=self.cohortes.maestriaadmision.carrera).exists()
        return True if Inscripcion.objects.filter(persona=self.inscripcionaspirante.persona, carrera=self.cohortes.maestriaadmision.carrera).exists() and self.inscripcion and self.inscripcion.matriculado_periodo(self.cohortes.periodoacademico) else False

    def eliminar_aspirante_matricula(self):
        rubro1 = self.rubro_set.filter(status=True)
        return rubro1

    def puede_eliminar_aspirante_matricula(self):
        rubros1 = self.rubro_set.filter(status=True)
        elimina = True
        if self.genero_rubro_matricula() or self.genero_rubro_programa():
            for rubro in rubros1:
                if not (rubro.total_pagado() >= 0 and rubro.total_pagado() <= 0):
                    elimina = False
        else:
            elimina = False
        return elimina

    def eval_entrevista(self):
        return self.integrantegrupoentrevitamsc_set.filter(status=True)[0].estadoentrevista

    def listacuotas(self):
        return Pago.objects.filter(inscripcioncohorte=self,status=True).order_by('id')

    def sube_evidenciapagoexamen(self):
        return self.evidenciapagoexamen_set.filter(status=True)

    def tiene_evidenciapagoexamen(self):
        return self.evidenciapagoexamen_set.filter(status=True)[0]

    def puedeeliminar(self):
        hoy = datetime.now().date()
        if not self.evidenciarequisitosaspirante_set.filter(status=True).exists() or self.cohortes.fechafinrequisito >= hoy:
            return True
        else:
            return False

    def puederevisar(self):
        hoy = datetime.now().date()
        if hoy > self.cohortes.fechafinrequisito:
            return True
        else:
            return False

    def pago_examen(self):
        if self.pago_set.filter(tipo_id=1, status=True):
            return self.pago_set.filter(tipo_id=1, status=True)[0].cuotapago_set.filter(status=True)[0].valor
        else:
            return 0

    def pago_matricula(self):
        if self.pago_set.filter(tipo_id=2, status=True):
            return self.pago_set.filter(tipo_id=2, status=True)[0].cuotapago_set.filter(status=True)[0].valor
        else:
            return 0

    def nota_examentest(self):
        if self.integrantegrupoexamenmsc_set.filter(status=True).exists():
            return self.integrantegrupoexamenmsc_set.filter(status=True)[0].notatest
        return None

    def nota_examen(self):
        if self.integrantegrupoexamenmsc_set.filter(status=True).exists():
            return self.integrantegrupoexamenmsc_set.filter(status=True)[0].notaexa
        return None

    def promedio(self):
        if self.integrantegrupoexamenmsc_set.filter(status=True).exists():
            return self.integrantegrupoexamenmsc_set.filter(status=True)[0].notafinal
        return None

    def total_evidencias(self):
        #requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
        # if self.formapagopac_id == 2:
        #     requisitosexcluir = []
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=1, obligatorio=True).values_list('id', flat=True)
        cont = 0
        if not self.grupo:
            for requisto in requistosmaestria:
                if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                               requisitos_id=requisto,
                                                               requisitos__requisito__claserequisito__clasificacion__id=1).exists():
                    cont += 1
            return cont
            #return self.evidenciarequisitosaspirante_set.values("id").filter(status=True).exclude(requisitos__requisito_id__in=requisitosexcluir).count()
        else:
            gruporequisitos = self.grupo.requisitosgrupocohorte_set.values_list('requisito_id', flat=True).filter(status=True)

            for requisto in requistosmaestria:
                if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                               requisitos_id=requisto,
                                                               requisitos__requisito__claserequisito__clasificacion__id=1,
                                                               requisitos__requisito__id__in=gruporequisitos).exists():
                    cont += 1
            return cont
                #return self.evidenciarequisitosaspirante_set.values("id").filter(requisitos__requisito_id__in=gruporequisitos,status=True).exclude(requisitos__requisito_id__in=requisitosexcluir).count()

    def total_evidence_lead(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=1, obligatorio=True).values_list('id', flat=True)
        cont = 0
        estado = False
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self, requisitos_id=requisto, requisitos__requisito__claserequisito__clasificacion__id=1).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self, requisitos_id=requisto, requisitos__requisito__claserequisito__clasificacion__id=1).order_by('-id').first()
                deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                if deta.estadorevision == 1 or deta.estado_aprobacion == 2:
                    cont += 1

        if cont == requistosmaestria.count():
            estado = True

        return estado

    def total_evidence_lead_fi(self):
        if self.subirrequisitogarante:
            requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=3, obligatorio=True).values_list('id', flat=True)
        else:
            requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=3, requisito__tipopersona__id=1, obligatorio=True).values_list('id', flat=True)
        cont = 0
        estado = False
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self, requisitos_id=requisto, requisitos__requisito__claserequisito__clasificacion__id=3).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self, requisitos_id=requisto, requisitos__requisito__claserequisito__clasificacion__id=3).order_by('-id').first()
                deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                if deta.estadorevision == 1 or deta.estado_aprobacion == 2:
                    cont += 1

        if cont == requistosmaestria.count():
            estado = True

        return estado

    def act_evidencias_rechazadas(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=1).values_list('id', flat=True)
        cont = 0
        estado = False
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).order_by('-id').first()
                if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).exists():
                    deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                    if deta.estado_aprobacion == 3:
                        estado = True
                        break
        return estado

    def act_evidencias_subidas(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=1).values_list('id', flat=True)
        cont = 0
        estado = False
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).order_by('-id').first()
                if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).exists():
                    deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                    if deta.estado_aprobacion == 1:
                        estado = True
                        break
        return estado

    def nombre_evidencias_rechazadas(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=1).values_list('id', flat=True)
        cont = 0
        estado = False
        lista = []
        evidences = ""
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).order_by('-id').first()
                if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).exists():
                    deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                    if deta.estado_aprobacion == 3:
                        lista.append(evi.requisitos.requisito.nombre)
        if len(lista) > 0:
            co = 1
            for element in lista:
                if co == len(lista):
                    evidences += str(element) + "."
                    co += 1
                else:
                    evidences += str(element) + ", "
                    co += 1
        return evidences

    def fecha_ultimaevidenciaobligatoria(self):
        requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
        ultimafecha = None
        requisitos_cohorte = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes).values_list('id', flat=True).exclude(requisito__claserequisito__clasificacion=3)
        if not self.grupo:
            ultimafecha = self.evidenciarequisitosaspirante_set.values("fecha_creacion").filter(status=True, requisitos__obligatorio=True, requisitos__id__in=requisitos_cohorte).exclude(
                requisitos__requisito_id__in=requisitosexcluir)
        else:
            gruporequisitos = self.grupo.requisitosgrupocohorte_set.values_list('requisito_id', flat=True).filter(
                status=True)
            ultimafecha = self.evidenciarequisitosaspirante_set.values("fecha_creacion").filter(
                requisitos__requisito_id__in=gruporequisitos, status=True, requisitos__obligatorio=True).exclude(
                requisitos__requisito_id__in=requisitosexcluir)
        if ultimafecha:
            ultimafecha = ultimafecha.order_by("-fecha_creacion").first()['fecha_creacion']
        return ultimafecha

    def tuvo_evidencias_rechazo(self):
        return True if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia__inscripcioncohorte=self, estado_aprobacion=3).exists() else False

    def fecha_ultimo_rechazo(self):
        detalles = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia__inscripcioncohorte=self, estado_aprobacion=3).order_by('-fecha_aprobacion').first()
        return detalles.fecha_aprobacion.date()

    def fecha_ultima_subida(self):
        detalles = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia__inscripcioncohorte=self, estado_aprobacion=1).order_by('-fecha').first()
        return detalles.fecha.date()

    def dias_transcurridos(self):
        dias = 0
        if self.fecha_ultimaevidenciaobligatoria():
            dias = (datetime.now().date() - self.fecha_ultimaevidenciaobligatoria().date()).days
            dias = dias if dias > 0 else 0
        return dias

    def dias_transcurridos_over(self):
        dias = 0
        if self.fecha_aprobador and self.fecha_ultimaevidenciaobligatoria():
            dias = (self.fecha_aprobador.date() - self.fecha_ultimaevidenciaobligatoria().date()).days
            dias = dias if dias > 0 else 0
        return dias

    def tiene_preaprobacion_histo(self):
        return True if DetallePreAprobacionPostulante.objects.filter(status=True, inscripcion=self).exists() else False

    def ultima_fecha_preaprobacion(self):
        return DetallePreAprobacionPostulante.objects.filter(status=True, inscripcion=self,
                                                                 preaprobado=True).order_by('-id').first().fecha_creacion.date()

    def dias_sin_revisar(self):
        try:
            dias = 0
            dias_no_contados = 0
            # Fecha Actual
            factual = datetime.now().date()
            # Fecha de Pre-aprobacion
            if DetallePreAprobacionPostulante.objects.filter(status=True, inscripcion=self, preaprobado=True).exists():
                deta = DetallePreAprobacionPostulante.objects.filter(status=True, inscripcion=self,
                                                                     preaprobado=True).order_by('id').first()
                fpreapro = deta.fecha_creacion.date()
                if deta.dias == 0:
                    #Ultima fecha de rechazo
                    if self.act_evidencias_rechazadas():
                        frecha = self.fecha_ultimo_rechazo()
                        dias = (frecha - fpreapro).days
                        dias = dias if dias > 0 else 0
                    elif DetallePreAprobacionPostulante.objects.filter(status=True, inscripcion=self, preaprobado=True).count() > 1 and self.tuvo_evidencias_rechazo():
                        detalle = DetallePreAprobacionPostulante.objects.filter(status=True, inscripcion=self, preaprobado=True).order_by('-id').first()
                        #Fecha de nueva Pre-aprobación
                        fnupreapro = detalle.fecha_creacion.date()
                        frecha = self.fecha_ultimo_rechazo()
                        dias_no_contados = (fnupreapro - frecha).days
                        if self.estado_aprobador == 2 and self.fecha_aprobador:
                            fapro = self.fecha_aprobador.date()
                            dias = (fapro - fpreapro).days
                            dias = dias - dias_no_contados
                            deta.dias = dias
                            deta.save()
                        else:
                            dias = (factual - fpreapro).days
                            dias = dias - dias_no_contados
                            dias = dias if dias > 0 else 0
                    elif self.act_evidencias_subidas() and self.tuvo_evidencias_rechazo():
                        frecha = self.fecha_ultimo_rechazo()
                        dias = (frecha - fpreapro).days
                        dias = dias if dias > 0 else 0
                    elif self.estado_aprobador == 2 and self.fecha_aprobador:
                        # Fecha de aprobación requisitos
                        fapro = self.fecha_aprobador.date()
                        dias = (fapro - fpreapro).days
                        dias = dias if dias > 0 else 0
                        deta.dias = dias
                        deta.save()
                    else:
                        dias = (factual - fpreapro).days
                        dias = dias if dias > 0 else 0
                else:
                    dias = deta.dias
            return dias
        except Exception as ex:
            pass

    def total_evidenciasgrupocohorte(self):
        requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
        # if self.formapagopac_id == 2:
        #     requisitosexcluir = []
        if not self.grupo:
            return self.cohortes.requisitosmaestria_set.values('id').filter(status=True).exclude(requisito_id__in=requisitosexcluir).count()
        else:
            gruporequisitos = self.grupo.requisitosgrupocohorte_set.values_list('requisito_id',flat=True).filter(status=True)
            return self.cohortes.requisitosmaestria_set.values('id').filter(requisito_id__in=gruporequisitos, status=True).exclude(requisito_id__in=requisitosexcluir).count()

    def total_evidenciasgrupocohorteobligatorias(self):
        requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
        # if self.formapagopac_id == 2:
        #     requisitosexcluir = []
        if not self.grupo:
            return self.cohortes.requisitosmaestria_set.values('id').filter(obligatorio=True, status=True).exclude(requisito_id__in=requisitosexcluir).count()
        else:
            gruporequisitos = self.grupo.requisitosgrupocohorte_set.values_list('requisito_id',flat=True).filter(status=True)
            return self.cohortes.requisitosmaestria_set.values('id').filter(obligatorio=True, requisito_id__in=gruporequisitos, status=True).exclude(requisito_id__in=requisitosexcluir).count()

    def total_evidenciasaprobadas(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=1).values_list('id', flat=True)
        cont = 0
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).order_by('-id').first()
                if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).exists():
                    deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                    if deta.estado_aprobacion == 2:
                        cont += 1
        return cont
        # requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
        # if self.formapagopac_id == 2:
        #     requisitosexcluir = []
        # requisitos_cohorte = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes).values_list('id', flat=True).exclude(requisito__claserequisito__clasificacion=3)
        # evidencias = self.evidenciarequisitosaspirante_set.filter(status=True, requisitos__id__in=requisitos_cohorte).exclude(requisitos__requisito_id__in=requisitosexcluir)
        # num_apro = 0
        # for evi in evidencias:
        #     if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).exists():
        #         if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).order_by('-id')[0].esta_aprobado():
        #             num_apro=num_apro+1
        # return num_apro

    def total_evidenciassinrechazar(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=1).values_list('id', flat=True)
        cont = 0
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).order_by('-id').first()
                if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).exists():
                    deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                    if deta.estado_aprobacion != 3:
                        cont += 1
        return cont

        # requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
        # if self.formapagopac_id == 2:
        #     requisitosexcluir = []
        # requisitos_cohorte = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes).values_list('id', flat=True).exclude(requisito__claserequisito__clasificacion=3)
        # evidencias = self.evidenciarequisitosaspirante_set.filter(status=True, requisitos__id__in=requisitos_cohorte).exclude(requisitos__requisito_id__in=requisitosexcluir).values_list('id', flat=True)
        # num = 0
        # for evi in evidencias:
        #     if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).exists():
        #         if evi.detalleevidenciarequisitosaspirante_set.filter(
        #                 Q(status=True) & ~Q(estado_aprobacion=3)).order_by('-id'):
        #             num = num + 1
        # num = DetalleEvidenciaRequisitosAspirante.objects.values('id').filter(
        #                                 Q(evidencia__in=evidencias) & (
        #                                     Q(status=True) & ~Q(estado_aprobacion=3))).distinct().count()
        # return num

    def total_evidenciasaprobadas_clase(self):
        try:
            # requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
            # if self.formapagopac_id == 2:
            #     requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=1, status=True)
            if self.subirrequisitogarante:
                evidencias = self.evidenciarequisitosaspirante_set.filter(status=True, requisitos__requisito__claserequisito__clasificacion__id=3).exclude(requisitos__requisito__id__in=[56, 57, 59])
                num_apro = 0
                for evi in evidencias:
                    if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).exists():
                        if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).order_by('-id')[0].esta_aprobado():
                            num_apro=num_apro+1
            else:
                evidencias = self.evidenciarequisitosaspirante_set.filter(status=True, requisitos__requisito__claserequisito__clasificacion__id=3, requisitos__requisito__tipopersona__id=1)
                num_apro = 0
                for evi in evidencias:
                    if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).exists():
                        if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).order_by('-id')[0].esta_aprobado():
                            num_apro=num_apro+1
            return num_apro
        except Exception as ex:
            pass

    def total_evidenciasrechazadas(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=1).values_list('id', flat=True)
        cont = 0
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=1).order_by('-id').first()
                if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).exists():
                    deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                    if deta.estado_aprobacion == 3:
                        cont += 1
        return cont
        # requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
        # # if self.formapagopac_id == 2:
        # #     requisitosexcluir = []
        # requisitos_cohorte = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes).values_list('id', flat=True).exclude(requisito__claserequisito__clasificacion=3)
        # evidencias = self.evidenciarequisitosaspirante_set.filter(status=True, requisitos__id__in=requisitos_cohorte).exclude(requisitos__requisito_id__in=requisitosexcluir)
        # num_apro = 0
        # for evi in evidencias:
        #     if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).exists():
        #         if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).order_by('-id')[0].estado_rechazado():
        #             num_apro=num_apro+1
        # return num_apro

    def total_evidencias_financiamiento(self):
        # idrequisitoscomer = ClaseRequisito.objects.filter(clasificacion=3).values_list('requisito__id', flat=True)
        if self.subirrequisitogarante:
            requisitosfinan = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=3).values_list('id', flat=True).exclude(requisito__id__in=[56, 57, 59])
        else:
            requisitosfinan = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=3, requisito__tipopersona__id=1).values_list('id', flat=True)
        return self.evidenciarequisitosaspirante_set.filter(status=True, requisitos__id__in=requisitosfinan).count()

    def total_requisitos_financiamiento(self):
        # idrequisitoscomer = ClaseRequisito.objects.filter(clasificacion=3).values_list('requisito__id', flat=True)
        if self.subirrequisitogarante:
            return RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=3).values_list('id', flat=True).exclude(requisito__id__in=[56, 57, 59]).count()
        else:
            return RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=3, requisito__tipopersona__id=1).values_list('id', flat=True).count()

    def total_evidenciasrechazadas_fi(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=3, obligatorio=True).values_list('id', flat=True)
        cont = 0
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=3).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=3).order_by('-id').first()
                if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).exists():
                    deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                    if deta.estado_aprobacion == 3:
                        cont += 1
        return cont

    def total_evidenciasaprobadas_fi(self):
        requistosmaestria = RequisitosMaestria.objects.filter(status=True, cohorte=self.cohortes, requisito__claserequisito__clasificacion__id=3).values_list('id', flat=True)
        cont = 0
        for requisto in requistosmaestria:
            if EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=3).exists():
                evi = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self,
                                                           requisitos_id=requisto,
                                                           requisitos__requisito__claserequisito__clasificacion__id=3).order_by('-id').first()
                if DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).exists():
                    deta = DetalleEvidenciaRequisitosAspirante.objects.filter(status=True, evidencia=evi).order_by('-id').first()
                    if deta.estado_aprobacion == 2:
                        cont += 1
        return cont

    def total_evidencias_obligatorio(self):
        claserequisitoadmision = ClaseRequisito.objects.values_list('requisito__id', flat=True).filter(clasificacion=1, status=True)
        # if self.formapagopac_id == 2:
        #     requisitosexcluir = []
        evidencias = self.evidenciarequisitosaspirante_set.filter(status=True, requisitos__requisito_id__in=claserequisitoadmision)
        num_apro = 0
        for evi in evidencias:
            if evi.detalleevidenciarequisitosaspirante_set.filter(status=True, evidencia__requisitos__obligatorio=True).exists():
                if evi.detalleevidenciarequisitosaspirante_set.filter(status=True).order_by('-id')[0].esta_aprobado():
                    num_apro=num_apro+1
        return num_apro

    def tiene_contrato_subido(self):
        if Contrato.objects.filter(status=True, inscripcion=self).exists():
            contra = Contrato.objects.get(status=True, inscripcion=self)
            if contra.archivocontrato:
                flag = 2
            else:
                flag = 0
        else:
            flag = 0
        return flag

    def tiene_pagare_subido(self):
        if Contrato.objects.filter(status=True, inscripcion=self).exists():
            contra = Contrato.objects.get(status=True, inscripcion=self)
            if contra.archivopagare:
                flag = 2
            else:
                flag = 0
        else:
            flag = 0
        return flag

    def estado_contrato_subido(self):
        if Contrato.objects.filter(status=True, inscripcion=self).exists():
            contra = Contrato.objects.get(status=True, inscripcion=self)
            if contra.detalleaprobacioncontrato_set.filter(status=True, espagare=False).exists():
                evicon = contra.detalleaprobacioncontrato_set.filter(status=True, espagare=False).order_by('-id')[0]
                if evicon.esta_con_pendiente():
                    flag = 1
                elif evicon.esta_aprobado():
                    flag = 2
                elif evicon.esta_con_rechazado():
                    flag = 3
        return flag

    def estado_pagare_subido(self):
        if Contrato.objects.filter(status=True, inscripcion=self).exists():
            contra = Contrato.objects.get(status=True, inscripcion=self)
            if contra.detalleaprobacioncontrato_set.filter(status=True, espagare=True).exists():
                evicon = contra.detalleaprobacioncontrato_set.filter(status=True, espagare=True).order_by('-id')[0]
                if evicon.esta_con_pendiente():
                    flag = 1
                elif evicon.esta_aprobado():
                    flag = 2
                elif evicon.esta_con_rechazado():
                    flag = 3
        return flag

    def cumple_con_requisitos(self):
        requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=3, status=True)
        return True if self.total_evidenciasaprobadas_clase() == self.cohortes.requisitosmaestria_set.values("id").filter(status=True).exclude(requisito_id__in=requisitosexcluir).count() else False

    def cumple_con_requisitos_comercializacion(self):
        # requisitosexcluir = ClaseRequisito.objects.values_list('requisito__id').filter(clasificacion=1, status=True)
        if self.subirrequisitogarante:
            return True if self.total_evidenciasaprobadas_clase() >= self.cohortes.requisitosmaestria_set.values("id").filter(status=True, obligatorio=True, requisito__claserequisito__clasificacion__id=3).exclude(requisito__id__in=[56, 57, 59]).count() else False
        else:
            return True if self.total_evidenciasaprobadas_clase() >= self.cohortes.requisitosmaestria_set.values("id").filter(status=True, obligatorio=True, requisito__tipopersona__id=1, requisito__claserequisito__clasificacion__id=3).count() else False

    def validar_boton(self):
        cohorte = self.cohortes
        bandera = 0
        for re in cohorte.requisitosmaestria_set.filter(status=True, obligatorio=True):
            ingresoevidencias = re.detalle_requisitosmaestriacohorte(self)
            if not ingresoevidencias.ultima_evidencia().estado_aprobacion == 2:
                bandera = 1
        if bandera == 0:
            return True
        return False

    def tiene_inscripcion(self):
        return self.inscripcion_set.values('id').filter(status=True).count()

    def notas_examen(self, cohorte):
        if self.integrantegrupoexamenmsc_set.filter(grupoexamen__cohorte__id=cohorte).exists():
            return self.integrantegrupoexamenmsc_set.filter(grupoexamen__cohorte__id=cohorte)[0]
        return None

    def mi_entrevista(self, cohorte):
        if self.integrantegrupoentrevitamsc_set.filter(grupoentrevista__cohortes__id=cohorte).exists():
            return self.integrantegrupoentrevitamsc_set.filter(grupoentrevista__cohortes__id=cohorte)[0]
        return None

    def genero_rubro_matricula(self):
        return self.rubro_set.filter(status=True,admisionposgradotipo=2, inscripcion=self, cohortemaestria=self.cohortes).exists()

    def cancelo_rubro_matricula(self):
        if self.formapagopac:
            if self.formapagopac.id == 2:
                totalpagado = self.total_pagado_rubro_cohorte()
                costomaestria = self.cohortes.valorprograma
                if totalpagado == costomaestria:
                    return True
                else:
                    return False
            else:
                return self.rubro_set.filter(status=True, admisionposgradotipo=2, inscripcion=self, cohortemaestria=self.cohortes, cancelado=True).exists()
        else:
            return self.rubro_set.filter(status=True, admisionposgradotipo=2, inscripcion=self, cohortemaestria=self.cohortes, cancelado=True).exists()

    def genero_rubro_programa(self):
        return self.rubro_set.filter(status=True,admisionposgradotipo=3, inscripcion=self, cohortemaestria=self.cohortes).exists()

    def genero_rubro_programa2(self):
        return self.rubro_set.filter(status=True,admisionposgradotipo=3, inscripcion=self, cohortemaestria=self.cohortes).exists()

    def cancelo_rubro_programa(self):
        if self.formapagopac:
            if self.formapagopac.id == 2:
                totalpagado = self.total_pagado_rubro_cohorte()
                costomaestria = self.cohortes.valorprograma
                if totalpagado == costomaestria:
                    return True
                else:
                    return False
            else:
                return self.rubro_set.filter(status=True, admisionposgradotipo=3, inscripcion=self, cohortemaestria=self.cohortes, cancelado=True).exists()
        else:
            return self.rubro_set.filter(status=True,admisionposgradotipo=3, inscripcion=self, cohortemaestria=self.cohortes, cancelado=True).exists()


    def tiene_garante(self):
        return True if GarantePagoMaestria.objects.filter(status=True, inscripcioncohorte=self).exists() else False

    def garantemaestria(self):
        return GarantePagoMaestria.objects.filter(status=True, inscripcioncohorte=self).order_by('-id')[0]

    def tiene_pagos_rubros(self):
        from sagest.models import Rubro
        if Rubro.objects.values('id').filter(status=True, admisionposgradotipo__in=[2,3], inscripcion=self, cohortemaestria=self.cohortes).exists():
            rubros = Rubro.objects.filter(status=True, admisionposgradotipo__in=[2, 3], inscripcion=self, cohortemaestria=self.cohortes).order_by('id')
            for rubro in rubros:
                if rubro.tiene_pagos():
                    pago = True
                    break
                else:
                    pago = False
        else:
            pago = False

        return pago

    def esadmitido(self):
        return IntegranteGrupoEntrevitaMsc.objects.filter(estado_emailadmitido=2, cohorteadmitidasinproceso__isnull=True, status=True, inscripcion__status=True, inscripcion=self)

    def valor_maestria(self):
        return self.cohortes.valorprogramacertificado

    def tiene_rubro_generado(self):
        if self.cohortes.valorprograma > 0:
            return self.genero_rubro_programa()
        else:
            return self.genero_rubro_matricula()

    def tiene_rubro_pagado(self):
        if self.cohortes.valorprograma > 0:
            return self.cancelo_rubro_programa()
        else:
            return self.cancelo_rubro_matricula()

    def rubro_generado_ins(self):
        from sagest.models import Rubro
        return True if Rubro.objects.filter(status=True, inscripcion=self, persona=self.inscripcionaspirante.persona).exists() else False

    def solicitudbeca(self):
        return self.descuentoposgradomatricula_set.filter(status=True)[0]

    def curso_matriculado(self):
        from sga.models import Matricula, MateriaAsignada
        cursos = []
        matricula = Matricula.objects.filter(status=True, inscripcion=self.inscripcion).order_by('-id').first()
        if MateriaAsignada.objects.filter(status=True, matricula=matricula).exists():
            for curso in matricula.materiaasignada_set.filter(matricula__status=True, status=True):
                if curso.materia.paralelo not in cursos:
                    cursos.append(curso.materia.paralelo)
        return cursos

    def tiene_matricula_cohorte(self):
        from sga.models import Matricula
        return True if Matricula.objects.filter(status=True, inscripcion=self.inscripcion, retiradomatricula=False).exists() else False

    def tiene_contrato_legalizado(self):
        estado = False
        if Contrato.objects.filter(status=True, inscripcion=self, contratolegalizado=True).exists():
            estado = True
        return estado

    def matricula_cohorte(self):
        from sga.models import Matricula
        return Matricula.objects.filter(status=True, inscripcion=self.inscripcion).order_by('-id')[0]

    def total_pagado_cohorte(self):
        from sagest.models import Pago
        return null_to_numeric(
            Pago.objects.filter(rubro__persona=self.inscripcionaspirante.persona, status=True, rubro__tipo__tiporubro=1, rubro__inscripcion=self).exclude(pagoliquidacion__isnull=False).exclude(
                factura__valida=False).aggregate(valor=Sum('valortotal'))['valor'])

    def tiene_cambiada_forma_pago(self):
        deta = DetalleAprobacionFormaPago.objects.filter(status=True, inscripcion=self, tipofinanciamiento__isnull=True).exclude(observacion='TODAS LAS EVIDENCIAS HAN SIDO APROBADAS').count()
        if deta >= 1:
            return 'SI'
        else:
            return 'NO'

    def fecha_asignacion_asesor(self):
        if HistorialAsesor.objects.filter(inscripcion=self, asesor=self.asesor).exists():
            histo = HistorialAsesor.objects.filter(inscripcion=self, asesor=self.asesor).order_by('-fecha_creacion').first()
            return histo.fecha_inicio
        else:
            return self.fecha_creacion

    def ultima_obervacion(self):
        return HistorialRespuestaProspecto.objects.filter(status=True, inscripcion=self).order_by('-fecha_creacion').first()

    def ultima_asignacion(self):
        return HistorialAsesor.objects.filter(status=True, inscripcion=self).order_by('-fecha_creacion').first()

    def fecha_matriculacion(self):
        try:
            from sga.models import Matricula
            matri = Matricula.objects.filter(status=True, inscripcion=self.inscripcion).order_by('-id')[0]
            return matri.fecha_creacion
        except Exception as ex:
            pass

    def fecha_matriculacion2(self):
        try:
            from sga.models import Matricula
            matri = ''
            if self.inscripcion:
                if Matricula.objects.filter(status=True, inscripcion=self.inscripcion).exists():
                    matri = Matricula.objects.filter(status=True, inscripcion=self.inscripcion).order_by('-id').first().fecha_creacion.date()
                else:
                    matri = 'NO REGISTRA'
            else:
                matri = 'NO REGISTRA'
            return matri
        except Exception as ex:
            pass

    def matriculado_por(self):
        try:
            from sga.models import Matricula, Persona, MateriaAsignada
            matri = ''
            if self.inscripcion:
                if Matricula.objects.filter(status=True, inscripcion=self.inscripcion).exists():
                    usu = Matricula.objects.filter(status=True, inscripcion=self.inscripcion).order_by('-id').first()
                    if MateriaAsignada.objects.filter(status=True, matricula=usu).exists():
                        mateasi = MateriaAsignada.objects.filter(status=True, matricula=usu).order_by('id').first()
                        per = Persona.objects.get(status=True, usuario=mateasi.usuario_creacion)
                        matri = per.nombre_completo_inverso()
                    else:
                        per = Persona.objects.get(status=True, usuario=usu.usuario_creacion)
                        matri = per.nombre_completo_inverso()
                else:
                    matri = 'NO REGISTRA'
            else:
                matri = 'NO REGISTRA'
            return matri
        except Exception as ex:
            pass

    def dias_sin_atender(self):
        try:
            if self.asesor:
                d1 = self.fecha_asignacion_asesor()
                d2 = self.ultima_obervacion().fecha_creacion
                intervalo = d2 - d1
                return intervalo.days
            else:
                return 0
        except Exception as ex:
            pass

    def numero_reservaciones(self):
        return HistorialReservacionProspecto.objects.filter(status=True, inscripcion=self).count()

    def tiene_reservaciones(self):
        return True if HistorialReservacionProspecto.objects.filter(status=True, inscripcion=self).exists() else False

    def reservacion_prospectos(self):
        return HistorialReservacionProspecto.objects.filter(status=True, inscripcion=self).order_by('-id')[0]

    def fue_atendido(self):
        return True if self.tiporespuesta is not None and self.tiporespuesta != 1 else False

    def reservacion_asesor(self):
        return HistorialReservacionProspecto.objects.get(status=True, inscripcion=self)

    def supervisor_que_asigno(self):
        return HistorialAsesor.objects.filter(status=True, inscripcion=self).order_by('-fecha_creacion')[0]

    def prospecto_calle(self):
        if self.asesor:
            if self.asesor.id == 13 and self.supervisor_que_asigno().usuario_creacion.id == 24559:
                calle = True
            else:
                calle = False
        else:
            calle = False
        return calle

    def login_admision_posgrado(self):
        from bd.models import LogEntryLogin
        if LogEntryLogin.objects.filter(action_app=3, user=self.inscripcionaspirante.persona.usuario).exists():
            login = LogEntryLogin.objects.filter(action_app=3, user=self.inscripcionaspirante.persona.usuario).order_by('-action_time')[0]
            if login.action_flag == 1:
                flag = 1
            elif login.action_flag == 2:
                flag = 2
            else:
                flag = 3
        else:
            flag = 3
        return flag

    def acceso_sistema(self):
        from bd.models import LogEntryLogin
        if LogEntryLogin.objects.filter(action_app=3, user=self.inscripcionaspirante.persona.usuario).exists():
            login = LogEntryLogin.objects.filter(action_app=3, user=self.inscripcionaspirante.persona.usuario).order_by('-action_time')[0]
            if login.action_flag == 1:
                flag = 'LOGIN EXITOSO'
            elif login.action_flag == 2:
                flag = 'LOGIN FALLIDO'
            else:
                flag = 'NO HA ACCEDIDO AL SISTEMA'
        else:
            flag = 'NO HA ACCEDIDO AL SISTEMA'
        return flag

    def detalle_finan(self):
        fina = DetalleAprobacionFormaPago.objects.filter(inscripcion=self, status=True)
        return fina.order_by('fecha_creacion')[0] if fina.exists() else None


    def total_generado_rubro(self):
        from sagest.models import Rubro
        if Rubro.objects.filter(status=True, inscripcion=self).exists():
            totalgenerado = Decimal(null_to_decimal(Rubro.objects.values_list('valor').filter(status=True, inscripcion=self).aggregate(valor=Sum('valor'))['valor'], 2)).quantize(Decimal('.01'))
            return totalgenerado
        else:
            return 0

    def total_pagado_rubro_cohorte(self):
        from sagest.models import Pago
        if Pago.objects.filter(status=True, rubro__inscripcion__id=self.id).exists():
            totalpagado = Decimal(null_to_decimal(Pago.objects.values_list('valortotal').filter(status=True, rubro__status=True, rubro__inscripcion__id=self.id).exclude(factura__valida=False).aggregate(valor=Sum('valortotal'))['valor'], 2)).quantize(Decimal('.01'))
            return totalpagado
        else:
            return 0

    def fecha_inscrito(self):
        from sga.models import Inscripcion
        fecha = ''
        if self.inscripcion:
            fechains = Inscripcion.objects.filter(pk=self.inscripcion.id, status=True).first()
            if fechains:
                fecha = fechains.fecha_creacion.date()
            else:
                fecha = 'NO REGISTRA'
        else:
            fecha = 'NO REGISTRA'
        return fecha

    def inscrito_por(self):
        from sga.models import Inscripcion, Persona
        ins = ''
        if self.inscripcion:
            inscri = Inscripcion.objects.filter(pk=self.inscripcion.id, status=True).first()
            if inscri:
                per = Persona.objects.get(status=True, usuario=inscri.usuario_creacion)
                if per.id in [10813, 24145]:
                    ins = per.nombre_completo_inverso() + " (INSCRITO POR APROBACIÓN DE CONTRATO)"
                else:
                    ins = per.nombre_completo_inverso()
            else:
                ins = 'NO REGISTRA'
        else:
            ins = 'NO REGISTRA'
        return ins

    def ids_rubros(self):
        from sagest.models import Rubro
        ids = []
        rubros = Rubro.objects.filter(status=True, inscripcion=self).order_by('id')
        for ru in rubros:
            ids.append(ru.id)
        return ids

    def total_pendiente(self):
        vpp = self.cohortes.valorprogramacertificado
        vp = self.total_pagado_rubro_cohorte()
        return vpp - float(vp)

    def total_vencido_rubro(self):
        from sagest.models import Rubro
        hoy = datetime.now().date()
        if Rubro.objects.filter(status=True, inscripcion=self, fechavence__lt=hoy, cancelado=False).exists():
            totalvencido = Decimal(null_to_decimal(Rubro.objects.values_list('valor').filter(status=True, inscripcion=self, fechavence__lt=hoy, cancelado=False).aggregate(valor=Sum('valor'))['valor'], 2)).quantize(Decimal('.01'))
            return totalvencido
        else:
            return 0

    def listado_rubros_maestria(self):
        from sagest.models import Rubro
        return Rubro.objects.filter(status=True, inscripcion=self).order_by('id')

    def cantidad_rubros_ins(self):
        from sagest.models import Rubro
        if Rubro.objects.filter(status=True, inscripcion=self).exists():
            return Rubro.objects.filter(status=True, inscripcion=self).count()
        else:
            return 0

    def amortizacion(self):
        if self.Configfinanciamientocohorte:
            cuotaini = self.Configfinanciamientocohorte.valormatricula
            if Contrato.objects.filter(status=True, inscripcion=self).exists():
                contract = Contrato.objects.filter(status=True, inscripcion=self).order_by('-fecha_creacion')[0]
                if TablaAmortizacion.objects.filter(status=True, contrato=contract).exists():
                    cuotas = TablaAmortizacion.objects.filter(status=True, contrato=contract).count()
                    valorcu = TablaAmortizacion.objects.filter(status=True, contrato=contract)[0].valor
                    return '$ ' + str(cuotaini) + ' con ' + str(cuotas) + ' cuotas de ' + '$ ' + str(valorcu)
                else:
                    return 'NO HA ACEPTADO NI DESCARGADO PAGARÉ'
            else:
                return 'NO TIENE PAGARÉ'
        else:
            return 'NO TIENE TIPO DE FINANCIAMIENTO ASIGNADO'

    def tiene_documentos(self):
        if Contrato.objects.filter(status=True, inscripcion=self).exists():
            contract = Contrato.objects.filter(status=True, inscripcion=self).order_by('-fecha_creacion')[0]
            if contract.archivocontrato and contract.archivopagare:
                if contract.estado == 2 and contract.estadopagare == 2:
                    return 'TIENE APROBADO CONTRATO Y PAGARÉ'
                elif contract.estado == 2:
                    return 'SOLO TIENE APROBADO CONTRATO'
                elif contract.estadopagare == 2:
                    return 'SOLO TIENE APROBADO PAGARÉ'
                else:
                    return 'EN PROCESO'
            elif contract.archivocontrato:
                return 'SOLO HA SUBIDO CONTRATO'
            elif contract.archivopagare:
                return 'SOLO HA SUBIDO PAGARÉ'
            else:
                return 'NO HA SUBIDO LOS DOCUMENTOS'
        else:
            return 'NO HA DESCARGADO CONTRATO'

    def nombre_garante(self):
        if GarantePagoMaestria.objects.filter(status=True, inscripcioncohorte=self).exists():
            gara = GarantePagoMaestria.objects.filter(status=True, inscripcioncohorte=self).order_by('-fecha_creacion')[0]
            return gara.apellido1 + ' ' + gara.apellido2 + ' ' + gara.nombres
        else:
            return 'SIN GARANTE'
    def garante_prospecto(self):
        if GarantePagoMaestria.objects.filter(status=True, inscripcioncohorte=self).exists():
            return GarantePagoMaestria.objects.filter(status=True, inscripcioncohorte=self).order_by('-fecha_creacion')[0]

    def tiene_rubro_cuadrado(self):
        cuadre = None
        if self.cohortes.valorprograma:
            valormaestria = self.cohortes.valorprograma
            if self.total_generado_rubro() == valormaestria:
                cuadre = True
            else:
                cuadre = False
        elif self.cohortes.valorprogramacertificado:
            valormaestria = self.cohortes.valorprogramacertificado
            if self.total_generado_rubro() == valormaestria:
                cuadre = True
            else:
                cuadre = False

        return cuadre


    def tiene_contrato_aprobado(self):
        estado = False
        if Contrato.objects.filter(status=True, inscripcion=self).exists():
            contra = Contrato.objects.filter(status=True, inscripcion=self).order_by('-id')[0]
            if contra.archivocontrato:
                if contra.detalleaprobacioncontrato_set.filter(status=True, espagare=False).exists():
                    evicon = contra.detalleaprobacioncontrato_set.filter(status=True, espagare=False).order_by('-id')[0]
                    if evicon.esta_aprobado():
                        estado = True
        return estado

    def tiene_pagare_aprobado(self):
        estado = 'NO'
        if self.formapagopac and self.formapagopac.id == 2:
            if Contrato.objects.filter(status=True, inscripcion=self).exists():
                contra = Contrato.objects.filter(status=True, inscripcion=self).order_by('-id')[0]
                if contra.archivopagare:
                    if contra.detalleaprobacioncontrato_set.filter(status=True, espagare=True).exists():
                        evicon = contra.detalleaprobacioncontrato_set.filter(status=True, espagare=True).order_by('-id')[0]
                        if evicon.esta_aprobado():
                            estado = 'SI'
        else:
            estado = 'PAGO DE CONTADO (NO REQUIERE PAGARÉ)'
        return estado

    def pago_rubro_matricula(self):
        from sagest.models import Rubro
        if self.formapagopac:
            if self.formapagopac.id == 2:
                return True if Rubro.objects.filter(status=True, inscripcion=self, admisionposgradotipo=2, cancelado=True).exists() else False
            elif self.formapagopac.id == 1:
                return True if self.total_pagado_rubro_cohorte() == self.cohortes.valorprogramacertificado else False

    def cuadre_con_epunemi(self):
        from django.db import connections
        from sagest.models import Rubro
        cuadre = False
        rubrosunemi = Rubro.objects.filter(status=True, inscripcion=self, persona=self.inscripcionaspirante.persona)
        rubrosepunemi = []
        sumaepunemi = sumarubrosunemi = 0
        cursor = connections['epunemi'].cursor()
        for rubro in rubrosunemi:
            sql = """SELECT id, valor FROM sagest_rubro WHERE idrubrounemi=%s AND status=TRUE AND anulado=FALSE; """ % (rubro.id)
            cursor.execute(sql)
            registrorubro = cursor.fetchone()
            if registrorubro is not None:
                rubrosepunemi.append(registrorubro[0])
                sumaepunemi = sumaepunemi + registrorubro[1]

        if rubrosunemi.count() == len(rubrosepunemi):
            sumarubrosunemi = self.total_generado_rubro()

            if sumarubrosunemi == sumaepunemi:
                cuadre = True

        return cuadre

    def tiene_comprobante_subido(self):
        from sagest.models import ComprobanteAlumno
        return True if ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona, asesor=self.asesor).exists() else False

    def comprobantes_leads(self):
        from sagest.models import ComprobanteAlumno
        return ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona).order_by('-id')

    def mencion_cohorte(self):
        from sga.models import ItinerarioMallaEspecilidad
        mencion = ''
        if ItinerarioMallaEspecilidad.objects.filter(status=True, malla=self.cohortes.maestriaadmision.carrera.malla()).exists():
            if self.itinerario > 0:
                iti = ItinerarioMallaEspecilidad.objects.filter(status=True, malla=self.cohortes.maestriaadmision.carrera.malla(), itinerario=self.itinerario).first()
                if iti:
                    mencion = iti.nombre
                else:
                    mencion = 'TIENE ASIGNADO UN ITINERARIO INEXISTENTE'
            else:
                mencion = 'NO TIENE ASIGNADA UNA MENCIÓN'
        else:
            mencion = 'ESTA MAESTRÍA NO TIENE VARIAS MENCIONES'
        return mencion

    def comprobantes_epunemi(self):
        from django.db import connections
        try:
            cursor = connections['epunemi'].cursor()
            sql = """SELECT comp.id, comp.fecha_creacion, (NOW()::DATE - comp.fecha_creacion::DATE) AS dias, comp.curso, comp.carrera, comp.valor, comp.fechapago, comp.observacion, comp.tipocomprobante, comp.comprobantes, comp.estados, comp.cuentadeposito_id, comp.idcomprobanteunemi, RIGHT(comp.comprobantes, 4), comp.persona_id FROM sagest_comprobantealumno comp INNER JOIN sga_persona per ON comp.persona_id = per.id WHERE comp.status = TRUE AND per.cedula = '%s'""" % (self.inscripcionaspirante.persona.cedula)
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
        except Exception as ex:
            pass

    def pedidos_epunemi(self):
        from django.db import connections
        try:
            cursor = connections['epunemi'].cursor()
            sql = """SELECT TO_CHAR(pedidoonline.fecha_creacion, 'dd-mm-YYYY') AS fecha,
                        TO_CHAR(pedidoonline.fecha_creacion, 'hh:mm') AS hora,
                        pedidoonline.estado,
                        pedidoonline.tipopago,
                        pagotransdep.tipocomprobante,
                        pedidoonline.subtotal,
                        pedidoonline.total,
                        pagotransdep.comprobantes,
                        pedidoonline.observacion,
                        (ARRAY_TO_STRING(array(SELECT rubro.nombre FROM sagest_rubro rubro WHERE rubro.id = detallepedidoonline.rubro_id), ', ')) AS rubros,
                        TO_CHAR(pedidoonline.fpago, 'dd-mm-YYYY') AS fpago,
                        pagotransdep.cuentadeposito_id                        
                        FROM crm_pedidoonline pedidoonline
                        INNER JOIN crm_detallepedidoonline detallepedidoonline ON pedidoonline.id = detallepedidoonline.pedido_id
                        LEFT JOIN crm_pagotransdep pagotransdep ON pagotransdep.pedido_id = pedidoonline.id
                        INNER JOIN sga_persona persona ON pedidoonline.persona_id = persona.id
                        WHERE pedidoonline."status" 
                        AND persona.cedula='%s' """ % (self.inscripcionaspirante.persona.cedula)
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
        except Exception as ex:
            pass

    def fecha_primer_pago(self):
        from sagest.models import Rubro, Pago
        pago = None
        try:
            if self.formapagopac and self.formapagopac.id == 2:
                if Rubro.objects.filter(status=True, inscripcion=self, admisionposgradotipo=2).exists():
                    primerrubro = Rubro.objects.filter(status=True, inscripcion=self, admisionposgradotipo=2).order_by('id')[0]
                    pago = Pago.objects.filter(status=True, rubro = primerrubro).order_by('id')[0]
                else:
                    primerrubro = Rubro.objects.filter(status=True, inscripcion=self).order_by('id')[0]
                    pago = Pago.objects.filter(status=True, rubro = primerrubro).order_by('id')[0]
            else:
                if Rubro.objects.filter(status=True, inscripcion=self).exists():
                    primerrubro = Rubro.objects.filter(status=True, inscripcion=self).order_by('id')[0]
                    pago = Pago.objects.filter(status=True, rubro=primerrubro).order_by('id')[0]
            return pago.fecha if pago else None
        except Exception as ex:
            pass

    def comprobante_subido(self):
        from sagest.models import ComprobanteAlumno
        estado = False
        if ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona, asesor=self.asesor, asesor__isnull=False).exists():
            estado = True
        # elif ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona, carrera__icontains=str(self.cohortes.maestriaadmision.carrera.nombre)).exists():
        #     estado = True
        return estado

    def comprobante_subido_epunemi(self):
        try:
            from django.db import connections
            from sagest.models import ComprobanteAlumno

            estado = False
            cursor = connections['epunemi'].cursor()

            sql = """SELECT pe.id FROM sga_persona AS pe WHERE (pe.cedula='%s' OR pe.pasaporte='%s' OR pe.ruc='%s') AND pe.status=TRUE;  """ % (self.inscripcionaspirante.persona.cedula, self.inscripcionaspirante.persona.cedula, self.inscripcionaspirante.persona.cedula)
            cursor.execute(sql)
            idalumno = cursor.fetchone()

            if self.asesor:
                if idalumno is None:
                    estado = False
                else:
                    sql = """SELECT comalu.id FROM sagest_comprobantealumno comalu INNER JOIN sga_persona perso on comalu.persona_id=perso.id 
                    WHERE perso.id=%s AND comalu.status=TRUE AND comalu.asesor = '%s' AND comalu.telefono_asesor = '%s' ORDER BY comalu.id asc LIMIT 1; """ % (idalumno[0], self.asesor.persona.nombre_completo_inverso(), self.asesor.persona.telefono)
                    cursor.execute(sql)
                    registrocomprobante = cursor.fetchone()
                    if registrocomprobante is not None:
                        estado = True
                    else:
                        estado = False
            else:
                estado = False
            return estado
        except Exception as ex:
            pass

    def get_comprobante_subido(self):
        from sagest.models import ComprobanteAlumno
        if ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona, asesor=self.asesor).exists():
            return ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona, asesor=self.asesor).order_by('id')[0]
        # elif ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona, carrera__icontains=str(self.cohortes.maestriaadmision.carrera.nombre)).exists():
        #     return ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona, carrera__icontains=str(self.cohortes.maestriaadmision.carrera.nombre)).order_by('id')[0]

    def get_comprobante_inscripcion(self):
        from sagest.models import ComprobanteAlumno
        if ComprobanteAlumno.objects.filter(status=True, inscripcioncohorte=self.id, asesor=self.asesor).exists():
            return ComprobanteAlumno.objects.filter(status=True, inscripcioncohorte=self.id, asesor=self.asesor).order_by('-id')[0]
        else:
            if ComprobanteAlumno.objects.filter(status=True, persona=self.inscripcionaspirante.persona, asesor=self.asesor).exists():
                return ComprobanteAlumno.objects.filter(status=True, asesor=self.asesor, persona=self.inscripcionaspirante.persona).order_by('-id')[0]


    def get_comprobante_subido_epunemi(self):
        from django.db import connections
        from sagest.models import ComprobanteAlumno

        try:
            cursor = connections['epunemi'].cursor()
            sql = """SELECT comalu.fecha_creacion FROM sagest_comprobantealumno comalu INNER JOIN sga_persona perso on comalu.persona_id=perso.id 
            WHERE perso.cedula='%s' AND comalu.status=TRUE AND comalu.asesor = '%s' AND comalu.telefono_asesor = '%s' ORDER BY comalu.id asc LIMIT 1; """ % (self.inscripcionaspirante.persona.cedula, self.asesor.persona.nombre_completo_inverso(), self.asesor.persona.telefono)
            cursor.execute(sql)
            registrocomprobante = cursor.fetchone()

            return registrocomprobante[0]
        except Exception as ex:
            pass

    def tiene_pedidoonline_transferencia(self):
        try:
            from django.db import connections
            from sagest.models import Rubro
            primer = Rubro.objects.filter(status=True, inscripcion=self).order_by('id').first()
            estado = False
            idpedidos = []
            cursor = connections['epunemi'].cursor()
            sql = """SELECT deta.id FROM crm_pedidoonline pedi 
                    INNER JOIN crm_detallepedidoonline deta ON deta.pedido_id = pedi.id
                    INNER JOIN sga_persona per ON pedi.persona_id = per.id
                    INNER JOIN crm_pagotransdep pag on pag.pedido_id = pedi.id
                    WHERE (per.cedula='%s' OR per.pasaporte='%s' OR per.ruc='%s') AND pedi."status"
                    AND deta."status" AND deta.rubro_id = %s AND pedi.estado IN (1,2) 
                    AND pedi.tipopago = 2 AND pag.tipocomprobante = 2""" % (
                    self.inscripcionaspirante.persona.cedula, self.inscripcionaspirante.persona.cedula,
                    self.inscripcionaspirante.persona.cedula, primer.idrubroepunemi)
            cursor.execute(sql)
            tienepedido = cursor.fetchone()

            if tienepedido is not None:
                estado = True
            cursor.close()
            return estado
        except Exception as ex:
            pass

    def fecha_pedidoonline_transferencia(self):
        try:
            from django.db import connections
            from sagest.models import Rubro
            primer = Rubro.objects.filter(status=True, inscripcion=self).order_by('id').first()
            idpedidos = []
            cursor = connections['epunemi'].cursor()
            sql = """SELECT pedi.fecha_creacion FROM crm_pedidoonline pedi 
                    INNER JOIN crm_detallepedidoonline deta ON deta.pedido_id = pedi.id
                    INNER JOIN sga_persona per ON pedi.persona_id = per.id
                    INNER JOIN crm_pagotransdep pag on pag.pedido_id = pedi.id
                    WHERE (per.cedula='%s' OR per.pasaporte='%s' OR per.ruc='%s') AND pedi."status"
                    AND deta."status" AND deta.rubro_id = %s AND pedi.estado IN (1,2) 
                    AND pedi.tipopago = 2 AND pag.tipocomprobante = 2 ORDER BY deta.id DESC LIMIT 1;""" % (
                    self.inscripcionaspirante.persona.cedula, self.inscripcionaspirante.persona.cedula,
                    self.inscripcionaspirante.persona.cedula, primer.idrubroepunemi)
            cursor.execute(sql)
            fechapedido = cursor.fetchone()
            return fechapedido[0]
        except Exception as ex:
            pass

    def tiene_pedidoonline_deposito(self):
        try:
            from django.db import connections
            from sagest.models import Rubro
            primer = Rubro.objects.filter(status=True, inscripcion=self).order_by('id').first()
            estado = False
            idpedidos = []
            cursor = connections['epunemi'].cursor()
            sql = """SELECT deta.id FROM crm_pedidoonline pedi 
                    INNER JOIN crm_detallepedidoonline deta ON deta.pedido_id = pedi.id
                    INNER JOIN sga_persona per ON pedi.persona_id = per.id
                    INNER JOIN crm_pagotransdep pag on pag.pedido_id = pedi.id
                    WHERE (per.cedula='%s' OR per.pasaporte='%s' OR per.ruc='%s') AND pedi."status"
                    AND deta."status" AND deta.rubro_id = %s AND pedi.estado IN (1,2) 
                    AND pedi.tipopago = 2 AND pag.tipocomprobante = 1""" % (
                    self.inscripcionaspirante.persona.cedula, self.inscripcionaspirante.persona.cedula,
                    self.inscripcionaspirante.persona.cedula, primer.idrubroepunemi)
            cursor.execute(sql)
            tienepedido = cursor.fetchone()

            if tienepedido is not None:
                estado = True
            cursor.close()
            return estado
        except Exception as ex:
            pass

    def fecha_pedidoonline_deposito(self):
        try:
            from django.db import connections
            from sagest.models import Rubro
            primer = Rubro.objects.filter(status=True, inscripcion=self).order_by('id').first()
            idpedidos = []
            cursor = connections['epunemi'].cursor()
            sql = """SELECT pedi.fecha_creacion FROM crm_pedidoonline pedi 
                    INNER JOIN crm_detallepedidoonline deta ON deta.pedido_id = pedi.id
                    INNER JOIN sga_persona per ON pedi.persona_id = per.id
                    INNER JOIN crm_pagotransdep pag on pag.pedido_id = pedi.id
                    WHERE (per.cedula='%s' OR per.pasaporte='%s' OR per.ruc='%s') AND pedi."status"
                    AND deta."status" AND deta.rubro_id = %s AND pedi.estado IN (1,2) 
                    AND pedi.tipopago = 2 AND pag.tipocomprobante = 1 ORDER BY deta.id DESC LIMIT 1;""" % (
                    self.inscripcionaspirante.persona.cedula, self.inscripcionaspirante.persona.cedula,
                    self.inscripcionaspirante.persona.cedula, primer.idrubroepunemi)
            cursor.execute(sql)
            fechapedido = cursor.fetchone()
            return fechapedido[0]
        except Exception as ex:
            pass

    def tiene_pedidoonline_kushki(self):
        try:
            from django.db import connections
            from sagest.models import Rubro
            primer = Rubro.objects.filter(status=True, inscripcion=self).order_by('id').first()
            estado = False
            idpedidos = []
            cursor = connections['epunemi'].cursor()
            sql = """SELECT deta.id FROM crm_pedidoonline pedi 
                    INNER JOIN crm_detallepedidoonline deta ON deta.pedido_id = pedi.id
                    INNER JOIN sga_persona per ON pedi.persona_id = per.id
                    WHERE (per.cedula='%s' OR per.pasaporte='%s' OR per.ruc='%s') AND pedi."status"
                    AND deta."status" AND deta.rubro_id = %s AND pedi.estado IN (1,2) AND pedi.tipopago = 1""" % (
                    self.inscripcionaspirante.persona.cedula, self.inscripcionaspirante.persona.cedula,
                    self.inscripcionaspirante.persona.cedula, primer.idrubroepunemi)
            cursor.execute(sql)
            tienepedido = cursor.fetchone()

            if tienepedido is not None:
                estado = True
            cursor.close()
            return estado
        except Exception as ex:
            pass

    def fecha_pedidoonline_kushki(self):
        try:
            from django.db import connections
            from sagest.models import Rubro
            primer = Rubro.objects.filter(status=True, inscripcion=self).order_by('id').first()
            idpedidos = []
            cursor = connections['epunemi'].cursor()
            sql = """SELECT pedi.fecha_creacion FROM crm_pedidoonline pedi 
                    INNER JOIN crm_detallepedidoonline deta ON deta.pedido_id = pedi.id
                    INNER JOIN sga_persona per ON pedi.persona_id = per.id
                    WHERE (per.cedula='%s' OR per.pasaporte='%s' OR per.ruc='%s') AND pedi."status"
                    AND deta."status" AND deta.rubro_id = %s AND pedi.estado IN (1,2) AND pedi.tipopago = 1 ORDER BY deta.id DESC LIMIT 1;""" % (
                    self.inscripcionaspirante.persona.cedula, self.inscripcionaspirante.persona.cedula,
                    self.inscripcionaspirante.persona.cedula, primer.idrubroepunemi)
            cursor.execute(sql)
            fechapedido = cursor.fetchone()
            return fechapedido[0]
        except Exception as ex:
            pass

    def nombre_mencion(self):
        from sga.models import ItinerarioMallaEspecilidad
        try:
            iti = ItinerarioMallaEspecilidad.objects.filter(status=True, malla=self.cohortes.maestriaadmision.carrera.malla(), itinerario=self.itinerario).order_by('-id').first()
            return iti.nombre
        except Exception as ex:
            pass

    def nombre_resolucion(self):
        from sga.models import ItinerarioMallaEspecilidad
        try:
            iti = ItinerarioMallaEspecilidad.objects.filter(status=True, malla=self.cohortes.maestriaadmision.carrera.malla(), itinerario=self.itinerario).order_by('-id').first()
            return iti.numeroresolucion if iti.numeroresolucion else ''
        except Exception as ex:
            pass

    def fecha_cancelacion(self):
        listado_fechas2 = []
        if self.comprobante_subido():
            d = {'fecha': self.get_comprobante_subido().fecha_creacion.date(),
                 'medio': 'COMPROBANTE SUBIDO POR ASESOR'}
            listado_fechas2.append(d)
        elif self.comprobante_subido_epunemi():
            d = {'fecha': self.get_comprobante_subido_epunemi(), 'medio': 'COMPROBANTE SUBIDO POR CONSULTA SALDOS'}
            listado_fechas2.append(d)
        elif self.total_pagado_rubro_cohorte() > 0:
            d = {'fecha': self.fecha_primer_pago(), 'medio': 'VENTA DIRECTA DE CAJA'}
            listado_fechas2.append(d)
        first = listado_fechas2[0]['fecha']
        return first

    def tiene_grupo_examen(self):
        return True if self.integrantegrupoexamenmsc_set.filter(grupoexamen__estado_emailentrevista=2, status=True, inscripcion__status=True).exists() else False

    def grupo_examen(self):
        return self.integrantegrupoexamenmsc_set.get(grupoexamen__estado_emailentrevista=2, status=True)

    def tiene_grupo_entrevista(self):
        return True if self.integrantegrupoentrevitamsc_set.filter(grupoentrevista__estado_emailentrevista=2, status=True, inscripcion__status=True).exists() else False

    def grupo_entrevista(self):
        return self.integrantegrupoentrevitamsc_set.get(grupoentrevista__estado_emailentrevista=2, status=True)

    def matricula_activa_cohorte(self):
        from sagest.models import Matricula
        return True if Matricula.objects.filter(status=True, inscripcion=self.inscripcion, inscripcion__carrera=self.cohortes.maestriaadmision.carrera, retiradomatricula=False).exists() else False

    def retirado_matricula(self):
        from sagest.models import Matricula
        return True if Matricula.objects.filter(status=True, inscripcion=self.inscripcion,
                                                inscripcion__carrera=self.cohortes.maestriaadmision.carrera,
                                                retiradomatricula=True).exists() else False
    def contrato_posgrado(self):
        return Contrato.objects.filter(status=True, inscripcion=self, inscripcion__status=True).last()

    def garante_posgrado(self):
        return True if GarantePagoMaestria.objects.filter(status=True, inscripcioncohorte=self).exists() else False

    def tiene_contrato_anulado(self):
        return True if Contrato.objects.filter(status=False, estado=5, inscripcion=self).exists() else False

    def reservar_lead_territorio(self):
        from sga.funciones import notificacion4
        reservacion = None
        if AsesorTerritorio.objects.filter(status=True, canton=self.inscripcionaspirante.persona.canton).exists():
            if not self.tiene_reservaciones() and self.leaddezona:
                territorio = AsesorTerritorio.objects.filter(status=True, canton=self.inscripcionaspirante.persona.canton).first()
                asesor = AsesorComercial.objects.get(status=True, pk=territorio.asesor.id)
                reservacion = HistorialReservacionProspecto(inscripcion_id=self.id,
                                                            persona_id=asesor.persona.id,
                                                            observacion='Reservado automáticamente por concepto de zonas o territorio')
                reservacion.save()

                asunto = u"RESERVACIÓN DE PROSPECTO DE TERRITORIO"
                observacion = f'Se le comunica que se ha reservado de forma automática al prospecto {self} para su posterior asignación al asesor de territorio {reservacion.persona.nombre_completo_inverso()} por concepto de atención de zonas. Por favor, dar seguimiento a la reservación.'

                supervisores = Persona.objects.filter(status=True, id__in=variable_valor('PERSONAL_SUPERVISION'))

                for supervisor in supervisores:
                    para = supervisor
                    perfiu = supervisor.perfilusuario_administrativo()

                    notificacion4(asunto, observacion, para, None,
                                  '/comercial?action=leadsregistrados&id=' + str(asesor.id) + '&s=' + str(self.inscripcionaspirante.persona.cedula) + '&idc=0',
                                  reservacion.pk, 1,
                                  'sga', HistorialReservacionProspecto, perfiu)
        else:
            self.leaddezona = False
            self.save()
        return reservacion

    def asignar_asesor_convenio(self):
        from sga.funciones import notificacion4
        if self.convenio:
            if ConvenioAsesor.objects.filter(status=True, convenio=self.convenio).exists():
                convenio = ConvenioAsesor.objects.filter(status=True, convenio=self.convenio).first()
                self.asesor = convenio.asesor
                self.estado_asesor = 2
                self.save()

                histo = HistorialAsesor(inscripcion_id=self.id, fecha_inicio=self.fecha_modificacion,
                                        fecha_fin=None, asesor=self.asesor,
                                        observacion='Fue asignado a un asesor relacionado al convenio seleccionado')
                histo.save()

                asunto= u"POSTULACIÓN A MAESTRIA ASIGNADA POR CONVENIO"
                observacion= u"Se le comunica que se le ha asignado la siguiente postulación mediante la selección de convenio"
                para = self.asesor.persona
                perfiu = para.perfilusuario_administrativo()
                notificacion4(asunto, observacion, para, None,
                              '/comercial?s=' + str(self.inscripcionaspirante.persona.cedula) + '&idc=0&ide=0&ida=0&idanio=2024&desde=&hasta=&cantidad=25&idcan=0',
                              self.pk, 1, 'sga', InscripcionCohorte, perfiu)
                return True
            else:
                return False
        else:
            return False

    def asignar_mismo_asesor(self):
        if InscripcionCohorte.objects.filter(status=True, asesor__isnull=False, inscripcionaspirante__persona=self.inscripcionaspirante.persona, asesor__activo=True).exists():
            asesor = InscripcionCohorte.objects.filter(status=True, asesor__isnull=False, inscripcionaspirante__persona=self.inscripcionaspirante.persona, asesor__activo=True).order_by('-id').first().asesor
            self.asesor = asesor
            self.estado_asesor = 2
            self.save()

            histo = HistorialAsesor(inscripcion_id=self.id, fecha_inicio=self.fecha_modificacion,
                                    fecha_fin=None, asesor=self.asesor, observacion='Fue asignado a un asesor que ya lo trabajó anteriormente')
            histo.save()
            return True
        else:
            return False

    def revivir_postulacion(self):
        from sagest.models import Rubro
        from django.db import connections

        hoy = datetime.now().date()
        per = Persona.objects.get(pk=1)
        if CohorteMaestria.objects.values('id').filter(maestriaadmision__carrera=self.cohortes.maestriaadmision.carrera, fechainicioinsp__lte=hoy, fechafininsp__gte=hoy, activo=True, status=True, procesoabierto=True).exists():
            cohorte = CohorteMaestria.objects.filter(maestriaadmision__carrera=self.cohortes.maestriaadmision.carrera, fechainicioinsp__lte=hoy, fechafininsp__gte=hoy, activo=True, status=True, procesoabierto=True).first()

            listarequisitos = EvidenciaRequisitosAspirante.objects.filter(inscripcioncohorte=self,
                                                                          requisitos__requisito__claserequisito__clasificacion=1)
            canrequi = RequisitosMaestria.objects.filter(status=True, obligatorio=True,
                                                         cohorte__id=cohorte.id,
                                                         requisito__claserequisito__clasificacion=1).distinct().count()
            listarequisitosfinan = EvidenciaRequisitosAspirante.objects.filter(inscripcioncohorte=self,
                                                                               requisitos__requisito__claserequisito__clasificacion=3)

            if self.subirrequisitogarante:
                canrequifi = RequisitosMaestria.objects.filter(status=True, obligatorio=True,
                                                               cohorte__id=cohorte.id,
                                                               requisito__claserequisito__clasificacion=3).distinct().count()
            else:
                canrequifi = RequisitosMaestria.objects.filter(status=True, obligatorio=True,
                                                               cohorte__id=cohorte.id,
                                                               requisito__claserequisito__clasificacion=3).exclude(
                    requisito__id__in=[56, 57, 59]).distinct().count()

            # SI TIENE EVIDENCIAS DE ADMISION EN LA COHORTE PASADA
            for lis in listarequisitos:
                if RequisitosMaestria.objects.filter(requisito=lis.requisitos.requisito, cohorte_id=cohorte.id,
                                                     status=True):
                    requi = RequisitosMaestria.objects.filter(requisito=lis.requisitos.requisito,
                                                              cohorte_id=cohorte.id, status=True)[0]
                    lis.requisitos = requi
                    lis.save()

            canevi = EvidenciaRequisitosAspirante.objects.filter(inscripcioncohorte=self,
                                                                 requisitos__cohorte__id=cohorte.id,
                                                                 requisitos__requisito__claserequisito__clasificacion=1,
                                                                 detalleevidenciarequisitosaspirante__estado_aprobacion=2,
                                                                 requisitos__status=True).distinct().count()

            if canevi == canrequi:
                self.estado_aprobador = 2
            else:
                self.estado_aprobador = 1
                self.todosubido = False
                self.preaprobado = False

            self.save()

            # SI TIENE EVIDENCIAS DE FINANCIAMIENTO EN LA COHORTE PASADA
            if self.formapagopac:
                if self.formapagopac.id == 2:
                    for listf in listarequisitosfinan:
                        if RequisitosMaestria.objects.filter(requisito=listf.requisitos.requisito,
                                                             cohorte_id=cohorte.id, status=True,
                                                             requisito__claserequisito__clasificacion=3):
                            requifinan = RequisitosMaestria.objects.filter(requisito=listf.requisitos.requisito,
                                                                           cohorte_id=cohorte.id, status=True,
                                                                           requisito__claserequisito__clasificacion=3)[0]
                            listf.requisitos = requifinan
                            listf.save()

                    canevifi = EvidenciaRequisitosAspirante.objects.filter(inscripcioncohorte=self,
                                                                           requisitos__cohorte__id=cohorte.id,
                                                                           requisitos__requisito__claserequisito__clasificacion=3,
                                                                           detalleevidenciarequisitosaspirante__estado_aprobacion=2).count()

                    if canevifi == canrequifi:
                        self.estadoformapago = 2
                    else:
                        self.estadoformapago = 1
                        self.todosubidofi = False

                    self.save()

            # SI TIENE RUBROS GENERADOS
            chorte = CohorteMaestria.objects.get(id=cohorte.id, status=True)
            if Rubro.objects.filter(inscripcion=self, status=True).exists():
                rubros = Rubro.objects.filter(inscripcion=self, status=True)
                for rubro in rubros:
                    if rubro.idrubroepunemi != 0:
                        cursor = connections['epunemi'].cursor()
                        sql = """SELECT id FROM sagest_pago WHERE rubro_id=%s; """ % (rubro.idrubroepunemi)
                        cursor.execute(sql)
                        tienerubropagos = cursor.fetchone()

                        if tienerubropagos is None:
                            sql = """DELETE FROM sagest_rubro WHERE sagest_rubro.id=%s AND sagest_rubro.idrubrounemi=%s; """ % (
                                rubro.idrubroepunemi, rubro.id)
                            cursor.execute(sql)
                            cursor.close()

                        rubro.status = False
                        rubro.save()

            if self.cohortes.tipo == 1:
                if IntegranteGrupoExamenMsc.objects.filter(status=True, inscripcion=self).exists():
                    lista = IntegranteGrupoExamenMsc.objects.filter(status=True, inscripcion=self)
                    for li in lista:
                        li.status = False
                        li.save()

                if IntegranteGrupoEntrevitaMsc.objects.filter(status=True, inscripcion=self).exists():
                    lista2 = IntegranteGrupoEntrevitaMsc.objects.filter(status=True, inscripcion=self)
                    for li2 in lista2:
                        li2.status = False
                        li2.save()

            elif self.cohortes.tipo == 2:
                if IntegranteGrupoExamenMsc.objects.filter(status=True, inscripcion=self).exists():
                    lista = IntegranteGrupoExamenMsc.objects.filter(status=True, inscripcion=self)
                    for li in lista:
                        li.status = False
                        li.save()

            if Contrato.objects.filter(status=True, inscripcion=self).exists():
                contratopos = Contrato.objects.get(status=True, inscripcion=self)

                detalleevidencia = DetalleAprobacionContrato(contrato_id=contratopos.id, espagare=False,
                                                             observacion='Rechazado por cambio de cohorte',
                                                             persona=per, estado_aprobacion=3,
                                                             fecha_aprobacion=datetime.now(),
                                                             archivocontrato=contratopos.archivocontrato)
                detalleevidencia.save()

                if contratopos.inscripcion.formapagopac.id == 2:
                    detalleevidencia = DetalleAprobacionContrato(contrato_id=contratopos.id, espagare=True,
                                                                 observacion='Rechazado por cambio de cohorte',
                                                                 persona=per, estado_aprobacion=3,
                                                                 fecha_aprobacion=datetime.now(),
                                                                 archivocontrato=contratopos.archivopagare)
                    detalleevidencia.save()

                contratopos.estado = 3
                contratopos.estadopagare = 3
                contratopos.save()

            observacion = f'Cambio de {self.cohortes} a {chorte}.'
            cambio = CambioAdmitidoCohorteInscripcion(inscripcionCohorte=self, cohortes=chorte, observacion=observacion)
            cambio.save()

            self.cohortes_id = chorte
            self.tiporespuesta = None
            self.status = True
            self.save()
        else:
            self.tiporespuesta = None
            self.status = True
            self.save()
        return True

    def subio_requisitos_homologacion(self):
        estado = False
        cantirequisitos = RequisitosMaestria.objects.filter(status=True, maestria=self.cohortes.maestriaadmision, requisito__claserequisito__clasificacion__id=4, obligatorio=True).count()
        cantidadrequisubidos = EvidenciaRequisitosAspirante.objects.filter(status=True, inscripcioncohorte=self, requisitos__maestria=self.cohortes.maestriaadmision,
                                                                           requisitos__requisito__claserequisito__clasificacion__id=4, requisitos__obligatorio=True).count()
        if cantirequisitos == cantidadrequisubidos:
            estado = True

        return estado

    def delete(self, *args, **kwargs):
        if self.estado_aprobador == 2:
            raise NameError(u"No puede eliminar la inscripción, porque el lead se encuentra admitido en el programa de maestría")
        if self.tiene_contrato_subido() or self.tiene_pagare_subido():
            raise NameError(u"No puede eliminar la inscripción, porque el lead tiene subido contratos")
        if self.total_pagado_rubro_cohorte() > 0:
            raise NameError(u"No puede eliminar la insripción, porque el lead registra pagos de rubros de maestría")
        super(InscripcionCohorte, self).delete(*args, **kwargs)

class DetallePreAprobacionPostulante(ModeloBase):
    inscripcion = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Prospecto', on_delete=models.CASCADE)
    preaprobado = models.BooleanField(default=False, verbose_name=u'Verfica si el postulante cumple con sus requisitos de admision')
    dias = models.IntegerField(default=0, verbose_name=u'Dias que tomó la aprobación')

    def __str__(self):
        return u'%s' % self.inscripcion

    class Meta:
        verbose_name = "Detalle de Pre aprobación de Postulante"
        verbose_name_plural = "Detalles de Pre aprobación de Postulante"
        ordering = ['-id']


class HistorialRespuestaProspecto(ModeloBase):
    inscripcion = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Prospecto', on_delete=models.CASCADE)
    tiporespuesta = models.ForeignKey(TipoRespuestaProspecto, blank=True, null=True, verbose_name=u'Respuesta del Prospecto', on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True, verbose_name=u"Observación")

    def __str__(self):
        return u'%s' % self.inscripcion.inscripcionaspirante

    class Meta:
        verbose_name = "Historial de Respuesta de Contacto de Lead"
        verbose_name_plural = "Historiales de Respuesta de Contacto de Leads"
        ordering = ['-id']

class HistorialReservacionProspecto(ModeloBase):
    inscripcion = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Prospecto', on_delete=models.CASCADE)
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Asesor Comercial', on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True, verbose_name=u"Observación")
    estado_asesor = models.IntegerField(choices=ESTADO_ASESOR_COMERCIAL, default=1, verbose_name=u'Estado de la Reservación')

    def __str__(self):
        return u'%s' % self.inscripcion.inscripcionaspirante

    class Meta:
        verbose_name = "Historial de Reservación de Prospecto"
        verbose_name_plural = "Historiales de Reservación de Prospecto"
        ordering = ['-id']



class DetalleAprobacionFormaPago(ModeloBase):
    inscripcion = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Prospecto', on_delete=models.CASCADE)
    formapagopac = models.ForeignKey('inno.TipoFormaPagoPac', blank=True, null=True, verbose_name=u'Forma de Pago', on_delete=models.CASCADE)
    estadoformapago = models.IntegerField(choices=ESTADO_FORMA_PAGO, default=1, verbose_name=u'Estado de forma de pago')
    observacion = models.TextField(blank=True, null=True, verbose_name=u"Observación")
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Asesor Comercial/Financiamiento', on_delete=models.CASCADE)
    tipofinanciamiento = models.ForeignKey(ConfigFinanciamientoCohorte, blank=True, null=True, verbose_name=u'Tipo de Financiamiento', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s' % self.inscripcion.inscripcionaspirante

    class Meta:
        verbose_name = u"Detalle de Aprobacion"
        verbose_name_plural = u"Detalles de Aprobacion"
        ordering = ['-id']

    def estadohistorial(self):
        return dict(ESTADO_FORMA_PAGO)[self.estadoformapago]


class GarantePagoMaestria(ModeloBase):
    inscripcioncohorte = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Aspirante', on_delete=models.CASCADE)
    # personajuridica = models.IntegerField(choices=GARANTE_PERSONA_JURIDICA, default=2, verbose_name=u'Es persona jurídica')
    cedula = models.CharField(default='', max_length=20, verbose_name=u"Número de cédula")
    nombres = models.CharField(default='', max_length=100, verbose_name=u'Nombres')
    apellido1 = models.CharField(default='', max_length=50, verbose_name=u"1er Apellido")
    apellido2 = models.CharField(default='', max_length=50, verbose_name=u"2do Apellido")
    genero = models.ForeignKey("sga.Sexo", blank=True, null=True, verbose_name=u'Género', on_delete=models.CASCADE)
    # estadocivil = models.ForeignKey('sga.PersonaEstadoCivil', blank=True, null=True,verbose_name=u"Estado civil", on_delete=models.CASCADE)
    email = models.CharField(default='', max_length=200, verbose_name=u"Correo electrónico")
    telefono = models.CharField(default='', max_length=50, verbose_name=u"Teléfono movil")
    direccion = models.CharField(default='', max_length=300, verbose_name=u"Dirección")
    # relaciondependencia = models.IntegerField(choices=GARANTE_RELACION_DEPENDENCIA, blank=True, null=True, verbose_name=u'Trabaja con relacción de dependencia')

    def __str__(self):
        return u'%s - %s %s %s' % (self.cedula, self.nombres, self.apellido1, self.apellido2)

    class Meta:
        verbose_name = u"Garante Pago Maestría"
        verbose_name_plural = u"Garantes Pago Maestría"
        ordering = ['-id']

    def nombre_completo(self):
        return self.nombres + ' ' + self.apellido1 + ' ' + self.apellido2

    def save(self, *args, **kwargs):
        self.nombres = self.nombres.strip().upper()
        self.apellido1 = self.apellido1.strip().upper()
        self.apellido2 = self.apellido2.strip().upper() if self.apellido2 else ''
        self.direccion = self.direccion.strip().upper()
        super(GarantePagoMaestria, self).save(*args, **kwargs)

class SecuenciaContratoPagare(ModeloBase):
    anioejercicio = models.ForeignKey('sagest.AnioEjercicio', verbose_name=u'Anio Ejercicio', on_delete=models.CASCADE)
    secuenciacontrato = models.IntegerField(default=0, verbose_name=u'Secuencia Contratos')
    secuenciapagare = models.IntegerField(default=0, verbose_name=u'Secuencia Pagarés')

    class Meta:
        verbose_name = u"Secuencia de contrato y pagaré"
        verbose_name_plural = u"Secuencias de contratos y pagarés"

    def save(self, *args, **kwargs):
        super(SecuenciaContratoPagare, self).save(*args, **kwargs)

class RecordatorioPagoMaestrante(ModeloBase):
    matricula = models.ForeignKey('sga.Matricula', blank=True, null=True, verbose_name=u'Maestrante', on_delete=models.CASCADE)
    rubro = models.ForeignKey('sagest.Rubro', verbose_name=u'Rubro Vencido', blank=True, null=True, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='recordatoriomaestrante/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de recordatorio de pagos vencidos')

    def __str__(self):
        return u'%s' % self.matricula.inscripcion.persona

    class Meta:
        verbose_name = u"Recordatorio de pago"
        verbose_name_plural = u"Recordatorios de pago"
        ordering = ['-id']

class Contrato(ModeloBase):
    inscripcion = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Aspirante', on_delete=models.CASCADE)
    numerocontrato = models.IntegerField(blank=True, null=True, verbose_name=u'Numero de contrato')
    fechacontrato = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de contrato')
    formapago = models.ForeignKey('inno.TipoFormaPagoPac', null=True, blank=True, verbose_name=u'Forma de Pago', on_delete=models.CASCADE)
    estado = models.IntegerField(choices=ESTADO_CONTRATO, default=1, verbose_name=u'Estado')
    archivocontrato = models.FileField(upload_to='contratopagoaspitanteposgradofirmado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de contrato aspirante posgrado firmado')
    observacion = models.TextField(blank=True, null=True, verbose_name=u'Observacion archivo contrato')
    numeropagare = models.IntegerField(blank=True, null=True, verbose_name=u'Numero de pagaré')
    fechapagare = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de pagaré')
    estadopagare = models.IntegerField(choices=ESTADO_CONTRATO, default=1, verbose_name=u'Estado de pagaré')
    archivopagare = models.FileField(upload_to='pagareaspitanteposgradofirmado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de pagaré aspirante posgrado firmado')
    observacionpagare = models.TextField(blank=True, null=True, verbose_name=u'Observación archivo pagaré')
    tablaamortizacionajustada = models.BooleanField(default=False, verbose_name=u'¿Se há ajustado la tabla de amortización?')
    contratolegalizado = models.BooleanField(default=False, verbose_name=u'¿Se há legalizado contrato?')
    respaldoarchivocontrato = models.FileField(upload_to='respaldocontratopago/%Y/%m/%d', blank=True, null=True, verbose_name=u'Respaldo cotrato pago')
    archivodescargado = models.FileField(upload_to='archivodescargado', blank=True, null=True, verbose_name=u'Contrato descargado')
    archivooficiodescargado = models.FileField(upload_to='oficiodescargado', blank=True, null=True, verbose_name=u'Archivo de solicitud de terminación de contrato descargado')
    archivooficio = models.FileField(upload_to='oficioterminacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de solicitud de terminación de contrato firmado')
    motivo_terminacion = models.IntegerField(choices=MOTIVO_OFICIO, default=0, verbose_name=u'Motivo de terminación')

    def __str__(self):
        return u'%s' % self.inscripcion.inscripcionaspirante

    def ultima_evidencia(self):
        if self.detalleaprobacioncontrato_set.filter(status=True, espagare=False, esoficio=False).exists():
            return self.detalleaprobacioncontrato_set.filter(status=True, espagare=False, esoficio=False).order_by('-id')[0]
        return None

    def contrato_acorde_formapago(self):
        try:
            if self.archivocontrato:
                pdf2contrato = PyPDF2.PdfFileReader(self.archivocontrato)
                if pdf2contrato:
                    numeropagina = pdf2contrato.numPages-1
                    if self.inscripcion.formapagopac.id == 1:
                        if numeropagina == 5:
                            return True
                    else:
                        if self.inscripcion.formapagopac.id == 2:
                            if numeropagina == 6:
                                return True
            return False
        except Exception as ex:
            return None


    def ultima_evidencia_estado(self):
        if self.detalleaprobacioncontrato_set.filter(status=True, espagare=False).exists():
            deta = self.detalleaprobacioncontrato_set.filter(status=True, espagare=False).order_by('-id')[0]
            if deta.estado_aprobacion == 1:
                return 'PENDIENTE'
            elif deta.estado_aprobacion == 2:
                return 'APROBADO'
            elif deta.estado_aprobacion == 3:
                return 'RECHAZADO'
        return None

    def ultima_evidencia_aspirante(self):
        if self.detalleaprobacioncontrato_set.filter(status=True, espagare=False, estadorevision=1).exists():
            return self.detalleaprobacioncontrato_set.filter(status=True, espagare=False, estadorevision=1).order_by('-id')[0]
        return None

    def download_evidencia(self):
        return self.archivocontrato.url

    def download_evidencia_respaldo(self):
        return self.respaldoarchivocontrato.url

    def download_descargado(self):
        return self.archivodescargado.url

    def download_oficio(self):
        return self.archivooficio.url

    def ultima_evidenciapagare(self):
        if self.detalleaprobacioncontrato_set.filter(status=True, espagare=True, esoficio=False).exists():
            return self.detalleaprobacioncontrato_set.filter(status=True, espagare=True, esoficio=False).order_by('-id')[0]
        return None

    def ultima_evidenciaoficio(self):
        if self.detalleaprobacioncontrato_set.filter(status=True, esoficio=True).exists():
            return self.detalleaprobacioncontrato_set.filter(status=True, esoficio=True).order_by('-id')[0]
        return None

    def ultima_evidenciapagare_estado(self):
        if self.detalleaprobacioncontrato_set.filter(status=True, espagare=True).exists():
            deta = self.detalleaprobacioncontrato_set.filter(status=True, espagare=True).order_by('-id')[0]
            if deta.estado_aprobacion == 1:
                return 'PENDIENTE'
            elif deta.estado_aprobacion == 2:
                return 'APROBADO'
            elif deta.estado_aprobacion == 3:
                return 'RECHAZADO'
        return None

    def ultima_evidencia_aspirantepagare(self):
        if self.detalleaprobacioncontrato_set.filter(status=True, espagare=True, estadorevision=1).exists():
            return self.detalleaprobacioncontrato_set.filter(status=True, espagare=True, estadorevision=1).order_by('-id')[0]
        return None

    def download_evidenciapagare(self):
        return self.archivopagare.url

    class Meta:
        verbose_name = u"Contrato de pago"
        verbose_name_plural = u"Contratos de pago"
        ordering = ['-id']

class DetalleAprobacionContrato(ModeloBase):
    contrato = models.ForeignKey(Contrato, blank=True, null=True, verbose_name=u'Contrato', on_delete=models.CASCADE)
    estadorevision = models.IntegerField(choices=ESTADO_CONTRATO, default=1, verbose_name=u'Estado Revisión')
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Quien aprueba', on_delete=models.CASCADE)
    estado_aprobacion = models.IntegerField(choices=ESTADO_CONTRATO, default=1, verbose_name=u'Estado Aprobacion')
    fecha_aprobacion = models.DateTimeField(blank=True, null=True, verbose_name=u"Fecha de aprobacion o rechazo")
    observacion = models.TextField(blank=True, null=True, verbose_name=u"Observación aprobador")
    espagare = models.BooleanField(default=False, verbose_name=u'¿Es un registro de pagaré?')
    esoficio = models.BooleanField(default=False, verbose_name=u'¿Es un registro de oficio?')
    archivocontrato = models.FileField(upload_to='contratopagoaspitanteposgradofirmado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de contrato aspirante posgrado firmado')
    archivopagare = models.FileField(upload_to='pagareaspitanteposgradofirmado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de pagaré aspirante posgrado firmado')
    archivooficio = models.FileField(upload_to='oficioterminacion/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo de solicitud de terminación de contrato')
    motivo_terminacion = models.IntegerField(choices=MOTIVO_OFICIO, default=0, verbose_name=u'Motivo de terminación')

    def __str__(self):
        return u'%s' % self.contrato.inscripcion.inscripcionaspirante

    def esta_aprobado(self):
        return True if self.estado_aprobacion == 2 else False

    def esta_rechazado(self):
        return True if self.estado_aprobacion == 3 else False

    def esta_pendiente(self):
        return True if self.estadorevision == 1 else False

    def esta_con_pendiente(self):
        return True if self.estado_aprobacion == 1 else False

    def esta_con_rechazado(self):
        return True if self.estado_aprobacion == 3 else False

    def responsable(self):
        return Persona.objects.get(status=True, usuario_id=self.usuario_creacion.id)

    def download_evidencia(self):
        return self.archivocontrato.url

    def download_evidenciapagare(self):
        return self.archivopagare.url

    def download_evidenciaoficio(self):
        return self.archivooficio.url

    class Meta:
        verbose_name = u"Detalle de Aprobacion"
        verbose_name_plural = u"Detalles de Aprobacion"
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.observacion:
            self.observacion = self.observacion.upper()
        super(DetalleAprobacionContrato, self).save(*args, **kwargs)

class TablaAmortizacion(ModeloBase):
    contrato = models.ForeignKey(Contrato, blank=True, null=True, verbose_name=u'Contrato', on_delete=models.CASCADE)
    # numerocuota = models.IntegerField(default=0, verbose_name=u'Número de cuota')
    cuota = models.IntegerField(default=0, verbose_name=u'Número de cuota')
    nombre = models.CharField(max_length= 500, blank=True, null=True, verbose_name=u'Nombre')
    valor = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u'Valor')
    # fechainiciopago= models.DateField(blank=True, null=True, verbose_name=u"Fecha de aprobacion o rechazo")
    # fechafinpago = models.DateField(blank=True, null=True, verbose_name=u"Fecha de aprobacion o rechazo")
    fecha = models.DateField(blank=True, null=True, verbose_name=u"Fecha ")
    fechavence = models.DateField(blank=True, null=True, verbose_name=u"Fecha vence")

    def __str__(self):
        return u'%s' % self.nombre

    # def esta_pendiente(self):
    #     return True if self.estadorevision == 1 else False

    def esta_enuso(self):
        return True if self.rubro_set.filter(status=True) else False

    class Meta:
        verbose_name = u"Tabla de amortización"
        verbose_name_plural = u"Tablas de amortización"
        ordering = ['cuota']

    def save(self, *args, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        super(TablaAmortizacion, self).save(*args, **kwargs)

class HistorialAsesor(ModeloBase):
    inscripcion = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Lead', on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de Inicio Asesor')
    fecha_fin = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de Fin Asesor')
    asesor = models.ForeignKey(AsesorComercial, blank=True, null=True, verbose_name=u'Asesor Comercial', on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True, verbose_name=u"Observación")

    def __str__(self):
        return u'%s' % self.inscripcion.inscripcionaspirante

    class Meta:
        verbose_name = u"Historial Asesor"
        verbose_name_plural = u"Historiales Asesores"
        ordering = ['-id']

class CambioAdmitidoCohorteInscripcion(ModeloBase):
    observacion = models.CharField(default='', max_length=500, verbose_name=u"Observación")
    inscripcionCohorte = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Inscripción cohorte', on_delete=models.CASCADE)
    cohortes = models.ForeignKey(CohorteMaestria, blank=True, null=True, verbose_name=u'Cohorte maestría', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s' % self.cohortes

class TipoPago(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")

    def __str__(self):
        return u'%s' % self.nombre


class Pago(ModeloBase):
    inscripcioncohorte = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'InscripcionCohorte', on_delete=models.CASCADE)
    inscripcion = models.ForeignKey('sga.Inscripcion', blank=True, null=True, verbose_name=u'Inscripcion', on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoPago, blank=True, null=True, verbose_name=u'Tipo', on_delete=models.CASCADE)
    numerocuota = models.FloatField(default=0, blank=True, null=True,verbose_name=u'Numero cuota')
    cancelado = models.BooleanField(default=False, verbose_name=u'Cancelado')

    def __str__(self):
        return u'%s' % self.inscripcioncohorte

    def valorpagado(self):
        if self.cuotapago_set.filter(status=True).exists():
            return self.cuotapago_set.filter(status=True)[0].valor
        else:
            return ''

    def valorpagadopago(self):
        if self.cuotapago_set.filter(status=True).exists():
            return self.cuotapago_set.filter(status=True)[0].valor


    # def valorincompleto(self):
    #     if self.cuotapagadas_set.filter(cancelado=False, status=True).exists():
    #         return self.cuotapagadas_set.filter(cancelado=False, status=True).aggregate(valor=Sum('valor'))['valor']
    #     else:
    #         return ''


class CuotaPago(ModeloBase):
    pago = models.ForeignKey(Pago, verbose_name=u'Persona', on_delete=models.CASCADE)
    fechapago = models.DateField(blank=True, null=True, verbose_name=u"Fecha de pago")
    valor = models.FloatField(default=0, verbose_name=u'Valor mensual')

    def __str__(self):
        return u'%s' % self.valor


class CuotaPagadas(ModeloBase):
    pago = models.ForeignKey(Pago, verbose_name=u'Pago', on_delete=models.CASCADE)
    cuotapago = models.ForeignKey(CuotaPago, verbose_name=u'Cuota Pago', on_delete=models.CASCADE)
    valor = models.FloatField(default=0, verbose_name=u'Valor mensual')
    cancelado = models.BooleanField(default=False, verbose_name=u'Cancelado')

    def __str__(self):
        return u'%s' % self.valor


class TipoPreguntasPrograma(ModeloBase):
    descripcion = models.TextField(default='', verbose_name=u'Descripcion')

    def __str__(self):
        return u'%s' % self.descripcion

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(TipoPreguntasPrograma, self).save(*args, **kwargs)


class PreguntasPrograma(ModeloBase):
    tipopregunta = models.ForeignKey(TipoPreguntasPrograma, null=True, blank=True, verbose_name=u'Tipo Pregunta', on_delete=models.CASCADE)
    descripcion = models.TextField(default='', verbose_name=u'Descripcion')

    def __str__(self):
        return u'%s' % self.descripcion

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(PreguntasPrograma, self).save(*args, **kwargs)


class PreguntaMaestria(ModeloBase):
    cohortes = models.ForeignKey(CohorteMaestria, blank=True, null=True,verbose_name=u'Cohore Maestría', on_delete=models.CASCADE)
    pregunta = models.ForeignKey(PreguntasPrograma, blank=True, null=True,verbose_name=u'Pregunta', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s - %s' % (self.cohortes, self.pregunta)

    def mi_respuesta(self, idinscripentreviata):
        if self.respuestaentrevitamsc_set.filter(status=True, integrante_id=idinscripentreviata).exists():
            return self.respuestaentrevitamsc_set.filter(status=True, integrante_id=idinscripentreviata)[0].respuesta
        return None

    class Meta:
        verbose_name = u"PreguntaMaestria"
        verbose_name_plural = u"PreguntasMaestrias"
        ordering = ['cohortes']

    def save(self, *args, **kwargs):
        super(PreguntaMaestria, self).save(*args, **kwargs)


class TipoPersonaRequisito(ModeloBase):
    nombre = models.CharField(default='', max_length=250, verbose_name=u"Nombre del tipo de persona que sube el requisito")

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"TipoPersonaRequisito"
        verbose_name_plural = u"TipoPersonaRequisitos"
        ordering = ['nombre']
        unique_together = ('nombre',)

class Requisito(ModeloBase):
    nombre = models.CharField(default='', max_length=250, verbose_name=u"Nombre del archivo")
    observacion = models.CharField(default='', max_length=500, verbose_name=u"Observación")
    activo = models.BooleanField(default=True, verbose_name=u"Activo")
    archivo = models.FileField(upload_to='formatorequisito/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo')
    tipoarchivo = models.IntegerField(choices=TIPO_ARCHIVO, default=1, verbose_name=u'Formato pdf o img')
    tipopersona = models.ForeignKey(TipoPersonaRequisito, null=True, blank=True, verbose_name=u'Tipo de Persona', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s' % self.nombre

    def esta_uso(self):
        estado = False
        if self.claserequisito_set.all().exists():
            for clase in self.claserequisito_set.all():
                if clase.clasificacion.id in [1,3]:
                    estado = True if clase.requisito.requisitosmaestria_set.exists() else False
                    if estado == True:
                        return estado
                if clase.clasificacion.id == 2:
                    estado = True if clase.requisito.detallerequisitoingreso_set.exists() else False
                    if estado == True:
                        return estado
        return estado

    def download_link(self):
        return self.archivo.url

    def mi_requisito(self, idcohorte):
        if self.requisitosmaestria_set.filter(status=True).exists():
            if self.requisitosmaestria_set.filter(cohorte_id=idcohorte).exists():
                return self.requisitosmaestria_set.filter(cohorte_id=idcohorte)[0]
            else:
                return False
        else:
            return False

    class Meta:
        verbose_name = u"Requisito"
        verbose_name_plural = u"Requisitos"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.observacion = self.observacion.upper()
        super(Requisito, self).save(*args, **kwargs)

class TipoClasificacionRequisito(ModeloBase):
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u"Tipo de clasificación de requisito")

    def __str__(self):
        return u'%s' %self.descripcion

    def esta_uso(self):
        return True if self.claserequisito_set.all().exists() else False

    class Meta:
        verbose_name = u"Tipo Clasificación Requisito"
        verbose_name_plural = u"Tipo de clasificaciones de requisito"
        ordering = ['id']

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(TipoClasificacionRequisito, self).save(*args, **kwargs)

class ClaseRequisito(ModeloBase):
    requisito = models.ForeignKey(Requisito, null=True, blank=True, verbose_name=u'Requisito', on_delete=models.CASCADE)
    clasificacion = models.ForeignKey(TipoClasificacionRequisito, null=True, blank=True, verbose_name=u'Clasificación', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s - %s' % (self.requisito.nombre, self.clasificacion)

    def esta_uso(self):
        if self.clasificacion.id == 1:
            return True if self.requisito.requisitosmaestria_set.exists() else False
        if self.clasificacion.id == 2:
            return True if self.requisito.detallerequisitoingreso_set.exists() else False

    class Meta:
        verbose_name = u"Clase de Requisito"
        verbose_name_plural = u"Clase de Requisitos"
        ordering = ['requisito']

class RequisitosMaestria(ModeloBase):
    requisito = models.ForeignKey(Requisito, null=True, blank=True, verbose_name=u'Cohorte Maestria', on_delete=models.CASCADE)
    cohorte = models.ForeignKey(CohorteMaestria, null=True, blank=True, verbose_name=u'Cohorte Maestria', on_delete=models.CASCADE)
    maestria = models.ForeignKey(MaestriasAdmision, null=True, blank=True, verbose_name=u'Maestria', on_delete=models.CASCADE)
    obligatorio = models.BooleanField(default=True, verbose_name=u"Obligatorio")

    def __str__(self):
        return u'%s' % self.requisito

    def esta_uso(self):
        return True if self.evidenciarequisitosaspirante_set.all().exists() else False

    def detalle_requisitosmaestria(self, aspirante):
        if self.evidenciarequisitosaspirante_set.filter(inscripcioncohorte=aspirante,status=True).exists():
            return self.evidenciarequisitosaspirante_set.filter(inscripcioncohorte__inscripcionaspirante=aspirante,status=True)[0]
        else:
            return None

    def detalle_requisitosmaestriacohorte(self, inscripcioncohorte):
        if self.evidenciarequisitosaspirante_set.values("id").filter(inscripcioncohorte=inscripcioncohorte,status=True).exists():
            return self.evidenciarequisitosaspirante_set.filter(inscripcioncohorte=inscripcioncohorte,status=True).first()
        else:
            return None

    class Meta:
        verbose_name = u"MaestriaPeriodoAdmision"
        verbose_name_plural = u"MaestriaPeriodoAdmisiones"
        ordering = ['cohorte']

    def save(self, *args, **kwargs):
        super(RequisitosMaestria, self).save(*args, **kwargs)


class RequisitosGrupoCohorte(ModeloBase):
    requisito = models.ForeignKey(Requisito, null=True, blank=True, verbose_name=u'Requisito Maestria', on_delete=models.CASCADE)
    grupo = models.ForeignKey(GrupoRequisitoCohorte, null=True, blank=True, verbose_name=u'Grupo Cohorte Maestria', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s' % self.requisito

class EvidenciaRequisitosAspirante(ModeloBase):
    inscripcioncohorte = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Inscripcion Cohorte', on_delete=models.CASCADE)
    requisitos = models.ForeignKey(RequisitosMaestria, blank=True, null=True, verbose_name=u'Requisitos', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='evidenciaaspirantes/%Y/%m/%d', blank=True, null=True,verbose_name=u'Archivo')


    def __str__(self):
        return u'%s' % self.requisitos

    def ultima_evidencia(self):
        if self.detalleevidenciarequisitosaspirante_set.filter(status=True).exists():
            return self.detalleevidenciarequisitosaspirante_set.filter(status=True).order_by('-id')[0]
        return None

    def ultima_evidencia_aspirante(self):
        if self.detalleevidenciarequisitosaspirante_set.filter(status=True, estadorevision=1).exists():
            return self.detalleevidenciarequisitosaspirante_set.filter(status=True, estadorevision=1).order_by('-id')[0]
        return None

    # def ultima_evidencia_aprobador(self):
    #     if self.detalleevidenciarequisitosaspirante_set.filter(Q(status=True), (Q(estadorevision=2)| Q(estadorevision=3))).exists():
    #         return self.detalleevidenciarequisitosaspirante_set.filter(Q(status=True), (Q(estadorevision=2)| Q(estadorevision=3))).order_by('-id')[0]
    #     return None

    def download_evidencia(self):
        return self.archivo.url

    def save(self, *args, **kwargs):
        # self.observacion = self.observacion.upper()
        super(EvidenciaRequisitosAspirante, self).save(*args, **kwargs)


class DetalleEvidenciaRequisitosAspirante(ModeloBase):
    evidencia = models.ForeignKey(EvidenciaRequisitosAspirante, blank=True, null=True, verbose_name=u'Evidencia', on_delete=models.CASCADE)
    estadorevision = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u'Estado Revisión')
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Quien aprueba', on_delete=models.CASCADE)
    fecha = models.DateTimeField(blank=True, null=True, verbose_name=u"Fecha de subida evidencia")
    observacion = models.TextField(blank=True, null=True, verbose_name=u"Observación postulante")
    fecha_aprobacion = models.DateTimeField(blank=True, null=True, verbose_name=u"Fecha de aprobacion o rechazo")
    observacion_aprobacion = models.TextField(blank=True, null=True, verbose_name=u"Observación aprobador")
    estado_aprobacion = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u'Estado Aprobacion')

    def __str__(self):
        return u'%s' % self.observacion

    def esta_aprobado(self):
        return True if self.estado_aprobacion == 2 else False

    def estado_rechazado(self):
        return True if self.estado_aprobacion == 3 else False

    def esta_rechazado(self):
        return True if self.estadorevision == 3 else False

    def esta_pendiente(self):
        return True if self.estadorevision == 1 else False

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.upper()
        if self.observacion_aprobacion:
            self.observacion_aprobacion = self.observacion_aprobacion.upper()
        super(DetalleEvidenciaRequisitosAspirante, self).save(*args, **kwargs)


class EvidenciaPagoExamen(ModeloBase):
    inscripcioncohorte = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Inscripcion Cohorte', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='evidenciapagoexamen/%Y/%m/%d', blank=True, null=True,verbose_name=u'Archivo')
    estadorevision = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u'Estado Revisión')

    def __str__(self):
        return u'%s' % self.inscripcioncohorte

    def download_pagoexamen(self):
        return self.archivo.url

    def save(self, *args, **kwargs):
        super(EvidenciaPagoExamen, self).save(*args, **kwargs)


class GrupoExamenMsc(ModeloBase):
    profesor = models.ForeignKey('sga.Profesor', blank=True, null=True, verbose_name=u'Profesor', on_delete=models.CASCADE)
    cohorte = models.ForeignKey(CohorteMaestria, blank=True, null=True, verbose_name=u'Cohorte de maestria', on_delete=models.CASCADE)
    lugar = models.CharField(default='', max_length=100, verbose_name=u'Lugar de examen')
    fecha = models.DateField(blank=True, null=True, verbose_name=u'fecha bde exsamen')
    hora = models.TimeField(blank=True, null=True, verbose_name=u'Hora de examen')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    urlzoom = models.TextField(default='', verbose_name=u'URL Zoom')
    visible = models.BooleanField(default=True, verbose_name=u'Visible')
    estado_emailentrevista = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u'Estado Email evidencia')
    fecha_emailentrevista = models.DateTimeField(blank=True, null=True)
    persona_emailentrevista = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Quien aprueba o rechaza evidencias', on_delete=models.CASCADE)
    idgrupomoodle = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'id de grupo de moodle')
    codigonumber = models.CharField(default='', max_length=100, verbose_name=u'Codigo number sagest')

    def __str__(self):
        return u'%s - %s' % (self.lugar, self.cohorte.descripcion)

    class Meta:
        ordering = ['profesor', ]


    def mis_integrantes(self):
        return self.integrantegrupoexamenmsc_set.filter(inscripcion__status=True,status=True).order_by('inscripcion__inscripcionaspirante__persona__apellido1','inscripcion__inscripcionaspirante__persona__apellido2')

    def fecha_pasada(self):
        if self.fecha > datetime.now().date():
            return True
        else:
            return False

    def total_inscritos(self):
        return self.mis_integrantes().values('id').count()

    def puede_eliminar_grupo(self):
        return True if not self.integrantegrupoexamenmsc_set.values("id").filter(status=True).exists() else False

    def crear_actualizar_estudiantes_cursogrupoex(self, moodle):
        #################################################################################################################
        # AGREGAR ESTUDIANTE
        #################################################################################################################
        from sga.funciones import log
        try:
            # if self.idcursomoodle:
            contador = 0
            cursoid = 3
            # cursoid = self.idcursomoodle
            for estudiante in self.integrantegrupoexamenmsc_set.filter(status=True):
                contador += 1
                persona = estudiante.inscripcion.inscripcionaspirante.persona
                idnumber_user = persona.identificacion()
                bestudiante = moodle.BuscarUsuario('idnumber', 1, idnumber_user)
                estudianteid = 0
                # if not bestudiante:
                #     bestudiante = moodle.BuscarUsuario('idnumber', idnumber_user)
                #
                # if bestudiante['users']:
                #     if 'id' in bestudiante['users'][0]:
                #         estudianteid = bestudiante['users'][0]['id']
                # else:
                #     notuser = moodle.BuscarUsuario('username', persona.usuario.username)
                #     if not notuser:
                #         notuser = moodle.BuscarUsuario('username', persona.usuario.username)
                #     if notuser['users']:
                #         elminar = moodle.EliminarUsuario(notuser['users'][0]['id'])

                bestudiante = moodle.CrearUsuario(u'%s' % persona.usuario.username,
                                                  u'%s' % persona.identificacion(),
                                                  u'%s %s' % (persona.apellido1, persona.apellido2),
                                                  u'%s' % persona.nombres,
                                                  u'%s' % persona.email,
                                                  idnumber_user,
                                                  u'%s' % persona.canton.nombre if persona.canton else '',
                                                  u'%s' % persona.pais.nombre if persona.pais else '')
                # estudianteid = bestudiante[0]['id']
                if estudianteid > 0:
                    rolest = moodle.EnrolarCurso(5, 1, estudianteid, cursoid)
                    if persona.idusermoodle != estudianteid:
                        persona.idusermoodle = estudianteid
                        persona.save()
                print('************Estudiante: %s *** %s' % (contador, persona))
            # self.quitar_estudiantes_curso(moodle)
        except Exception as ex:
            log(u'Moodle Error al crear Estudiante: %s' % persona, None, "add", User.objects.get(pk=1))
            print('Error al crear estudiante %s' % ex)

    def crear_actualizar_docente_grupo_posgrado(self, moodle, tipourl):
        #################################################################################################################
        # AGREGAR DOCENTE
        #################################################################################################################
        from sga.funciones import log
        from sga.models import Profesor
        try:
            if self.idgrupomoodle:
                cursoid = self.idgrupomoodle
                if self.quitar_docente_grupo(moodle, tipourl):
                    # docentes = self.mis_profesores_autores()
                    docentes = Profesor.objects.filter(pk=self.profesor.id)
                    for curpro in docentes:
                        profesor = curpro
                        if profesor and profesor.persona.usuario and not 'POR DEFINIR' in profesor.persona.nombres:
                            persona = profesor.persona
                            username = persona.usuario.username
                            bprofesor = moodle.BuscarUsuario(self.cohorte, tipourl, 'username', username)
                            profesorid = 0
                            if not bprofesor:
                                bprofesor = moodle.BuscarUsuario(self.cohorte, tipourl, 'username', username)

                            if bprofesor['users']:
                                if 'id' in bprofesor['users'][0]:
                                    profesorid = bprofesor['users'][0]['id']
                            else:
                                idnumber_user = persona.identificacion()
                                notuser = moodle.BuscarUsuario(self.cohorte, tipourl, 'idnumber', idnumber_user)
                                if not notuser:
                                    notuser = moodle.BuscarUsuario(self.cohorte, tipourl, 'idnumber', idnumber_user)
                                if notuser['users']:
                                    elminar = moodle.EliminarUsuario(self.cohorte, tipourl, notuser['users'][0]['id'])

                                bprofesor = moodle.CrearUsuario(self.cohorte, tipourl, u'%s' % persona.usuario.username,
                                                                u'%s' % persona.identificacion(),
                                                                u'%s' % persona.nombres,
                                                                u'%s %s' % (persona.apellido1, persona.apellido2),
                                                                u'%s' % persona.emailinst,
                                                                idnumber_user,
                                                                u'%s' % persona.canton.nombre if persona.canton else '',
                                                                u'%s' % persona.pais.nombre if persona.pais else '')
                                profesorid = bprofesor[0]['id']

                            if profesorid > 0:
                                # PROFESOR-ABR-SEP2018
                                # rolest = moodle.EnrolarCurso(self.nivel.periodo, 3, profesorid, cursoid)
                                # PROFESOR-OCT-FEB2019
                                rolest = moodle.EnrolarCurso(self.cohorte, tipourl,9, profesorid, cursoid)
                                if persona.idusermoodleposgrado != profesorid:
                                    persona.idusermoodleposgrado = profesorid
                                    persona.save()
                            print('**********PROFESOR: %s' % profesor)
        except Exception as ex:
            # log(u'Moodle Error al crear docente: %s' % persona, None, "add", User.objects.get(pk=1))
            print('Error al crear docente %s' % ex)

    def quitar_docente_grupo(self, moodle , tipourl):
        from django.db import connections
        cursor = connections['moodle_pos'].cursor()
        #################################################################################################################
        # QUITAR DOCENTE
        #################################################################################################################
        if self.idgrupomoodle:
            cursoid = self.idgrupomoodle
            idprofesores = ""
            for x in self.values_list('profesor__persona__idusermoodle', flat=False).filter(status=True).order_by('id'):
                idprofesores += "%s," % x[0]
            idprofesores = self.profesor_id
            query = """SELECT DISTINCT enrol.userid, asi.roleid from mooc_user_enrolments enrol 
                        inner join mooc_role_assignments asi on asi.userid=enrol.userid and asi.roleid in(%s) 
                        where enrol.enrolid in(select en.id from mooc_enrol en where en.courseid=%s) 
                        AND enrol.userid not in(%s0) """ % (9, cursoid, idprofesores)
            cursor.execute(query)
            row = cursor.fetchall()
            if row:
                for deluser in row:
                    unrolest = moodle.UnEnrolarCurso(self.cohorte, tipourl, deluser[1], deluser[0], cursoid)
                    print('************ Eliminar Profesor: *** %s' % deluser[0])
        return True

    def crear_actualizar_estudiantes_grupo_posgrado(self, moodle, tipourl, codigoinscritogrupoexamen):
        #################################################################################################################
        # AGREGAR ESTUDIANTE
        #################################################################################################################
        from sga.funciones import log
        if self.idgrupomoodle:
            contador = 0
            cursoid = self.idgrupomoodle
            for estudiante in self.integrantegrupoexamenmsc_set.filter(pk=codigoinscritogrupoexamen,status=True):
                try:
                    contador += 1
                    bandera=0
                    persona = estudiante.inscripcion.inscripcionaspirante.persona
                    username = persona.usuario.username
                    bestudiante = moodle.BuscarUsuario(self.cohorte, tipourl, 'username', username)
                    estudianteid = 0
                    if not bestudiante:
                        bestudiante = moodle.BuscarUsuario(self.cohorte, tipourl, 'username', username)

                    if bestudiante['users']:
                        if 'id' in bestudiante['users'][0]:
                            estudianteid = bestudiante['users'][0]['id']
                    else:
                        idnumber_user = persona.identificacion()
                        notuser = moodle.BuscarUsuario(self.cohorte, tipourl, 'idnumber', idnumber_user)
                        if not notuser:
                            notuser = moodle.BuscarUsuario(self.cohorte, tipourl, 'idnumber', idnumber_user)
                        if notuser['users']:
                            elminar = moodle.EliminarUsuario(self.cohorte, tipourl, notuser['users'][0]['id'])

                        bestudiante = moodle.CrearUsuario(self.cohorte, tipourl, u'%s' % persona.usuario.username,
                                                          u'%s' % persona.identificacion(),
                                                          u'%s' % persona.nombres,
                                                          u'%s %s' % (persona.apellido1, persona.apellido2),
                                                          # u'%s' % persona.email,
                                                          u'%s' % persona.emailinst,
                                                          idnumber_user,
                                                          u'%s' % persona.canton.nombre if persona.canton else '',
                                                          u'%s' % persona.pais.nombre if persona.pais else '')
                        estudianteid = bestudiante[0]['id']
                    if estudianteid > 0:
                        # rolest = moodle.EnrolarCurso(5, estudianteid, cursoid)
                        # Estudiante-oct-feb2019
                        # rolest = moodle.EnrolarCurso(5, estudianteid, cursoid)
                        rolest = moodle.EnrolarCurso(self.cohorte,tipourl, 10, estudianteid, cursoid)
                        if persona.idusermoodleposgrado != estudianteid:
                            persona.idusermoodleposgrado = estudianteid
                            persona.save()
                    print('************Estudiante: %s *** %s' % (contador, persona))
                except Exception as ex:
                    log(u'Moodle Error al crear Estudiante: %s' % persona, None, "add", User.objects.get(pk=1))
                    print('Error al crear estudiante %s' % ex)

    def crear_actualizar_categoria_notas_grupo_posgrado(self):
        from django.db import connections
        from sga.models import ModeloEvaluativo
        cursor = connections['moodle_pos'].cursor()
        #################################################################################################################
        # AGREGAR SISTEMA DE CALIFICACION
        #################################################################################################################
        if self.idgrupomoodle:
            cursoid = self.idgrupomoodle
            modeloevaluativo = ModeloEvaluativo.objects.get(pk=3)
            modelonotas = modeloevaluativo.detallemodeloevaluativo_set.filter(migrarmoodle=True)
            if modelonotas:
                query = u"SELECT id FROM mooc_grade_categories WHERE parent is null and depth=1 and courseid= %s" % cursoid
                cursor.execute(query)
                row = cursor.fetchall()
                padrenota = 0
                fecha = int(time.mktime(datetime.now().date().timetuple()))
                if not row:
                    query = u"INSERT INTO mooc_grade_categories(courseid, parent, depth, path, fullname, aggregation, keephigh, droplow, aggregateonlygraded, hidden, timecreated, timemodified) VALUES (%s, null, 1, E'', E'?', 13, 0, 0, 0, 0, %s, %s)" % (cursoid, fecha, fecha)
                    cursor.execute(query)
                    query = u"SELECT id FROM mooc_grade_categories WHERE parent is null and depth=1 and courseid= %s" % cursoid
                    cursor.execute(query)
                    row = cursor.fetchall()
                    query = u"UPDATE mooc_grade_categories SET path='/%s/' WHERE id= %s" % (row[0][0], row[0][0])
                    cursor.execute(query)
                    padrenota = row[0][0]
                else:
                    padrenota = row[0][0]
                if padrenota > 0:
                    ordennota = 1
                    query = u"SELECT id FROM mooc_grade_items WHERE courseid=%s and itemtype='course' and iteminstance=%s" % (cursoid, padrenota)
                    cursor.execute(query)
                    row = cursor.fetchall()
                    if not row:
                        query = u"INSERT INTO mooc_grade_items (courseid, categoryid, itemname, itemtype, itemmodule, iteminstance, itemnumber, iteminfo, idnumber, calculation, gradetype, grademax, grademin, scaleid, outcomeid, gradepass, multfactor, plusfactor, aggregationcoef, aggregationcoef2, sortorder, display, decimals, hidden, locked, locktime, needsupdate, weightoverride, timecreated, timemodified) VALUES (%s, null, null, E'course', null, %s, null, null, null, null, 1, 100, 0, null, null, 0, 1, 0, 0, 0, %s, 0, 2, 0, 0, 0, 0, 0, %s, %s)" % (cursoid, padrenota, ordennota, fecha, fecha)
                        cursor.execute(query)

                    for modelo in modelonotas:
                        query = u"SELECT id FROM mooc_grade_categories WHERE parent=%s and depth=2 and courseid= %s and fullname='%s'" % (padrenota, cursoid, modelo.nombre)
                        cursor.execute(query)
                        row = cursor.fetchall()
                        padremodelo = 0
                        if not row:
                            query = u"INSERT INTO mooc_grade_categories(courseid, parent, depth, path, fullname, aggregation, keephigh, droplow, aggregateonlygraded, hidden, timecreated, timemodified) VALUES (%s, %s, 2, E'', E'%s', 0, 0, 0, 0, 0, %s, %s)" % (cursoid, padrenota, modelo.nombre, fecha, fecha)
                            cursor.execute(query)
                            query = u"SELECT id FROM mooc_grade_categories WHERE parent=%s and depth=2 and courseid= %s and fullname='%s'" % (padrenota, cursoid, modelo.nombre)
                            cursor.execute(query)
                            row = cursor.fetchall()
                            padremodelo = row[0][0]
                            query = u"UPDATE mooc_grade_categories SET path='/%s/%s/' WHERE id= %s" % (padrenota, padremodelo, padremodelo)
                            cursor.execute(query)
                        else:
                            padremodelo = row[0][0]
                        if padremodelo > 0:
                            ordennota += 1
                            query = u"SELECT id FROM mooc_grade_items WHERE courseid=%s and itemtype='category' and iteminstance=%s" % (cursoid, padremodelo)
                            cursor.execute(query)
                            row = cursor.fetchall()
                            if not row:
                                query = u"INSERT INTO mooc_grade_items (courseid, categoryid, itemname, itemtype, itemmodule, iteminstance, itemnumber, iteminfo, idnumber, calculation, gradetype, grademax, grademin, scaleid, outcomeid, gradepass, multfactor, plusfactor, aggregationcoef, aggregationcoef2, sortorder, display, decimals, hidden, locked, locktime, needsupdate, weightoverride, timecreated, timemodified) " \
                                        u"VALUES (%s, null, E'', E'category', null, %s, null, E'', E'', null, 1, %s, 0, null, null, 0, 1, 0, 0, %s, %s, 0, %s, 0, 0, 0, 0, 0, %s, %s)" \
                                        % (cursoid, padremodelo, modelo.notamaxima, null_to_decimal(modelo.notamaxima / 100, 2), ordennota, modelo.decimales, fecha, fecha)
                                cursor.execute(query)

    def crear_grupo_moodle(self, codigoinscritogrupoexamen, contadoringreso):
        from django.db import connections
        from moodle import moodle
        from sga.models import Coordinacion, Carrera, NivelMalla
        cursor = connections['moodle_pos'].cursor()
        #################################################################################################################
        #################################################################################################################
        # servidor
        AGREGAR_MODELO_NOTAS = True
        AGREGAR_ESTUDIANTE = True
        AGREGAR_DOCENTE = True

        parent_grupoid = 0
        tipourl = 1
        periodo = self.cohorte
        bgrupo = moodle.BuscarCategoriasid(periodo, tipourl, 70)
        # bgrupo = moodle.BuscarCategoriasid(periodo, tipourl,periodo.categoria)
        if bgrupo:
            if 'id' in bgrupo[0]:
                parent_grupoid = bgrupo[0]['id']
        contador = 0

        if parent_grupoid >= 0:
            if contadoringreso == 0:
                """"
                CREANDO EL PERIODO DE COHORTE EL ID SE CONFIGURA EN VARIABLES GLABALES
                """
                bperiodo = moodle.BuscarCategorias(periodo, tipourl, periodo.idnumber())
                parent_periodoid = 0
                if bperiodo:
                    if 'id' in bperiodo[0]:
                        parent_periodoid = bperiodo[0]['id']
                else:
                    bperiodo = moodle.CrearCategorias(periodo, tipourl, periodo.__str__(), periodo.idnumber(), periodo.__str__(), parent=parent_grupoid)
                    parent_periodoid = bperiodo[0]['id']
                # print('Periodo lectivo: %s' % periodo)
                if parent_periodoid > 0:
                    """"
                    CREANDO LAS COORDINACIONES
                    """
                    cordinaciones = Coordinacion.objects.filter(id=7).distinct()
                    for coordinacion in cordinaciones:
                        idnumber_coordinacion = u'%s-COR%s' % (periodo.idnumber(), coordinacion.id)
                        bcoordinacion = moodle.BuscarCategorias(periodo, tipourl, idnumber_coordinacion)
                        parent_coordinacionid = 0
                        if bcoordinacion:
                            if 'id' in bcoordinacion[0]:
                                parent_coordinacionid = bcoordinacion[0]['id']
                        else:
                            bcoordinacion = moodle.CrearCategorias(periodo, tipourl, coordinacion, idnumber_coordinacion,coordinacion.nombre, parent=parent_periodoid)
                            parent_coordinacionid = bcoordinacion[0]['id']
                        # print('**Facultad: %s' % coordinacion)
                        if parent_coordinacionid > 0:
                            """"
                            CREANDO LAS CARRERAS
                            """
                            idcarrera = self.cohorte.maestriaadmision.carrera.id
                            carreras = Carrera.objects.filter(pk=idcarrera).distinct()
                            for carrera in carreras:
                                idnumber_carrera = u'%s-COR%s-CARR%s' % (periodo.idnumber(), coordinacion.id, carrera.id)
                                bcarrera = moodle.BuscarCategorias(periodo, tipourl, idnumber_carrera)
                                parent_carreraid = 0
                                if bcarrera:
                                    if 'id' in bcarrera[0]:
                                        parent_carreraid = bcarrera[0]['id']
                                else:
                                    bcarrera = moodle.CrearCategorias(periodo, tipourl, carrera, idnumber_carrera,carrera.nombre, parent=parent_coordinacionid)
                                    parent_carreraid = bcarrera[0]['id']
                                # print('****Carrera: %s' % carrera)
                                if parent_carreraid > 0:
                                    """"
                                    CREANDO LOS NIVELES DE MALLA
                                    """
                                    niveles = NivelMalla.objects.filter(pk=1).distinct()
                                    for semestre in niveles:
                                        idnumber_semestre = u'%s-COR%s-CARR%s-NIVEL%s' % (
                                            periodo.idnumber(), coordinacion.id, carrera.id, semestre.id)
                                        bsemestre = moodle.BuscarCategorias(periodo, tipourl, idnumber_semestre)
                                        categoryid = 0
                                        if bsemestre:
                                            if 'id' in bsemestre[0]:
                                                categoryid = bsemestre[0]['id']
                                        else:
                                            bsemestre = moodle.CrearCategorias(periodo, tipourl, semestre,idnumber_semestre, semestre.nombre,parent=parent_carreraid)
                                            categoryid = bsemestre[0]['id']
                                        # print('******Semestre: %s' % semestre)
                                        if categoryid > 0:
                                            """"
                                            CREANDO LOS CURSOS
                                            """
                                            cursos = GrupoExamenMsc.objects.filter(id=self.id)
                                            for curso in cursos:
                                                if curso.codigonumber:
                                                    idnumber_curso = curso.codigonumber
                                                else:
                                                    idnumber_curso = u'%s-COR%s-CARR%s-NIVEL%s-CURS%s' % (periodo.idnumber(), coordinacion.id, carrera.id, semestre.id, curso.id)
                                                bcurso = moodle.BuscarCursos(periodo, tipourl, 'idnumber', idnumber_curso)
                                                if not bcurso:
                                                    bcurso = moodle.BuscarCursos(periodo, tipourl, 'idnumber',idnumber_curso)
                                                numsections = 1
                                                # planificacionclasesilabo = curso.planificacionclasesilabo_materia_set.filter(status=True)
                                                # if planificacionclasesilabo:
                                                #     numsections = planificacionclasesilabo[0].tipoplanificacion.detalle_planificacion().count()
                                                # objetivocur = ObjetivoProgramaAnaliticoAsignatura.objects.filter(programaanaliticoasignatura__asignaturamalla=curso.asignaturamalla,programaanaliticoasignatura__activo=True,programaanaliticoasignatura__status=True)
                                                summary = u''
                                                # if objetivocur:
                                                #     summary = objetivocur[0].descripcion
                                                startdate = int(time.mktime(curso.fecha.timetuple()))
                                                enddate = int(time.mktime(curso.fecha.timetuple()))
                                                cursoid = 0
                                                if bcurso['courses']:
                                                    if 'id' in bcurso['courses'][0]:
                                                        cursoid = bcurso['courses'][0]['id']
                                                else:
                                                    bcurso = moodle.CrearCursos(periodo, tipourl,u'%s' % curso.__str__(),u'%s,[%s] - %s[%s]' % (str(curso.fecha),curso.id, curso.id,curso.id), categoryid, idnumber_curso,summary, startdate, enddate, numsections)
                                                    cursoid = bcurso[0]['id']
                                                # print('********Curso: %s' % curso)
                                                if cursoid > 0:
                                                    if curso.idgrupomoodle != cursoid:
                                                        curso.codigonumber = idnumber_curso
                                                        curso.idgrupomoodle = cursoid
                                                        curso.save()

                                                    if AGREGAR_MODELO_NOTAS:
                                                        curso.crear_actualizar_categoria_notas_grupo_posgrado()

                                                    if AGREGAR_DOCENTE:
                                                        curso.crear_actualizar_docente_grupo_posgrado(moodle, 1)

                                                    if AGREGAR_ESTUDIANTE:
                                                        curso.crear_actualizar_estudiantes_grupo_posgrado(moodle, 1, codigoinscritogrupoexamen)
            else:
                curso = GrupoExamenMsc.objects.get(id=self.id)
                if AGREGAR_ESTUDIANTE:
                    curso.crear_actualizar_estudiantes_grupo_posgrado(moodle, 1, codigoinscritogrupoexamen)


    def categorias_moodle_curso(self):
        from django.db import connections
        cursor = connections['moodle_pos'].cursor()
        sql = """select DISTINCT upper(gc.fullname),it.sortorder  from mooc_grade_grades nota 
                 inner join mooc_grade_items it on nota.itemid=it.id and courseid=%s and itemtype='category' 
                 inner join mooc_grade_categories gc on gc.courseid=it.courseid and gc.id=it.iteminstance and gc.depth=2 
                 where not upper(gc.fullname)='RE'
                 order by it.sortorder ;
                """ % str(self.idgrupomoodle)
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def categorias_moodle_curso_count(self):
        from django.db import connections
        cursor = connections['moodle_pos'].cursor()
        sql = "select count(contar.fullname) from(select DISTINCT gc.fullname,it.sortorder  from mooc_grade_grades nota " \
              " inner join mooc_grade_items it on nota.itemid=it.id and courseid=" + str(self.idgrupomoodle) + " and itemtype='category' " \
                                                                                                               " inner join mooc_grade_categories gc on gc.courseid=it.courseid and gc.id=it.iteminstance and gc.depth=2 order by it.sortorder) as contar ;"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def notas_de_moodle(self, persona):
        from django.db import connections
        cursor = connections['moodle_pos'].cursor()
        sql = """
                        SELECT ROUND(nota.finalgrade,2), UPPER(gc.fullname)
                                FROM mooc_grade_grades nota
                        INNER JOIN mooc_grade_items it ON nota.itemid=it.id AND courseid=%s AND itemtype='category'
                        INNER JOIN mooc_grade_categories gc ON gc.courseid=it.courseid AND gc.id=it.iteminstance AND gc.depth=2
                        INNER JOIN mooc_user us ON nota.userid=us.id
                        WHERE us.id ='%s' and not UPPER(gc.fullname)='RE'
                        ORDER BY it.sortorder
                        """ % (str(self.idgrupomoodle), persona.idusermoodleposgrado)

        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def save(self, *args, **kwargs):
        self.lugar = self.lugar.upper()
        self.observacion = self.observacion.upper()
        super(GrupoExamenMsc, self).save(*args, **kwargs)


class IntegranteGrupoExamenMsc(ModeloBase):
    inscripcion = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Inscripción', on_delete=models.CASCADE)
    grupoexamen = models.ForeignKey(GrupoExamenMsc, blank=True, null=True, verbose_name=u'Grupo de examen', on_delete=models.CASCADE)
    notaexa = models.FloatField(blank=True, null=True, verbose_name=u'Nota examen')
    notatest = models.FloatField(blank=True, null=True, verbose_name=u'Nota Test')
    notafinal = models.FloatField(blank=True, null=True, verbose_name=u'Nota Final')
    estado = models.IntegerField(choices=ESTADO_EXAMEN_MSC, default=1, verbose_name=u'Estado del examen')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    encursomoodle = models.BooleanField(default=False, verbose_name=u"Esta en curso moodle")

    def __str__(self):
        return u'%s' % self.inscripcion

    class Meta:
        ordering = ['inscripcion', ]

    def campo(self, campo):
        # if self.evaluacion_generica().filter(detallemodeloevaluativo__nombre=campo).exists():
        #     return self.evaluacion_generica().filter(detallemodeloevaluativo__nombre=campo)[0]
        return null_to_decimal(self.notafinal,2)

    def puede_eliminar_integrante(self):
        return True if self.estado == 1 else False


    def save(self, *args, **kwargs):
        self.observacion = self.observacion.upper()
        super(IntegranteGrupoExamenMsc, self).save(*args, **kwargs)


class GrupoEntrevistaMsc(ModeloBase):
    administrativo = models.ForeignKey('sga.Administrativo', blank=True, null=True, verbose_name=u'Profesor', on_delete=models.CASCADE)
    cohortes = models.ForeignKey(CohorteMaestria, blank=True, null=True, verbose_name=u'Cohorte de maestría', on_delete=models.CASCADE)
    lugar = models.CharField(default='', max_length=100, verbose_name=u'Lugar de examen')
    fecha = models.DateField(blank=True, null=True, verbose_name=u'fecha bde exsamen')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    visible = models.BooleanField(default=True, verbose_name=u'Visible')
    estado_emailentrevista = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u'Estado Email evidencia')
    fecha_emailentrevista = models.DateTimeField(blank=True, null=True)
    persona_emailentrevista = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Quien aprueba o rechaza evidencias', on_delete=models.CASCADE)
    horainicio = models.TimeField(blank=True, null=True, verbose_name=u'Hora de inicio de entrevista')
    urlzoom = models.TextField(default='', verbose_name=u'URL Zoom')

    def __str__(self):
        return u'%s - %s' % (self.observacion, self.administrativo)

    class Meta:
        ordering = ['administrativo', ]

    def mis_integrantes(self):
        return self.integrantegrupoentrevitamsc_set.filter(status=True).order_by('inscripcion__inscripcionaspirante__persona__apellido1','inscripcion__inscripcionaspirante__persona__apellido2')

    def total_inscritos(self):
        return self.mis_integrantes().values('id').count()

    def mis_participantes_entrevista(self):
        if self.integrantegrupoentrevitamsc_set.values("id").filter(status=True).exists():
            return self.integrantegrupoentrevitamsc_set.filter(status=True)
        return None

    def total_participantes_entrevista(self):
        if self.integrantegrupoentrevitamsc_set.values("id").filter(status=True).exists():
            return self.integrantegrupoentrevitamsc_set.values("id").filter(status=True).count()
        return 0

    def puede_eliminar_grupo_entrevista(self):
        return True if not self.integrantegrupoentrevitamsc_set.filter(status=True).exists() else False

    def total_admitidos_cohorte(self):
        if self.integrantegrupoentrevitamsc_set.filter(estado_emailadmitido=2, cohorteadmitidasinproceso__isnull=True, status=True).exists():
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.upper()
        super(GrupoEntrevistaMsc, self).save(*args, **kwargs)


ESTADO_ENTREVISTA = (
    (1, u'PENDIENTE'),
    (2, u'APROBADO'),
    (3, u'RECHAZADO')
)

class IntegranteGrupoEntrevitaMsc(ModeloBase):
    inscripcion = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Inscripción', on_delete=models.CASCADE)
    grupoentrevista = models.ForeignKey(GrupoEntrevistaMsc, blank=True, null=True, verbose_name=u'Grupo de entrevista', on_delete=models.CASCADE)
    estadoentrevista = models.ForeignKey(EstadoEntrevista, blank=True, null=True, verbose_name=u'Estado Entrevista', on_delete=models.CASCADE)
    lugar = models.CharField(default='', max_length=300, verbose_name=u'Lugar de entrevista')
    fecha = models.DateField(blank=True, null=True, verbose_name=u'fecha de entrevista')
    horadesde = models.TimeField(blank=True, null=True, verbose_name=u'Hora desde')
    horahasta = models.TimeField(blank=True, null=True, verbose_name=u'Hora hasta')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    estado = models.IntegerField(choices=ESTADO_ENTREVISTA, default=1, verbose_name=u'Estado del examen')
    notaentrevista = models.FloatField(blank=True, null=True, verbose_name=u'Nota Entrevista')
    notafinal = models.FloatField(default=0,blank=True, null=True, verbose_name=u'Nota Final')
    entrevista = models.BooleanField(default=False, verbose_name=u'Entrevistado')
    estado_emailadmitido = models.IntegerField(choices=ESTADO_REVISION, default=1, verbose_name=u'Estado Email evidencia')
    fecha_emailadmitido = models.DateTimeField(blank=True, null=True)
    persona_emailadmitido = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Quien aprueba o rechaza evidencias', on_delete=models.CASCADE)
    cohorteadmitidasinproceso = models.ForeignKey(CohorteMaestria, blank=True, null=True, verbose_name=u'Cohorte Maestria', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s' % self.inscripcion

    class Meta:
        ordering = ['inscripcion', ]



    def tiene_entrevista(self):
        return True if self.respuestaentrevitamsc_set.filter(status=True).exists() else False

    def eliminar_aspirante_programa(self):
        from sagest.models import Rubro
        rubro1 = Rubro.objects.filter(inscripcion=self.inscripcion, status=True)
        return rubro1


    def save(self, *args, **kwargs):
        self.observacion = self.observacion.upper()
        self.lugar = self.lugar.upper()
        super(IntegranteGrupoEntrevitaMsc, self).save(*args, **kwargs)


class RespuestaEntrevitaMsc(ModeloBase):
    integrante = models.ForeignKey(IntegranteGrupoEntrevitaMsc, blank=True, null=True, verbose_name=u'Integrante', on_delete=models.CASCADE)
    preguntacohorte = models.ForeignKey(PreguntaMaestria, blank=True, null=True, verbose_name=u'Pregunta Cohorte', on_delete=models.CASCADE)
    respuesta = models.TextField(default='', verbose_name=u'Respuesta')

    def __str__(self):
        return u'%s' % self.respuesta

    def save(self, *args, **kwargs):
        self.respuesta = self.respuesta.upper()
        super(RespuestaEntrevitaMsc, self).save(*args, **kwargs)


class FormatoCarreraIpec(ModeloBase):
    carrera = models.ForeignKey('sga.Carrera', blank=True, null=True, verbose_name=u'Carrera', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='formatocarrerapreinscripcionipec', blank=True, null=True,verbose_name=u'Archivo')
    correomaestria = models.EmailField(default='',blank=True, null=True, verbose_name=u'Correo de la maestría')
    banner = models.FileField(upload_to='banner', blank=True, null=True, verbose_name=u'Banner de la maestría')


    def __str__(self):
        return u'%s' % self.correomaestria

    def download_link(self):
        return self.archivo.url

    def download_banner(self):
        return self.banner.url


class PreInscripcion(ModeloBase):
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Persona', on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(blank=True, null=True, verbose_name=u'fecha de registro')
    carrera = models.ForeignKey('sga.Carrera', blank=True, null=True, verbose_name=u'Carrera', on_delete=models.CASCADE)
    formato = models.ForeignKey(FormatoCarreraIpec, blank=True, null=True, verbose_name=u'Formato', on_delete=models.CASCADE)
    enviocorreo = models.BooleanField(default=False, verbose_name=u'Verfica si envio correo de requisitos')
    rutapdf = models.FileField(upload_to='qrcode/certificados', blank=True, null=True,verbose_name=u'Archivo certificado de preinscripcion')
    evidencias = models.BooleanField(default=False, verbose_name=u'Verifica si envio las evidencias de la maestria')
    aceptarpreinscripcion = models.BooleanField(default=False, verbose_name=u'Verifica si se acepto la inscripcion para la maestria')


    def __str__(self):
        return u'%s' % self.persona

    def download_formato(self):
        return self.formato.download_link()

    class Meta:
        ordering = ['persona', ]


class InteresadoMaestria(ModeloBase):
    nombre = models.TextField(default='', verbose_name=u'Nombre')
    email = models.EmailField(default='', blank=True, null=True, verbose_name=u'Email Interesado')
    telefono = models.TextField(default='', verbose_name=u'Teléfono')
    profesion = models.TextField(default='', verbose_name=u'Profesión')
    fecha_hora = models.DateTimeField(blank=True, null=True, verbose_name=u'fecha de registro')
    carrera = models.ForeignKey('sga.Carrera', blank=True, null=True, verbose_name=u'Carrera', on_delete=models.CASCADE)

    def __str__(self):
        return u'%s - %s' % (self.nombre, self.correo)

    class Meta:
        ordering = ['nombre', ]


class EvidenciasMaestrias(ModeloBase):
    preinscripcion = models.ForeignKey(PreInscripcion, verbose_name=u'PreInscripcion', on_delete=models.CASCADE)
    hojavida = models.FileField(upload_to='requisitosmaestriapreinscripcionipec', blank=True, null=True,verbose_name=u'Archivo hoja de vida pre inscripcion ipec')
    copiavotacion = models.FileField(upload_to='requisitosmaestriapreinscripcionipec', blank=True, null=True,verbose_name=u'Archivo certificado votacion pre inscripcion ipec')
    copiacedula = models.FileField(upload_to='requisitosmaestriapreinscripcionipec', blank=True, null=True,verbose_name=u'Archivo cedula pre inscripcion ipec')
    senescyt  = models.FileField(upload_to='requisitosmaestriapreinscripcionipec', blank=True, null=True,verbose_name=u'Archivo titulo senescyt pre inscripcion ipec')
    lenguaextranjera = models.FileField(upload_to='requisitosmaestriapreinscripcionipec', blank=True, null=True,verbose_name=u'Archivo certificado lengua extranjera pre inscripcion ipec')
    observaciones = models.TextField(default='', blank=True, null=True, verbose_name=u'Observaciones')

    def __str__(self):
        return u'%s' % self.preinscripcion

    def download_hojavida(self):
        return self.hojavida.url

    def download_copiavotacion(self):
        return self.copiavotacion.url

    def download_copiacedula(self):
        return self.copiacedula.url

    def download_senescyt(self):
        return self.senescyt.url

    def download_lenguaextranjera(self):
        return self.senescyt.url

    class Meta:
        ordering = ['preinscripcion', ]


HISTORIAL_CHOICES = (
    (1, "PENDIENTE"),
    (2, "EL ESTUDIANTE CONTESTÓ"),
    (3, "EL ESTUDIANTE NO CONTESTÓ"),
    (4, "EL ESTUDIANTE NO ESTÁ INTERESADO"),
    (5, "EL ESTUDIANTE CONFIRMO SU PARTICIPACIÓN"),
)

class InteresadoProgramaMaestria(ModeloBase):
    nombres = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name='Nombres')
    cedula = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name='Cédula')
    telefono = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name='Teléfono')
    telefono_adicional = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name='Teléfono Adicional')
    correo = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name='Correo')
    observacion = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name='Observación')
    programa = models.ForeignKey(MaestriasAdmision, null=True, blank=True, verbose_name=u'Programa', on_delete=models.CASCADE)
    accion = models.PositiveIntegerField(choices=HISTORIAL_CHOICES, default=1, blank=True, null=True, verbose_name='Acción')

    def get_lastobser(self):
        return HistorialInteresadoProgramaMaestria.objects.filter(status=True, cab=self).order_by('pk').last()

    def get_accion(self):
        return dict(HISTORIAL_CHOICES)[self.accion]

    def __str__(self):
        return u'%s %s' % (self.programa, self.nombres)

    class Meta:
        verbose_name = u"Interesado en Programa Maestría"
        verbose_name_plural = u"Interesados en Programas Maestrías"

    def save(self, *args, **kwargs):
        self.nombres = self.nombres.upper()
        super(InteresadoProgramaMaestria, self).save(*args, **kwargs)


class HistorialInteresadoProgramaMaestria(ModeloBase):
    cab = models.ForeignKey(InteresadoProgramaMaestria, null=True, blank=True, verbose_name="Ficha", on_delete=models.CASCADE)
    accion = models.PositiveIntegerField(choices=HISTORIAL_CHOICES, verbose_name='Acción')
    detalle = models.TextField(null=True, blank=True)

    def get_accion(self):
        return dict(HISTORIAL_CHOICES)[self.accion]

    class Meta:

        verbose_name = "Historial de Interesados"
        verbose_name_plural = "Historial de Interesados"
        ordering = ('pk',)

class ConfigurarFirmaAdmisionPosgrado(ModeloBase):
    administrativo = models.ForeignKey(Administrativo, null=True, blank=True, verbose_name='Administrativo', on_delete=models.CASCADE)
    cargo = models.CharField(verbose_name='Cargo', null=True, blank=True, max_length=1000)

    def __str__(self):
        return u'%s' % (self.administrativo.persona)

    class Meta:
        verbose_name = "Configurar Firma para Admisión Posgrado"
        verbose_name_plural = "Configurar Firmas para Admisión Posgrado"
        ordering = ('administrativo',)


ESTADO_PROYECTO_VINCULACION = ((1, 'APROBADO'), (2, 'PENDIENTE'), (3, 'RECHAZADO'))
TIPO_EVIDENCIA = ((1, 'PDF'), (2, 'LINK'))

class ProyectoVinculacion(ModeloBase):
    titulo = models.TextField(verbose_name=u'Titulo', null=True, blank=True)
    descripcion = models.TextField(verbose_name=u'Descripcion', null=True, blank=True)
    estadoaprobacion = models.IntegerField(choices=ESTADO_PROYECTO_VINCULACION, blank=True, null=True, verbose_name=u"Estado", default=2)

    def __str__(self):
        return u'%s' % self.titulo

    class Meta:
        verbose_name = u"Proyecto de vinculacion"
        verbose_name_plural = u"Proyectos de vinculacion"
        ordering = ('-pk',)

    def save(self, *args, **kwargs):
        self.titulo = self.titulo.strip().upper() if self.titulo else ''
        super(ProyectoVinculacion, self).save(*args, **kwargs)

    def get_detalleaprobacion(self):
        return self.detalleaprobacionproyecto_set.filter(status=True)

    def color_estadoaprobacion(self):
        estado = 'primary'
        if self.estadoaprobacion == 1:
            estado = 'success'
        elif self.estadoaprobacion == 2:
            estado = 'secondary'
        elif self.estadoaprobacion == 3:
            estado = 'danger'
        return estado

class ParticipanteProyectoVinculacionPos(ModeloBase):
    inscripcion = models.ForeignKey('sga.Inscripcion', blank=True, null=True, verbose_name=u'Inscripcion', on_delete=models.CASCADE)
    proyectovinculacion = models.ForeignKey(ProyectoVinculacion, verbose_name=u"Proyecto de vinculacion", blank=True, null=True, on_delete=models.CASCADE)
    evidencia = models.FileField(verbose_name=u"Evidencia", upload_to='posgrado/proyectovinculacion/%Y/%m/%d', null=True, blank=True, default='')
    tipoevidencia = models.IntegerField(choices=TIPO_EVIDENCIA, blank=True, null=True, verbose_name=u"Tipo de evidencia", default=1)

    def __str__(self):
        return u'%s' % self.inscripcion.persona.nombre_completo_inverso()

    class Meta:
        verbose_name = u"Participante del proyecto de vinculacion"
        verbose_name_plural = u"Participantes del proyecto de vinculacion"
        ordering = ('-pk',)
        unique_together = ('proyectovinculacion', 'inscripcion',)

class DetalleAprobacionProyecto(ModeloBase):
    observacion = models.TextField(verbose_name=u"Observacion", blank=True, null=True)
    proyectovinculacion = models.ForeignKey(ProyectoVinculacion, verbose_name=u"Proyecto de vinculacion", blank=True, null=True, on_delete=models.CASCADE)
    estadoaprobacion = models.IntegerField(choices=ESTADO_PROYECTO_VINCULACION, blank=True, null=True, verbose_name=u"Estado", default=2)
    persona = models.ForeignKey('sga.Persona', verbose_name=u"Persona", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u'%s' % self.proyectovinculacion

    class Meta:
        verbose_name = u"Detalle aprobacion de proyecto"
        verbose_name_plural = u"Detalle aprobacion de proyectos"
        ordering = ('-pk',)

    def color_estadoaprobacion(self):
        estado = 'primary'
        if self.estadoaprobacion == 1:
            estado = 'success'
        elif self.estadoaprobacion == 2:
            estado = 'secondary'
        elif self.estadoaprobacion == 3:
            estado = 'danger'
        return estado

class SolicitudProrrogaIngresoTemaMatricula(ModeloBase):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, verbose_name=u'Matricula')
    observacion = models.TextField(verbose_name=u"Observación")
    estado = models.IntegerField(choices=ESTADO_SOLICITUD_MATRICULA, default=1, verbose_name=u"Estado solicitud")
    fechainicioprorroga = models.DateField(verbose_name=u'Fecha inicio prorroga', blank=True, null=True)
    fechafinprorroga = models.DateField(verbose_name=u'Fecha fin prorroga', blank=True, null=True)

    def historial_solicitud(self):
        return self.historialsolicitudprorrogaingresotemamatricula_set.filter(status=True)

    def __str__(self):
        return u'%s' % (self.matricula)

    class Meta:
        verbose_name = "Solicitud Prorroga  Ingreso Tema Matricula"
        verbose_name_plural = "Solicitud Prorroga  Ingreso Tema Matricula"
        ordering = ('id',)


class HistorialSolicitudProrrogaIngresoTemaMatricula(ModeloBase):
    solicitud = models.ForeignKey(SolicitudProrrogaIngresoTemaMatricula, on_delete=models.CASCADE,verbose_name=u'Solicitud')
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE,verbose_name=u'Persona')
    estado = models.IntegerField(choices=ESTADO_SOLICITUD_MATRICULA, default=1, verbose_name=u"Estado solicitud")

    def __str__(self):
        return u'%s' % (self.solicitud)

    class Meta:
        verbose_name = u'Historial Solicitud Prorroga  Ingreso Tema Matricula'
        verbose_name_plural = u'Historial Solicitud Prorroga  Ingreso Tema Matricula'
        ordering = ('id',)

## revision trabajo final de titulacion posgrado
class Pregunta(ModeloBase):
    descripcion = models.TextField(default='', verbose_name=u'Descripcion')

    def __str__(self):
        return u'%s' % (self.descripcion)

    class Meta:
        verbose_name = u'Pregunta'
        verbose_name_plural = u'Preguntas'
        ordering = ('id',)

class Informe(ModeloBase):
    descripcion = models.TextField(default='', verbose_name=u'Descripcion')
    tipo = models.IntegerField(choices=TIPO_INFORME, default=1, verbose_name=u"Tipo informe")
    mecanismotitulacionposgrado= models.ForeignKey('sga.MecanismoTitulacionPosgrado', on_delete=models.CASCADE , verbose_name=u'Mecanismo Titulación',blank=True, null = True,)
    estado = models.BooleanField(default=False, verbose_name=u'Activo')

    def __str__(self):
        return u'%s' % (self.descripcion)

    def en_uso(self):
        return self.seccioninforme_set.filter(status=True).exists()

    def obtener_secciones(self):
        return self.seccioninforme_set.filter(status=True).order_by('id')

    def obtener_dictamen(self):
        return ESTADO_DICTAMEN[1:]

    class Meta:
        verbose_name = u'Informe'
        verbose_name_plural = u'Informes'
        ordering = ('id',)

class SeccionInforme(ModeloBase):
    informe = models.ForeignKey(Informe, on_delete=models.CASCADE,verbose_name=u'informe')
    seccion = models.ForeignKey('sga.EtapaTemaTitulacionPosgrado', on_delete=models.CASCADE,verbose_name=u'Sección')
    orden = models.IntegerField(default=0, verbose_name=u'Orden')

    def __str__(self):
        return u'%s: %s' % (self.informe,self.seccion)

    def obtener_preguntas_seccion(self):
        return self.seccioninformepregunta_set.filter(status=True)

    def en_uso(self):
        return  self.seccioninformepregunta_set.filter(status=True).exists()

    class Meta:
        verbose_name = u'Informe etapa'
        verbose_name_plural = u'Informe etapa'
        ordering = ('id',)

class SeccionInformePregunta(ModeloBase):
    seccion_informe = models.ForeignKey(SeccionInforme, on_delete=models.CASCADE,verbose_name=u'informe etapa')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE,verbose_name=u'Pregunta')
    tipo_pregunta = models.IntegerField(choices=TIPO_PREGUNTA, default=1, verbose_name=u"Tipo pregunta")

    def __str__(self):
        return u'%s' % (self.pregunta)

    def en_uso(self):
        return self.preguntarevision_set.filter(status=True).exists()

    class Meta:
        verbose_name = u'Informe etapa'
        verbose_name_plural = u'Informe etapa'
        ordering = ('id',)

class Revision(ModeloBase):
    tribunal = models.ForeignKey('sga.TribunalTemaTitulacionPosgradoMatricula', on_delete=models.CASCADE,verbose_name=u'tribunal')
    archivo = models.FileField(upload_to='archivorevisionpos/%Y/%m/%d', blank=True, null=True, verbose_name=u'Archivo')
    estado = models.IntegerField(choices=ESTADO_DICTAMEN, default=1, verbose_name=u"Estado")
    observacion = models.TextField(verbose_name=u"Observación")

    def __str__(self):
        return u'%s' % (self.tribunal)

    def obtener_secciones(self):
        return self.seccionrevision_set.filter(status=True).order_by('id')

    def existen_preguntas_sin_responder(self):
        return self.preguntarevision_set.filter(status=True, respuesta ='').exists()

    def obtener_dictamen(self):
        return ESTADO_DICTAMEN[1:]

    def crear_estructura_informe(self,informe,request):
        for seccion in informe.obtener_secciones():
            seccionrevision = SeccionRevision(
                revision=self,
                seccion_informe=seccion
            )
            seccionrevision.save(request)
            for pregunta in seccion.obtener_preguntas_seccion():
                preguntarevision = PreguntaRevision(
                    revision=self,
                    seccion_revision=seccionrevision,
                    seccion_informe_pregunta=pregunta
                )
                preguntarevision.save(request)

    def obtener_temas_individual_o_pareja_titulacion(self):
        maestrantes = []
        if self.tribunal.tematitulacionposgradomatriculacabecera:
            for tema in self.tribunal.tematitulacionposgradomatriculacabecera.obtener_parejas():
                maestrantes.append(tema)
        else:
            maestrantes.append(self.tribunal.tematitulacionposgradomatricula)

        return maestrantes

    def obtener_tutor_individual_pareja(self):
        tutor = None
        if self.tribunal.tematitulacionposgradomatriculacabecera:
            tutor = self.tribunal.tematitulacionposgradomatriculacabecera.tutor
        else:
            tutor = self.tribunal.tematitulacionposgradomatricula.tutor
        return tutor

    def obtener_maestria(self):
        if self.tribunal.tematitulacionposgradomatriculacabecera:
            maestria = self.tribunal.tematitulacionposgradomatriculacabecera.obtener_parejas()[0].matricula.inscripcion.carrera
        else:
            maestria = self.tribunal.tematitulacionposgradomatricula.matricula.inscripcion.carrera
        return maestria

    def obtener_historial_de_revisiones(self):
        return self.historialdocrevisiontribunal_set.filter(status=True).order_by('-id')

    def obtener_mecanismo(self):
        if self.tribunal.tematitulacionposgradomatriculacabecera:
            mecanismo = self.tribunal.tematitulacionposgradomatriculacabecera.mecanismotitulacionposgrado
        else:
            mecanismo = self.tribunal.tematitulacionposgradomatricula.mecanismotitulacionposgrado
        return mecanismo

    def obtener_correccion_revision_tribunal(self):
        tema =None
        correccion =None
        if self.tribunal.tematitulacionposgradomatriculacabecera:
            tema = self.tribunal.tematitulacionposgradomatriculacabecera
            correccion = self.tribunal.tematitulacionposgradomatriculacabecera.tematitulacionposarchivofinal_set.filter(status=True)
        else:
            tema = self.tribunal.tematitulacionposgradomatricula
            correccion = self.tribunal.tematitulacionposgradomatricula.tematitulacionposarchivofinal_set.filter(status=True)

        return correccion.first() if correccion else None







    class Meta:
        verbose_name = u'Revision'
        verbose_name_plural = u'Revisiones'
        ordering = ('id',)

class SeccionRevision(ModeloBase):
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE,verbose_name=u'Revisión')
    seccion_informe = models.ForeignKey(SeccionInforme, on_delete=models.CASCADE,verbose_name=u'Sección')
    observacion = models.TextField(verbose_name=u"Observación")

    def __str__(self):
        return u'%s: %s' % (self.revision,self.seccion_informe)

    def obtener_preguntas_revision(self):
        return self.preguntarevision_set.filter(status=True)

    class Meta:
        verbose_name = u'Seccion Revisión'
        verbose_name_plural = u'Seccion Revisiones'
        ordering = ('id',)

class PreguntaRevision(ModeloBase):
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE,verbose_name=u'Revisión')
    seccion_revision = models.ForeignKey(SeccionRevision, on_delete=models.CASCADE,verbose_name=u'Sección Revisión')
    seccion_informe_pregunta = models.ForeignKey(SeccionInformePregunta, on_delete=models.CASCADE,verbose_name=u'Sección pregunta')
    respuesta = models.TextField(default='', verbose_name=u'Respuesta')
    def __str__(self):
        return u'%s: %s' % (self.revision,self.seccion_informe_pregunta)

    class Meta:
        verbose_name = u'Seccion Revisión'
        verbose_name_plural = u'Seccion Revisiones'
        ordering = ('id',)


class HistorialDocRevisionTribunal(ModeloBase):
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE,verbose_name=u'Revisión')
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE,verbose_name=u'Persona')
    estado = models.IntegerField(choices=ESTADO_DICTAMEN, default=1, verbose_name=u"Estado")
    observacion = models.TextField(verbose_name=u"Observación")
    def __str__(self):
        return u'%s' % (self.revision)

    class Meta:
        verbose_name = u'Historial Revisión'
        verbose_name_plural = u'Historial Revisión'

class EstadoDocumentoTitulacionPosgrado(ModeloBase):
    descripcion = models.CharField(default='', max_length=200, verbose_name=u'Descripcion')
    nombrefirma = models.CharField(default='', max_length=500, verbose_name=u'Nombre')
    habilitado = models.BooleanField(default=True, verbose_name=u'Habilitado')
    orden = models.IntegerField(blank=True, null=True, verbose_name=u'Orden')

    def __str__(self):
        return u'%s' % self.descripcion

    class Meta:
        verbose_name = u"Estado Documento Titulacion Posgrado"
        verbose_name_plural = u"Estados de Documento Titulacion Posgrado"
        unique_together = ('descripcion',)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(EstadoDocumentoTitulacionPosgrado, self).save(*args, **kwargs)

    def en_uso(self):
        return True if self.documentotitulacionposgrado_set.values('id').filter(status=True).exists() else False

class TipoDocumentoTitulacionPosgrado(ModeloBase):
    descripcion = models.CharField(default='', max_length=300, verbose_name=u'Descripcion')

    def __str__(self):
        return u'%s' % self.descripcion

    class Meta:
        verbose_name = u"Tipo Documento Titulacion Posgrado"
        verbose_name_plural = u"Tipos de Documento Titulacion Posgrado"
        unique_together = ('descripcion',)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(TipoDocumentoTitulacionPosgrado, self).save(*args, **kwargs)

    def en_uso(self):
        return True if self.documentotitulacionposgrado_set.values('id').filter(status=True).exists() else False

class DocumentoTitulacionPosgrado(ModeloBase):
    tematitulacionposgrado = models.ForeignKey('sga.TemaTitulacionPosgradoMatricula', blank=True, null=True, verbose_name=u"Tema Titulacion Posgrado Matricula", on_delete=models.CASCADE)
    tipodocumentotitulacion = models.ForeignKey(TipoDocumentoTitulacionPosgrado, blank=True, null=True, verbose_name=u"Tipo Documento Titulacion Posgrado", on_delete=models.CASCADE)
    estadodocumentotitulacion = models.ForeignKey(EstadoDocumentoTitulacionPosgrado, blank=True, null=True, verbose_name=u"EstadoDocumentoTitulacionPosgrado", on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='documentotitulacionposgrado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Documento titulacion posgrado')
    fecha = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha')

    def __str__(self):
        return u'%s - %s: %s' % (self.tematitulacionposgrado.__str__(), self.tipodocumentotitulacion.__str__(), self.estadodocumentotitulacion.__str__())

    class Meta:
        verbose_name = u"Documento Titulacion Posgrado"
        verbose_name_plural = u"Documentos Titulacion Posgrado"
        ordering = ['-id']

class HistorialDocumentoTitulacionPosgrado(ModeloBase):
    documentotitulacion = models.ForeignKey(DocumentoTitulacionPosgrado, blank=True, null=True, verbose_name=u"Documento Titulacion Posgrado", on_delete=models.CASCADE)
    estadodocumentotitulacion = models.ForeignKey(EstadoDocumentoTitulacionPosgrado, blank=True, null=True, verbose_name=u"EstadoDocumentoTitulacionPosgrado", on_delete=models.CASCADE)
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Quien modifica', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='documentotitulacionposgradohistorial/%Y/%m/%d', blank=True, null=True, verbose_name=u'Documento titulacion posgrado historial')
    fecha = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha')

    def __str__(self):
        return u'%s: %s' % (self.documentotitulacion.__str__(), self.persona.__str__())

    class Meta:
        verbose_name = u"Historial Documento Titulacion Posgrado"
        verbose_name_plural = u"Historial Documentos Titulacion Posgrado"
        ordering = ['-id']


class ConfiguraInformePrograma(ModeloBase):
    informe = models.ForeignKey(Informe, blank=True, null=True, verbose_name=u'Informe', on_delete=models.CASCADE)
    mecanismotitulacionposgrado = models.ForeignKey('sga.mecanismotitulacionposgrado', verbose_name=u'Mecanismo', on_delete=models.CASCADE)
    programa = models.ForeignKey('sga.carrera', blank=True, null=True, verbose_name=u'Programa', on_delete=models.CASCADE)
    estado = models.BooleanField(default=False, verbose_name=u'Activo')
    def __str__(self):
        return f'{self.informe} - {self.mecanismotitulacionposgrado} - {self.programa}'

    class Meta:
        verbose_name = u"Configura Informe Programa"
        verbose_name_plural = u"Configura Informe Programa"
        ordering = ['-id']

class ProductoSecretaria(ModeloBase):
    codigo = models.CharField(max_length=10, verbose_name=u"Código")
    descripcion = models.CharField(max_length=350, verbose_name=u"Descripcion", db_index=True)
    servicio = models.ForeignKey('secretaria.Servicio', related_name='+', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Servicio")
    costo = models.DecimalField(max_digits=30, decimal_places=16, default=0, blank=True, null=True, verbose_name=u'Costo')
    tiempo_cobro = models.IntegerField(default=72, blank=True, null=True, verbose_name=u"Tiempo de cobro")
    visible = models.BooleanField(default=False, verbose_name=u"Visible?")

    def __str__(self):
        return f'{self.codigo} - {self.descripcion}'

    def costo_ingreso_titulacion(self, inscripcion):
        from sga.models import Matricula, AsignaturaMalla
        dosmod = 0
        matricula = Matricula.objects.filter(status=True, inscripcion=inscripcion).order_by('id').first()
        cohorte = CohorteMaestria.objects.filter(status=True, periodoacademico=matricula.nivel.periodo).first()
        mallas = AsignaturaMalla.objects.filter(status=True, malla__carrera=cohorte.maestriaadmision.carrera, asignatura__status=True, itinerario__in=[0, inscripcion.itinerario]).count()
        if cohorte.valorprogramacertificado:
            dosmod = (cohorte.valorprogramacertificado / mallas) * 2
        elif cohorte.valorprograma:
            dosmod = (cohorte.valorprograma / mallas) * 2
        return dosmod

    class Meta:
        verbose_name = u"Producto de secretaria"
        verbose_name_plural = u"Productos de secretarias"
        ordering = ['-id']

class ActividadCronogramaTitulacion(ModeloBase):
    nombre = models.CharField(max_length=350, verbose_name=u"Actividad", db_index=True)
    descripcion = models.TextField(default='', verbose_name=u'Descripcion')

    def __str__(self):
        return f'{self.nombre}'

    class Meta:
        verbose_name = u"Actividad de cronograma de titulación"
        verbose_name_plural = u"Actividades de cronograma de titulación"
        ordering = ['-id']

    def subido_por(self):
        from sga.models import Persona
        return Persona.objects.get(usuario=self.usuario_creacion.id)

class DetalleActividadCronogramaTitulacion(ModeloBase):
    solicitud = models.ForeignKey('secretaria.Solicitud', verbose_name="Solicitud del maestrante", on_delete=models.CASCADE)
    periodo = models.ForeignKey('sga.Periodo', verbose_name="Periodo de titulacion", on_delete=models.CASCADE)
    actividad = models.ForeignKey(ActividadCronogramaTitulacion, verbose_name="Actividad", on_delete=models.CASCADE)
    inicio = models.DateField(verbose_name=u"Fecha de inicio", null=True, blank=True)
    fin = models.DateField(verbose_name=u"Fecha de fin", null=True, blank=True)
    observacion = models.TextField(default='', verbose_name=u'Observacion')

    def __str__(self):
        return f'{self.solicitud} - {self.actividad}'

    class Meta:
        verbose_name = u"Detalle de actividad de cronograma de titulación"
        verbose_name_plural = u"Detalles de actividades de cronograma de titulación"
        ordering = ['-id']

class VentasProgramaMaestria(ModeloBase):
    inscripcioncohorte = models.ForeignKey(InscripcionCohorte, blank=True, null=True, verbose_name=u'Postulante', on_delete=models.CASCADE)
    fecha = models.DateField(blank=True, null=True, verbose_name=u"Fecha")
    hora = models.TimeField(blank=True, null=True, verbose_name=u"Hora")
    asesor = models.ForeignKey(AsesorComercial, blank=True, null=True, verbose_name=u'Asesor Comercial', on_delete=models.CASCADE)
    mediopago = models.CharField(default='', max_length=100, verbose_name=u'Medio de Pago')
    facturado = models.BooleanField(default=False, verbose_name=u'¿Venta Facturada?')
    valida = models.BooleanField(default=True, verbose_name=u'¿Venta Válida?')

    def __str__(self):
        return f'{self.inscripcioncohorte.inscripcionaspirante.persona} - {self.inscripcioncohorte.cohortes}'

    class Meta:
        verbose_name = u"Venta de programa de maestría"
        verbose_name_plural = u"Ventas de programa de maestría"
        ordering = ['-id']


class EscuelaPosgrado(ModeloBase):
    nombre= models.CharField(max_length=350, verbose_name=u"Escuela de negocios", db_index=True)

    def __str__(self):
        return f'{self.nombre}'

    class Meta:
        verbose_name = u"Escuela Posgrado"
        verbose_name_plural = u"Escuela Posgrado"
        ordering = ['-id']


class SolicitudIngresoTitulacionPosgrado(ModeloBase):
    matricula = models.ForeignKey('sga.Matricula', on_delete=models.CASCADE,verbose_name=u'Matricula')
    archivo = models.FileField(upload_to='solicitudingresotitulacion/%Y/%m/%d',verbose_name=u'Archivo')
    mecanismotitulacionposgrado = models.ForeignKey('sga.MecanismoTitulacionPosgrado', on_delete=models.CASCADE,verbose_name=u'Mecanismo Titulación')
    firmado = models.BooleanField(default=False, verbose_name=u'firmado')

    def __str__(self):
        return "solicitud de ingreso a unidad de titulación"

    def download_link(self):
        return self.archivo.url

    class Meta:
        verbose_name = u'Solicitud Ingreso Titulacion Posgrado'
        verbose_name_plural = u'Solicitud Ingreso Titulacion Posgrado'
        ordering = ('id',)

class Convenio(ModeloBase):
    descripcion = models.CharField(default='', max_length=250, verbose_name=u'Descripcion')
    fechaInicio = models.DateField(verbose_name=u'Fecha Inicio')
    valido_form = models.BooleanField(default=False, verbose_name=u"Para presentar en formulario externo", blank=True, null=True)

    def lista_asesores_asignados(self):
        lista = None
        if ConvenioAsesor.objects.filter(status=True, convenio=self).exists():
            lista = ConvenioAsesor.objects.filter(status=True, convenio=self).order_by('asesor__id').distinct()
            #lista = AsesorComercial.objects.filter(status=True, id__in=idase)
        return lista

    def __str__(self):
        return f'[{self.id}] - {self.descripcion}'

    class Meta:
        verbose_name = u'Convenio'
        verbose_name_plural = u'Convenios'
        ordering = ('id',)


class ConvenioAsesor(ModeloBase):
    convenio = models.ForeignKey(Convenio, verbose_name=u'Convenio', on_delete=models.CASCADE)
    asesor = models.ForeignKey(AsesorComercial, verbose_name=u'Asesor', on_delete=models.CASCADE)
    fechaFin = models.DateField(verbose_name=u'Fecha Fin')

    def __str__(self):
        return f'Convenio [{self.convenio.id}] - {self.asesor}'

    class Meta:
        verbose_name = u'Convenio Asesor'
        verbose_name_plural = u'Convenio Asesores'
        ordering = ('id',)

class MecanismoDocumentosTutoriaPosgrado(ModeloBase):
    mecanismotitulacionposgrado = models.ForeignKey("sga.MecanismoTitulacionPosgrado", on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Mecanismo')
    convocatoria = models.ForeignKey("sga.ConfiguracionTitulacionPosgrado",on_delete=models.CASCADE, verbose_name=u'Convocatoria', blank=True, null=True)
    tipo = models.IntegerField(choices=TIPO_ARCHIVO_PORSGRADO, default=1, verbose_name=u"Tipo de Archivo")
    orden = models.IntegerField(default=0, verbose_name=u'Orden')

    class Meta:
        verbose_name = u"MecanismoDocumentosTutoriaPosgrado"
        verbose_name_plural = u"MecanismoDocumentosTutoriaPosgrado"
        ordering = ['id']

    def __str__(self):
        return u'%s' % self.get_tipo_display()



class Perms(models.Model):
    class Meta:
        permissions = (
            ("puede_asignar_asesor", "Puede asignar asesor comercial"),
            ("puede_confirmar_pre_asignacion", "Puede confirmar la asignacion de un lead"),
            ("puede_ver_historial", "Puede ver el historial de asesores de un lead"),
            ("puede_ver_metas_personales", "Puede ver metas personales"),
            ("puede_configurar_asesor", "Puede configurar asesores"),
            ("puede_adicionar_leads", "Puede adicionar leads"),
            ("puede_ver_leads_asesor", "Puede ver leads registrados por un asesor"),
            ("puede_reasignar_asesor_masivo", "Puede reasignar un asesor de forma masiva a varios leads"),
            ("puede_adicionar_meta", "Puede adicionar meta de ventas"),
            ("puede_editar_meta", "Puede editar meta de ventas"),
            ("puede_eliminar_meta", "Puede eliminar meta de ventas"),
            ("puede_ver_reporteria", "Puede ver Reporteria"),
            ("puede_cambiar_formapago", "Puede cambiar forma de pago"),
            ("puede_ver_historial_forma_pago", "Puede ver el historial de forma de pago"),
            ("puede_ver_requisitos_financiamiento", "Puede ver requisitos de financiamiento"),
            ("puede_aprobar_requisitos_financiamiento", "Puede aprobar requisitos de financiamiento"),
            ("puede_configurar_financiamiento", "Puede configurar financiamiento"),
            ("puede_ver_historial_reserva", "Puede ver historial de reservaciones"),
            ("puede_reservar_prospectos", "Puede realizar reservaciones"),
            ("puede_ver_detalle_requisitos_admision", "Puede ver detalle de requisitos de admisión"),
            ("puede_firmar_contratos_pago", "Puede firmar contratos pago"),
            ("puede_ver_contratos_pagares", "Puede ver contratos y pagarés"),
            ("puede_entrar_como_usuario", "Puede entrar como usuario posgrado"),
            ("puede_subir_comprobante_pago_posgrado", "Puede subir comprobante de pago posgrado"),
            ("puede_ver_estadisticas_comercializacion", "Puede ver estadisticas del area comercial de posgrado"),
            ("puede_editar_rubro_fechas", "Puede editar rubros con fechas anteriores"),
        )
