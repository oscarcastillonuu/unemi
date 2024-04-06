import os
import json
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
# from django.contrib.auth.models import ContentType
from django.contrib.contenttypes.fields import ContentType, GenericForeignKey
from django.db import models
from django.forms import model_to_dict
from PyPDF2 import PdfFileMerger
# from certi.funciones import unir_pdf
from sga.funciones import ModeloBase, remover_caracteres_especiales_unicode, notificacion2
from settings import SITE_STORAGE, JR_USEROUTPUT_FOLDER
from sga.funcionesxhtml2pdf import conviert_html_to_pdfsave_path
from sga.models import Reporte, Coordinacion, Carrera, Persona, LogReporteDescarga, Periodo, Inscripcion, Matricula, \
    PerfilUsuario, Notificacion, PerfilAccesoUsuario
from sagest.models import Departamento, DistributivoPersona, Rubro
from django.contrib.auth.models import Group
from posgrado.models import CohorteMaestria

class Perms(models.Model):
    class Meta:
        permissions = (
            ("puede_firmar_certificados", "Puede firmar certificados"),
            # ("puede_modificar_certificados", "Modificar certificados"),
            # ("puede_eliminar_certificados", "Eliminar certificados"),
            # ("puede_modificar_unidades_certificadoras", "Modificar unidades certificadoras"),
            # ("puede_eliminar_unidades_certificadoras", "Eliminar unidades certificadoras"),
            # ("puede_modificar_asistentes_certificadoras", "Modificar asistentes certificadoras"),
            # ("puede_eliminar_asistentes_certificadoras", "Eliminar asistentes certificadoras"),
        )
ROLES_TIPO_CATEGORIA = (
    ('1', 'Admisión'),
    ('2', 'Pregrado'),
    ('3', 'Posgrado'),
)

class CategoriaServicio(ModeloBase):
    nombre = models.CharField(default='', max_length=200, verbose_name=u'Nombre')
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u'Descripción')
    icono = models.TextField(default='', blank=True, null=True, verbose_name=u'Icono')
    roles = models.TextField(default='', max_length=50, blank=True, null=True, verbose_name=u'Roles')
    grupos = models.ManyToManyField(Group, verbose_name=u'Grupos', related_name='+')
    activo = models.BooleanField(default=True, verbose_name=u'Activo')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = u"Categoria"
        verbose_name_plural = u"Categorias"
        ordering = ['nombre']
        unique_together = ['nombre']

    def puede_eliminar(self):
        return not Servicio.objects.values("id").filter(categoria=self).exists()

    def get_displays_roles(self):
        listroles = []
        if self.roles:
            for rol in ROLES_TIPO_CATEGORIA:
                if rol[0] in self.roles:
                    listroles.append(rol)
        return listroles

    def displays_rol(self):
        cadena = ''
        if self.roles:
            c = 1
            for rol in ROLES_TIPO_CATEGORIA:
                if rol[0] in self.roles:
                    if c == len(self.roles.split(',')):
                        cadena += str(rol[1])
                        c += 1
                    else:
                        cadena += str(rol[1]) + ' - '
                        c += 1
        return cadena

    def es_admision(self):
        return True if '1' in self.roles else False

    def es_pregrado(self):
        return True if '2' in self.roles else False

    def es_posgrado(self):
        return True if '3' in self.roles else False

    def total_solicitudes(self):
        can = 0
        if self.id == 7:
            can = Solicitud.objects.filter(servicio__categoria=self).count()
        else:
            can = Solicitud.objects.filter(status=True, servicio__categoria=self).count()
        return can

    def total_solicitadas(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=1).count()

    def total_pendientes(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=3).count()

    def total_pagadas(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=4).count()

    def total_asignado(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=6).count()

    def total_reasignado(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=5).count()

    def total_rechazado(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=7).count()

    def total_vencidas(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=9).count()

    def total_entregados(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=2).count()

    def total_eliminados(self):
        return Solicitud.objects.filter(status=True, servicio__categoria=self, estado=8).count()

    def grupos_categoria(self):
        return self.grupos.all()

    def cantidades_gigantic(self):
        dicc = {}
        solicitudes = Solicitud.objects.filter(servicio__categoria=self).values_list('estado', flat=True).order_by('estado').distinct()
        for est in solicitudes:
            clave = dict(ESTADO_SOLICITUD)[est]
            valor = Solicitud.objects.filter(servicio__categoria=self, estado=est).distinct().count()
            dicc[clave] = valor
        return dicc

    def estados_activos(self):
        dicc = {}
        solicitudes = Solicitud.objects.filter(servicio__categoria=self).values_list('estado', flat=True).order_by('estado').distinct()
        for est in solicitudes:
            clave = dict(ESTADO_SOLICITUD)[est]
            valor = est
            dicc[clave] = valor
        return dicc

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip()
        self.descripcion = self.descripcion.strip()
        super(CategoriaServicio, self).save(*args, **kwargs)


PROCESO_SERVICIO = (
    (1, "Certificado Interno"),
    (2, "Certificado Externo"),
    (3, "Planes de estudios"),
    (4, "Copias certificadas"),
    (5, "Reimpresión de titulos"),
    (6, "Duplicados de carné"),
    (7, "Homologación"),
    (8, "Certificado Fisico"),
    (9, "Titulación Extraordinaria"),
    (10, "Certificados Rubrica"),
)


class Servicio(ModeloBase):
    orden = models.IntegerField(blank=True, null=True, default=0, verbose_name=u'Orden')
    nombre = models.CharField(default='', max_length=500, blank=True, null=True, verbose_name=u'Nombre')
    alias = models.CharField(default='', max_length=20, blank=True, null=True, verbose_name=u"Alias del servicio")
    categoria = models.ForeignKey(CategoriaServicio, on_delete=models.CASCADE, related_name='+', verbose_name=u'Categoria')
    tiporubro = models.ForeignKey('sagest.TipoOtroRubro', on_delete=models.CASCADE, blank=True, null=True, related_name='+', verbose_name=u'Tipo de Rubro')
    proceso = models.IntegerField(default=0, choices=PROCESO_SERVICIO, blank=True, null=True, verbose_name=u"Proceso")
    costo = models.DecimalField(max_digits=30, decimal_places=16, default=0, verbose_name=u'Costo')
    activo = models.BooleanField(default=True, verbose_name=u'Activo')

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre}) - ${Decimal(self.costo).quantize(Decimal('.01'))}"

    class Meta:
        verbose_name = u"Servicio"
        verbose_name_plural = u"Servicios"
        ordering = ['categoria', 'nombre']
        unique_together = ['categoria', 'nombre']

    def puede_eliminar(self):
        from certi.models import Certificado
        eSolicitudes = Solicitud.objects.values("id").filter(servicio=self)
        if eSolicitudes.exists():
            return False
        if self.es_certificado():
            return not Certificado.objects.values("id").filter(servicio=self).exists()
        return True

    def es_certificado(self):
        return self.proceso in [1, 2]

    def solicitudes(self):
        self.solicitud_set.all()

    def certificados_ofertados(self):
        from certi.models import Certificado
        lista_cer =[]
        certificados = Certificado.objects.filter(status=True, servicio=self)
        for certificado in certificados:
            co = certificado.codigo + ' - ' +  certificado.certificacion
            lista_cer.append(co)
        return  lista_cer

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip()
        self.alias = self.alias.strip()
        super(Servicio, self).save(*args, **kwargs)


ESTADO_SOLICITUD = (
    (1, u'Solicitado'),
    (2, u'Entregado'),
    (3, u'Pendiente'),
    (4, u'Pagado'),
    (5, u'Reasignado'),
    (6, u'Asignado'),
    (7, u'Rechazado'),
    (8, u'Eliminado'),
    (9, u'Vencido'),
    (10, u'Informe en proceso'),
    (11, u'Informe elaborado'),
    (12, u'Informe aprobado'),
    (13, u'Informe rechazado'),
    (14, u'Informe aceptado'),
    (15, u'Cronograma en proceso'),
    (16, u'Cronograma entregado'),
    (17, u'Informe revisado'),
    (18, u'Cronograma revisado'),
    (19, u'Cronograma elaborado'),
    (20, u'Cronograma aprobado'),
    (21, u'Cronograma rechazado'),
    (22, u'Pendiente de firmar'),
    (23, u'Borrador'),
    (24, u'Asignaturas revisadas'),
    (25, u'Asignaturas aceptadas'),
    (26, u'Homologación en proceso'),
    (27, u'Homologación ejecutada'),
)

ESTADO_SOLICITUD_COLOR = (
    (1, 'color: #3a87ad!important; font-weight: bold; font-size:12px'),
    (2, 'color: #198754!important; font-weight: bold; font-size:12px'),
    (3, 'color: #FE9900!important; font-weight: bold; font-size:12px'),
    (4, 'color: #0d6efd!important; font-weight: bold; font-size:12px'),
    (5, 'color: #6c757d!important; font-weight: bold; font-size:12px'),
    (6, 'color: #212529!important; font-weight: bold; font-size:12px'),
    (7, 'color: #dc3545!important; font-weight: bold; font-size:12px'),
    (8, 'color: #dc3545!important; font-weight: bold; font-size:12px'),
    (9, 'color: #dc3545!important; font-weight: bold; font-size:12px'),
    (10, 'color: #FE9900!important; font-weight: bold; font-size:12px'),
    (11, 'color: #000000!important; font-weight: bold; font-size:12px'),
    (12, 'color: #198754!important; font-weight: bold; font-size:12px'),
    (13, 'color: #dc3545!important; font-weight: bold; font-size:12px'),
    (14, 'color: #00BFFF!important; font-weight: bold; font-size:12px'),
    (15, 'color: #FE9900!important; font-weight: bold; font-size:12px'),
    (16, 'color: #00BFFF!important; font-weight: bold; font-size:12px'),
    (17, 'color: #FE9900!important; font-weight: bold; font-size:12px'),
    (18, 'color: #FE9900!important; font-weight: bold; font-size:12px'),
    (19, 'color: #000000!important; font-weight: bold; font-size:12px'),
    (20, 'color: #198754!important; font-weight: bold; font-size:12px'),
    (21, 'color: #dc3545!important; font-weight: bold; font-size:12px'),
    (22, 'color: #FE9900!important; font-weight: bold; font-size:12px'),
    (23, 'color: #282828!important; font-weight: bold; font-size:12px'),
    (24, 'color: #3a87ad!important; font-weight: bold; font-size:12px'),
    (25, 'color: #198754!important; font-weight: bold; font-size:12px'),
    (26, 'color: #FE9900!important; font-weight: bold; font-size:12px'),
    (27, 'color: #198754!important; font-weight: bold; font-size:12px'),
)

TIPO_DOCUMENTO = (
    (1, u'Ninguno'),
    (2, u'Documento físico'),
    (3, u'Documento con firma electrónica'),
)

def solicitud_user_directory_path(instance, filename):
    # print(instance)
    fecha = datetime.now().date()
    return 'secretaria/solicitud/{0}/{1}/{2}/{3}/{4}'.format(instance.perfil.persona.pk, fecha.year, fecha.month, fecha.day, filename)


class Solicitud(ModeloBase):
    codigo = models.CharField(default='', max_length=100, blank=True, null=True, verbose_name=u'Código', db_index=True)
    secuencia = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'Secuencia')
    prefix = models.CharField(blank=True, null=True, max_length=10, verbose_name=u'Prefijo del código')
    suffix = models.CharField(blank=True, null=True, max_length=10, verbose_name=u'Sufijo del código')
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='+', verbose_name=u'Perfil')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='+', verbose_name=u'Servicio')
    origen_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+', verbose_name=u'Modelo de origen', blank=True, null=True)
    origen_object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name=u'ID de origen')
    descripcion = models.TextField(default='', verbose_name=u'Descripción')
    parametros = models.JSONField(verbose_name=u'Parametros', null=True, blank=True)
    archivo_solicitud = models.FileField(upload_to=solicitud_user_directory_path, max_length=1000, blank=True, null=True, verbose_name=u'Archivo de solicitud')
    fecha = models.DateField(blank=True, null=True, verbose_name=u"Fecha")
    hora = models.TimeField(blank=True, null=True, verbose_name=u"Hora")
    estado = models.IntegerField(default=1, choices=ESTADO_SOLICITUD, verbose_name=u'Estado')
    responsable = models.ForeignKey(Persona, on_delete=models.CASCADE, blank=True, null=True, related_name='+', verbose_name=u'Responsable')
    destino_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+', verbose_name=u'Modelo de destino', blank=True, null=True)
    destino_object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name=u'ID de destino')
    archivo_respuesta = models.FileField(upload_to=solicitud_user_directory_path, max_length=1000, blank=True, null=True, verbose_name=u'Archivo de respuesta')
    cantidad = models.IntegerField(blank=True, null=True, default=0, verbose_name=u'Cantidad')
    valor_unitario = models.DecimalField(max_digits=30, decimal_places=16, default=0, verbose_name=u'Valor unitario')
    subtotal = models.DecimalField(max_digits=30, decimal_places=16, default=0, verbose_name=u'Subtotal')
    iva = models.DecimalField(max_digits=30, decimal_places=16, default=0, verbose_name=u'I.V.A')
    descuento = models.DecimalField(max_digits=30, decimal_places=16, default=0, verbose_name=u'Descuento')
    tiempo_cobro = models.IntegerField(default=72, blank=True, null=True, verbose_name=u"Tiempo de cobro solicitud")
    en_proceso = models.BooleanField(default=False, verbose_name=u'En proceso de atención')
    origen_content_object = GenericForeignKey('origen_content_type', 'origen_object_id')
    destino_content_object = GenericForeignKey('destino_content_type', 'destino_object_id')
    archivo_solicitud_fisica = models.FileField(upload_to=solicitud_user_directory_path, max_length=1000, blank=True, null=True, verbose_name=u'Archivo de solicitud de certificado físico')
    fecha_retiro = models.DateField(blank=True, null=True, verbose_name=u"Fecha de retiro de certificado físico")
    hora_retiro = models.TimeField(blank=True, null=True, verbose_name=u"Hora e retiro de certificado físico")
    lugar_retiro = models.TextField(default='', verbose_name=u'Lugar de retiro')
    notificado_fisico = models.BooleanField(default=False, verbose_name=u'Notifica certificados físicos')
    notificado_segundorubro = models.BooleanField(default=False, verbose_name=u'Notifica pago de segundo rubro')
    tipodocumento = models.IntegerField(default=1, choices=TIPO_DOCUMENTO, verbose_name=u'Tipo de documento')
    certificadofirmado = models.BooleanField(default=False, verbose_name=u'¿Se ha firmado el certificado?')
    respaldo = models.FileField(upload_to='respaldocertificado/%Y/%m/%d', blank=True, null=True, verbose_name=u'Respaldo de certificado')
    inscripcioncohorte = models.ForeignKey('posgrado.InscripcionCohorte', blank=True, null=True, verbose_name=u'Aspirante', on_delete=models.CASCADE)
    firmadoec = models.BooleanField(default=False, verbose_name=u'¿Se ha firmado con firma electrónica?')
    carrera_homologada = models.ForeignKey('sga.Carrera', blank=True, null=True, verbose_name=u'Carrera con la que se va a homologar', on_delete=models.CASCADE)
    visible = models.BooleanField(default=False, verbose_name=u'¿Mostrar notas de asignaturas?')

    def __str__(self):
        return f"{self.perfil.persona.__str__()} - {self.servicio.nombre} ({self.fecha.__str__()} {self.hora.__str__()})"

    def total(self):
        return Decimal(self.subtotal + self.iva + self.descuento).quantize(Decimal('.01'))

    def puede_eliminar(self):
        return (not self.en_proceso and (self.estado == 1 )) and not self.estado == 8

    def color_estado_display(self):
        return dict(ESTADO_SOLICITUD_COLOR)[self.estado]

    def generar_certificado(self):
        from secretaria.funciones import generar_certificado_digital
        eCertificado = self.origen_content_object
        parametros = self.parametros
        ids_persona = [x.id for x in Persona.objects.filter(pk__in=[self.perfil.persona_id])]
        parametros['dirigidos'] = json.dumps(ids_persona)
        parametros['no_persona_session'] = True
        parametros['app'] = 'sie'
        result, aData, mensaje = generar_certificado_digital(self.perfil.persona, eCertificado.reporte, self.perfil.persona.usuario, parametros, self)
        if not result:
            raise NameError(mensaje)

    def procesar_pago_certificado_digital(self, eRubro):
        from sga.models import Notificacion
        eSolicitud = self
        ePagos = eRubro.pago_set.filter(status=True)
        if eRubro.cancelado:
            eSolicitud.en_proceso = True
            eSolicitud.estado = 4
            eSolicitud.save()
            eSolicitud.crea_historial_pago(ePagos)
            self.generar_certificado()
        elif ePagos.values("id").exists():
            eSolicitud.en_proceso = True
            eSolicitud.estado = 3
            eSolicitud.save()
            fechas = list(ePagos.values_list('fecha')) if ePagos.values("id").exists() else []
            eSolicitud.crea_historial_pago(ePagos)
            eSolicitud.generar_notificacion(eSolicitud.perfil.persona)

    def procesar_pagos(self, eRubro):
        if self.servicio.proceso in (1, 2, 10):
            self.procesar_pago_certificado_digital(eRubro)

    def save(self, *args, **kwargs):
        super(Solicitud, self).save(*args, **kwargs)

    def crea_historial_pago(self, ePagos):
        from sga.models import Notificacion
        eSolicitud = self
        eSolicitud.proceso = True
        for pago in ePagos:
            pagoContentType = ContentType.objects.get_for_model(pago)
            eHistorialSolicitud = HistorialSolicitud(solicitud=eSolicitud,
                                                     observacion=f'Realizó un pago por el valor de: ',
                                                     fecha=datetime.now().date(),
                                                     hora=datetime.now().time(),
                                                     estado=eSolicitud.estado,
                                                     responsable_id=1,
                                                     destino_content_type=pagoContentType,
                                                     destino_object_id=pago.id)
            eHistorialSolicitud.save()

    def fecha_limite_pago(self):
        fecha_limite = datetime.combine(self.fecha, self.hora) + timedelta(hours=self.tiempo_cobro)
        return fecha_limite

    def anular_solicitud(self):
        self.estado = 8
        self.save()
        return self.estado

    def anular_solicitudes_vencidas(self):
        eSolicitudes = Solicitud.objects.filter(status=True, estado__in=(1,3))
        for eSolicitud in eSolicitudes:
            fecha_limite = eSolicitud.fecha_limite_pago()
            if fecha_limite <= datetime.today():
                solicitudVencida = eSolicitud
                ePersona = solicitudVencida.perfil.persona
                solicitudVencida.estado = 9
                solicitudVencida.en_proceso = False
                solicitudVencida.save()
                eRubro = Rubro.objects.get(persona= ePersona, solicitud=solicitudVencida)
                # if not eRubro.tiene_pagos():
                #     eRubro.status = False
                #     eRubro.save()
                #eRubro.delete()
                eHistorialSolicitud = HistorialSolicitud(solicitud=solicitudVencida,
                                                         observacion=f'Cambio de estado por solicitud vencida',
                                                         fecha=datetime.now().date(),
                                                         hora=datetime.now().time(),
                                                         estado=solicitudVencida.estado,
                                                         responsable=ePersona)
                eHistorialSolicitud.save()

                solicitudVencida.generar_notificacion(ePersona)



        eSolicitudes = Solicitud.objects.filter(status=True, estado=9)

        if eSolicitudes:
            for solicitudVencida in eSolicitudes:
                fecha_comparacion= solicitudVencida.fecha_limite_pago() + timedelta(days=1)
                ePersona = solicitudVencida.perfil.persona
                if fecha_comparacion.date() < datetime.today().date():
                    eRubro = Rubro.objects.get(persona= ePersona, solicitud=solicitudVencida)
                    if eRubro.tiene_pagos():
                        solicitudVencida.estado = 3
                        solicitudVencida.en_proceso = True
                        eRubro.save()
                    else:
                        eRubro.status = False
                        solicitudVencida.en_proceso = False
                        eRubro.save()

    def verificar_proceso(self, persona):
        if self.estado == 1 :
            self.en_proceso = True
            self.estado = 3
            self.save()
            eHistorialSolicitud = HistorialSolicitud(solicitud=self,
                                                             observacion=f'Cambio de estado por proceso de atención',
                                                             fecha=datetime.now().date(),
                                                             hora=datetime.now().time(),
                                                             estado=self.estado,
                                                             responsable=persona)
            eHistorialSolicitud.save()

    def generar_historial(self, responsable, observacion):

        eHistorialSolicitud = HistorialSolicitud(solicitud=self,
                                                 observacion=observacion,
                                                 fecha=datetime.now().date(),
                                                 hora=datetime.now().time(),
                                                 estado=self.estado,
                                                 responsable=responsable)
        eHistorialSolicitud.save()

    def verificar_fecha(self, fecha_verificacion):
        fecha_verificacion = fecha_verificacion
        fecha_comparacion = self.fecha_limite_pago().date() + timedelta(days=1)
        if fecha_verificacion.date() >= fecha_comparacion:
            if not self.en_proceso and self.estado == 9:
                #rubro = self.rubro_set.filter(solicitud=self)[0]
                rubro = Rubro.objects.get(solicitud=self)
                pago = rubro.pago_set.filter(status=True)
                if pago:
                    self.estado == 3
                    rubro.status = True
                    rubro.save()

    def generar_notificacion(self, ePersona):
        eSolicitud = self
        titulo = f'Cambio de estado de la solicitud código {eSolicitud.codigo}'
        cuerpo = f'Solicitud código {eSolicitud.codigo} se encuentra en estado {eSolicitud.get_estado_display()}'
        eNotificacion = Notificacion(titulo=titulo,
                                     cuerpo=cuerpo,
                                     destinatario=ePersona,
                                     perfil=eSolicitud.perfil,
                                     url='/alu_secretaria/mis_pedidos',
                                     prioridad=1,
                                     app_label='SIE',
                                     fecha_hora_visible=datetime.now() + timedelta(days=2),
                                     tipo=1,
                                     en_proceso=False,
                                     content_type=ContentType.objects.get_for_model(eSolicitud),
                                     object_id=eSolicitud.pk,
                                     )
        eNotificacion.save()

    def generar_notificacion_2(self, ePersona):
        eSolicitud = self
        titulo = f'Cambio de estado de la solicitud código {eSolicitud.codigo}'
        cuerpo = f'Solicitud código {eSolicitud.codigo} se encuentra en estado {eSolicitud.get_estado_display()}. Le recordamos que tiene 3 días más para efectuar el pago. De lo contrario, los rubros serán eliminados y la solicitud también y tendrá que repetir el proceso.'
        eNotificacion = Notificacion(titulo=titulo,
                                     cuerpo=cuerpo,
                                     destinatario=ePersona,
                                     perfil=eSolicitud.perfil,
                                     url='/alu_secretaria/mis_pedidos',
                                     prioridad=1,
                                     app_label='SIE',
                                     fecha_hora_visible=datetime.now() + timedelta(days=2),
                                     tipo=1,
                                     en_proceso=False,
                                     content_type=ContentType.objects.get_for_model(eSolicitud),
                                     object_id=eSolicitud.pk,
                                     )
        eNotificacion.save()


    def obtener_pagos(self):
        eRubro = Rubro.objects.get(solicitud= self)
        ePagos = eRubro.pago_set.filter(status= True)
        return ePagos

    def tiene_rubro_pagado(self):
        from sagest.models import Pago
        eRubro = Rubro.objects.filter(status=True, solicitud=self, cancelado=True).order_by('id').first()
        return True if Pago.objects.filter(status=True, rubro=eRubro).exists() else False

    def tiene_2do_rubro_pagado(self):
        from sagest.models import Pago
        eRubro = Rubro.objects.filter(status=True, solicitud=self, cancelado=True, tipo__id=3442).order_by('id').first()
        return True if Pago.objects.filter(status=True, rubro=eRubro).exists() else False

    def tiene_rubro_informe(self):
        return True if Rubro.objects.filter(status=True, solicitud=self, tipo__id=3401).exists() else False

    def tiene_rubro_ingreso(self):
        return True if Rubro.objects.filter(status=True, solicitud=self, tipo__id=3442).exists() else False

    def certificado_solicitado(self):
        from certi.models import Certificado
        certifi = Certificado.objects.get(pk=self.origen_object_id)
        return certifi

    def esta_siendo_atendido(self):
        return True if HistorialSolicitud.objects.filter(status=True, atendido=True, solicitud=self) else False

    def secretaria_encargada(self):
        histo = HistorialSolicitud.objects.filter(status=True, atendido=True, solicitud=self).order_by('-id').first()
        return histo.responsable

    def tiene_actividades_tituex(self):
        from posgrado.models import DetalleActividadCronogramaTitulacion
        return True if DetalleActividadCronogramaTitulacion.objects.filter(status=True, solicitud=self).exists() else False

    def download_descargado(self):
        return self.archivo_solicitud.url

    def lista_asignaturas(self):
        return SolicitudAsignatura.objects.filter(status=True, solicitud=self).order_by('id')

    def lista_asignaturas_nombres(self):
        asignaturas = SolicitudAsignatura.objects.filter(status=True, solicitud=self).order_by('id')
        nombres_asignaturas = ", ".join(asig.asignaturamalla.asignatura.nombre for asig in asignaturas)
        return f'{nombres_asignaturas}.'

    def lista_asignaturas_favorables(self):
        asignaturas = SolicitudAsignatura.objects.filter(status=True, solicitud=self, estado=2).order_by('id')
        nombres_asignaturas = ", ".join(asig.asignaturamalla.asignatura.nombre for asig in asignaturas)
        return f'{nombres_asignaturas}.'

    def lista_asignaturas_no_favorables(self):
        asignaturas = SolicitudAsignatura.objects.filter(status=True, solicitud=self, estado=3).order_by('id')
        nombres_asignaturas = ", ".join(asig.asignaturamalla.asignatura.nombre for asig in asignaturas)
        return f'{nombres_asignaturas}.'

    def notificar_escuela(self):
        if self.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN').values_list('carrera_id', flat=True):
            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN'
            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
            titulo = "REVISIÓN DE INFORME TÉCNICO DE PERTINENCIA"
            cuerpo = f'Se informa a {dir} que el coordinador del programa de {self.perfil.inscripcion.carrera} ha subido el informe técnico de pertinencia del maestrante {self.perfil.inscripcion.persona}. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(self.servicio.categoria.id) + '&ids=0&s=' + str(self.codigo), dir.pk, 1, 'sga', dir)
        elif self.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD').values_list('carrera_id', flat=True):
            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD'
            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
            titulo = "REVISIÓN DE INFORME TÉCNICO DE PERTINENCIA"
            cuerpo = f'Se informa a {dir} que el coordinador del programa de {self.perfil.inscripcion.carrera} ha subido el informe técnico de pertinencia del maestrante {self.perfil.inscripcion.persona}. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(self.servicio.categoria.id) + '&ids=0&s=' + str(self.codigo), dir.pk, 1, 'sga', dir)
        elif self.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO').values_list('carrera_id', flat=True):
            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO'
            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
            titulo = "REVISIÓN DE INFORME TÉCNICO DE PERTINENCIA"
            cuerpo = f'Se informa a {dir} que el coordinador del programa de {self.perfil.inscripcion.carrera} ha subido el informe técnico de pertinencia del maestrante {self.perfil.inscripcion.persona}. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(self.servicio.categoria.id) + '&ids=0&s=' + str(self.codigo), dir.pk, 1, 'sga', dir)
        return True

    def coordinador(self):
        coordinador = None
        if CohorteMaestria.objects.filter(status=True, maestriaadmision__carrera=self.perfil.inscripcion.carrera).exists():
            coordinador = CohorteMaestria.objects.filter(status=True, maestriaadmision__carrera=self.perfil.inscripcion.carrera).order_by('-id').first().coordinador
        return coordinador

    def solicitud_asignatura(self, eAsignatura):
        try:
            from sga.models import Malla, AsignaturaMalla
            soli = None

            if SolicitudAsignatura.objects.filter(status=True, solicitud=self, asignaturamalla__asignatura__id=eAsignatura.id).exists():
                soli = SolicitudAsignatura.objects.filter(status=True, solicitud=self, asignaturamalla__asignatura__id=eAsignatura.id).first()
            return soli
        except Exception as ex:
            pass

    def solicitud_asignatura_matches(self, eAsignaturaMalla):
        try:
            from sga.models import Inscripcion, InscripcionMalla, AsignaturaMalla, RecordAcademico
            reg = None
            inscrito = Inscripcion.objects.filter(status=True, carrera=self.perfil.inscripcion.carrera, persona=self.perfil.persona).first()
            malla = InscripcionMalla.objects.filter(status=True, inscripcion=inscrito).first().malla
            idch = AsignaturaMalla.objects.filter(status=True, malla=malla, nohomologa=False).values_list('asignatura__id', flat=True)

            inscritoa = Inscripcion.objects.filter(status=True, carrera=self.carrera_homologada, persona=self.perfil.persona).first()
            if eAsignaturaMalla.asignatura.id in idch:
                reg = AsignaturaMalla.objects.filter(status=True, malla=malla, nohomologa=False, asignatura__id=eAsignaturaMalla.asignatura.id).first()
            return reg
        except Exception as ex:
            pass

    def solicitud_asignatura_record(self, eAsignaturaMalla):
        try:
            from sga.models import Inscripcion, InscripcionMalla, AsignaturaMalla, RecordAcademico
            nota = 0

            inscrito = Inscripcion.objects.filter(status=True, carrera=self.perfil.inscripcion.carrera, persona=self.perfil.persona).first()
            malla = InscripcionMalla.objects.filter(status=True, inscripcion=inscrito).first().malla
            idch = AsignaturaMalla.objects.filter(status=True, malla=malla, nohomologa=False).values_list('asignatura__id', flat=True)

            inscritoa = Inscripcion.objects.filter(status=True, carrera=self.carrera_homologada, persona=self.perfil.persona).first()
            if eAsignaturaMalla.asignatura.id in idch:
                reg = RecordAcademico.objects.filter(status=True, inscripcion=inscritoa, asignaturamalla__asignatura=eAsignaturaMalla.asignatura).first()
                nota = reg.nota
            return nota
        except Exception as ex:
            pass

    class Meta:
        verbose_name = u"Solicitud"
        verbose_name_plural = u"Solicitudes"
        ordering = ['perfil', 'fecha', 'hora']
        indexes = [
            models.Index(fields=["origen_content_type", "origen_object_id"]),
            models.Index(fields=["destino_content_type", "destino_object_id"]),
        ]
        unique_together = ('codigo',)


class HistorialSolicitud(ModeloBase):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='+', verbose_name=u'Solicitud')
    observacion = models.TextField(default='', verbose_name=u'Observación')
    archivo = models.FileField(upload_to=solicitud_user_directory_path, blank=True, null=True, verbose_name=u'Archivo')
    fecha = models.DateField(blank=True, null=True, verbose_name=u"Fecha")
    hora = models.TimeField(blank=True, null=True, verbose_name=u"Hora")
    estado = models.IntegerField(default=1, choices=ESTADO_SOLICITUD, verbose_name=u'Estado')
    responsable = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='+', blank=True, null=True, verbose_name=u'Responsable')
    destino_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+', verbose_name=u'Modelo de destino', blank=True, null=True)
    destino_object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name=u'ID de destino')
    destino_content_object = GenericForeignKey('destino_content_type', 'destino_object_id')
    atendido = models.BooleanField(default=False, verbose_name=u'Verfica si la solicitud de certificado física esta siendo atendida')
    urldrive = models.CharField(default='', max_length=500, null=True, blank=True, verbose_name=u"Url Drive")
    tipodocumento = models.IntegerField(default=1, choices=TIPO_DOCUMENTO, verbose_name=u'Tipo de documento')

    def __str__(self):
        return f"{self.solicitud.__str__()} - {self.get_estado_display()})"

    def color_estado_display(self):
        return dict(ESTADO_SOLICITUD_COLOR)[self.estado]

    def save(self, *args, **kwargs):
        super(HistorialSolicitud, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Historial de Solicitud"
        verbose_name_plural = u"Historial de Solicitudes"
        ordering = ['solicitud', 'fecha', 'hora']
        indexes = [
            models.Index(fields=["destino_content_type", "destino_object_id"]),
        ]

ESTADO_ASIGNATURA = (
    (1, "En revisión"),
    (2, "Aplica"),
    (3, "No aplica"),
)

ESTADO_ASIGNATURA_COLOR = (
    (1, 'color: #FE9900!important; font-weight: bold; font-size:12px'),
    (2, 'color: #198754!important; font-weight: bold; font-size:12px'),
    (3, 'color: #dc3545!important; font-weight: bold; font-size:12px'),
)

class SolicitudAsignatura(ModeloBase):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='+', verbose_name=u'Solicitud')
    asignaturamalla = models.ForeignKey('sga.AsignaturaMalla', blank=True, null=True, verbose_name=u'Asignatura malla', on_delete=models.CASCADE)
    estado = models.IntegerField(default=1, choices=ESTADO_ASIGNATURA, blank=True, null=True, verbose_name=u"Tipo origen")
    nota = models.FloatField(default=0, blank=True, null=True, verbose_name=u'Nota de record')

    def __str__(self):
        return f"{self.solicitud.inscripcioncohorte} - {self.asignaturamalla} - {self.get_estado_display()})"

    def color_estado_display(self):
        return dict(ESTADO_ASIGNATURA_COLOR)[self.estado]

    class Meta:
        verbose_name = u"Detalle de asignatura homologadas"
        verbose_name_plural = u"Detalles de asignaturas homologadass"
        ordering = ['id']

TIPO_FORMATO_CERTIFICADO = (
    (1, "Fisico"),
    (2, "Personalizado"),
    (3, "Interno"),
    (4, "Externo"),
)

class FormatoCertificado(ModeloBase):
    certificacion = models.CharField(default='', max_length=350, verbose_name=u"Certificación")
    tipo_origen = models.IntegerField(default=1, choices=TIPO_FORMATO_CERTIFICADO, blank=True, null=True, verbose_name=u"Tipo origen")
    formato = models.FileField(upload_to='certis/formatos', max_length=500, blank=True, null=True, verbose_name=u'Formato de certificados')
    roles = models.TextField(default='', max_length=50, blank=True, null=True, verbose_name=u'Roles')

    def __str__(self):
        return f"{self.certificacion} - {self.get_tipo_origen_display()})"

    def download_evidencia(self):
        return self.formato.url

    def subido_por(self):
        from sga.models import Persona
        return Persona.objects.get(usuario=self.usuario_creacion.id)

    def displays_rol(self):
        cadena = ''
        if self.roles:
            c = 1
            for rol in ROLES_TIPO_CATEGORIA:
                if rol[0] in self.roles:
                    if c == len(self.roles.split(',')):
                        cadena += str(rol[1])
                        c += 1
                    else:
                        cadena += str(rol[1]) + ' - '
                        c += 1
        return cadena

    def save(self, *args, **kwargs):
        super(FormatoCertificado, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Formato de certificados"
        verbose_name_plural = u"Formatos de certificados"
        ordering = ['id']
