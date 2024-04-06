import random
from datetime import datetime
import time
from itertools import chain

from django.contrib.auth.models import Group
from django.db import models

# Create your models here.
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce
from django.forms import FloatField

from moodle.models import UserAuth
from sagest.models import TipoOtroRubro, DenominacionPuesto, ESTADO_FINAL_INSCRITO, APLICA_GRATUIDAD_INSCRITO, Rubro, \
    Pago
from sga.funciones import ModeloBase, variable_valor, null_to_decimal
from sga.models import MESES_CHOICES, Externo


class PeriodoFormaEjecutiva(ModeloBase):
    nombre = models.CharField(max_length=500, verbose_name=u'Nombre')
    descripcion = models.CharField(max_length=1000, verbose_name=u'Descripcion')
    fechainicio = models.DateField(blank=True, null=True)
    fechafin = models.DateField(blank=True, null=True)
    archivo = models.FileField(upload_to='capformaejecutiva/%Y/%m/%d', blank=True, null=True, verbose_name=u'Titulo')
    instructivo = models.FileField(upload_to='instructivoformaejecutivo/%Y/%m/%d', blank=True, null=True,
                                   verbose_name=u'Instructivo')
    urlmoodle = models.CharField(default='https://aulaposgrado.unemi.edu.ec', max_length=500, verbose_name=u'url moodle')
    keymoodle = models.CharField(default='1823dd47f3c35c924e066289aae91360', max_length=500, verbose_name=u'key moodle')

    class Meta:
        verbose_name=u'Periodo formacion ejecutiva'
        verbose_name_plural=u'Periodos formacion ejecutiva'
        ordering = ['id']

    def __str__(self):
        return f"{self.nombre} - {self.descripcion} ({self.fechafin} - {self.fechafin})"

    def typefile_archivo(self):
        if self.archivo:
            return self.archivo.name[self.archivo.name.rfind("."):]
        else:
            return None

    def typefile_instructivo(self):
        if self.instructivo:
            return self.instructivo.name[self.instructivo.name.rfind("."):]
        else:
            return None

    def puede_eliminar(self):
        return True

    def contar_inscripcion_periodo(self):
        total = 0
        if CapacitaEventoFormacionEjecutiva.objects.values('id').filter(status=True, periodo=self.id).exists():
            for evento in CapacitaEventoFormacionEjecutiva.objects.filter(status=True, periodo=self.id):
                total += evento.contar_inscripcion_evento_periodo()
        return total

    def idnumber(self):
        anoini = self.fechainicio.year
        anofin = self.fechafin.year
        if anoini != anofin:
            ano = '%s-%s' % (anoini, anofin)
        else:
            ano = '%s' % anoini
        return u'PERFORMEJECU%s-%s' % (self.id, ano)

class EventoFormaEjecutiva(ModeloBase):
    nombre = models.TextField(verbose_name=u'Nombre')

    class Meta:
        verbose_name = u'Evento formacion ejecutiva'
        verbose_name_plural = u'Eventos formacion ejecutiva'
        ordering = ['id']

    def __str__(self):
        return f"{self.nombre}"

class EnfoqueFormaEjecutiva(ModeloBase):
    nombre = models.TextField(verbose_name=u'Nombre')

    class Meta:
        verbose_name = u'Enfoque formacion ejecutiva'
        verbose_name_plural = u'Enfoques formacion ejecutiva'
        ordering = ['id']

    def __str__(self):
        return f"{self.nombre}"


class TurnoFormaEjecutiva(ModeloBase):
    turno = models.IntegerField(default=0, verbose_name=u'Turno')
    horainicio = models.TimeField(verbose_name=u'Comienza')
    horafin = models.TimeField(verbose_name=u'Termina')
    horas = models.FloatField(default=0, verbose_name=u'Horas')

    class Meta:
        verbose_name = u"Turno de clase formacion ejecutiva"
        verbose_name_plural = u"Turnos de clases formacion ejecutiva"
        ordering = ['id','horainicio']

    def __str__(self):
        return f'Turno {self.turno} [{self.horainicio.strftime("%H:%M %p")} a {self.horafin.strftime("%H:%M %p")}]'

class ModeloEvaluativoFormaEjecutiva(ModeloBase):
    nombre = models.CharField(default='', max_length=500, verbose_name=u"Nombre")
    notamaxima = models.FloatField(default=0, verbose_name=u'Nota maxima')
    notaminima = models.FloatField(default=0, verbose_name=u'Nota para aprobar')
    principal = models.BooleanField(default=False, verbose_name=u"Principal")
    evaluacion = models.BooleanField(default=False, verbose_name=u"Es Evaluacion")

    class Meta:
        verbose_name = u"Modelo evaluativo formacion ejecutiva"
        verbose_name_plural = u"Modaelos evaluativos formacion ejecutiva"
        ordering = ['id']

    def __str__(self):
        return u'%s (%s a %s)' % (self.nombre, self.notaminima.__str__(), self.notamaxima.__str__())

class ConfiguracionFormaEjecutiva(ModeloBase):
    minasistencia = models.IntegerField(default=0, verbose_name=u'Minimo Asistencia')
    minnota = models.IntegerField(default=0, verbose_name=u'Minimo Notas')
    aprobado2 = models.ForeignKey('sga.Persona', blank=True, null=True, related_name='aprobad_ejecuform',
                                  verbose_name=u"Aprobador Formacion Ejecutiva", on_delete=models.CASCADE)
    aprobado3 = models.ForeignKey('sga.Persona', blank=True, null=True, related_name='aprobad_ejecuform3',
                                  verbose_name=u"Vicerrector Adtvo.", on_delete=models.CASCADE)
    denominacionaprobado2 = models.ForeignKey(DenominacionPuesto, blank=True, null=True,
                                              related_name='denominacionaprobad_ejecuform2',
                                              verbose_name=u"Denominacion Aprobador Formacion Ejecutiva", on_delete=models.CASCADE)
    denominacionaprobado3 = models.ForeignKey(DenominacionPuesto, blank=True, null=True,
                                              related_name='denominacionaprobad_ejecuform3',
                                              verbose_name=u"Denominacion Vicerrector Adtvo.", on_delete=models.CASCADE)

    def __str__(self):
        return u'%s - %s' % (self.minasistencia, self.minnota)

    class Meta:
        verbose_name = u"Configuración Capacitación IPEC"
        verbose_name_plural = u"Configuración Capacitación IPEC"

class CapacitaEventoFormacionEjecutiva(ModeloBase):
    from sga.models import MODALIDAD_CAPACITACION
    periodo = models.ForeignKey(PeriodoFormaEjecutiva, verbose_name=u"Capacitacion Periodo", on_delete=models.CASCADE)
    capevento = models.ForeignKey(EventoFormaEjecutiva, verbose_name=u"Evento", on_delete=models.CASCADE)
    enfoque = models.ForeignKey(EnfoqueFormaEjecutiva, verbose_name=u"Capacitacion Enfoque", on_delete=models.CASCADE)
    horas = models.IntegerField(default=0, verbose_name=u'Horas Academica')
    minasistencia = models.IntegerField(default=0, verbose_name=u'Minimo Asistencia')
    minnota = models.IntegerField(default=0, verbose_name=u'Minimo Notas')
    cupo = models.IntegerField(default=0, verbose_name=u'Cupo')
    costo = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Costo Interno")
    costoexterno = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Costo Externo")
    tipocertificacion = models.ForeignKey('sga.TipoCertificacion', blank=True, null=True,
                                          verbose_name=u"Tipo certificación", on_delete=models.CASCADE)
    tipoparticipacion = models.ForeignKey('sga.TipoParticipacion', blank=True, null=True,
                                          verbose_name=u"Tipo participación", on_delete=models.CASCADE)
    contextocapacitacion = models.ForeignKey('sga.ContextoCapacitacion', blank=True, null=True,
                                             verbose_name=u'Contexto capacitacion', on_delete=models.CASCADE)
    tipocapacitacion = models.ForeignKey('sga.TipoCapacitacion', blank=True, null=True,
                                         verbose_name=u"Tipo capacitación", on_delete=models.CASCADE)
    modalidad = models.IntegerField(choices=MODALIDAD_CAPACITACION, blank=True, null=True,
                                    verbose_name=u'Modalidad Capacitacion')
    responsable = models.ForeignKey('sga.Persona', verbose_name=u"Persona", on_delete=models.CASCADE)
    aula = models.ForeignKey('sga.Aula', verbose_name=u'Aula', on_delete=models.CASCADE)
    fechainicio = models.DateField(blank=True, null=True)
    fechafin = models.DateField(blank=True, null=True)
    areaconocimiento = models.ForeignKey('sga.AreaConocimientoTitulacion', blank=True, null=True,
                                         verbose_name=u'Area de conocimiento', on_delete=models.CASCADE)
    aprobado2 = models.ForeignKey('sga.Persona', blank=True, null=True, related_name='aprobaejecform2',
                                  verbose_name=u"Aprobador2", on_delete=models.CASCADE)
    aprobado3 = models.ForeignKey('sga.Persona', blank=True, null=True, related_name='aprobaejecform3',
                                  verbose_name=u"Vicerrector Adtvo.", on_delete=models.CASCADE)
    denominacionaprobado2 = models.ForeignKey(DenominacionPuesto, blank=True, null=True,
                                              related_name='denominacionaprobaejecform2',
                                              verbose_name=u"Denominacion Aprobador2", on_delete=models.CASCADE)
    denominacionaprobado3 = models.ForeignKey(DenominacionPuesto, blank=True, null=True,
                                              related_name='denominacionaprobaejecform3',
                                              verbose_name=u"Denominacion Vicerrector Adtvo.", on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True, verbose_name=u"Observacion")
    objetivo = models.TextField(blank=True, null=True, verbose_name=u"Objetivo")
    contenido = models.TextField(blank=True, null=True, verbose_name=u"Contenido")
    visualizar = models.BooleanField(default=False, verbose_name=u"Visualizar")
    convalidar = models.BooleanField(default=False, verbose_name=u"Convalidar")
    fechainicioinscripcion = models.DateField(blank=True, null=True)
    fechafininscripcion = models.DateField(blank=True, null=True)
    tiporubro = models.ForeignKey(TipoOtroRubro, blank=True, null=True, verbose_name=u"Tipo", on_delete=models.CASCADE)
    publicarinscripcion = models.BooleanField(default=False, verbose_name=u"Incripción Pública")
    fechamaxpago = models.DateField(blank=True, null=True)
    envionotaemail = models.BooleanField(default=False, verbose_name=u"Envió de nota al email")
    generarrubro = models.BooleanField(default=True, verbose_name=u"Se generan rubros")
    fechacertificado = models.TextField(blank=True, null=True, verbose_name=u"Fecha certificado")
    archivo = models.FileField(upload_to='capacitacionformejec', blank=True, null=True, verbose_name=u'Archivo de imagen')
    banner = models.FileField(upload_to='capacitacionformejec_banner', blank=True, null=True, verbose_name=u'Banner')
    brochure = models.FileField(upload_to='brochureejecuform', blank=True, null=True, verbose_name=u'Brochure')
    modeloevaludativoindividual = models.BooleanField(default=False, verbose_name=u"Modelo Evaluativo Individual?")
    mes = models.IntegerField(choices=MESES_CHOICES, blank=True, null=True, verbose_name=u'Mes de capacitacion')
    rubroepunemi = models.BooleanField(verbose_name=u'Cobro rubro epunemi', null=True, blank=True,default=False)


    def __str__(self):
        obser = ""
        if self.observacion:
            obser = "-" + self.observacion
        return u'%s - Periodo:[%s] %s' % (self.capevento, self.periodo, obser)

    class Meta:
        verbose_name = u"Evento Capacitación Formacion ejecutiva"
        verbose_name_plural = u"Evento Capacitaciones Formacion ejecutiva"
        ordering = ('fechainicio',)

    def contar_inscripcion_evento_periodo(self):
        return len(self.capaeventoinscritoformaejecutiva_set.values('id').filter(status=True))

    def hay_cupo_inscribir(self):
        return True if self.contar_inscripcion_evento_periodo() < self.cupo else False

    def instructores_principal(self):
        if self.instructorformaejecutiva_set.values('id').filter(status=True).exists():
            return self.instructorformaejecutiva_set.filter(status=True)
        return None

    def estado_evento(self):
        estado = ''
        if datetime.now().date() >= self.fechainicio and datetime.now().date() <= self.fechafin:
            estado = 'EN CURSO'
        elif datetime.now().date() < self.fechainicio:
            estado = 'PENDIENTE'
        else:
            estado = 'CERRADO'
        return estado

    def en_uso(self):
        return True if self.capaeventoinscritoformaejecutiva_set.filter(status=True).exists() else False

    def limitar_objetivo_presentacion(self):
        objetivo = self.objetivo
        if objetivo:
            if self.objetivo.__len__() > 200:
                objetivo = self.objetivo[0:200] + "..."
        return objetivo

    def limitar_observacion_presentacion(self):
        observacion = self.observacion
        if observacion:
            if self.observacion.__len__() > 200:
                observacion = self.observacion[0:200] + "..."
        return observacion

    def limitar_contenido_presentacion(self):
        contenido = self.contenido
        if contenido:
            if contenido.__len__() > 200:
                contenido = self.contenido[0:200] + "..."
        else:
            contenido = ''
        return contenido

    def total_pagado_real(self):
        inscritos = self.capaeventoinscritoformaejecutiva_set.filter(status=True)
        rubros = Rubro.objects.filter(Q(capeventoperiodoformejecu=self)).filter(status=True).values_list('pk', flat=True)
        total = null_to_decimal(
            Pago.objects.filter(rubro__in=rubros, status=True).aggregate(valort=Sum('valortotal'))['valort'], 2)
        return total

    def list_inscritos_costo(self):
        rub = Rubro.objects.filter(tipo=self.tiporubro, cancelado=True).values_list('persona__id', flat=True)
        return self.capaeventoinscritoformaejecutiva_set.filter(status=True, desactivado=False, participante__id__in=rub).distinct()

    def list_inscritos_sin_costo(self):
        return self.capaeventoinscritoformaejecutiva_set.filter(status=True, desactivado=False).distinct()

    def exiten_inscritos(self):
        return self.capaeventoinscritoformaejecutiva_set.values('id').filter(status=True).exists()

    def inscritos(self):
        return self.capaeventoinscritoformaejecutiva_set.filter(status=True).order_by('participante__persona__id',
                                                                     'participante__apellido1',
                                                                     'participante__apellido2',
                                                                     'participante__nombres') if self.capaeventoinscritoformaejecutiva_set.values('id').filter(
            status=True).exists() else []

    def idnumber(self):
        anoini = self.fechainicio.year
        anofin = self.fechafin.year
        if anoini != anofin:
            ano = '%s-%s' % (anoini, anofin)
        else:
            ano = '%s' % anoini
        return u'CURSOFORMEJECU%s-%s' % (self.id, ano)

class CapaEventoInscritoFormaEjecutiva(ModeloBase):
    capeventoperiodo = models.ForeignKey(CapacitaEventoFormacionEjecutiva, verbose_name=u'Evento Capacitación',
                                         on_delete=models.CASCADE)
    participante = models.ForeignKey('sga.Persona', verbose_name=u'Participante', on_delete=models.CASCADE)
    observacion = models.TextField(default='', verbose_name=u'Observación')
    personalunemi = models.BooleanField(default=False, verbose_name=u'Personal Unemi')
    emailnotificado = models.BooleanField(default=False, verbose_name=u'Notificar email')
    fecha_emailnotifica = models.DateTimeField(blank=True, null=True)
    persona_emailnotifica = models.ForeignKey('sga.Persona', blank=True, null=True, related_name='+',
                                              verbose_name=u'Quien notifica y envia certificado',
                                              on_delete=models.CASCADE)
    # rutapdf = models.CharField(default='', max_length=500, verbose_name=u"Ruta del certificado")
    rutapdf = models.FileField(upload_to='formacionejecutiva/qrcode/certificados', blank=True, null=True,
                               verbose_name=u'Archivo retencion pdf')
    observacionmanual = models.TextField(default='', verbose_name=u'Observación manual')
    observacionmover = models.TextField(default='', verbose_name=u'Observación mover')
    archivo = models.FileField(upload_to='archivoinscripcionipec/%Y/%m/%d/', blank=True, null=True,
                               verbose_name=u'Archivo inscripcion ipec')
    desactivado = models.BooleanField(default=False, verbose_name=u'Desactivado por falta de pago')
    encursomoodle = models.BooleanField(default=False, verbose_name=u"Esta en curso moodle")
    notafinal = models.FloatField(blank=True, null=True, verbose_name=u'Nota Final')
    estado = models.IntegerField(choices=ESTADO_FINAL_INSCRITO, default=1, verbose_name=u'Estado del curso')
    urlhtmlinsignia = models.CharField(blank=True, null=True, max_length=200, verbose_name=u'url html insignia')
    htmlinsignia = models.FileField(upload_to='formacionejecutiva/qrcode/insignia', blank=True, null=True,
                               verbose_name=u'Archivo html insignia')
    namehtmlinsignia = models.CharField(blank=True, null=True, max_length=100, verbose_name=u'name html insignia')
    aplicagratuidad = models.IntegerField(choices=APLICA_GRATUIDAD_INSCRITO, default=2,
                                          verbose_name=u'Aplica gratuidad')
    reseteopordesuso = models.BooleanField(blank=True, null=True, default=False, verbose_name=u"Reseteo sga/sagest por desuso")

    class Meta:
        verbose_name = u"Inscripción de Evento - Formacion Ejecutiva"
        verbose_name_plural = u"Inscripciones de Evento - Formacion Ejecutiva"
        ordering = ['participante']

    def __str__(self):
        return u'%s' % self.participante

    def numrandom(self):
        return random.randint(0,9999)

    def download_link_archivo(self):
        return self.archivo.url

    def download_link(self):
        return self.rutapdf.url

    def existerubrocurso(self):
        valor = None
        if Rubro.objects.values('id').filter(persona=self.participante, capeventoperiodoformejecu=self.capeventoperiodo,
                                             status=True).exclude(pago__factura__valida=False):
            valor = Rubro.objects.filter(persona=self.participante, capeventoperiodoformejecu=self.capeventoperiodo,
                                         status=True).exclude(pago__factura__valida=False)
        return valor

    def pagorubrocurso(self):
        valor = Rubro.objects.filter(persona=self.participante, capeventoperiodoformejecu=self.capeventoperiodo,
                                     cancelado=True, status=True).exclude(pago__factura__valida=False)
        return valor

    def total_pagado_conrubro(self):
        if Rubro.objects.filter(persona=self.participante, capeventoperiodoformejecu=self.capeventoperiodo,
                                status=True).exclude(pago__factura__valida=False):
            # if Rubro.objects.filter(persona=self.participante, tipo=self.capeventoperiodo.tiporubro, status=True).exclude(pago__factura__valida=False):
            rub = Rubro.objects.filter(persona=self.participante, capeventoperiodoformejecu=self.capeventoperiodo,
                                       status=True).exclude(pago__factura__valida=False)
            # rub = Rubro.objects.filter(persona=self.participante, tipo=self.capeventoperiodo.tiporubro, status=True).exclude(pago__factura__valida=False)[0]
            det = 0
            for r in rub:
                det += null_to_decimal(r.pago_set.filter(rubro__status=True).exclude(pagoliquidacion__isnull=False).distinct().aggregate(valor=Sum('valortotal'))['valor'], 2)
            return det
        else:
            return 0


    def total_valoradeuda(self):
        if Rubro.objects.values('id').filter(persona=self.participante, capeventoperiodoformejecu=self.capeventoperiodo, status=True):
            # if Rubro.objects.filter(persona=self.participante, tipo=self.capeventoperiodo.tiporubro, status=True):
            total = 0
            for re in Rubro.objects.filter(persona=self.participante, capeventoperiodoformejecu=self.capeventoperiodo, status=True):
            # rub = Rubro.objects.filter(persona=self.participante, tipo=self.capeventoperiodo.tiporubro, status=True)[0]
                total += re.total_adeudado()
            return total
        else:
            return 1


    def rubrofuemigradoaepunemi(self):
        return Rubro.objects.values('id').filter(persona=self.participante, capeventoperiodoformejecu=self.capeventoperiodo,
                status=True, idrubroepunemi__isnull=False, idrubroepunemi__gt=0).exclude(pago__factura__valida=False)

    def nota_total_evento(self, ide):
        from django.db.models import Avg
        totaldocentes = self.capeventoperiodo.instructorformaejecutiva_set.all().count()
        if CapDetalleNotaFormaEjecutiva.objects.filter(status=True, inscrito=self,
                                             cabeceranota__instructor__capeventoperiodo_id=ide).exists():
            return CapDetalleNotaFormaEjecutiva.objects.filter(status=True, inscrito=self,
                                                     cabeceranota__instructor__capeventoperiodo_id=ide).aggregate(
                nota=Coalesce(Sum(F('nota'), output_field=FloatField()), 0.0)).get('nota') / totaldocentes
        return None

    def cancelo_rubro(self):
        return Rubro.objects.filter(cancelado=True, status=True, persona=self.participante,
                                    capeventoperiodoformejecu=self.capeventoperiodo).exists()

    def get_nota_individual(self, idm, ide):
        if CapDetalleNotaFormaEjecutiva.objects.values('id').filter(status=True, cabeceranota_id=int(idm), inscrito=self,
                                             cabeceranota__instructor__capeventoperiodo_id=ide).exists():
            return CapDetalleNotaFormaEjecutiva.objects.get(status=True, cabeceranota_id=int(idm), inscrito_id=self.id,
                                                  cabeceranota__instructor__capeventoperiodo_id=ide)
        return None

    def nota_total_evento_porinstructor(self, ide, idi):
        if CapDetalleNotaFormaEjecutiva.objects.values('id').filter(status=True, inscrito=self,
                                             cabeceranota__instructor__capeventoperiodo_id=ide).exists():
            return CapDetalleNotaFormaEjecutiva.objects.filter(status=True, inscrito=self,
                                                     cabeceranota__instructor__id=idi).aggregate(
                nota=(Sum(F('nota')))).get('nota')
        return None

    def regpago(self):
        return self.pagoformacionejecutiva_set.filter(status=True) if self.pagoformacionejecutiva_set.values('id').filter(status=True).exists() else None

    def total_saldo_rubro(self):
        valor = null_to_decimal(
            Rubro.objects.filter(persona=self.participante, tipo=self.capeventoperiodo.tiporubro,status=True)
            .exclude(pago__factura__valida=False)
            .aggregate(valor=Sum('saldo'))['valor'],2
        )
        return valor

class InstructorFormaEjecutiva(ModeloBase):
    capeventoperiodo = models.ForeignKey(CapacitaEventoFormacionEjecutiva, verbose_name=u"Capacitacion Evento Periodo",
                                         on_delete=models.CASCADE)
    instructor = models.ForeignKey('sga.Persona', verbose_name=u"Capacitacion Periodo", on_delete=models.CASCADE)
    instructorprincipal = models.BooleanField(default=False, verbose_name=u"Estado Asistencia")
    activo = models.BooleanField(default=False, verbose_name=u"Perfil")
    rutapdf = models.FileField(upload_to='qrcode/certificados_facilitadores', blank=True, null=True,
                               verbose_name=u'Certificado capacitacion pdf')
    emailnotificado = models.BooleanField(default=False, verbose_name=u'Notificar email')
    fecha_emailnotifica = models.DateTimeField(blank=True, null=True)
    persona_emailnotifica = models.ForeignKey('sga.Persona', blank=True, null=True, related_name='+',
                                              verbose_name=u'Quien notifica y envia certificado',
                                              on_delete=models.CASCADE)
    idcursomoodle = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'id de curso de moodle')
    codigonumber = models.CharField(default='', max_length=100, verbose_name=u'Codigo number edcom')
    nombrecurso = models.TextField(default='', verbose_name=u'Nombre de materia moodle')

    def __str__(self):
        return u'%s - %s - %s - [ %s ]' % (
        self.instructor.cedula, self.instructor.nombre_completo_inverso(), self.instructor.email, self.id)

    class Meta:
        verbose_name = u"Instructor Evento Capacitación"
        verbose_name_plural = u"Instructores Evento Capacitación"
        ordering = ['instructor']

    def tiene_perfilusuario(self):
        from sga.models import PerfilUsuario
        return PerfilUsuario.objects.filter(instructorejecutiva__instructor=self.instructor).exists()


    def perfilusuario_instructor(self):
        from sga.models import PerfilUsuario
        if PerfilUsuario.objects.filter(instructorejecutiva__instructor=self.instructor, instructorejecutiva__activo=True).exists():
            if self.instructorprincipal:
                return self.perfilusuario_set.filter(instructor__isnull=False, instructor__instructorprincipal=True)
        return None

    def crear_eliminar_perfil_instructor(self, activarperfil):
        # CREAR PERFIL
        if activarperfil:
            if not self.perfilusuario_instructor() and self.instructorprincipal:
                self.instructor.crear_perfil(instructorejecutiva=self)
                self.save()
        # ADICIONAR A GRUPOS
        grupo = Group.objects.get(id=variable_valor('INSTRUCTOR_GROUP_ID'))
        if activarperfil:
            if not self.instructor.en_grupo(grupo.id):
                grupo.user_set.add(self.instructor.usuario)
                grupo.save()
        elif self.instructor.en_grupo(grupo.id):
            grupo.user_set.remove(self.instructor.usuario)

    def estado_perfil(self):
        return InstructorFormaEjecutiva.objects.values('id').filter(instructor=self.instructor, activo=True,status=True).exists()

    def notas_por_instructor(self):
        return self.capnotaformaejecutiva_set.filter(status=True)

    def modelo_evaluativo_utilizado_sin_evaluacion(self):
        return ModeloEvaluativoFormaEjecutiva.objects.filter(capnotaformaejecutiva__instructor=self, evaluacion=False).order_by(
            'fecha_creacion')

    def modelo_evaluativo_utilizado_evaluacion(self):
        return ModeloEvaluativoFormaEjecutiva.objects.filter(capnotaformaejecutiva__instructor=self, evaluacion=True).order_by(
            'fecha_creacion')

    def unido_modelo_evaluativo_evaluativo_utilizado(self):
        return list(
            chain(self.modelo_evaluativo_utilizado_sin_evaluacion(), self.modelo_evaluativo_utilizado_evaluacion()))

    def crear_actualizar_instructor_curso(self, moodle, tipourl):
        #################################################################################################################
        # AGREGAR DOCENTE
        #################################################################################################################
        from sga.models import Profesor
        try:
            if self.idcursomoodle:
                cursoid = self.idcursomoodle
                periodo = self.capeventoperiodo.periodo
                if self.quitar_docente_grupo(moodle, tipourl):
                    instructor = self.instructor
                    if instructor and instructor.usuario and not 'POR DEFINIR' in instructor.nombres:
                        persona = instructor
                        username = instructor.usuario.username
                        bprofesor = moodle.BuscarUsuario(periodo, tipourl, 'username', username)
                        profesorid = 0
                        if not bprofesor:
                            bprofesor = moodle.BuscarUsuario(periodo, tipourl, 'username', username)

                        if bprofesor['users']:
                            if 'id' in bprofesor['users'][0]:
                                profesorid = bprofesor['users'][0]['id']
                        else:
                            idnumber_user = persona.identificacion()
                            notuser = moodle.BuscarUsuario(periodo, tipourl, 'idnumber', idnumber_user)
                            if not notuser:
                                notuser = moodle.BuscarUsuario(periodo, tipourl, 'idnumber', idnumber_user)

                            bprofesor = moodle.CrearUsuario(periodo, tipourl, u'%s' % persona.usuario.username,
                                                            u'%s' % persona.identificacion(),
                                                            u'%s' % persona.nombres,
                                                            u'%s %s' % (persona.apellido1, persona.apellido2),
                                                            u'%s' % persona.emailinst,
                                                            idnumber_user,
                                                            u'%s' % persona.canton.nombre if persona.canton else '',
                                                            u'%s' % persona.pais.nombre if persona.pais else '')
                            profesorid = bprofesor[0]['id']

                        if profesorid > 0:
                            rolest = moodle.EnrolarCurso(periodo, tipourl, 9, profesorid, cursoid)
                            if persona.idusermoodleposgrado != profesorid:
                                persona.idusermoodleposgrado = profesorid
                                persona.save()
                        print('**********INSTRUCTOR: %s' % instructor)
        except Exception as ex:
            print('Error al crear docente %s' % ex)

    def quitar_docente_grupo(self, moodle, tipourl):
        from django.db import connections
        cursor = connections['moodle_pos'].cursor()
        #################################################################################################################
        # QUITAR DOCENTE
        #################################################################################################################
        if self.idcursomoodle:
            cursoid = self.idcursomoodle
            idprofesores = self.instructor.idusermoodleposgrado

            query = """SELECT DISTINCT enrol.userid, asi.roleid from mooc_user_enrolments enrol 
                        inner join mooc_role_assignments asi on asi.userid=enrol.userid and asi.roleid in(%s) 
                        where enrol.enrolid in(select en.id from mooc_enrol en where en.courseid=%s) 
                        AND enrol.userid not in(%s0) """ % (9, cursoid, idprofesores)
            cursor.execute(query)
            row = cursor.fetchall()
            if row:
                for deluser in row:
                    unrolest = moodle.UnEnrolarCurso(self.nombrecurso, tipourl, deluser[1], deluser[0], cursoid)
                    print('************ Eliminar Profesor: *** %s' % deluser[0])
        return True

    def crear_actualizar_estudiantes_curso(self, moodle, tipourl, codigoinscrito, formeje=False):
        #################################################################################################################
        # AGREGAR ESTUDIANTE
        #################################################################################################################
        from sga.funciones import log, generar_usuario_sin_perfil, calculate_username
        periodo = self.capeventoperiodo.periodo
        if self.idcursomoodle:
            contador = 0
            cursoid = self.idcursomoodle
            estudiante = CapaEventoInscritoFormaEjecutiva.objects.get(pk=codigoinscrito, status=True)
            try:
                contador += 1
                bandera = 0
                usuario = None
                persona = estudiante.participante
                # if not persona.emailinst and persona.emailinst != '':
                #     persona.emailinst = persona.email
                #     persona.save()
                if persona.usuario:
                    username = persona.usuario.username
                    usuario = persona.usuario
                else:
                    username = calculate_username(persona)
                    generar_usuario_sin_perfil(persona, username)
                    if not Externo.objects.filter(status=True, persona=persona).exists():
                        externo = Externo(persona=persona,
                                          nombrecomercial='',
                                          nombrecontacto='',
                                          telefonocontacto='')
                        externo.save()
                    else:
                        externo = Externo.objects.get(status=True, persona=persona)
                    persona.crear_perfil(externo=externo)
                    persona.mi_perfil()
                    usuario = persona.usuario
                    usuario.set_password(persona.identificacion())
                    usuario.save()
                    persona.participante.clave_cambiada()
                # Registar correo institucional con el usuario
                if not persona.emailinst:
                    persona.emailinst = f'{persona.usuario.username}@unemi.edu.ec'
                    persona.save()
                # OK
                if not UserAuth.objects.filter(usuario=usuario).exists():
                    usermoodle = UserAuth(usuario=usuario)
                    usermoodle.set_data()
                    usermoodle.set_password(persona.identificacion())
                    usermoodle.save()
                else:
                    usermoodle = UserAuth.objects.filter(usuario=usuario).first()
                    usermoodle.set_data()

                    # Resetear contrasea si es estudiante o personal UNEMI y su ultimo acceso fue hace un mes o más
                    if formeje:
                        if estudiante.personalunemi or estudiante.es_alumnounemi():
                            ultimo_acceso_dias = (datetime.now().date() - persona.usuario.last_login.date()).days
                            if ultimo_acceso_dias >= 30:
                                estudiante.reseteopordesuso = resetear_clave_edcon(persona)
                                estudiante.save()
                    # Resetear contrasea si es estudiante o personal UNEMI y su ultimo acceso fue hace un mes o más

                    usermoodle.save()
                bestudiante = moodle.BuscarUsuario(periodo, tipourl, 'username', username)
                estudianteid = 0
                if not bestudiante:
                    bestudiante = moodle.BuscarUsuario(periodo, tipourl, 'username', username)

                if bestudiante['users']:
                    if 'id' in bestudiante['users'][0]:
                        estudianteid = bestudiante['users'][0]['id']
                else:
                    idnumber_user = persona.identificacion()
                    notuser = moodle.BuscarUsuario(periodo, tipourl, 'idnumber', idnumber_user)
                    if not notuser:
                        notuser = moodle.BuscarUsuario(periodo, tipourl, 'idnumber', idnumber_user)

                    bestudiante = moodle.CrearUsuario(periodo, tipourl, u'%s' % persona.usuario.username,
                                                      u'%s' % persona.identificacion(),
                                                      u'%s' % persona.nombres,
                                                      u'%s %s' % (persona.apellido1, persona.apellido2),
                                                      u'%s' % persona.emailinst if (
                                                                  persona.emailinst and persona.emailinst != '') else persona.email,
                                                      idnumber_user,
                                                      u'%s' % persona.canton.nombre if persona.canton else '',
                                                      u'%s' % persona.pais.nombre if persona.pais else '')
                    estudianteid = bestudiante[0]['id']
                if estudianteid > 0:
                    rolest = moodle.EnrolarCurso(periodo, tipourl, 10, estudianteid, cursoid)
                    if persona.idusermoodleposgrado != estudianteid:
                        persona.idusermoodleposgrado = estudianteid
                        persona.save()
                    print('************Estudiante: %s *** %s' % (contador, persona))
            except Exception as ex:
                log(u'Moodle Error al crear Estudiante: %s' % persona, None, "add", User.objects.get(pk=1))
                print('Error al crear estudiante %s' % ex)

    def crear_actualizar_categoria_notas_curso(self):
        from django.db import connections
        cursor = connections['moodle_pos'].cursor()
        #################################################################################################################
        # AGREGAR SISTEMA DE CALIFICACION
        #################################################################################################################
        if self.idcursomoodle:
            cursoid = self.idcursomoodle
            modelonotas = self.unido_modelo_evaluativo_evaluativo_utilizado()
            if modelonotas:
                query = u"SELECT id FROM mooc_grade_categories WHERE parent is null and depth=1 and courseid= %s" % cursoid
                cursor.execute(query)
                row = cursor.fetchall()
                padrenota = 0
                fecha = int(time.mktime(datetime.now().date().timetuple()))
                if not row:
                    query = u"INSERT INTO mooc_grade_categories(courseid, parent, depth, path, fullname, aggregation, keephigh, droplow, aggregateonlygraded, hidden, timecreated, timemodified) VALUES (%s, null, 1, E'', E'?', 13, 0, 0, 0, 0, %s, %s)" % (
                    cursoid, fecha, fecha)
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
                    query = u"SELECT id FROM mooc_grade_items WHERE courseid=%s and itemtype='course' and iteminstance=%s" % (
                    cursoid, padrenota)
                    cursor.execute(query)
                    row = cursor.fetchall()
                    if not row:
                        query = u"INSERT INTO mooc_grade_items (courseid, categoryid, itemname, itemtype, itemmodule, iteminstance, itemnumber, iteminfo, idnumber, calculation, gradetype, grademax, grademin, scaleid, outcomeid, gradepass, multfactor, plusfactor, aggregationcoef, aggregationcoef2, sortorder, display, decimals, hidden, locked, locktime, needsupdate, weightoverride, timecreated, timemodified) VALUES (%s, null, null, E'course', null, %s, null, null, null, null, 1, 100, 0, null, null, 0, 1, 0, 0, 0, %s, 0, 2, 0, 0, 0, 0, 0, %s, %s)" % (
                        cursoid, padrenota, ordennota, fecha, fecha)
                        cursor.execute(query)

                    for modelo in modelonotas:
                        query = u"SELECT id FROM mooc_grade_categories WHERE parent=%s and depth=2 and courseid= %s and fullname='%s'" % (
                        padrenota, cursoid, modelo.nombre)
                        cursor.execute(query)
                        row = cursor.fetchall()
                        padremodelo = 0
                        if not row:
                            query = u"INSERT INTO mooc_grade_categories(courseid, parent, depth, path, fullname, aggregation, keephigh, droplow, aggregateonlygraded, hidden, timecreated, timemodified) VALUES (%s, %s, 2, E'', E'%s', 0, 0, 0, 0, 0, %s, %s)" % (
                            cursoid, padrenota, modelo.nombre, fecha, fecha)
                            cursor.execute(query)
                            query = u"SELECT id FROM mooc_grade_categories WHERE parent=%s and depth=2 and courseid= %s and fullname='%s'" % (
                            padrenota, cursoid, modelo.nombre)
                            cursor.execute(query)
                            row = cursor.fetchall()
                            padremodelo = row[0][0]
                            query = u"UPDATE mooc_grade_categories SET path='/%s/%s/' WHERE id= %s" % (
                            padrenota, padremodelo, padremodelo)
                            cursor.execute(query)
                        else:
                            padremodelo = row[0][0]
                        if padremodelo > 0:
                            ordennota += 1
                            query = u"SELECT id FROM mooc_grade_items WHERE courseid=%s and itemtype='category' and iteminstance=%s" % (
                            cursoid, padremodelo)
                            cursor.execute(query)
                            row = cursor.fetchall()
                            if not row:
                                query = u"INSERT INTO mooc_grade_items (courseid, categoryid, itemname, itemtype, itemmodule, iteminstance, itemnumber, iteminfo, idnumber, calculation, gradetype, grademax, grademin, scaleid, outcomeid, gradepass, multfactor, plusfactor, aggregationcoef, aggregationcoef2, sortorder, display, decimals, hidden, locked, locktime, needsupdate, weightoverride, timecreated, timemodified) " \
                                        u"VALUES (%s, null, E'', E'category', null, %s, null, E'', E'', null, 1, %s, 0, null, null, 0, 1, 0, 0, %s, %s, 0, %s, 0, 0, 0, 0, 0, %s, %s)" \
                                        % (cursoid, padremodelo, modelo.notamaxima,
                                           null_to_decimal(modelo.notamaxima / 100, 2), ordennota, 2, fecha, fecha)
                                cursor.execute(query)

    def crear_curso_moodle(self, codigoinscritogrupoexamen, contadoringreso, formeje=False):
        from django.db import connections
        from moodle import moodle
        from sga.models import Coordinacion
        cursor = connections['moodle_pos'].cursor()
        #################################################################################################################
        #################################################################################################################
        # servidor
        AGREGAR_MODELO_NOTAS = True
        AGREGAR_ESTUDIANTE = True
        AGREGAR_DOCENTE = True

        parent_grupoid = 0
        tipourl = 1
        periodo = self.capeventoperiodo.periodo
        curso = self.capeventoperiodo
        bgrupo = moodle.BuscarCategoriasid(periodo, tipourl, 4285)
        if bgrupo:
            if 'id' in bgrupo[0]:
                parent_grupoid = bgrupo[0]['id']
        contador = 0

        if parent_grupoid >= 0:
            if contadoringreso == 0:
                """"
                CREANDO EL PERIODO DE CURSO EL ID SE CONFIGURA EN VARIABLES GLOBALES
                """
                bperiodo = moodle.BuscarCategorias(periodo, tipourl, periodo.idnumber())
                parent_periodoid = 0
                if bperiodo:
                    if 'id' in bperiodo[0]:
                        parent_periodoid = bperiodo[0]['id']
                else:
                    bperiodo = moodle.CrearCategorias(periodo, tipourl, periodo.nombre, periodo.idnumber(),
                                                      periodo.nombre, parent=parent_grupoid)
                    parent_periodoid = bperiodo[0]['id']
                if parent_periodoid > 0:
                    """"
                    CREANDO CURSO IPEC
                    """
                    idnumber_curso = u'%s-CUR%s' % (periodo.idnumber(), curso.id)
                    bcurso = moodle.BuscarCategorias(periodo, tipourl, idnumber_curso)
                    parent_cursoid = 0
                    if bcurso:
                        if 'id' in bcurso[0]:
                            parent_cursoid = bcurso[0]['id']
                    else:
                        bcurso = moodle.CrearCategorias(periodo, tipourl, curso.capevento.nombre, idnumber_curso, curso,
                                                        parent=parent_periodoid)
                        parent_cursoid = bcurso[0]['id']
                    if parent_cursoid > 0:
                        """"
                        CREANDO EL INSTRUCTOR
                        """
                        if self.codigonumber:
                            idnumber_instructor = self.codigonumber
                        else:
                            idnumber_instructor = u'%s-CUR%s-INS%s' % (periodo.idnumber(), curso.id, self.id)
                        binstructor = moodle.BuscarCursos(periodo, tipourl, 'idnumber', idnumber_instructor)
                        if not binstructor:
                            binstructor = moodle.BuscarCursos(periodo, tipourl, 'idnumber', idnumber_instructor)
                        numsections = 1
                        summary = u''
                        startdate = int(time.mktime(curso.fechainicio.timetuple()))
                        enddate = int(time.mktime(curso.fechafin.timetuple()))
                        instructorid = 0
                        if binstructor['courses']:
                            if 'id' in binstructor['courses'][0]:
                                instructorid = binstructor['courses'][0]['id']
                        else:
                            binstructor = moodle.CrearCursos(periodo, tipourl, u'%s' % self.nombrecurso,
                                                             u'INS-%s-[%s]' % (str(curso.fechainicio), self.id),
                                                             parent_cursoid, idnumber_instructor, summary, startdate,
                                                             enddate, numsections)
                            instructorid = binstructor[0]['id']
                        if instructorid > 0:
                            if self.idcursomoodle != instructorid:
                                self.codigonumber = idnumber_instructor
                                self.idcursomoodle = instructorid
                                self.save()
                            if AGREGAR_MODELO_NOTAS:
                                self.crear_actualizar_categoria_notas_curso()

                            if AGREGAR_DOCENTE:
                                self.crear_actualizar_instructor_curso(moodle, 1)

                            if AGREGAR_ESTUDIANTE:
                                self.crear_actualizar_estudiantes_curso(moodle, 1, codigoinscritogrupoexamen, formeje=True)
            else:
                if AGREGAR_ESTUDIANTE:
                    self.crear_actualizar_estudiantes_curso(moodle, 1, codigoinscritogrupoexamen, formeje=True)


class CapRegistrarDatosInscritoFormaEjecutiva(ModeloBase):
    persona = models.ForeignKey('sga.Persona', null=True, blank=True, verbose_name=u'Persona', on_delete=models.CASCADE)
    lugarestudio = models.CharField(null=True, blank=True, max_length=400, verbose_name=u"Lugar de estudio")
    carrera = models.CharField(null=True, blank=True, max_length=400, verbose_name=u"Carrera")
    profesion = models.CharField(null=True, blank=True, max_length=400, verbose_name=u"Profesion")
    institucionlabora = models.CharField(null=True, blank=True, max_length=400,
                                         verbose_name=u"Institucion donde labora")
    cargodesempena = models.CharField(null=True, blank=True, max_length=400, verbose_name=u"Cargo que desempeña")
    esparticular = models.BooleanField(default=True, verbose_name=u"Es Particular?")

    def __str__(self):
        return u'%s - %s - %s' % (self.carrera, self.profesion, self.cargodesempena)

    class Meta:
        verbose_name = u"Registro de datos de inscripcion"
        verbose_name_plural = u"Registros de datos de inscripciones"
        ordering = ['persona']

    def save(self, *args, **kwargs):
        if self.lugarestudio:
            self.lugarestudio = self.lugarestudio.upper()
        if self.carrera:
            self.carrera = self.carrera.upper()
        if self.profesion:
            self.profesion = self.profesion.upper()
        if self.institucionlabora:
            self.institucionlabora = self.institucionlabora.upper()
        if self.cargodesempena:
            self.cargodesempena = self.cargodesempena.upper()
        super(CapRegistrarDatosInscritoFormaEjecutiva, self).save(*args, **kwargs)


class CapModeloEvaluativoGeneralFormaEjecutiva(ModeloBase):
    modelo = models.ForeignKey(ModeloEvaluativoFormaEjecutiva, blank=True, null=True, verbose_name=u'Modelo Evaluativo',
                               on_delete=models.CASCADE)
    orden = models.IntegerField(default='0', verbose_name=u"Orden")

    class Meta:
        verbose_name = u"Modelo evaluativo general formacion ejecutiva"
        verbose_name_plural = u"Modelos evaluativos general formacion ejecutiva"
        ordering = ['modelo']

    def __str__(self):
        return u'%s - %s' % (self.orden, self.modelo)


class CapNotaFormaEjecutiva(ModeloBase):
    modelo = models.ForeignKey(ModeloEvaluativoFormaEjecutiva, blank=True, null=True, verbose_name=u'Modelo Evaluativo',
                               on_delete=models.CASCADE)
    fecha = models.DateField(blank=True, null=True, verbose_name=u'fecha')
    instructor = models.ForeignKey(InstructorFormaEjecutiva, blank=True, null=True, verbose_name=u'Instructor',
                                   on_delete=models.CASCADE)
    class Meta:
        verbose_name = u"Capacitacion Nota Formación Ejecutiva"
        verbose_name_plural = u"Capacitaciones Notas Formación Ejecutiva"
        ordering = ['instructor']

    def __str__(self):
        return u'%s - %s - %s' % (self.instructor.capeventoperiodo, self.modelo.nombre, self.instructor)

    def contar_calificados(self):
        return self.capdetallenotaformaejecutiva_set.values('id').filter(status=True, nota__isnull=False).count()

    def existen_calificados(self):
        return self.capdetallenotaformaejecutiva_set.values('id').filter(status=True, nota__isnull=False).exists()

    def extraer_detallenotaipec(self, inscrito):
        if self.capdetallenotaformaejecutiva_set.filter(status=True, inscrito=inscrito).exists():
            return self.capdetallenotaformaejecutiva_set.filter(status=True, inscrito=inscrito)[0]
        return None

    def save(self, *args, **kwargs):
        super(CapNotaFormaEjecutiva, self).save(*args, **kwargs)

class CapDetalleNotaFormaEjecutiva(ModeloBase):
    cabeceranota = models.ForeignKey(CapNotaFormaEjecutiva, blank=True, null=True, on_delete=models.CASCADE)
    inscrito = models.ForeignKey(CapaEventoInscritoFormaEjecutiva, blank=True, null=True, on_delete=models.CASCADE)
    nota = models.FloatField(blank=True, null=True, verbose_name=u'nota')
    observacion = models.CharField(max_length=200, default='', verbose_name=u'Nombre')

    def __str__(self):
        return u'%s %s' % (self.cabeceranota, self.inscrito)

    class Meta:
        verbose_name = u"Detalle de nota"
        verbose_name_plural = u"Detalles de notas"
        ordering = ['inscrito']

    def save(self, *args, **kwargs):
        super(CapDetalleNotaFormaEjecutiva, self).save(*args, **kwargs)


class ClaseFormaEjecutiva(ModeloBase):
    from sga.models import DIAS_CHOICES
    capeventoperiodo = models.ForeignKey(CapacitaEventoFormacionEjecutiva, verbose_name=u'Evento', on_delete=models.CASCADE)
    fechainicio = models.DateField(blank=True, null=True, verbose_name=u'Fecha Inicial')
    fechafin = models.DateField(blank=True, null=True, verbose_name=u'Fecha Fin')
    turno = models.ForeignKey(TurnoFormaEjecutiva, verbose_name=u'Turno', on_delete=models.CASCADE)
    dia = models.IntegerField(choices=DIAS_CHOICES, default=0, verbose_name=u'Dia')
    instructor = models.ForeignKey(InstructorFormaEjecutiva, blank=True, null=True, verbose_name=u'Evento',on_delete=models.CASCADE)

    def __str__(self):
        return u'%s - %s - [%s - %s]' % (
        self.get_dia_display(), self.turno, self.fechainicio.strftime('%d-%m-%Y'), self.fechafin.strftime('%d-%m-%Y'))

    class Meta:
        verbose_name = u"Clase de Evento Capacitación"
        verbose_name_plural = u"Clase de Evento Capacitación"
        ordering = ['id']

class AsistenciaFormaEjecutiva(ModeloBase):
    clase = models.ForeignKey(ClaseFormaEjecutiva, blank=True, null=True, on_delete=models.CASCADE)
    fecha = models.DateField(verbose_name=u'fecha')
    horaentrada = models.TimeField(verbose_name=u'Hora entrada')
    horasalida = models.TimeField(blank=True, null=True, verbose_name=u'Hora salida')
    contenido = models.TextField(default='', verbose_name=u'Tema y Subtema')
    observaciones = models.TextField(default='', verbose_name=u'Observaciones')

    def __str__(self):
        return u'%s %s' % (self.clase, self.fecha)

    class Meta:
        verbose_name = u"Asistencia de Evento Capacitación"
        verbose_name_plural = u"Asistencias de Evento Capacitación"
        ordering = ['id']

class DetalleAsistenciaFormaEjecutiva(ModeloBase):
    cabeceraasistencia = models.ForeignKey(AsistenciaFormaEjecutiva, blank=True, null=True, on_delete=models.CASCADE)
    inscrito = models.ForeignKey(CapaEventoInscritoFormaEjecutiva, blank=True, null=True, on_delete=models.CASCADE)
    asistio = models.BooleanField(default=False, verbose_name=u"Estado Asistencia")

    def __str__(self):
        return u'%s %s' % (self.cabeceraasistencia, self.inscrito)

    class Meta:
        verbose_name = u"Detalle Asistencia de Evento Capacitación"
        verbose_name_plural = u"Detalle Asistencias de Evento Capacitación"
        ordering = ['id']

TIPO_COMPROBANTE_EJEC = (
    (1,'DEPÓSITO'),
    (2,'TRANSFERENCIA'),
    (3,'PAGO EN LINEA')
)

class PagoFormacionEjecutiva(ModeloBase):
    inscripcionevento = models.ForeignKey(CapaEventoInscritoFormaEjecutiva,verbose_name=u'Inscripción Evento',on_delete=models.CASCADE)
    valor = models.DecimalField(verbose_name=u'Valor Pago',decimal_places=2, max_digits=30)
    observacion = models.TextField(verbose_name=u"Observación")
    banco = models.CharField(verbose_name=u"Banco", max_length=500)
    fpago = models.DateField(verbose_name=u"Fecha Pago")
    tipocomprobante = models.IntegerField(choices=TIPO_COMPROBANTE_EJEC,default=0)
    archivo = models.FileField(upload_to="formacionejecutiva/pagos/%Y/%m/%d",blank=True, null=True, verbose_name=u'Archivo')

    def __str__(self):
        return f"{self.observacion} - {self.valor} [{self.fpago}]"

    class Meta:
        verbose_name = u"Pago Formación Ejecutiva"
        verbose_name_plural = u"Pagos Formación Ejecutiva"
        ordering = ['id']



