from django.db import models
from sga.funciones import ModeloBase, remover_caracteres_especiales_unicode
from sagest.models import *
from django.utils import timezone
from django.db.models.aggregates import Count, Max
import calendar as c

from sga.models import DiasNoLaborable, DIAS_CHOICES, Turno, Paralelo, Nivel


class Perms(models.Model):
    class Meta:
        permissions = (
            ("puede_editar_contrato_posgrado", "Puede editar contrato de posgrado"),
        )


ESTADO_CONTRATO = (
    (0, u'PENDIENTE'),
    (1, u'APROBADO'),
    (2, u'EN PROCESO'),
    (3, u'SUSCRIBIR GERENTE'),
    (4, u'SUSCRIBIR BENEFICIARIO'),
    (5, u'FINALIZADO'),
    (6, u'RECHAZADO'),
    (7, u'ANULADO'),

)

PERFIL_CONTRATO = (
    (0, u'TUTOR'),
    (1, u'DOCENTE'),
    (2, u'COORDINADOR'),
)

TIPO_CAMPO = (
    (1, u'TEXTO'),
    (2, u'NUMERO'),
    (3, u'FECHA'),
    (4, u'HORA'),
    (5, u'COMBO'),
    (6, u'FUNCION')
)

ESTADO_CERTIFICACION = (
    (0, u'PENDIENTE'),
    (1, u'ELABORADO'),
    (2, u'APROBADO'),
    (3, u'RECHAZADO'),
)
TIPO_INFORME = (
    (0, u'MEMORANDO'),
    (1, u'ACTIVIDAD Y JORNADA'),
    (2, u'ACTA CONTROL'),
    (3, u'INFORME ACTIVIDAD'),
)

class ActividadesPerfil(ModeloBase):
    descripcion= models.TextField(default='',blank=True, null=True, verbose_name=u"Actividades Registrada")

    def __str__(self):
        return u'%s ' % self.descripcion

    def en_uso(self):
        return self.perfilpuestodip_set.exists()

    def bitcaroaactividad_uso(self):
        return self.bitacoraactividaddiaria_set.filter(status=True).exists()

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(ActividadesPerfil, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Actividad del Puesto'
        verbose_name_plural = u'Actividades del Puesto'
        ordering = ('descripcion',)

class PerfilPuestoDip(ModeloBase):
    nombre = models.CharField(max_length=1000, default='', verbose_name=u'Nombre')
    actividades  = models.ManyToManyField(ActividadesPerfil)
    def __str__(self):
        return u'%s' % (self.nombre)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(PerfilPuestoDip, self).save(*args, **kwargs)
    def actividadesperfil(self):
        return self.actividadescontratoperfil_set.filter(status=True).all().order_by('actividad_id').distinct('actividad_id')
    def en_uso(self):
        return self.plantillacontratodip_set.exists()

    class Meta:
        verbose_name = u"Perfil Puesto"
        verbose_name_plural = u"Perfiles de Puesto"


class CertificacionPresupuestariaDip(ModeloBase):
    valor = models.DecimalField(max_digits=30, decimal_places=2, default=0,
                                verbose_name=u"Valor total de certificación")
    fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha de certificación')
    descripcion = models.CharField(default='', max_length=1000, verbose_name=u"Descripcion")
    partida = models.CharField(default='', max_length=300, verbose_name=u"partida")
    archivo = models.FileField(upload_to='certificacionepunemi/%Y', verbose_name=u'Archivo')
    estado = models.IntegerField(default=0, choices=ESTADO_CERTIFICACION, verbose_name=u'Estado de Contrato')
    codigo = models.CharField(null=True, blank=True, max_length=25, verbose_name=u'Codigo certificacion presupuestaria')
    saldo = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Saldo total de certificación")

    def __str__(self):
        return u"%s - %s - %s (%s)" % (self.descripcion, self.valor,self.codigo, self.fecha)

    def esta_en_contrato(self):
        return self.contratodip_set.filter(status=True).exists()

    def detalles_certificacion(self):
        return self.detallecertificacionpresupuestariadip_set.filter(status=True)

    def tiene_detalles(self):
        return self.detalles_certificacion().exists()

    class Meta:
        verbose_name = u'Certificación'
        verbose_name_plural = u'Certificaciones'
        ordering = ('descripcion',)

    def get_str_codigo_fecha(self):
        return f"{self.codigo} - {self.fecha}"

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        self.codigo = self.codigo.upper()
        super(CertificacionPresupuestariaDip, self).save(*args, **kwargs)


class CampoContratoDip(ModeloBase):
    descripcion = models.CharField(default='', max_length=300, verbose_name=u"Descripcion")
    tipo = models.IntegerField(choices=TIPO_CAMPO, default=1, verbose_name=u"Tipo Campo")
    script = models.TextField(default='', verbose_name=u"Script")
    identificador = models.CharField(default='', max_length=300, verbose_name=u"Identificador")

    def __str__(self):
        return u"%s" % self.descripcion

    class Meta:
        verbose_name = u'Campo Contrato'
        verbose_name_plural = u'Campos Contratos'
        ordering = ('descripcion',)
        # unique_together = ('descripcion',)

    def en_uso(self):
        return self.campoplantillacontratodip_set.exists()

    def identifica(self):
        return '${CAMPO%s}'% self.identificador

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        self.identificador = self.identificador.upper()
        super(CampoContratoDip, self).save(*args, **kwargs)


class PlantillaContratoDip(ModeloBase):
    anio = models.IntegerField(default=0, verbose_name=u"Año")
    descripcion = models.CharField(default='', max_length=300, verbose_name=u"Descripcion")
    archivo = models.FileField(upload_to='contratoepunemi/plantilla/%Y', verbose_name=u'Archivo')
    vigente = models.BooleanField(default=False, verbose_name=u"Vigente")
    perfil = models.ForeignKey(PerfilPuestoDip,null=True, blank=True,on_delete=models.CASCADE, verbose_name=u"Perfil de contrato")

    def __str__(self):
        return u"%s" % self.descripcion

    class Meta:
        verbose_name = u'Tipo Contrato'
        verbose_name_plural = u'Tipos Contratos'
        ordering = ('anio', 'descripcion',)

    def download_link(self):
        return self.archivo.url

    def en_uso(self):
        return self.contratodip_set.filter(status=True).exists()

    def cantidad_campos(self):
        return self.campoplantillacontratodip_set.count()

    def color_configurado(self):
        label = 'label label-warning'
        if self.campoplantillacontratodip_set.exists():
            label = 'label label-succes'
        return label

    def configurado(self):
        texto = 'FALTA CONFIGURAR'
        if self.campoplantillacontratodip_set.exists():
            texto = 'CONFIGURADO'
        return texto

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(PlantillaContratoDip, self).save(*args, **kwargs)


class CampoPlantillaContratoDip(ModeloBase):
    contrato = models.ForeignKey(PlantillaContratoDip, verbose_name=u"Contrato",on_delete=models.CASCADE)
    campos = models.ForeignKey(CampoContratoDip, verbose_name=u"Campos",on_delete=models.CASCADE)

    def __str__(self):
        return u"%s - %s" % (self.contrato, self.campos)

    def combo(self):
        return self.campos.script.split(';')

    def funcion(self):
        lista = []
        resultquery = eval(self.campos.script)
        for listacampos in resultquery:
            lista.append(listacampos)
        return lista

    def extraer_datos(self, contratodip):
        genero = contratodip.persona.sexo.id
        campos = ContratoDipDetalle.objects.filter(contratodip=contratodip, campo=self)
        if campos:
            campo = campos[0].valor
            if campo != '':
                return campos[0].valor
        if self.campos.tipo == 5:
            datos = self.campos.script.split(";")
            if datos.__len__() == 2:
                return datos[genero - 1]
            else:
                return ''
        else:
            contrato = contratodip
            campo = ContratoDipDetalle.objects.filter(contratodip=contrato, campo=self).order_by('-id')
            if campo:
                return campo[0].valor
            else:
                return ''

    class Meta:
        verbose_name = u'Campo Seleccionado Contrato'
        verbose_name_plural = u'Campos Seleccionados Contratos'
        ordering = ('contrato', 'campos')
        # unique_together = ('contrato', 'campos')


FORMA_PAGO_CONTRATO = (
    (0, u'MENSUAL'),
    (1, u'FIN DE MÓDULO'),
)

class Departamento(ModeloBase):
    nombre = models.CharField(verbose_name=u'Nombre departameno', null=True, blank=True, max_length=300)
    responsable = models.ForeignKey('sga.Persona', related_name='+', blank=True, null=True, verbose_name=u'Responsable', on_delete=models.CASCADE)
    responsable_subrogante = models.ManyToManyField('sga.Persona', related_name='+', verbose_name=u'Responsable Subrogante')

    class Meta:
        verbose_name = u'Departamento posgrado'
        verbose_name_plural = u'Departamentos posgrado'
        ordering = ('-id','nombre')

    def __str__(self):
        return f"{self.nombre} - {self.responsable}"

    def en_uso(self):
        return self.gestion_set.values('id').filter(status=True).exists()


class Gestion(ModeloBase):
    departamento = models.ForeignKey(Departamento, verbose_name=u"Departamento posgrado", on_delete=models.CASCADE)
    gestion = models.CharField(max_length=300, verbose_name=u"Gestión o maestría")
    cargo = models.CharField(max_length=500, verbose_name=u"Cargo")
    responsable = models.ForeignKey('sga.Persona', related_name='+', blank=True, null=True, verbose_name=u'Responsable',on_delete=models.CASCADE)
    responsablesubrogante = models.ForeignKey('sga.Persona', related_name='+', blank=True, null=True,verbose_name=u'Responsable', on_delete=models.CASCADE)

    class Meta:
        verbose_name = u'Gestión posgrado'
        verbose_name_plural = u'Gestiones posgrado'
        ordering = ('-id', 'gestion')

    def __str__(self):
        return f"{self.cargo}-{self.gestion}({self.responsable})"

TIPO_GRUPO = (
    (0, u"-----------"),
    (1, u"ADMINISTRATIVO"),
    (2, u"PROFESOR"),
)
TIPO_PAGO = (
    (0, u"-----------"),
    (1, u"MENSUAL"),
    (2, u"MÓDULAR"),
)

class ContratoDip(ModeloBase):
    codigocontrato = models.CharField(default='', max_length=20, verbose_name=u"Código Contrato")
    plantilla = models.ForeignKey(PlantillaContratoDip,null=True, blank=True, verbose_name=u"Plantilla de Contrato",on_delete=models.CASCADE)
    invitacion = models.ForeignKey('postulaciondip.InscripcionInvitacion', blank=True, null=True, verbose_name=u'Invitación',on_delete=models.CASCADE)
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Persona',on_delete=models.CASCADE)
    descripcion = models.TextField(default='', null=True, blank=True, verbose_name=u'Descripción')
    materia = models.ForeignKey('sga.ProfesorMateria', verbose_name=u'Materia', blank=True, null=True,on_delete=models.CASCADE)
    nummeses = models.IntegerField(default=0, verbose_name=u"Num. Meses",blank=True, null=True)
    rmu = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"RMU")
    estado = models.IntegerField(default=0, choices=ESTADO_CONTRATO, verbose_name=u'Estado de Contrato')
    tipo = models.IntegerField(default=0, choices=PERFIL_CONTRATO, verbose_name=u'Tipo Contrato')
    tipogrupo = models.IntegerField(default=0, choices=TIPO_GRUPO, verbose_name=u'Tipo Grupo')
    tipopago = models.IntegerField(default=0, choices=TIPO_PAGO, verbose_name=u'Tipo Pago')
    fechainicio = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicio del contrato')
    fechafin = models.DateField(blank=True, null=True, verbose_name=u'Fecha fin del contrato')
    archivo = models.FileField(upload_to='contratosepunemi/contrato',blank=True, null=True, max_length=150, verbose_name=u'Archivo')
    certificacion = models.ForeignKey(CertificacionPresupuestariaDip, null=True, blank=True, verbose_name='Certificacion Presupuestaria',on_delete=models.CASCADE)
    iva = models.ForeignKey('sagest.IvaAplicado',null=True, verbose_name=u'IVA',on_delete=models.CASCADE)
    valoriva = models.DecimalField(default=0, max_digits=30, null=True,decimal_places=2, verbose_name=u'Valor IVA')
    valortotal = models.DecimalField(default=0, max_digits=30,null=True, decimal_places=2, verbose_name=u'Valor total')
    seccion = models.ForeignKey('sagest.SeccionDepartamento',on_delete=models.SET_NULL,null=True, blank=True, verbose_name=u"Seccion Departamento")
    gestion = models.ForeignKey(Gestion,on_delete=models.SET_NULL,null=True, blank=True, verbose_name=u"Gestion Departamento")
    cargo = models.ForeignKey(PerfilPuestoDip,on_delete=models.SET_NULL,null=True, blank=True, verbose_name=u"Cargo/Puesto")
    manual = models.BooleanField(verbose_name="Gestion manual",default=False)
    fechafinalizacion = models.DateField(blank=True, null=True, verbose_name=u'Fecha de Finalizacion')
    actividadesextra = models.ManyToManyField(ActividadesPerfil,verbose_name='Actividades Extra')
    carrera = models.ForeignKey("sga.Carrera", blank=True, null=True, verbose_name=u'Carrera', on_delete=models.CASCADE) #Se sustituyó por la tabla ContratoCarrera
    # bitacora = models.BooleanField(default=False,blank=True,null=True, verbose_name=u'Activa bitacora')
    fechaaplazo = models.DateField(blank=True,null=True, verbose_name='Fecha aplazado')
    validadorgp = models.ForeignKey('sga.Persona',related_name='validadorgp', blank=True, null=True, verbose_name=u'Persona',on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if self.descripcion:
            self.descripcion = self.descripcion.upper()
        if self.codigocontrato:
            self.codigocontrato = self.codigocontrato.upper()
        super(ContratoDip, self).save(*args, **kwargs)

    def titulo_contrato(self):
        return '#{} {} ${}'.format(self.pk, self.get_tipo_display(), self.rmu)

    def get_contratos_a_su_cargo(self):
        return ContratoDip.objects.filter(validadorgp = self.persona,fechainicio__lte=datetime.now() , fechafin__gte = datetime.now())

    def color_estado(self):
        estado = 'text-muted'
        if self.estado == 1 or self.estado == 3:
            estado = 'text-success'
        elif self.estado == 2:
            estado = 'text-warning'
        elif self.estado == 5:
            estado = 'text-info'
        elif self.estado >= 6:
            estado = 'text-danger'
        return estado

    def total_dias(self):
        return (self.fechafin-self.fechainicio).days

    def cuotas(self):
        return self.contratodipmetodopago_set.filter(status=True)

    def total_pagado(self):
        return self.contratodipmetodopago_set.filter(status=True, cancelado=True).aggregate(total=Sum('valorcuota')).get('total')

    def total_pendiente(self):
        return self.contratodipmetodopago_set.filter(status=True, cancelado=False).aggregate(total=Sum('valorcuota')).get('total')

    def __str__(self):
        return u'#%s %s - $ %s' % (self.codigocontrato, self.persona, self.rmu)

    def download_link(self):
        return self.archivo.url

    def secuencia_codigo(self):
        reg = MemoActividadPosgrado.objects.filter(status=True,secuenciamemo__anioejercicio__anioejercicio = datetime.now().year).aggregate(sec=Max('secuencia')+1)

        if reg['sec'] is None:
            secuencia = 1
        else:
            secuencia = reg['sec']
        return secuencia

    def secuencia_informe(self):
        reg = SolicitudPago.objects.values('id').filter(status=True,contrato=self)
        if not reg:
            secuencia = 1
        else:
            secuencia = len(reg)+1
        return secuencia
    def secuencia_inftecnico(self):
        reg = InformeTecnico.objects.filter(status=True,secuenciageneral__anioejercicio__anioejercicio = datetime.now().year).aggregate(sec=Max('secuencia')+1)
        if reg['sec'] is None:
            secuencia = 1
        else:
            secuencia = reg['sec']
        return secuencia
    def secuencia_actapago(self):
        reg = ActaPago.objects.filter(status=True,secuenciageneral__anioejercicio__anioejercicio = datetime.now().year).aggregate(sec=Max('secuencia')+1)
        if reg['sec'] is None:
            secuencia = 1
        else:
            secuencia = reg['sec']
        return secuencia

    def calfindesemana(self, dia, mes, anio):
        try:
            from sagest.models import BitacoraActividadDiaria
            if c.SATURDAY == c.weekday(int(anio), int(mes), int(dia)):
                return 'fin'
            elif c.SUNDAY == c.weekday(int(anio), int(mes), int(dia)):
                return 'fin'
            elif BitacoraActividadDiaria.objects.filter(status=True, fecha__day=int(dia), fecha__month=int(mes), fecha__year=int(anio), persona=self.persona).exists():
                return BitacoraActividadDiaria.objects.filter(status=True, fecha__day=int(dia), fecha__month=int(mes), fecha__year=int(anio), persona=self.persona)
            return None
        except Exception as ex:
            return 0
    def actividadescontrato(self):
        return self.actividadescontratoperfil_set.filter(status=True).all().distinct()

    def actividades_posgrado(self,f):
        from sagest.models import BitacoraActividadDiaria
        actividades = BitacoraActividadDiaria.objects.filter(status=True,persona=self.persona,fecha__date=f.date())
        if actividades:
            return True, actividades, f
        elif DiasNoLaborable.objects.values('id').filter(status=True,fecha=f.date(),motivo=1).exists():
            dias = DiasNoLaborable.objects.filter(status=True, fecha=f.date()).order_by('-id').first()
            return None, f'{dias.get_motivo_display()} - {dias.observaciones}'.upper(), f
        elif f.weekday() in [5, 6]:
            return None, 'FIN DE SEMANA', f
        return None, 'SIN ACTIVIDADES', f

    class Meta:
        verbose_name = u"Contrato Pagos"
        verbose_name_plural = u"Contratos de Pagos"

    def get_horario(self):
        return self.horarioplanificacioncontrato_set.filter(status=True)

    def get_turno_por_fecha(self, dia):
        return self.horarioplanificacioncontrato_set.filter(inicio__lte=dia, fin__gte=dia, dia=dia.weekday() + 1, status=True).first()

    def get_tiempo_dedicacion(self):
        if self.cargo:
            cargo = self.cargo.id
            if cargo == 101:
                return 40
            elif cargo == 100:
                return 20
            return 1000
        return 1000

    def get_requisitos_contratacion_cargados_ids(self):
        try:
            from postulaciondip.models import Requisito
            requisito_id =  ContratoRequisito.objects.filter(status=True,contratodip = self).values_list('requisito_id',flat=True)
            return Requisito.objects.filter(pk__in = requisito_id) if requisito_id else []
        except Exception as ex:
            pass

    def get_requisitos_contratacion_cargados(self):
        try:
            from postulaciondip.models import Requisito
            return  ContratoRequisito.objects.filter(status=True,contratodip = self)
        except Exception as ex:
            pass

    def get_requisitos_contratacion_pendientes_cargar(self):
        try:
            from postulaciondip.models import Requisito
            eRequisitos = None
            eContratacionConfiguracionRequisito = ContratacionConfiguracionRequisito.objects.filter(status=True,  activo=True)
            requisitos = eContratacionConfiguracionRequisito.first() if eContratacionConfiguracionRequisito.exists() else None
            requisitos_pendientes_ids =  requisitos.get_requisitos().exclude(requisito__in =self.get_requisitos_contratacion_cargados_ids()).values_list('requisito_id', flat=True)  if requisitos else None
            if requisitos_pendientes_ids:
                eRequisitos = Requisito.objects.filter(pk__in=requisitos_pendientes_ids)
            return eRequisitos
        except Exception as ex:
            pass

class ContratoCarrera(ModeloBase):
    contrato = models.ForeignKey(ContratoDip, blank=True, null=True, verbose_name=u'Contrato', on_delete=models.CASCADE)
    carrera = models.ForeignKey("sga.Carrera", blank=True, null=True, verbose_name=u'Carrera', on_delete=models.CASCADE)

    def __str__(self):
        return u'#%s %s - $ %s' % (self.contrato.codigocontrato, self.contrato.invitacion, self.carrera.nombre)

    class Meta:
        verbose_name = u"Contrato por carrera"
        verbose_name_plural = u"Contratos por carrera"
        ordering = ('-id',)

class ContratoAreaPrograma(ModeloBase):
    contrato = models.ForeignKey(ContratoDip, blank=True, null=True, verbose_name=u'Contrato', on_delete=models.CASCADE)
    departamento = models.ForeignKey("sagest.SeccionDepartamento", blank=True, null=True, verbose_name=u'Area o programa', on_delete=models.CASCADE)
    gestion = models.ForeignKey(Gestion, blank=True, null=True, verbose_name=u'Area o programa', on_delete=models.CASCADE)

    def __str__(self):
        return u'#%s - %s' % (self.contrato.codigocontrato, self.gestion.cargo)

    class Meta:
        verbose_name = u"Contrato area o programa"
        verbose_name_plural = u"Contratos area o programas"
        ordering = ('-id',)

class HistorialContratoDipCarreras(ModeloBase):
    contratocarrera = models.ForeignKey(ContratoCarrera, blank=True, null=True, verbose_name=u'Contrato', on_delete=models.CASCADE)
    carrera = models.ForeignKey("sga.Carrera", blank=True, null=True, verbose_name=u'Carrera', on_delete=models.CASCADE)

    def __str__(self):
        return u'#%s - (%s)' % (self.contratocarrera, self.carrera.nombre)

    class Meta:
        verbose_name = u"Historial contrato por carrera"
        verbose_name_plural = u"Historial contratos por carrera"
        ordering = ('-id',)


class ContratoDipDetalle(ModeloBase):
    contratodip = models.ForeignKey(ContratoDip, verbose_name=u"Cabecera de contrato",on_delete=models.CASCADE)
    campo = models.ForeignKey(CampoPlantillaContratoDip, verbose_name=u"Campo configurado",on_delete=models.CASCADE)
    valor = models.TextField(default='', verbose_name=u"Valor del Campo configurado")

    class Meta:
        verbose_name = u"Detalle del contrato"
        verbose_name_plural = u"Detalles de contratos"

class HistorialContratoDip(ModeloBase):
    contratodip = models.ForeignKey(ContratoDip, null=True, blank=True, verbose_name=u"Contrato Dip",on_delete=models.CASCADE)
    observacion = models.TextField(default='', null=True, blank=True, verbose_name=u'observación')
    estado = models.IntegerField(default=0, choices=ESTADO_CONTRATO, verbose_name=u'Estado de Contrato')
    persona = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Persona que realiza la acción',on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.upper()
        super(HistorialContratoDip, self).save(*args, **kwargs)

    def color_estado(self):
        estado = 'label-primary'
        if self.estado == 1 or self.estado == 3:
            estado = 'label-success'
        elif self.estado == 2:
            estado = 'label-warning'
        elif self.estado >= 6:
            estado = 'label-important'
        return estado

    class Meta:
        verbose_name = u"Historial del contrato"
        verbose_name_plural = u"Historiales del contrato"

TIPO_TRANSACCION = (
    (0, u'INGRESO'),
    (1, u'EGRESO'),
)

class DetalleCertificacionPresupuestariaDip(ModeloBase):
    certificado = models.ForeignKey(CertificacionPresupuestariaDip, null=True, blank=True, verbose_name=u"Certificacion Presupuestaria",on_delete=models.CASCADE)
    contratodip = models.ForeignKey(ContratoDip, null=True, blank=True, verbose_name=u"Contrato Dip",on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Valor")
    fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha de certificación')
    tipo = models.IntegerField(default=0, choices=TIPO_TRANSACCION, verbose_name=u'Tipo Transaccion')
    devengado = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Valor devengado")
    saldo = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Saldo")

    def __str__(self):
        return u"%s - %s -%s" % (self.valor, self.fecha.strftime(''), self.get_tipo_display())

    class Meta:
        verbose_name = u'DetalleCertificación'
        verbose_name_plural = u'DetalleCertificaciones'
        ordering = ('certificado',)

class ActividadesContratoPerfil(ModeloBase):
    contrato = models.ForeignKey(ContratoDip,on_delete=models.CASCADE,null =True,blank=True,verbose_name="Contratos")
    perfil = models.ForeignKey(PerfilPuestoDip,on_delete=models.CASCADE,null=True,blank=True,verbose_name="Cargo")
    actividad = models.ForeignKey(ActividadesPerfil,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Actividad')
    obligatoria = models.BooleanField(default=False,verbose_name='¿Es obligatoria?')

    def __str__(self):
        return 'El estado de la actividad %s es: %s'%(str(self.actividad),str(self.obligatoria))

    def actividades(self):
        if self.actividad.filter(status=True).exists():
            return self.actividad.filter(status=True)
        return None

    class Meta:
        verbose_name = u"Actividad Contrato Perfil"
        verbose_name_plural = u"Actividades Contratos Perfiles"
        ordering = ('id',)

#MODELOS PROCESO DE PAGOS

class ContratoDipMetodoPago(ModeloBase):
    contratodip = models.ForeignKey(ContratoDip, null=True, blank=True, verbose_name=u"Contrato",on_delete=models.CASCADE)
    numerocuota = models.IntegerField(verbose_name=u'Nùmero de Cuota', default=1)
    valorcuota = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Valor Cuota")
    cancelado = models.BooleanField(default=False, verbose_name=u"¿Cuota Cancelada?")
    fecha_pago = models.DateField(null=True, blank=True, verbose_name=u"Fecha de pago")

    class Meta:
        verbose_name = u"Contrato Mètodo Pago"
        verbose_name_plural = u"Contratos  MètodosPagos"

    def __str__(self):
        return u'Cuota: %s - valor: %s - Fecha: %s' % (self.numerocuota, self.valorcuota, self.fecha_pago)

    def tiene_solicitud(self):
        return self.solicitudpago_set.filter(status=True).exists()

    def solicitud_pago(self):
        return self.solicitudpago_set.filter(status=True).first()

class ClasificacionRequisitoPago(ModeloBase):
    descripcion = models.TextField(default='', verbose_name=u'Descripcion')

class RequisitoPagoDip(ModeloBase):
    nombre = models.CharField(max_length=1000, default='', verbose_name=u'Requisito')
    leyenda = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Mensaje Ayuda')
    archivo = models.FileField(upload_to='requisitopagodip', blank=True, null=True, verbose_name=u'Documento de Guía')
    clasificacion = models.ForeignKey(ClasificacionRequisitoPago,on_delete=models.SET_NULL, null=True, blank=True)

    def nombre_input(self):
        return remover_caracteres_especiales_unicode(self.nombre).lower().replace(' ', '_')

    def __str__(self):
        return u'%s' % (self.nombre)

    class Meta:
        verbose_name = u"Requisito Pagos"
        verbose_name_plural = u"Requisitos de Pagos"

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.leyenda = self.leyenda.upper()
        super(RequisitoPagoDip, self).save(*args, **kwargs)

class ProcesoPago(ModeloBase):
    version = models.IntegerField(default=1, verbose_name=u'Nro de versión')
    nombre = models.CharField(max_length=1000, default='', verbose_name=u'Nombre del proceso')
    descripcion = models.TextField(default='', null=True, blank=True, verbose_name=u'Descripción')
    mostrar = models.BooleanField(default=False, verbose_name=u'Mostrar/No mostrar')
    perfil = models.IntegerField(default=0, choices=PERFIL_CONTRATO, verbose_name=u'Tipo Contrato')

    def traer_pasos(self):
        return self.pasoprocesopago_set.filter(status=True).order_by('numeropaso')

    def __str__(self):
        return u'%s - %s' % (self.nombre, self.version)

    class Meta:
        verbose_name = u"Proceso Pagos"
        verbose_name_plural = u"Procesos de Pagos"

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip().upper()
        self.descripcion = self.descripcion.strip().upper()
        super(ProcesoPago, self).save(*args, **kwargs)

    def tiene_pasos(self):
        return self.pasoprocesopago_set.filter(status=True).exists()

ESTADOS_PAGO_SOLICITUD = (
    (0, u'PENDIENTE'),
    (3, u'PENDIENTE G.P'),
    (4, u'VALIDADO G.P.'),
    (5, u'DEVUELTO G.P.'),
    (6, u'POR LEGALIZAR JEFE INMEDIATO'),
    (7, u'LEGALIZADO JEFE INMEDIATO'),
    (8, u'PROCESO EN EJEUCION G.P.'),
    (1, u'VALIDADO'),
    (2, u'APROBADO'),
)

ESTADOS_PAGO_REQUISITO = (
    (0, u'PENDIENTE'),
    (1, u'VALIDADO JEFE INMEDIATO'),
    (2, u'APROBADO'),
    (3, u'EN PROCESO'),
    (4, u'FINALIZADA'),
    (5, u'RECHAZADO'),
    (6, u'ANULADO'),
    (7, u'ESPERA APROBACIÓN'),
    (8, u'ACTUALIZAR DOCUMENTO'),
)

#REVISION G.P.
#DEVUELTO G.P.
#POR LEGALIZAR JEFE INMEDIATO
#LEGALIZADO JEFE INMEDIATO
#PROCESO EN EJEUCION G.P.
#REVISIÓN VICERECTORADO
#REVISÓN RECTORADO
#APROBADO PARA EP.



class PasoProcesoPago(ModeloBase):
    pasoanterior = models.ForeignKey('self', blank=True, null=True, related_name='paso_anterior', verbose_name='Paso Anterior',on_delete=models.CASCADE)
    numeropaso = models.IntegerField(default=0, verbose_name=u'Número de paso')
    proceso = models.ForeignKey(ProcesoPago, verbose_name=u'Proceso de pago',on_delete=models.CASCADE)
    descripcion = models.TextField(default='', null=True, blank=True, verbose_name=u'Descripción')
    valida = models.ForeignKey('sagest.DenominacionPuesto', related_name='+', blank=True, null=True, verbose_name=u'Valida Documentación',on_delete=models.CASCADE)
    carga = models.ForeignKey('sagest.DenominacionPuesto', related_name='+', blank=True, null=True, verbose_name=u'Carga Documentación',on_delete=models.CASCADE)
    estadovalida = models.IntegerField(default=0, choices=ESTADOS_PAGO_SOLICITUD, verbose_name=u'Estados de validación')
    estadorechazado = models.IntegerField(default=0, choices=ESTADOS_PAGO_SOLICITUD, verbose_name=u'Estados de rechazado')
    finaliza = models.BooleanField(default=False, verbose_name=u'Fin del proceso')
    beneficiario = models.BooleanField(default=False, verbose_name=u'Paso aplica a docente?')
    genera_informe = models.BooleanField(default=False, verbose_name=u'Genera Informe')
    carga_archivo = models.BooleanField(default=False, verbose_name=u'Carga Archivo')
    valida_archivo = models.BooleanField(default=False, verbose_name=u'Valida Archivo')
    leyenda = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Mensaje Ayuda')
    tiempoalerta_carga = models.IntegerField(default=0, verbose_name=u'Tiempo de Alerta Carga')
    tiempoalerta_validacion = models.IntegerField(default=0, verbose_name=u'Tiempo de Alerta Validación')

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.strip().upper()
        super(PasoProcesoPago, self).save(*args, **kwargs)

    def color_estado_valida(self):
        label = 'label label-default'
        if self.estadovalida == 0:
            label = 'label label-default'
        elif self.estadovalida == 1:
            label = 'label label-green'
        elif self.estadovalida == 2:
            label = 'label label-info'
        elif self.estadovalida == 3:
            label = 'label label-success'
        elif self.estadovalida == 4:
            label = 'label label-important'
        elif self.estadovalida == 5:
            label = 'label label-important'
        elif self.estadovalida == 6:
            label = 'label label-warning'
        return label

    def color_estado_rechazado(self):
        label = 'label label-default'
        if self.estadorechazado == 0:
            label = 'label label-default'
        elif self.estadorechazado == 1:
            label = 'label label-green'
        elif self.estadorechazado == 2:
            label = 'label label-info'
        elif self.estadorechazado == 3:
            label = 'label label-success'
        elif self.estadorechazado == 4:
            label = 'label label-important'
        elif self.estadorechazado == 5:
            label = 'label label-important'
        elif self.estadorechazado == 6:
            label = 'label label-warning'
        return label

    def finaliza_str(self):
        return 'fa fa-check-circle text-success' if self.finaliza else 'fa fa-times-circle text-error'

    def beneficiario_str(self):
        return 'fa fa-check-circle text-success' if self.beneficiario else 'fa fa-times-circle text-error'

    def genera_informe_str(self):
        return 'fa fa-check-circle text-success' if self.genera_informe else 'fa fa-times-circle text-error'

    def carga_archivo_str(self):
        return 'fa fa-check-circle text-success' if self.carga_archivo else 'fa fa-times-circle text-error'

    def valida_archivo_str(self):
        return 'fa fa-check-circle text-success' if self.valida_archivo else 'fa fa-times-circle text-error'

    def requisitos(self):
        return self.requisitopasopago_set.filter(status=True).order_by('requisito__nombre')

    def __str__(self):
        return u'PASO: %s' % (self.numeropaso)

    class Meta:
        verbose_name = u"Paso de Proceso"
        verbose_name_plural = u"Pasos de Procesos"

class RequisitoPasoPago(ModeloBase):
    requisito = models.ForeignKey(RequisitoPagoDip, verbose_name=u'Requisito',on_delete=models.CASCADE)
    paso = models.ForeignKey(PasoProcesoPago, verbose_name=u'Paso',on_delete=models.CASCADE)

    def __str__(self):
        return u'%s - %s' % (self.requisito, self.paso.numeropaso)

    class Meta:
        verbose_name = u"Requisito Paso"
        verbose_name_plural = u"Requisitos Pasos"

class SolicitudPago(ModeloBase):
    contrato = models.ForeignKey(ContratoDip, blank=True, null=True, verbose_name=u'Contrato',on_delete=models.CASCADE)
    cuentabancaria = models.ForeignKey('sga.CuentaBancariaPersona', blank=True, null=True, verbose_name=u'Cuenta Bancaria',on_delete=models.CASCADE)
    materia = models.ForeignKey('sga.ProfesorMateria', verbose_name=u'Materia', blank=True, null=True,on_delete=models.CASCADE)  # borrar despues no olvidar
    cuotapago = models.ForeignKey(ContratoDipMetodoPago, blank=True, null=True, verbose_name=u'Cuota de pago',on_delete=models.CASCADE)
    estado = models.IntegerField(default=0, choices=ESTADOS_PAGO_SOLICITUD, verbose_name=u'Estado de solicitud')
    numero = models.IntegerField(default=0, verbose_name=u'Número de solicitud')
    valor_solicitado = models.DecimalField(default=0, max_digits=16, decimal_places=2, verbose_name='Valor Solicitado')
    total_pagado = models.DecimalField(default=0, max_digits=16, decimal_places=2, verbose_name='Valor Pagado')
    fechainicio = models.DateTimeField(verbose_name='Fecha inicio', null=True, blank=True)
    fechaifin = models.DateTimeField(verbose_name='Fecha fin', null=True, blank=True)

    def no_eliminar(self):
        return not self.requisitosolicitudpago_set.filter(status=True, estado__in=[1, 2, 3, 4, 5]).exists()

    def historial_pago(self):
        return self.historialprocesosolicitud_set.filter(status=True).order_by('-pk')

    def iniciales_personas(self):
        nombresinciales, nombre = '', self.contrato.persona.nombres.split()
        if len(nombre) > 1:
            nombresiniciales = '{}{}'.format(nombre[0][0], nombre[1][0])
        else:
            nombresiniciales = '{}'.format(nombre[0][0])
        inicialespersona = '{}{}{}'.format(nombresiniciales,self.contrato.persona.apellido1[0], self.contrato.persona.apellido2[0])
        return inicialespersona

    def cod_solicitud(self):
        return 'PAGOS-{}-{}-{}-{}'.format(self.fecha_creacion.month, self.fecha_creacion.year,
                                          self.iniciales_personas(), self.numero)

    def color_estado(self):
        label = 'text-muted'
        if self.estado == 0:
            label = 'text-muted'
        elif self.estado == 1:
            label = 'text-success'
        elif self.estado == 2:
            label = 'text-info'
        elif self.estado == 3:
            label = 'text-success'
        elif self.estado == 4:
            label = 'text-danger'
        elif self.estado == 5:
            label = 'text-danger'
        elif self.estado == 6:
            label = 'text-warning'
        return label

    def traer_pasos_solicitud(self):
        return self.requisitosolicitudpago_set.filter(status=True)

    def traer_pasos_aprobados(self):
        return self.requisitosolicitudpago_set.filter(status=True, estado=1)

    def paso_principal_validado(self):
        return self.traer_pasos_solicitud().first()

    def paso_actual(self):
        pasoactual = 1
        for paso in self.traer_pasos_solicitud():
            if paso.estado == 2 or paso.estado == 3 or paso.estado == 2:
                pasoactual = paso.paso.numeropaso
        return pasoactual

    def traer_paso_actual(self):
        pasoactual = None
        for paso in self.traer_pasos_solicitud():
            if paso.estado == 2 or paso.estado == 3 or paso.estado == 2 or paso.estado == 6 or paso.estado == 4:
                pasoactual = paso
        return pasoactual

    def total_pasos(self):
        return self.requisitosolicitudpago_set.filter(status=True).count()

    def pasos_pendientes(self):
        return self.requisitosolicitudpago_set.filter(status=True, estado=0).count()

    def pasos_aprobados(self):
        return self.requisitosolicitudpago_set.filter(status=True, estado=1).count()

    def pasos_enproceso(self):
        return self.requisitosolicitudpago_set.filter(status=True, estado=2).count()

    def pasos_rechazados(self):
        return self.requisitosolicitudpago_set.filter(status=True, estado=3).count()

    def calcular_progreso(self):
        try:
            porcentaje, totalpasos, totalaprobados = 0, self.total_pasos(), self.pasos_aprobados()
            if totalaprobados > 0:
                porcentaje = (totalaprobados / totalpasos) * 100
                return round(porcentaje, 2)
            else:
                return 0
        except Exception as ex:
            return 0

    def color_barra(self):
        color, porcentaje = 'bar', self.calcular_progreso()
        if porcentaje >= 80:
            color = 'bar-success'
        elif porcentaje < 80 and porcentaje > 50:
            color = 'bar-warning'
        else:
            color = 'bar'
        return color

    def traer_ultimo_historial(self):
        return HistorialProcesoSolicitud.objects.filter(status=True,requisito__solicitud=self,requisito__solicitud__contrato=self.contrato, requisito__requisito_id=14).order_by('-pk').first()

    def traer_puesto_contrato_persona(self):
        return 'DOCENTE'  # Aqui va el PerfilPuesto Posgrado

    def traer_file_firmado_colaborador(self):
        return HistorialProcesoSolicitud.objects.filter(status=True,estado=0,requisito__solicitud=self,requisito__solicitud__contrato=self.contrato,persona_ejecucion=self.contrato.persona,requisito__requisito_id=14).order_by('-id').first()

    def __str__(self):
        return u'%s - %s' % (self.contrato.persona, self.get_estado_display())

    class Meta:
        verbose_name = u"Solicitud de Pagos Posgrado"
        verbose_name_plural = u"Solicitud de Pagos Posgrado"
        ordering = ('-id',)

    def load_info_monthly(self):
        return SolicitudInformePago.objects.filter(status=True, solicitud=self).order_by('id')

class SolicitudInformePago(ModeloBase):
    solicitud = models.ForeignKey(SolicitudPago, verbose_name="Solicitud de pago", null=True, blank=True, on_delete=models.SET_NULL)
    informe = models.ForeignKey("inno.InformeMensualDocente", verbose_name="Informe mensual docente", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Solicitud pago de informe mensual docente'
        verbose_name_plural = 'Solicitud pagos de informes mensuales docentes'
        ordering = ['-id']

    def __str__(self):
        return f"{self.solicitud}-{self.informe}"

class HistorialObseracionSolicitudPago(ModeloBase):
    solicitud = models.ForeignKey(SolicitudPago, verbose_name="Solicitud de pago", null=True, blank=True,
                                  on_delete=models.SET_NULL)
    observacion = models.TextField(verbose_name='Observacion', null=True, blank=True)
    estado = models.IntegerField(default=0, choices=ESTADOS_PAGO_SOLICITUD, null=True, blank=True)
    persona = models.ForeignKey(Persona, verbose_name='Persona ejecuta accion', null=True, blank=True,
                                on_delete=models.SET_NULL)
    fecha = models.DateTimeField(verbose_name='Fecha', null=True, blank=True)

    class Meta:
        verbose_name = 'Historial observacion solicitud pago'
        verbose_name_plural = 'Historial observacion solicitud pago'
        ordering = ['-id']

    def __str__(self):
        return f'{self.observacion}({self.get_estado_display()}): {self.solicitud}'

class RequisitoSolicitudPago(ModeloBase):
    solicitud = models.ForeignKey(SolicitudPago, verbose_name=u'Paso',on_delete=models.CASCADE)
    requisito = models.ForeignKey(RequisitoPagoDip, verbose_name=u'Requisito',on_delete=models.CASCADE)
    estado = models.IntegerField(default=0, choices=ESTADOS_PAGO_REQUISITO, verbose_name=u'Estado de requisito')
    observacion = models.TextField(default='', verbose_name=u'Observacion del requisito')

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.strip().upper()
        super(RequisitoSolicitudPago, self).save(*args, **kwargs)

    def color_estado(self):
        label = 'text-muted'
        if self.estado == 0:
            label = 'text-muted'
        elif self.estado == 1:
            label = 'text-success'
        elif self.estado == 2:
            label = 'text-info'
        elif self.estado == 3:
            label = 'text-success'
        elif self.estado == 4:
            label = 'text-danger'
        elif self.estado == 5:
            label = 'text-danger'
        elif self.estado == 6:
            label = 'text-warning'
        return label

    def last_historial(self):
        return HistorialProcesoSolicitud.objects.filter(status=True, requisito=self).order_by('-id').first()
    def last_historial_persona(self,persona_ejecucion):
        return HistorialProcesoSolicitud.objects.filter(status=True, requisito=self,persona_ejecucion=persona_ejecucion).order_by('-id').first()

    def __str__(self):
        return u'%s - %s' % (self.solicitud, self.requisito)

    class Meta:
        verbose_name = u"Requisito Paso Pago"
        verbose_name_plural = u"Requisito Paso Pago"


ACCIONES_PASOS = (
    (0, u'INICIO'),
    (1, u'CARGAR ARCHIVOS'),
    (2, u'VALIDAR ARCHIVOS'),
    (3, u'FINALIZO'),
)

def bitacora_user_directory_path(instance, filename):
    # print(instance)
    fecha = datetime.now().date()
    return 'historialsolicitudpagoposgrado/{0}/{1}/{2}/{3}/{4}'.format(instance.persona_ejecucion.pk, fecha.year, fecha.month, fecha.day, filename)

class HistorialProcesoSolicitud(ModeloBase):
    estado = models.IntegerField(default=0, choices=ESTADOS_PAGO_REQUISITO, verbose_name=u'Estado de requisito')
    observacion = models.TextField(default='', verbose_name=u'Observacion del requisito')
    fecha_maxima = models.DateTimeField(blank=True, null=True, verbose_name='Fecha y Hora de Alerta')
    fecha_ejecucion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha y Hora de Ejecución')
    persona_ejecucion = models.ForeignKey('sga.Persona', blank=True, null=True, verbose_name=u'Persona Ejecución', related_name='+',on_delete=models.CASCADE)
    accion = models.IntegerField(default=0, choices=ACCIONES_PASOS, verbose_name=u'Acción de pasos')
    requisito = models.ForeignKey(RequisitoSolicitudPago, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Requisito solicitud pago')
    archivo = models.FileField(upload_to=bitacora_user_directory_path, verbose_name=u'Archivo Firmado',  null=True, blank=True)

    def __str__(self):
        return u'%s' % (self.observacion)

    class Meta:
        verbose_name = u"Historial Paso Pago"
        verbose_name_plural = u"Historial Paso Pago"
        ordering = ('-id',)

    def diasfaltantes_estado(self):
        fechaactual = datetime.now()
        if self.fecha_maxima and self.estado == 2:
            x = self.fecha_maxima.astimezone(timezone.get_current_timezone()).replace(tzinfo=None) - fechaactual
            if x.days >= 0:
                return 1
            elif x.days < 0:
                return 2
            else:
                return 0
        else:
            return 0

    def diasfaltantes_days(self):
        try:
            fechaactual = datetime.now()
            if self.estado in (4, 5):
                return '<b class="text-important">{}</b>'.format(self.get_estado_display())
            if self.estado == 2:
                fechaactual = datetime.now()
                tiempo = self.fecha_maxima.astimezone(timezone.get_current_timezone()).replace(
                    tzinfo=None) - fechaactual
                if tiempo.days >= 0:
                    return '<b class="text-info">{} <i class="fa fa-question-circle tr" title="Tiempo que falta"></i></b>'.format(str(tiempo).replace('day', 'dia').split('.')[0])
                else:
                    tiempofuera = fechaactual - self.fecha_maxima.astimezone(timezone.get_current_timezone()).replace(tzinfo=None)
                    return '<b class="text-error">{} <i class="fa fa-question-circle tr" title="Fuera de tiempo"></i></b>'.format(str(tiempofuera).replace('day', 'dia').split('.')[0])
            else:
                return False
        except Exception as ex:
            return '<i class="fa fa-question-circle tr" title="Sin Generar"></i>'

    def tiemporealizado(self):
        if self.fecha_creacion:
            fechapaso = self.fecha_creacion.astimezone(timezone.get_current_timezone()).replace(tzinfo=None)
            fechalimite = self.fecha_maxima.astimezone(timezone.get_current_timezone()).replace(tzinfo=None)
            if self.fecha_ejecucion:
                if self.accion == 0:
                    return '<label class="label label-success tr" title="Inicio">EJECUTADO</label>'
                fechanotificacion = self.fecha_ejecucion.astimezone(timezone.get_current_timezone()).replace(tzinfo=None)
                tiempo = fechanotificacion - fechapaso
                tiemporeal = fechalimite - fechanotificacion
                if tiempo <= tiemporeal:
                    try:
                        return '<b class="text-info">{} <i class="fa fa-question-circle tr" title="Generado dentro de este tiempo {}"></i></b>'.format(str(tiempo).replace('day', 'dia').split('.')[0], str(tiemporeal).replace('day', 'dia').split('.')[0])
                    except Exception as ex:
                        return '<b class="text-info">{} <i class="fa fa-question-circle tr" title="Generado dentro de este tiempo {}"></i></b>'.format(str(tiempo).replace('day', 'dia'), str(tiemporeal).replace('day', 'dia'))
                else:
                    try:
                        return '<b class="text-important">{} <i class="fa fa-question-circle tr" title="Retrazado, debio ser generado dentro de {}"></i></b>'.format(str(tiempo).replace('day', 'dia').split('.')[0], str(tiemporeal).replace('day', 'dia').split('.')[0])
                    except Exception as ex:
                        return '<b class="text-important">{} <i class="fa fa-question-circle tr" title="Retrazado, debio ser generado dentro de  {}"></i></b>'.format(str(tiempo).replace('day', 'dia'), str(tiemporeal).replace('day', 'dia'))
            else:
                return '<i class="fa fa-question-circle tr" title="En Proceso"></i>'
        else:
            return '<i class="fa fa-question-circle tr" title="Sin Generar"></i>'

    def save(self, *args, **kwargs):
        self.observacion = self.observacion.strip().upper()
        super(HistorialProcesoSolicitud, self).save(*args, **kwargs)

    def color_estado(self):
        label = 'text-muted'
        if self.estado == 0:
            label = 'text-muted'
        elif self.estado == 1:
            label = 'text-success'
        elif self.estado == 2:
            label = 'text-info'
        elif self.estado == 3:
            label = 'text-success'
        elif self.estado == 4:
            label = 'text-danger'
        elif self.estado == 5:
            label = 'text-danger'
        elif self.estado == 6:
            label = 'text-warning'
        return label

#-------- PENDIENTE DEFINICION

# class PasoSolicitudPagos(ModeloBase):
#     fecha = models.DateField(blank=True, null=True, verbose_name=u'Fecha')  # BORRAR DESPUES
#     solicitud = models.ForeignKey(SolicitudPago, verbose_name=u'Solicitud',on_delete=models.CASCADE)
#     paso = models.ForeignKey(PasoProcesoPago, verbose_name=u'Paso',on_delete=models.CASCADE)
#     observacion = models.TextField(default='', verbose_name=u'Observacion de Revisión')
#     estado = models.IntegerField(default=0, choices=ESTADOS_PAGO_DIP, verbose_name=u'Estado de paso')
#
#     def save(self, *args, **kwargs):
#         self.observacion = self.observacion.strip().upper()
#         super(PasoSolicitudPagos, self).save(*args, **kwargs)
#
#     def color_estado(self):
#         label = 'label label-default'
#         if self.estado == 0:
#             label = 'label label-default'
#         elif self.estado == 1:
#             label = 'label label-green'
#         elif self.estado == 2:
#             label = 'label label-info'
#         elif self.estado == 3:
#             label = 'label label-success'
#         elif self.estado == 4:
#             label = 'label label-important'
#         elif self.estado == 5:
#             label = 'label label-important'
#         elif self.estado == 6:
#             label = 'label label-warning'
#         return label
#
#     def siguiente_paso(self):
#         return self.paso.numeropaso + 1
#
#     def puede_continuar(self):
#         return (self.estado == 1 and not self.paso.finaliza)
#
#     def requisito_paso(self):
#         return self.requisitopasosolicitudpagos_set.filter(status=True).order_by('requisito__nombre')
#
#     def __str__(self):
#         return u'%s - %s' % (self.solicitud, self.paso.numeropaso)
#
#     class Meta:
#         verbose_name = u"Pasos Solicitud Pago"
#         verbose_name_plural = u"Pasos Solicitud Pago"

class SecuenciaMemoActividadPosgrado(ModeloBase):
    anioejercicio = models.ForeignKey('sagest.AnioEjercicio',verbose_name='Anio ejercicio',on_delete=models.CASCADE)
    tipo = models.ForeignKey(PlantillaContratoDip,verbose_name='Tipo',on_delete=models.CASCADE,null=True,blank=True)
    secuencia = models.CharField(verbose_name='Secuencia',max_length=300)

    def __str__(self):
        return u'%s-%s' % (self.secuencia,self.anioejercicio)

    def en_uso(self):
        return self.memoactividadposgrado_set.values('id').exists()
    class Meta:
        verbose_name = u"Secuencia Actividad Posgrado"
        verbose_name_plural = u"Secuencia Actividad Posgrado"
        ordering = ('id',)

class HistorialPagoMes(ModeloBase):
    contrato = models.ForeignKey(ContratoDip,on_delete=models.CASCADE,verbose_name='Contrato')
    cancelado = models.BooleanField(default=False, verbose_name=u"¿Pago mensual Cancelada?")
    fecha_pago = models.DateField(null=True, blank=True, verbose_name=u"Fecha de pago")

    def __str__(self):
        return 'Mes %s - profesional: %s - estado de pago %s' % (self.fecha_pago,self.contrato.persona, 'Pagado' if self.cancelado else 'Pendiente')
    class Meta:
        verbose_name = u"Pago Mes"
        verbose_name_plural = u"Pagos Mensuales"
        ordering = ('id',)

class MemoActividadPosgrado(ModeloBase):
    secuenciamemo = models.ForeignKey(SecuenciaMemoActividadPosgrado,verbose_name='Secuencia Memo', on_delete=models.CASCADE)
    contrato = models.ForeignKey(ContratoDip, verbose_name='Contrato', on_delete=models.CASCADE,null=True,blank=True)
    mes = models.IntegerField(verbose_name='Mes Generado',null=True,blank=True,choices=MESES_CHOICES)
    secuencia = models.IntegerField(default='000',verbose_name='Secuencia')
    archivo = models.FileField(upload_to='contratoepunemi/memo/', verbose_name=u'Archivo')
    archivofirmado = models.FileField(upload_to='contratoepunemi/memo/', verbose_name=u'Archivo', null=True, blank=True)
    codigoqr = models.BooleanField(default=False, verbose_name=u"Admitidos generado con código QR")
    historialpago = models.ForeignKey(HistorialPagoMes, verbose_name='Historial de pago mensual', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u'%s-%s' %(self.secuencia,self.secuenciamemo)

    def download_link(self):
        return self.archivo.url
    class Meta:
        verbose_name = u"Secuencia Memo Posgrado"
        verbose_name_plural = u"Secuencia Memo Posgrado"
        ordering = ('id',)

class InformeActividadJornada(ModeloBase):
    secuenciageneral = models.ForeignKey(SecuenciaMemoActividadPosgrado,verbose_name='Secuencia Informe Actividad', on_delete=models.CASCADE)
    contrato = models.ForeignKey(ContratoDip, verbose_name='Contrato', on_delete=models.CASCADE, null=True, blank=True)
    mes = models.IntegerField(verbose_name='Mes Generado', null=True, blank=True, choices=MESES_CHOICES)
    fechainicio= models.DateTimeField(verbose_name='Fecha inicio',null=True,blank=True)
    fechaifin= models.DateTimeField(verbose_name='Fecha inicio',null=True,blank=True)
    secuencia = models.TextField(default='000', verbose_name='Secuencia',null=True,blank=True)
    archivo = models.FileField(upload_to='contratoepunemi/informe/', verbose_name=u'Archivo')
    historialpago = models.ForeignKey(HistorialPagoMes, verbose_name='Historial de pago mensual', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u'%s-%s' % (self.secuencia, self.secuenciageneral)

    def download_link(self):
        return self.archivo.url

    class Meta:
        verbose_name = u"Secuencia Actividad Horario"
        verbose_name_plural = u"Secuencia Actividad Horario"
        ordering = ('id',)
class InformeTecnico(ModeloBase):
    secuenciageneral = models.ForeignKey(SecuenciaMemoActividadPosgrado,verbose_name='Secuencia Informe Tecnico', on_delete=models.CASCADE)
    contrato = models.ForeignKey(ContratoDip, verbose_name='Contrato', on_delete=models.CASCADE, null=True, blank=True)
    mes = models.IntegerField(verbose_name='Mes Generado', null=True, blank=True, choices=MESES_CHOICES)
    secuencia = models.IntegerField(default='000', verbose_name='Secuencia')
    archivo = models.FileField(upload_to='contratoepunemi/inftec/', verbose_name=u'Archivo')
    archivofirmado = models.FileField(upload_to='contratoepunemi/inftec/', verbose_name=u'Archivo', null=True, blank=True)
    codigoqr = models.BooleanField(default=False, verbose_name=u"Admitidos generado con código QR")
    historialpago = models.ForeignKey(HistorialPagoMes, verbose_name='Historial de pago mensual', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u'%s-%s' % (self.secuencia, self.secuenciageneral)

    def download_link(self):
        return self.archivo.url

    class Meta:
        ordering = ('id',)
        verbose_name = u"Informe Tecnico"
        verbose_name_plural = u"Informes Tecnicos"

class ActaPago(ModeloBase):
    secuenciageneral = models.ForeignKey(SecuenciaMemoActividadPosgrado,verbose_name='Secuencia Acta Pago', on_delete=models.CASCADE)
    contrato = models.ForeignKey(ContratoDip, verbose_name='Contrato', on_delete=models.CASCADE, null=True, blank=True)
    mes = models.IntegerField(verbose_name='Mes Generado', null=True, blank=True, choices=MESES_CHOICES)
    secuencia = models.IntegerField(default='000', verbose_name='Secuencia')
    archivo = models.FileField(upload_to='contratoepunemi/actapago/', verbose_name=u'Archivo')
    archivofirmado = models.FileField(upload_to='contratoepunemi/actapago/', verbose_name=u'Archivo', null=True, blank=True)
    codigoqr = models.BooleanField(default=False, verbose_name=u"Admitidos generado con código QR")
    historialpago = models.ForeignKey(HistorialPagoMes,verbose_name='Historial de pago mensual',blank=True,null=True,on_delete=models.CASCADE)

    def __str__(self):
        return u'%s-%s' % (self.secuencia, self.secuenciageneral)

    def download_link(self):
        return self.archivo.url

    class Meta:
        ordering = ('id',)
        verbose_name = u"Acta de Pago"
        verbose_name_plural = u"Actas de Pagos"

class PlantillaInformes(ModeloBase):
    nombre = models.CharField(verbose_name = 'Plantilla ',max_length=250)
    tipo = models.IntegerField(verbose_name='Tipo Informe',default=0,choices=TIPO_INFORME)
    archivo = models.FileField(upload_to='contratoepunemi/informes/',verbose_name=u'Archivo')
    vigente = models.BooleanField(verbose_name='Vigente', )
    anio = models.IntegerField(default=0, verbose_name=u"Año")

    def __str__(self):
        return '%s' % self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        super(PlantillaInformes,self).save(*args, **kwargs)
    class Meta:
        verbose_name = u"Plantilla Informe"
        verbose_name_plural = u"Plantilla Informe"
        ordering = ('id',)

class DocumentoContrato(ModeloBase):
    nombre = models.CharField(verbose_name=u'Nombre documento', max_length=500)
    codigo = models.CharField(verbose_name=u'Codigo documento', max_length=500)
    campo = models.ForeignKey(CampoContratoDip, verbose_name=u'Campo referencia documento',on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre} {self.codigo}'

    class Meta:
        verbose_name = u"Documento contrato"
        verbose_name_plural = u"Documentos de contrato"
        ordering = ('id',)

class GrupoRevisionPago(ModeloBase):
    nombre = models.CharField(verbose_name=u'Nombre de grupo', max_length=500, null=True,blank=True)
    persona = models.ForeignKey(Persona, verbose_name='Persona encargada de revision', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Grupo revision de pago'
        verbose_name_plural = 'Grupos revisiones de pagos'
        ordering = ['-id']

    def __str__(self):
        return f'{self.persona} - {self.nombre}'

    def laodgrouppayment(self):
        return self.gruporevisionpagocontrato_set.filter(status=True)

class GrupoRevisionPagoContrato(ModeloBase):
    gruporevision = models.ForeignKey(GrupoRevisionPago, verbose_name=u'Grupo revision', null=True, blank=True, on_delete=models.SET_NULL)
    personacontrato = models.ForeignKey(Persona, verbose_name=u'Persona contratado', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Grupo revision contrato'
        verbose_name_plural = 'Grupo revision contrato'
        ordering = ['-id']

    def __str__(self):
        return f'{self.gruporevision}: {self.personacontrato}'

class HorarioPlanificacionContrato(ModeloBase):
    dia = models.IntegerField(choices=DIAS_CHOICES, default=1, verbose_name=u'Día')
    turno = models.ManyToManyField(Turno, verbose_name=u"Turnos", blank=True)
    inicio = models.DateField(blank=True, null=True, verbose_name=u'Fecha inicial', db_index=True)
    fin = models.DateField(blank=True, null=True, verbose_name=u'Fecha final', db_index=True)
    contrato = models.ForeignKey(ContratoDip, blank=True, null=True, verbose_name=u'contrato', on_delete=models.SET_NULL)

    def __str__(self):
        return u'%s' % self.get_dia_display()

    class Meta:
        verbose_name = u"Horario planificacion contrato"
        verbose_name_plural = u"Horario planificacion contrato"
        ordering = ['id']

    def get_color_dia(self):
        if self.dia == 1:
            return ''
        elif self.dia == 2:
            return ''
        elif self.dia == 3:
            return ''
        elif self.dia == 4:
            return ''
        elif self.dia == 5:
            return ''
        elif self.dia == 6:
            return ''
        elif self.dia == 27:
            return ''


class RecursoPresupuestarioPosgrado(ModeloBase):
    descripcion= models.CharField(max_length=350, verbose_name=u"Descripción")


    def __str__(self):
        return self.descripcion

    def get_programas_maestrias(self):
        return self.cabecerarecursopresupuestarioposgrado_set.filter(status=True)

    def get_total_recurso(self):
        total = 0
        cabecerarecursopresupuestarioposgrado_id = self.cabecerarecursopresupuestarioposgrado_set.values_list('id',flat=True).filter(status=True)
        eItemRecursoPresupuestarioPosgrado_id = ItemRecursoPresupuestarioPosgrado.objects.values_list('pk',flat=True).filter(status=True,cabecerarecursopresupuestarioposgrado_id__in=cabecerarecursopresupuestarioposgrado_id)
        eDetalleRecursoPresupuestarioPosgrado = DetalleRecursoPresupuestarioPosgrado.objects.filter(status=True,itemrecursopresupuestarioposgrado_id__in = eItemRecursoPresupuestarioPosgrado_id )
        for detalle in eDetalleRecursoPresupuestarioPosgrado:
            total += detalle.calcular_total_a_certificar()
        return total

    class Meta:
        verbose_name = u' Recurso Presupuestario Posgrado'
        verbose_name_plural = u'  Recurso Presupuestario Posgrado'
        ordering = ('id',)

class CabeceraRecursoPresupuestarioPosgrado(ModeloBase):
    recursopresupuestarioPosgrado = models.ForeignKey(RecursoPresupuestarioPosgrado, on_delete=models.CASCADE,verbose_name=u'cabecerarecursopresupuestarioposgrado')
    malla = models.ForeignKey("sga.Malla", verbose_name=u'Malla', on_delete=models.CASCADE)
    periodo = models.ForeignKey("sga.Periodo", on_delete=models.CASCADE, verbose_name=u'Periodo')


    def __str__(self):
        return u"%s - %s" %(self.malla.carrera.nombre,self.get_periodo_anio_romano())

    def get_items(self):
        return self.itemrecursopresupuestarioposgrado_set.filter(status=True)

    def get_periodo_anio_romano(self):
        return f"{self.periodo.numero_cohorte_romano()} - {self.periodo.anio}"


    class Meta:
        verbose_name = u'Cabecera Recurso Presupuestario Posgrado'
        verbose_name_plural = u' Cabecera Recurso Presupuestario Posgrado'
        ordering = ('id',)


class ItemRecursoPresupuestarioPosgrado(ModeloBase):
    cabecerarecursopresupuestarioposgrado = models.ForeignKey(CabeceraRecursoPresupuestarioPosgrado, on_delete=models.CASCADE, verbose_name=u'cabecerarecursopresupuestarioposgrado')
    total_paralelos = models.IntegerField(default=0, verbose_name=u'Total paralelos')
    modulos_a_dictar = models.IntegerField(default=0, verbose_name=u'Módulos a dictar')


    def get_items(self):
        return self.detallerecursopresupuestarioposgrado_set.filter(status=True)

    class Meta:
        verbose_name = u'Item Recurso Presupuestario Posgrado'
        verbose_name_plural = u'Item Recurso Presupuestario Posgrado'
        ordering = ('id',)

    def __str__(self):
        return u"total paralelos: %s - modulos dictar: %s" % (self.total_paralelos,self.modulos_a_dictar)


class DetalleRecursoPresupuestarioPosgrado(ModeloBase):
    itemrecursopresupuestarioposgrado = models.ForeignKey(ItemRecursoPresupuestarioPosgrado, blank=True, null=True, on_delete=models.CASCADE, verbose_name=u'cabecerarecursopresupuestarioposgrado')
    desglosemoduloadictar = models.IntegerField(default=0, verbose_name=u'Desglose de los  módulos a dictar')
    horaspormodulo = models.IntegerField(default=0, verbose_name=u'Horas por módulo')
    valor_x_hora = models.ForeignKey("postulaciondip.ValorPorHoraInformeContratacion", verbose_name='valor por hora', on_delete=models.CASCADE)
    categoriadocente = models.ForeignKey("sga.TipoProfesor", on_delete=models.CASCADE, verbose_name=u'Tipo de Docente')


    class Meta:
        verbose_name = u'Detalle Recurso Presupuestario Posgrado'
        verbose_name_plural = u'Detalle Recurso Presupuestario Posgrado'
        ordering = ('id',)

    def __str__(self):
        return u"%s - %s - %s - %s" % (self.desglosemoduloadictar, self.horaspormodulo, self.valor_x_hora, self.categoriadocente)

    def calcular_total_horas(self):
        total = self.desglosemoduloadictar * self.horaspormodulo
        return total

    def calcular_total_a_certificar(self):
        if self.categoriadocente_id ==15 :# profesor autor
            total = (self.calcular_total_horas() * self.valor_x_hora.valor)
        else:
            total = (self.calcular_total_horas() * self.valor_x_hora.valor) * self.itemrecursopresupuestarioposgrado.total_paralelos
        return total

class ContratacionConfiguracionRequisito(ModeloBase):
    nombre = models.CharField(max_length=1000, default='', verbose_name=u'Nombre')
    activo = models.BooleanField(verbose_name="Activo", default=True)

    class Meta:
        verbose_name = u'Contratacion Configuracion Requisito'
        verbose_name_plural = u'Contratacion Configuracion Requisito'
        ordering = ('id',)

    def __str__(self):
        return u"%s" % (self.nombre)

    def get_activo_str(self):
        etiqueta = f"<span class='badge rounded-pill bg-success'>Activo</span>"  if self.activo else f"<span class='badge rounded-pill bg-danger'>no Activo</span>"
        return etiqueta

    def get_requisitos(self):
        return self.requisitocontratacionconfiguracionrequisito_set.filter(status=True)

class RequisitoContratacionConfiguracionRequisito(ModeloBase):
    contratacionconfiguracionrequisito = models.ForeignKey(ContratacionConfiguracionRequisito, verbose_name=u'contratacionconfiguracionrequisito', on_delete=models.CASCADE)
    requisito = models.ForeignKey("postulaciondip.Requisito",  verbose_name=u'Requisito', on_delete=models.CASCADE)
    opcional = models.BooleanField(default=False, verbose_name=u"opcional")

    class Meta:
        verbose_name = u'Requisito Contratacion Configuracion Requisito'
        verbose_name_plural = u'Requisito Contratacion Configuracion Requisito'
        ordering = ('id',)

    def __str__(self):
        return u"%s" % (self.requisito)

    def get_opcional_str(self):
        etiqueta = f"<span class='badge rounded-pill bg-success'>Si</span>"  if self.opcional else f"<span class='badge rounded-pill bg-danger'>No</span>"
        return etiqueta

class ContratoRequisito(ModeloBase):
    contratodip =  models.ForeignKey(ContratoDip,  verbose_name=u'contrato', on_delete=models.CASCADE)
    requisito = models.ForeignKey("postulaciondip.Requisito",  verbose_name=u'Requisito', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='contratosepunemi/requisitos', blank=True, null=True, max_length=700,verbose_name=u'Archivo')
    fecha_caducidad = models.DateTimeField(blank=True, null=True, verbose_name=u"Fecha caducidad documento")

    class Meta:
        verbose_name = u'Contrato Requisito'
        verbose_name_plural = u'Contrato Requisito'
        ordering = ('id',)

    def __str__(self):
        return u"%s" % (self.contratodip)


class GrupoRequisitoPago(ModeloBase):
    descripcion = models.TextField(default='', verbose_name=u"Grupo requisito pago")
    tipogrupo = models.IntegerField(default=0, choices=TIPO_GRUPO, verbose_name=u'Tipo Grupo')
    activo = models.BooleanField(default=False, verbose_name=u"activo")

    class Meta:
        verbose_name = u'Grupo Requisito Pago'
        verbose_name_plural = u'Grupo Requisito Pago'
        ordering = ('id',)

    def __str__(self):
        return u"%s" % (self.descripcion)

    def en_uso(self):
        return self.requisitopagogruporequisito_set.filter(status=True).exists()

    def get_requisitos(self):
        return self.requisitopagogruporequisito_set.filter(status=True).order_by('orden')


class RequisitoPagoGrupoRequisito(ModeloBase):
    gruporequisitopago = models.ForeignKey(GrupoRequisitoPago, verbose_name=u'Requisito', on_delete=models.CASCADE)
    requisitopagodip = models.ForeignKey(RequisitoPagoDip, verbose_name=u'Requisito', on_delete=models.CASCADE)
    orden = models.IntegerField(verbose_name=u"Orden" , default = 0)

    class Meta:
        verbose_name = u'Requisito Pago Grupo Requisito'
        verbose_name_plural = u'Requisito Pago Grupo Requisito'
        ordering = ('id',)

    def __str__(self):
        return u"%s" % (self.requisitopagodip)

class OrdenFirmaActaPago(ModeloBase):
    responsabilidadfirma =models.ForeignKey("postulaciondip.ResponsabilidadFirma",  verbose_name=u'responsabilidad firma', on_delete=models.CASCADE)
    orden = models.IntegerField(verbose_name=u"Orden")

    def __str__(self):
        return f"{self.responsabilidadfirma}"

    class Meta:
        verbose_name = u"Orden Firma acta pago"
        verbose_name_plural = u"Orden acta pago"
        ordering = ['-id']

ESTADO_ACTA_PAGO = (
    (1, 'PENDIENTE'),
    (2, 'POR LEGALIZAR'),
    (3, 'LEGALIZADA')
)
class ActaPagoPosgrado(ModeloBase):
    fechaemision = models.DateField(verbose_name=u"Fecha Emisión")
    objetivo = models.TextField(blank=True, null=True, verbose_name="Objeto")
    solicitadopor = models.ForeignKey("sga.persona", blank=True, null=True, verbose_name=u'Solicitado por', on_delete=models.CASCADE)
    estado = models.IntegerField(choices=ESTADO_ACTA_PAGO, default=1, verbose_name=u'estado acta pago')

    class Meta:
        verbose_name = u" configuracion acta pago"
        verbose_name_plural = u"configuracion acta pago"
        ordering = ['-id']

    def __str__(self):
        return u"%s" % self.solicitadopor

    def acta_firmado_por_todos(self):
        return True if self.get_cantidad_de_integrantes_que_han_firmado() == self.get_integrantes_firman().count() else False

    def acta_pago_pendiente(self):
        return True if self.estado == 1 else False

    def acta_pago_por_legalizar(self):
        return True if self.estado == 2 else False

    def acta_pago_legalizado(self):
        return True if self.estado == 3 else False

    def get_integrantes_firman(self):
        return self.actapagointegrantesfirma_set.filter(status=True).order_by("ordenfirmaactapago__orden")

    def get_cantidad_de_integrantes_que_han_firmado(self):
        return self.actapagointegrantesfirma_set.filter(status=True,firmo=True).count()

    def get_debe_firmar(self):
        eActaPagoIntegranteFirma  = self.get_integrantes_firman()
        for integrante in eActaPagoIntegranteFirma:
            if not integrante.firmo:
                return integrante
        return None

    def get_integrante(self, persona):
        integrante = self.get_integrantes_firman().filter(persona=persona, status=True).first()
        return integrante if integrante else None

    def actualizar_todos_los_integrantes_a_firmado_completo(self,request):
        try:
            for integrante in self.get_integrantes_firman():
                integrante.firmo =True
                integrante.save(request)
        except Exception as ex:
            pass

    def existen_informes_que_deba_firmar_el_integrante_aprobador(self,persona):
        try:
            return ActaPagoIntegrantesFirma.objects.filter(status = True,ordenfirmaactapago__responsabilidadfirma_id__in = [3,4],persona = persona).exists()
        except Exception as ex:
            return False

    def puede_firmar_integrante_segun_orden(self,persona):
        integrante_logeado = self.get_integrante(persona)
        debe_firmar = self.get_debe_firmar()
        if not debe_firmar:
            return False, f"No existen integrantes que tengan que firmar."
        if integrante_logeado:
            if not debe_firmar.firmo:
                if integrante_logeado.pk == self.get_debe_firmar().pk:
                    return True , 'Es su turno de firmar'
                else:
                    return False, f"El integrante que debe firmar es: {self.get_debe_firmar()}"
        else:
            return False, f"{persona}, No se encuentra configurado para firmar acta de pago"

    def guardar_historial_acta_pago(self,request,persona,observacion,archivo):
        try:
            eHistorialActaPago = HistorialActaPago(
                actapagoposgrado=self,
                persona = persona,
                observacion = observacion,
                archivo = archivo
            )
            eHistorialActaPago.save(request)
        except Exception as ex:
            pass

    def get_historial_acta_pago(self):
        return self.historialactapago_set.filter(status=True).order_by('id')

    def actualizar_estado_del_acta_pago(self,request):
        if self.estado == 1:  # pendientes
            self.estado = 2  # firmado pasa a por legalizar
            self.save(request)

        if self.informe_firmado_por_todos():
            self.estado = 3  # paso a legalizado
            self.save(request)

    def get_estado_acta_pago(self):
        display = f'{self.get_estado_display()}'
        if self.estado == 1:
            display = f'<span  title="Estado acta pago" style="font-size: 11px" class=" badge bg-light-warning text-dark-warning">{self.get_estado_display()}</span>'
        if self.estado == 2:
            display = f'<span  title="Estado acta pago" style="font-size: 11px" class=" badge bg-light-primary text-dark-primary">{self.get_estado_display()}</span>'
        if self.estado == 3:
            display = f'<span  title="Estado acta pago" style="font-size: 11px" class=" badge bg-light-success text-dark-success">{self.get_estado_display()}</span>'

        return display

    def archivo_acta_pago_url(self):
        if self.archivo():
            return self.archivo.url
        else:
            return "#"

    def get_persona_elabora(self):
        integrante = self.actapagointegrantesfirma_set.filter(status=True,ordenfirmaactapago__responsabilidadfirma_id = 1)
        return integrante.first().persona if integrante.exists() else None

    def get_persona_valida_experta(self):
        integrante = self.actapagointegrantesfirma_set.filter(status=True,ordenfirmaactapago__responsabilidadfirma_id = 2)
        return integrante.first().persona if integrante.exists() else None

    def get_persona_valida_aprueba(self):
        integrante = self.actapagointegrantesfirma_set.filter(status=True,ordenfirmaactapago__responsabilidadfirma_id=4)
        return integrante.first().persona if integrante.exists() else None

    def get_persona_aprueba_director(self):
        integrante = self.actapagointegrantesfirma_set.filter(status=True,ordenfirmaactapago__responsabilidadfirma_id = 3)
        return integrante.first().persona if integrante.exists() else None

    def persona_es_quien_firma_acta_pago_memo(self,pk):
        return True if self.actapagointegrantesfirma_set.filter(status=True,pk = pk,ordenfirmaactapago__responsabilidadfirma_id__in = [3,4]).exists() else False

    def get_str_copia_nombre(self,persona):
        str_nombre = ''
        if persona:
            abr = 'Sr.' if persona.sexo.id == 2 else 'Sra.'
            nombre = persona.nombre_titulos3y4()
            str_nombre =f'{abr} {nombre}'

        return f'{str_nombre}'

    def get_str_copia_cargo(self,persona):
        str_cargo = ''
        if persona:
            str_cargo = persona.cargo_persona().denominacionpuesto.descripcion
        return f'{str_cargo}'

    def get_nombre_copia_experta(self):
        if self.get_persona_valida_experta():
            return self.get_str_copia_nombre(self.get_persona_valida_experta()) if  self.get_str_copia_nombre(self.get_persona_valida_experta()) else ''
        else:
            return self.get_str_copia_nombre(self.get_persona_valida_aprueba()) if  self.get_str_copia_nombre(self.get_persona_valida_aprueba()) else ''

    def get_abreviaturas_copia_elabora_analista_validado_experta(self):
        persona_elabora = self.get_persona_elabora()
        persona_valida= self.get_persona_valida_experta() if self.get_persona_valida_experta() else self.get_persona_valida_aprueba()
        abreviaturanombreelabora = ''
        abreviaturanombrevalida = ''
        abreviaturas = ""

        if persona_elabora:
            persona_elabora = f"{persona_elabora.primerNombre()} {persona_elabora.apellido1}"
            for c in persona_elabora.split(' '):
                abreviaturanombreelabora += c[0] if c.__len__() else ''

        if persona_valida:
            persona_valida = f"{persona_valida.primerNombre()} {persona_valida.apellido1}"
            for c in persona_valida.split(' '):
                abreviaturanombrevalida += c[0] if c.__len__() else ''

        abreviaturas = f"{abreviaturanombreelabora}/{abreviaturanombrevalida}"
        return abreviaturas

    def get_abreviaturas_copia_elabora_analista(self):
        persona_elabora = self.get_persona_elabora()
        persona_valida= self.get_persona_valida_experta() if self.get_persona_valida_experta() else self.get_persona_valida_aprueba()
        abreviaturanombreelabora = ''
        abreviaturanombrevalida = ''
        abreviaturas = ""

        if persona_elabora:
            persona_elabora = f"{persona_elabora.primerNombre()} {persona_elabora.apellido1}"
            for c in persona_elabora.split(' '):
                abreviaturanombreelabora += c[0] if c.__len__() else ''

        abreviaturas = f"{abreviaturanombreelabora}"
        return abreviaturas

    def get_cargo_copia_experta(self):
        if self.get_persona_valida_experta():
            return self.get_str_copia_cargo(self.get_persona_valida_experta()) if self.get_str_copia_nombre(self.get_persona_valida_experta()) else ''
        else:
            return self.get_str_copia_cargo(self.get_persona_valida_aprueba()) if self.get_str_copia_cargo( self.get_persona_valida_aprueba()) else ''

    def get_nombre_copia_analista(self):
        return self.get_str_copia_nombre(self.get_persona_elabora()) if self.get_str_copia_nombre(self.get_persona_elabora()) else ''

    def get_cargo_copia_analista(self):
        return self.get_str_copia_cargo(self.get_persona_elabora()) if self.get_str_copia_cargo(self.get_persona_elabora()) else ''

class HistorialActaPago(ModeloBase):
    actapagoposgrado = models.ForeignKey(ActaPagoPosgrado, blank=True, null=True, verbose_name=u'Acta pago', on_delete=models.CASCADE)
    persona = models.ForeignKey("sga.persona", blank=True, null=True, verbose_name=u'Persona', on_delete=models.CASCADE)
    observacion = models.TextField(verbose_name=u"Observación", blank=True, null=True, default='')
    archivo = models.FileField(upload_to='actaPagoHistorial/', blank=True, null=True,verbose_name=u"Acta firmada",max_length=600)
    def __str__(self):
        return u'%s' % self.actapagoposgrado

    def archivo_url(self):
        return self.archivo.url if self.archivo else '#'
    class Meta:
        verbose_name = u"Historial acta pago"
        verbose_name_plural = u"Historial acta pago"
        ordering = ['id']


class DetalleActaPago(ModeloBase):
    actapagoposgrado = models.ForeignKey(ActaPagoPosgrado, verbose_name='acta pago', on_delete=models.CASCADE)
    solicitudpago = models.ForeignKey(SolicitudPago, verbose_name='solicitud pago', on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.solicitudpago

    class Meta:
        verbose_name = u"Detalle acta pago"
        verbose_name_plural = u"Detalle acta pago"
        ordering = ['-id']

class ActaPagoIntegrantesFirma(ModeloBase):
    actapagoposgrado =models.ForeignKey(ActaPagoPosgrado,  verbose_name=u'Acta pago', on_delete=models.CASCADE)
    ordenfirmaactapago =models.ForeignKey(OrdenFirmaActaPago,  verbose_name=u'Responsabilidad', on_delete=models.CASCADE)
    persona =models.ForeignKey("sga.persona",  verbose_name=u'Persona', on_delete=models.CASCADE, blank=True, null =True)
    firmo =  models.BooleanField(verbose_name=u"¿Firmo?", default=False)

    def __str__(self):
        return f"{self.persona}"

    def get_cargo_responsable_firma(self):
        cargo =None
        if self.persona:
            if not self.persona.cargo_persona():
                eContratoDip = ContratoDip.objects.filter(persona=self.persona, status=True, estado=2).order_by('-id')
                cargo = eContratoDip.first().cargo if eContratoDip.exists() else 'Analista de Posgrado 1'
            else:
                cargo = self.persona.cargo_persona().denominacionpuesto.descripcion
        return cargo

    class Meta:
        verbose_name = u"Acta Pago Integrantes Firma"
        verbose_name_plural = u"Acta Pago Integrantes Firma"
        ordering = ['-id']
