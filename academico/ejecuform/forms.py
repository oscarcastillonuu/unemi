import datetime

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.utils.safestring import mark_safe

from ejecuform.models import PeriodoFormaEjecutiva, EventoFormaEjecutiva, EnfoqueFormaEjecutiva, \
    ModeloEvaluativoFormaEjecutiva, CapaEventoInscritoFormaEjecutiva, TIPO_COMPROBANTE_EJEC
from sagest.models import Partida, PartidaPrograma, Departamento, TIPO_RUBRO, IvaAplicado
from sga.forms import ExtFileField

from core.custom_forms import FormModeloBase

from django.forms.widgets import DateTimeInput, CheckboxInput, FileInput

from sga.models import MESES_CHOICES, AreaConocimientoTitulacion, ContextoCapacitacion, MODALIDAD_CAPACITACION, \
    TipoParticipacion, TipoCertificacion, TipoCapacitacion, Persona


def deshabilitar_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = True
    form.fields[campo].widget.attrs['disabled'] = True

def habilitar_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = False
    form.fields[campo].widget.attrs['disabled'] = False

def modolectura_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = True

class PeriodoFormaEjecutivaForm(FormModeloBase):
    nombre = forms.CharField(label=u'Nombre', max_length=500, required=True, widget=forms.TextInput(attrs={'col': '12', 'autocomplete': 'off'}))
    descripcion = forms.CharField(label=u"Descripción", required=True, widget=forms.Textarea(attrs={'col': '12','rows':2}))
    fechainicio = forms.DateField(label=u"Fecha Inicio",required=True, widget=DateTimeInput(attrs={'col':6}))
    fechafin = forms.DateField(label=u"Fecha Fin",required=True, widget=DateTimeInput(attrs={'col':6}))
    archivo = ExtFileField(label=u'Archivo', required=False, max_upload_size=20971520,
                                    help_text=u'Tamaño Maximo permitido 20Mb, en formato pdf, jpg, jpeg, png',
                                    ext_whitelist=(".pdf", ".jpg", ".jpeg", ".png"),
                                    widget=FileInput({'accept': 'application/pdf, image/jpeg, image/jpg, image/png'}))
    instructivo = ExtFileField(label=u'Instructivo', required=False, max_upload_size=20971520,
                                    help_text=u'Tamaño Maximo permitido 20Mb, en formato pdf, jpg, jpeg, png',
                                    ext_whitelist=(".pdf", ".jpg", ".jpeg", ".png"),
                                    widget=FileInput({'accept': 'application/pdf, image/jpeg, image/jpg, image/png'}))

    def editar(self):
        modolectura_campo(self,'fechainicio')
        modolectura_campo(self,'fechafin')

class EventoFormaEjecutivaForm(FormModeloBase):
    nombre = forms.CharField(label=u"Nombre", required=True, widget=forms.Textarea(attrs={'col': '12','rows':2}))

class EnfoqueFormaEjecutivaForm(FormModeloBase):
    nombre = forms.CharField(label=u"Nombre", required=True, widget=forms.Textarea(attrs={'col': '12','rows':2}))

class TurnoFormaEjecutivaForm(FormModeloBase):
    turno = forms.IntegerField(label=u"Turno", required=False, widget=forms.TextInput(attrs={'col': '6', 'decimal': '0', 'formwidth': '33%'}))
    horas = forms.IntegerField(label=u"Horas", required=False, initial=1, widget=forms.TextInput(attrs={'col': '6', 'decimal': '0', 'formwidth': '33%'}))
    horainicio = forms.TimeField(label=u"Hora Inicio",initial='08:00', required=True,widget=DateTimeInput(attrs={'col': '6'}))
    horafin = forms.TimeField(label=u'Hora Fin',initial='09:00', required=True,widget=DateTimeInput(attrs={'col': '6'}))

    def editar_horas(self):
        deshabilitar_campo(self,'horas')

    def editar(self):
        deshabilitar_campo(self,'turno')

class ModeloEvaluativoFormaEjecutivaForm(FormModeloBase):
    nombre = forms.CharField(label=u"Nombre", max_length=500, required=True,widget=forms.TextInput(attrs={'col': '12'}))
    notaminima = forms.FloatField(label=u"Nota Minima", initial="0.00", required=True,widget=forms.TextInput(attrs={'class': 'imp-numbermed-right','col':'6', 'decimal': '2'}))
    notamaxima = forms.FloatField(label=u"Nota Maxima", initial="0.00", required=True,widget=forms.TextInput(attrs={'class': 'imp-numbermed-right','col':'6', 'decimal': '2'}))
    principal = forms.BooleanField(initial=False, label=u'Principal?', required=False, widget=CheckboxInput(attrs={'col':'6'}))
    evaluacion = forms.BooleanField(initial=False, label=u'Es Evaluación?', required=False, widget=CheckboxInput(attrs={'col':'6'}))

class ConfiguracionFormaEjecutivaForm(FormModeloBase):
    minnota = forms.IntegerField(label=u"Minimo Calificación", required=True, widget=forms.TextInput(
        attrs={'class': 'imp-numbersmall','col':'6', 'decimal': '0', 'formwidth': '50%'}))
    minasistencia = forms.IntegerField(label=u"Minimo Asistencia", required=True, widget=forms.TextInput(
        attrs={'class': 'imp-numbersmall','col':'6', 'decimal': '0', 'formwidth': '50%'}))
    aprobado2 = forms.IntegerField(initial=0, required=False, label=u'Valida IPEC',
                                   widget=forms.TextInput(attrs={'select2search': 'true','col':'12'}))
    aprobado3 = forms.IntegerField(initial=0, required=False, label=u'Aprueba',
                                   widget=forms.TextInput(attrs={'select2search': 'true','col':'12'}))

    def editar(self, aprobador2, aprobador3):
        self.fields['aprobado2'].widget.attrs['descripcion'] = aprobador2[
            0].flexbox_repr_con_cargo() if aprobador2 else ""
        self.fields['aprobado2'].widget.attrs['value'] = aprobador2[0].id if aprobador2 else ""
        self.fields['aprobado3'].widget.attrs['descripcion'] = aprobador3[
            0].flexbox_repr_con_cargo() if aprobador3 else ""
        self.fields['aprobado3'].widget.attrs['value'] = aprobador3[0].id if aprobador3 else ""

class CapaEventoFormaEjecutivaForm(FormModeloBase):
    from sga.models import Aula
    periodo = forms.ModelChoiceField(label=u'Período', required=False,
                                     queryset=PeriodoFormaEjecutiva.objects.filter(status=True), widget=forms.Select())
    capevento = forms.ModelChoiceField(label=u'Evento', queryset=EventoFormaEjecutiva.objects.filter(status=True),
                                       required=True, widget=forms.Select())
    tipootrorubro = forms.IntegerField(initial=0, required=False, label=u'Tipo Rubro',
                                       widget=forms.TextInput(attrs={'select2search': 'true', 'formwidth': '100%'}))
    areaconocimiento = forms.ModelChoiceField(label=u"Área Conocimiento",
                                              queryset=AreaConocimientoTitulacion.objects.filter(status=True, tipo=1, vigente=True), required=True,
                                              widget=forms.Select(attrs={'class': 'imp-75'}))
    contextocapacitacion = forms.ModelChoiceField(label=u"Contexto de la Capacitación/Formación",
                                                  queryset=ContextoCapacitacion.objects.filter(status=True), required=False,
                                                  widget=forms.Select())
    responsable = forms.IntegerField(initial=0, required=False, label=u'Responsable',
                                     widget=forms.TextInput(attrs={'select2search': 'true'}))
    aula = forms.ModelChoiceField(label=u'Aula', required=True, queryset=Aula.objects.filter(status=True),
                                  widget=forms.Select(attrs={'formwidth': '100%'}))
    enfoque = forms.ModelChoiceField(label=u'Enfoque', required=True,
                                     queryset=EnfoqueFormaEjecutiva.objects.filter(status=True),
                                     widget=forms.Select(attrs={'formwidth': '100%'}))
    modalidad = forms.ChoiceField(label=u"Modalidad Capacitación", required=False, choices=MODALIDAD_CAPACITACION,
                                  widget=forms.Select(attrs={'class': 'imp-25', 'formwidth': '50%'}))
    tipoparticipacion = forms.ModelChoiceField(label=u"Tipo Aprobación", queryset=TipoParticipacion.objects.filter(status=True),
                                               required=False, widget=forms.Select(attrs={'formwidth': '50%'}))
    tipocertificacion = forms.ModelChoiceField(label=u"Tipo Certificación", queryset=TipoCertificacion.objects.filter(status=True),
                                               required=False, widget=forms.Select(attrs={'formwidth': '50%'}))
    tipocapacitacion = forms.ModelChoiceField(label=u"Programado Plan Institucional",
                                              queryset=TipoCapacitacion.objects.filter(status=True), required=False,
                                              widget=forms.Select(attrs={'formwidth': '50%'}))
    fechainicio = forms.DateField(label=u"Fecha Inicio",widget=DateTimeInput(attrs={'class': 'selectorfecha','col':'6'}))
    fechafin = forms.DateField(label=u"Fecha Fin", widget=DateTimeInput(attrs={'class': 'selectorfecha','col':'6'}))
    fechainiinscripcion = forms.DateField(label=u"Fecha Inicio Inscripción", required=False,widget=DateTimeInput(attrs={'class': 'selectorfecha','col':'6'}))
    fechafininscripcion = forms.DateField(label=u"Fecha Fin Inscripción", required=False,widget=DateTimeInput(attrs={'class': 'selectorfecha','col':'6'}))
    fechamaxpago = forms.DateField(label=u"Fecha Max Pago",widget=DateTimeInput(attrs={'class': 'selectorfecha', 'col':'6'}))
    fechacertificado = forms.CharField(label=u"Fecha certificado", required=False,widget=forms.TextInput(attrs={'col':'6'}))
    horas = forms.IntegerField(label=u"Horas Académica", required=True, widget=forms.TextInput(
        attrs={'class': 'imp-numbersmall', 'decimal': '0', 'formwidth': '50%','col':'6'}))
    cupo = forms.IntegerField(label=u"Cupo", required=True, widget=forms.TextInput(
        attrs={'class': 'imp-numbersmall', 'decimal': '0', 'formwidth': '50%','col':'6'}))
    minnota = forms.IntegerField(label=u"Mínimo Calificación", required=False, widget=forms.TextInput(
        attrs={'class': 'imp-numbersmall', 'decimal': '0', 'formwidth': '50%','col':'6'}))
    minasistencia = forms.IntegerField(label=u"Mínimo Asistencia", required=False, widget=forms.TextInput(
        attrs={'class': 'imp-numbersmall', 'decimal': '0', 'formwidth': '50%','col':'6'}))
    costo = forms.DecimalField(label=u'Costo Interno $', required=False,
                               widget=forms.TextInput(attrs={'class': 'imp-moneda', 'formwidth': '50%','col':'6'}))
    costoexterno = forms.DecimalField(label=u'Costo Externo $', required=False,
                                      widget=forms.TextInput(attrs={'class': 'imp-moneda', 'formwidth': '50%','col':'6'}))
    observacion = forms.CharField(label=u'Observación', widget=forms.Textarea(attrs={'rows': '5'}), required=True)
    objetivo = forms.CharField(label=u'Objetivo General', widget=forms.Textarea(attrs={'rows': '3'}), required=True)
    # contenido = forms.CharField(label=u'Contenido', widget=forms.Textarea(attrs={'rows': '7'}), required=True)
    contenido = forms.CharField(label=u'Contenido', widget=forms.Textarea(attrs={'rows': '3'}), required=True)
    aprobado2 = forms.CharField(label=u'Aprobador 2', widget=forms.TextInput(attrs={'class': 'imp-100'}),
                                required=False)
    aprobado3 = forms.CharField(label=u'Aprobador 3', widget=forms.TextInput(attrs={'class': 'imp-100'}),
                                required=False)
    rubroepunemi = forms.BooleanField(initial=False, label=u'Recauda Rubro Epunemi?', required=False)
    visualizar = forms.BooleanField(initial=True, label=u'Visualizar Evento', required=False)
    publicarinscripcion = forms.BooleanField(initial=True, label=u'Inscripción Online', required=False)
    envionotaemail = forms.BooleanField(initial=False, label=u'Envío de nota al email', required=False)
    modeloevaludativoindividual = forms.BooleanField(initial=False, label=u'Modelo Evaluativo Individual?',
                                                     required=False)
    mes=forms.ChoiceField(choices=MESES_CHOICES,label=u"Mes Seleccionado", required=False,widget=forms.Select(attrs={'class': 'imp-25', 'formwidth': '40%'}))
    # imagen = ExtFileField(label=u'Seleccione imagen logo aval', required=False,  help_text=u'Tamaño Maximo permitido 4Mb, en formato  jpg ,jpeg, png', ext_whitelist=(".jpg", ".jpeg", ".png"), max_upload_size=4194304)
    imagen = ExtFileField(label=mark_safe(
        u'<a href="javascript:;" class="btn btn-info tu" title="Ver imagen logo aval" id="view_imagen"><i class="fa fa-picture-o"></i></a>&nbsp;Seleccione imagen logo aval'),
        required=False, help_text=u'Tamaño Maximo permitido 4Mb, en formato  jpg ,jpeg, png',
        ext_whitelist=(".jpg", ".jpeg", ".png"), max_upload_size=4194304)
    banner = ExtFileField(label=mark_safe(
        u'<a href="javascript:;" class="btn btn-info tu" title="Ver banner" id="view_banner"><i class="fa fa-picture-o"></i></a>&nbsp;Seleccione banner'),
        required=False, help_text=u'Tamaño Maximo permitido 4Mb, en formato  jpg ,jpeg, png',
        ext_whitelist=(".jpg", ".jpeg", ".png"), max_upload_size=4194304)
    brochure = ExtFileField(label=u'Brochure', help_text=u'Tamaño Maximo permitido 4Mb, en formato pdf',
                           ext_whitelist=(".doc", ".docx", ".pdf", ".jpg", ".png"), max_upload_size=4194304,
                           required=False)

    def editar_grupo(self):
        deshabilitar_campo(self, 'periodo')
        deshabilitar_campo(self, 'aprobado2')
        deshabilitar_campo(self, 'aprobado3')

    def editar_responsable(self, responsable):
        self.fields['responsable'].widget.attrs['descripcion'] = responsable.flexbox_repr() if responsable else ""
        self.fields['responsable'].widget.attrs['value'] = responsable.id if responsable else ""

    def editar_rubro_deshabilitar(self):
        modolectura_campo(self, 'costo')
        modolectura_campo(self, 'costoexterno')

class CapaEventoInscritoFormaEjecutivaForm(FormModeloBase):
    participante = forms.ModelChoiceField(label=u"Participante", queryset=Persona.objects.select_related().filter(status=True).order_by('apellido1'), required=True, widget=forms.Select())

class CapaEventoInscritoFormaEjecutivaManualForm(FormModeloBase):
    from sga.models import Sexo
    cedula = forms.CharField(label=u"Cédula", max_length=10, required=True,
                             widget=forms.TextInput(attrs={'col':'6'}))
    nombres = forms.CharField(label=u'Nombres', max_length=100, required=True,
                              widget=forms.TextInput(attrs={'col':'6'}))
    apellido1 = forms.CharField(label=u"1er Apellido", max_length=50, required=True,
                                widget=forms.TextInput(attrs={'col':'6'}))
    apellido2 = forms.CharField(label=u"2do Apellido", max_length=50, required=True,
                                widget=forms.TextInput(attrs={'col':'6'}))
    email = forms.CharField(label=u"Correo electrónico", max_length=200, required=True,
                            widget=forms.TextInput(attrs={'col':'6'}))
    telefono = forms.CharField(label=u"Teléfono móvil", max_length=50, required=True,
                               widget=forms.TextInput(attrs={'col':'6'}))
    telefono_conv = forms.CharField(label=u"Teléfono fijo", max_length=50, required=True,
                                    widget=forms.TextInput(attrs={'col':'6'}))
    nacimiento = forms.DateField(label=u"Fecha nacimiento", required=True,widget=DateTimeInput(attrs={'class': 'selectorfecha','col':'6'}))
    sexo = forms.ModelChoiceField(label=u"Sexo", queryset=Sexo.objects.all(),
                                  widget=forms.Select(attrs={'col':'6'}))
    direccion = forms.CharField(label=u'Dirección', max_length=100, required=True,
                                widget=forms.TextInput(attrs={'col':'6'}))
    lugarestudio = forms.CharField(label=u'Lugar de estudio', max_length=300, required=False,
                                   widget=forms.TextInput(attrs={'col':'6'}))
    carrera = forms.CharField(label=u'Carrera', max_length=300, required=False,
                              widget=forms.TextInput(attrs={'col':'6'}))
    profesion = forms.CharField(label=u'Profesión', max_length=300, required=False,
                                widget=forms.TextInput(attrs={'col':'6'}))
    institucionlabora = forms.CharField(label=u'Institución donde labora', max_length=300, required=False,
                                        widget=forms.TextInput(attrs={'col':'6'}))
    cargodesempena = forms.CharField(label=u'Cargo que desempeña', max_length=300, required=False,
                                     widget=forms.TextInput(attrs={'col':'6'}))
    esparticular = forms.BooleanField(initial=True, label=u'Es particular?', required=False,
                                      widget=forms.CheckboxInput(attrs={'col':'6'}))

    def adicionar_instructor(self):
        del self.fields['lugarestudio']
        del self.fields['carrera']
        del self.fields['profesion']
        del self.fields['cargodesempena']
        del self.fields['esparticular']
        del self.fields['institucionlabora']

class InstructorFormaEjecutivaForm(FormModeloBase):
    instructor = forms.IntegerField(initial=0, required=False, label=u'Instructor', widget=forms.TextInput(attrs={'select2search': 'true', 'formwidth': '95%'}))
    nombrecurso = forms.CharField(label=u'Nombre curso moodle', max_length=500, widget=forms.TextInput(attrs={'class': 'imp-100'}), required=False)
    instructorprincipal = forms.BooleanField(initial=False, label=u'Principal?', required=False)

    def editar(self, capinstructor):
        self.fields['instructor'].widget.attrs['descripcion'] = capinstructor.instructor.flexbox_repr() if capinstructor.instructor else ""
        self.fields['instructor'].widget.attrs['value'] = capinstructor.instructor.id if capinstructor.instructor else ""

class TipoOtroRubroEjecutivaForm(FormModeloBase):
    nombre = forms.CharField(label=u'Nombre', max_length=250, required=True,
                             widget=forms.TextInput(attrs={'formwidth': '100%'}))
    partida = forms.ModelChoiceField(Partida.objects.filter(pk=100), initial=100, required=False, label=u'Item',
                                     widget=forms.Select(attrs={'formwidth': '100%'}))
    programa = forms.ModelChoiceField(PartidaPrograma.objects.filter(pk=8), initial=8, required=False,
                                      label=u'Programa', widget=forms.Select(attrs={'formwidth': '100%'}))
    unidad_organizacional = forms.ModelChoiceField(Departamento.objects.filter(pk=115), initial=115, required=False,
                                                   label=u'Unidad Or.',
                                                   widget=forms.Select(attrs={'formwidth': '100%'}))
    tipo = forms.ChoiceField(choices=TIPO_RUBRO, initial=8, required=False, label=u'Tipo Rubro',
                             widget=forms.Select(attrs={'formwidth': '100%'}))
    ivaaplicado = forms.ModelChoiceField(IvaAplicado.objects.filter(status=True), required=True, label=u'Iva Aplicado',
                                         widget=forms.Select(attrs={'formwidth': '50%','col':6}))
    valor = forms.DecimalField(label=u"Valor por defecto", required=True, initial="0.00",
                               widget=forms.TextInput(attrs={'class': 'imp-moneda', 'decimal': '2','col':6}))

    def addtiporubro(self):
        deshabilitar_campo(self,'partida')
        deshabilitar_campo(self,'programa')
        deshabilitar_campo(self,'unidad_organizacional')
        deshabilitar_campo(self,'tipo')
        deshabilitar_campo(self,'tipo')

class ObservacionInscritoEventoFormaEjecutivaForm(FormModeloBase):
    observacionmanual = forms.CharField(required=True, label=u'Observación', widget=forms.Textarea({'rows': '3'}))
    archivo = ExtFileField(label=u'Fichero', required=False, help_text=u'Tamaño Maximo permitido 10Mb, en formato pdf',
                           ext_whitelist=(".pdf",), max_upload_size=10485760)



class ModeloEvaluativoGeneralFormEjecutiva(FormModeloBase):
    orden = forms.IntegerField(initial=0, label=u"Orden", required=False,widget=forms.TextInput(attrs={'class': 'imp-number', 'decimal': '0'}))
    modelo = forms.ModelChoiceField(ModeloEvaluativoFormaEjecutiva.objects.filter(status=True).order_by('-id'),
                                    required=True,label=u'Modelo Evaluativo', widget=forms.Select())

class GenerarRubrosForm(FormModeloBase):
    cuota = forms.IntegerField(initial=0,label=u'# Cuota', required=True,widget=forms.TextInput(attrs={'class': 'imp-number', 'decimal': '0'}))

class PagoFormacionEjecutivaForm(FormModeloBase):
    # inscripcionevento = forms.ModelChoiceField(CapaEventoInscritoFormaEjecutiva.objects.filter(status=True).order_by('-id'), required=True, label=u"Inscrito", widget=forms.Select())
    observacion = forms.CharField(required=True, label=u'Observación', widget=forms.Textarea({'rows': '3'}))
    valor = forms.FloatField(label=u"Valor Pago", initial="0.00", required=True,widget=forms.TextInput(attrs={'class': 'imp-numbermed-right','col':'6', 'decimal': '2'}))
    fpago = forms.DateField(label=u"Fecha Pago",required=True, widget=DateTimeInput(attrs={'col':6}))
    banco = forms.CharField(required=True, label=u'Banco', widget=forms.TextInput())
    tipocomprobante = forms.ChoiceField(label=u"Tipo Pago", required=False, choices=TIPO_COMPROBANTE_EJEC,
                                  widget=forms.Select(attrs={'class': 'imp-25'}))
    archivo = ExtFileField(label=u'Documento', required=False, help_text=u'Tamaño Maximo permitido 10Mb, en formato pdf,png,jpg,jpeg',
                           ext_whitelist=(".pdf",".jpg",".png",".jpeg",), max_upload_size=10485760)

