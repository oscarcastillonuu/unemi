import os
from datetime import datetime

from django.db.models import Max, Q
from becadocente.models import InformeFactibilidad, ResolucionComite
from sagest.models import DistributivoPersona
from sga.funciones import variable_valor, cuenta_email_disponible_para_envio, validarcedula
from sga.models import Persona, ProfesorDistributivoHoras, Periodo, CUENTAS_CORREOS, ProfesorDistributivoHoras, ResponsableCoordinacion
from sga.tasks import send_html_mail

# Formatos de xlsxwriter
titulo1 = {
    'align': 'center',
    'valign': 'vcenter',
    'bold': 1,
    'font_size': 14,
    'font_name': 'Times New Roman'
}

titulo2 = {
    'align': 'center',
    'valign': 'vcenter',
    'bold': 1,
    'font_size': 11,
    'font_name': 'Times New Roman'
}

titulo3 = {
    'align': 'center',
    'valign': 'vcenter',
    'bold': 1,
    'font_size': 9,
    'font_name': 'Times New Roman'
}

titulo1izq = {
    'align': 'left',
    'valign': 'vcenter',
    'bold': 1,
    'font_size': 14,
    'font_name': 'Times New Roman'
}

titulo2izq = {
    'align': 'left',
    'valign': 'vcenter',
    'bold': 1,
    'font_size': 11,
    'font_name': 'Times New Roman'
}

titulo3izq = {
    'align': 'left',
    'valign': 'vcenter',
    'bold': 1,
    'font_size': 9,
    'font_name': 'Times New Roman'
}

cabeceracolumna = {
    'bold': 1,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': 'silver',
    'text_wrap': 1,
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdageneral = {
    'valign': 'vcenter',
    'text_wrap': 1,
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdageneralneg = {
    'valign': 'vcenter',
    'bold': 1,
    'text_wrap': 1,
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdageneralcent = {
    'align': 'center',
    'valign': 'vcenter',
    'text_wrap': 1,
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdafecha = {
    'num_format': 'yyyy-mm-dd',
    'align': 'center',
    'valign': 'vcenter',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdafechaDMA = {
    'num_format': 'dd-mm-yyyy',
    'align': 'center',
    'valign': 'vcenter',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdamoneda = {
    'num_format': '$ #,##0.00',
    'align': 'right',
    'valign': 'vcenter',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdanumerodecimal = {
    'num_format': '#,##0.00',
    'align': 'right',
    'valign': 'vcenter',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdanumerodecimal4dec = {
    'num_format': '#,##0.0000',
    'align': 'right',
    'valign': 'vcenter',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdaporcentaje = {
    'num_format': '0.00%',
    'align': 'right',
    'valign': 'vcenter',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

textonegrita = {
    'bold': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

formatomoneda = {
    'num_format': '$ #,##0.00',
    'align': 'right',
    'font_size': 8,
    'font_name': 'Verdana'
}

celdanegritacent = {
    'bold': 1,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': 'silver',
    'text_wrap': 1,
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdanegritaizq = {
    'bold': 1,
    'align': 'left',
    'valign': 'vcenter',
    'bg_color': 'silver',
    'text_wrap': 1,
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdanegritageneral = {
    'bold': 1,
    'valign': 'vcenter',
    'bg_color': 'silver',
    'text_wrap': 1,
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdamonedapie = {
    'bold': 1,
    'num_format': '$ #,##0.00',
    'align': 'right',
    'valign': 'vcenter',
    'bg_color': 'silver',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdanumerodecimal4decpie = {
    'bold': 1,
    'num_format': '#,##0.0000',
    'align': 'right',
    'valign': 'vcenter',
    'bg_color': 'silver',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

celdaporcentajepie = {
    'bold': 1,
    'num_format': '0.00%',
    'align': 'right',
    'valign': 'vcenter',
    'bg_color': 'silver',
    'border': 1,
    'font_size': 8,
    'font_name': 'Verdana'
}

FORMATOS_CELDAS_EXCEL = {
    "titulo1": titulo1,
    "titulo2": titulo2,
    "titulo3": titulo3,
    "titulo1izq": titulo1izq,
    "titulo2izq": titulo2izq,
    "titulo3izq": titulo3izq,
    "cabeceracolumna": cabeceracolumna,
    "celdageneral": celdageneral,
    "celdageneralneg": celdageneralneg,
    "celdageneralcent": celdageneralcent,
    "celdafecha": celdafecha,
    "celdafechaDMA": celdafechaDMA,
    "celdamoneda": celdamoneda,
    "textonegrita": textonegrita,
    "formatomoneda": formatomoneda,
    "celdanumerodecimal": celdanumerodecimal,
    "celdanumerodecimal4dec": celdanumerodecimal4dec,
    "celdanegritacent": celdanegritacent,
    "celdanegritaizq": celdanegritaizq,
    "celdanegritageneral": celdanegritageneral,
    "celdamonedapie": celdamonedapie,
    "celdanumerodecimal4decpie": celdanumerodecimal4decpie,
    "celdaporcentaje": celdaporcentaje,
    "celdaporcentajepie": celdaporcentajepie
}

def analista_investigacion():
    idcargo = variable_valor('ID_CARGO_ANALISTA_INV')
    if DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1, persona_id=29119).exists():
        analista = DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1, persona_id=29119).order_by('estadopuesto_id')[0].persona
    else:
        analista = None

    return analista


def experto_investigacion():
    idcargo = variable_valor('ID_CARGO_EXPERTO_INV')
    if DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).exists():
        experto = DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).order_by('estadopuesto_id')[0].persona
    else:
        experto = None

    return experto


def coordinador_investigacion():
    idcargo = variable_valor('ID_CARGO_COORDINADOR_INV')
    if DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).exists():
        coordinador = DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).order_by('estadopuesto_id')[0].persona
    else:
        coordinador = None

    return coordinador


def vicerrector_investigacion_posgrado():
    idcargo = variable_valor('ID_CARGO_VICERRECTOR_INV')
    if DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).exists():
        director = DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).order_by('estadopuesto_id')[0].persona
    else:
        director = None

    return director


def rector_institucion():
    idcargo = variable_valor('ID_CARGO_RECTOR')
    if DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).exists():
        rector = DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).order_by('estadopuesto_id')[0].persona
    else:
        rector = None

    return rector


def director_juridico():
    idcargo = variable_valor('ID_CARGO_DIRECTOR_JUR')
    if DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).exists():
        director = DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).order_by('estadopuesto_id')[0].persona
    else:
        director = None

    return director


def experto_juridico():
    idcargo = variable_valor('ID_CARGO_EXPERTO_JUR')
    if DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).exists():
        experto = DistributivoPersona.objects.filter(status=True, denominacionpuesto_id=idcargo, estadopuesto_id=1).order_by('estadopuesto_id')[0].persona
    else:
        experto = None

    return experto


def tecnicos_investigacion():
    # return Persona.objects.filter(status=True, cedula__in=['0925007189', '0926475971', '0919304907', '0929718419']).order_by('apellido1', 'apellido2', 'nombres')
    return Persona.objects.filter(status=True, cedula__in=['0942054024', '0941335531']).order_by('apellido1', 'apellido2', 'nombres')


def tecnico_investigacion():
    return Persona.objects.filter(status=True, cedula='0919304907')[0]


def tecnico_revisor_grupoinvestigacion():
    return Persona.objects.filter(status=True, cedula='0929718419')[0]


def secretaria_comite_becas(convocatoria):
    return convocatoria.comite_institucional_becas().filter(secretario=True, vigente=True)[0].persona


def nombre_archivo_cedula(documento):
    return os.path.basename(documento.cedula.name)


def nombre_archivo_papeleta_votacion(documento):
    return os.path.basename(documento.papeleta.name)


def diff_month(inicio, fin):
    return (fin.year - inicio.year) * 12 + fin.month - inicio.month


def diff_hours(inicio, fin):
    diff = fin - inicio
    return diff.total_seconds() / 3600


def secuencia_informe_factibilidad(tipo):
    reg = InformeFactibilidad.objects.filter(status=True, tipo=tipo).aggregate(secuencia=Max('secuencia') + 1)
    if reg['secuencia'] is None:
        secuencia = 1
    else:
        secuencia = reg['secuencia']
    return secuencia


def secuencia_informe_grupoinvestigacion():
    from investigacion.models import GrupoInvestigacionInforme
    reg = GrupoInvestigacionInforme.objects.filter(status=True).aggregate(secuencia=Max('secuencia') + 1)
    if reg['secuencia'] is None:
        secuencia = 1
    else:
        secuencia = reg['secuencia']
    return secuencia


def secuencia_solicitud_beca(convocatoria):
    reg = convocatoria.solicitud_set.filter(status=True).aggregate(secuencia=Max('numero') + 1)
    if reg['secuencia'] is None:
        secuencia = 1
    else:
        secuencia = reg['secuencia']
    return secuencia


def secuencia_resolucion_comite(anio):
    reg = ResolucionComite.objects.filter(status=True, fecha__year=anio).aggregate(secuencia=Max('secuencia') + 1)
    if reg['secuencia'] is None:
        secuencia = 1
    else:
        secuencia = reg['secuencia']
    return secuencia


def secuencia_codigo_proyecto(convocatoria, lineainvestigacion):
    from investigacion.models import ProyectoInvestigacion
    reg = ProyectoInvestigacion.objects.filter(status=True, convocatoria=convocatoria, lineainvestigacion=lineainvestigacion).aggregate(secuencia=Max('secuencia') + 1)
    if reg['secuencia'] is None:
        secuencia = 1
    else:
        secuencia = reg['secuencia']
    return secuencia


def periodo_vigente_distributivo_docente_investigacion(profesor):
    periodovigente = None
    # fechaactual = datetime.strptime('2023' + '-' + '04' + '-' + '13', '%Y-%m-%d').date()
    fechaactual = datetime.now().date()

    # Consulto los id de los periodos donde tiene registrado distributivo el docente
    periodosid = ProfesorDistributivoHoras.objects.values_list('periodo__id').filter(profesor=profesor, periodo__visible=True, periodo__status=True)
    if periodosid:
        # Consulto los periodos
        periodosdocente = Periodo.objects.select_related('tipo').filter(id__in=periodosid).order_by('-inicio')

        # Consulto el periodo vigente
        periodovigente = periodosdocente.filter(inicio__lte=fechaactual, fin__gte=fechaactual).order_by('-marcardefecto')[0] if periodosdocente.filter(inicio__lte=fechaactual, fin__gte=fechaactual).exists() else None

        # Verifico que tenga horas de investigación asignadas en el periodo
        if periodovigente:
            distributivo = profesor.profesordistributivohoras_set.filter(status=True, periodo=periodovigente)[0]

            if not distributivo.detalledistributivo_set.filter(status=True, criterioinvestigacionperiodo__isnull=False):
                periodovigente = None

        return periodovigente
    else:
        return periodovigente


def periodo_vigente_distributivo_docente(profesor):
    periodovigente = None
    fechaactual = datetime.now().date()

    # Consulto los id de los periodos donde tiene registrado distributivo el docente
    periodosid = ProfesorDistributivoHoras.objects.values_list('periodo__id').filter(profesor=profesor, periodo__visible=True, periodo__status=True)
    if periodosid:
        # Consulto los periodos
        periodosdocente = Periodo.objects.select_related('tipo').filter(id__in=periodosid).order_by('-inicio')

        # Consulto el periodo vigente
        periodovigente = periodosdocente.filter(inicio__lte=fechaactual, fin__gte=fechaactual).order_by('-marcardefecto')[0] if periodosdocente.filter(inicio__lte=fechaactual, fin__gte=fechaactual).exists() else None

        return periodovigente
    else:
        return periodovigente


def coordinacion_carrera_distributivo_docente(profesor):
    periodovigente = periodo_vigente_distributivo_docente(profesor)
    if periodovigente:
        distributivo = ProfesorDistributivoHoras.objects.filter(status=True, periodo=periodovigente, profesor=profesor)[0]
        return {"idcoordinacion": distributivo.coordinacion.id,
                "coordinacion": distributivo.coordinacion.nombre,
                "aliascoordinacion": distributivo.coordinacion.alias,
                "idcarrera": distributivo.carrera.id if distributivo.carrera else 0,
                "carrera": distributivo.carrera.nombre if distributivo.carrera else '',
                "aliascarrera": distributivo.carrera.alias if distributivo.carrera else ''}
    else:
        return {"idcoordinacion": 0,
                "coordinacion": "",
                "aliascoordinacion": "",
                "idcarrera": 0,
                "carrera": "",
                "aliascarrera": ""}


def salto_linea_nombre_firma_encontrado(texto):
    lista = texto.split("\n")
    c = 0

    for item in lista:
        if item not in ["", " "]:
            c += 1

    return c == 2


def secuencia_solicitud_certificacion(convocatoria):
    reg = convocatoria.certificacionpresupuestaria_set.filter(status=True).aggregate(secuencia=Max('numero') + 1)
    if reg['secuencia'] is None:
        secuencia = 1
    else:
        secuencia = reg['secuencia']
    return secuencia


def secuencia_solicitud_grupo_investigacion():
    from investigacion.models import GrupoInvestigacion
    reg = GrupoInvestigacion.objects.filter(status=True).aggregate(secuencia=Max('numero') + 1)
    if reg['secuencia'] is None:
        secuencia = 1
    else:
        secuencia = reg['secuencia']
    return secuencia


def responsable_coordinacion(periodo, coordinacion):
    if ResponsableCoordinacion.objects.values("id").filter(status=True, periodo=periodo, coordinacion=coordinacion, tipo=1).exists():
        return ResponsableCoordinacion.objects.get(status=True, periodo=periodo, coordinacion=coordinacion, tipo=1)
    else:
        return None


def identificacion_valida(cedula, pasaporte):
    if cedula:
        resp = validarcedula(cedula)
        if resp.lower() != "ok":
            return {"estado": "error", "mensaje": resp}

        if Persona.objects.values('id').filter(Q(cedula=cedula) | Q(pasaporte=cedula), status=True).exists():
            return {"estado": "error", "mensaje": "La persona ya está registrada en la base de datos"}

    if pasaporte:
        if pasaporte[:2] != 'VS':
            return {"estado": "error", "mensaje": "Pasaporte mal ingresado, no olvide colocar <b>VS</b> al inicio"}

        if Persona.objects.values('id').filter(Q(cedula=pasaporte) | Q(pasaporte=pasaporte), status=True).exists():
            return {"estado": "error", "mensaje": "La persona ya está registrada en la base de datos"}

    return {"estado": "OK"}


def notificar_revision_solicitud_produccion_cientifica(solicitudpublicacion):
    # Si no es pre-aprobado se notifica a solicitante
    if solicitudpublicacion.estado.valor != 6:
        persona = solicitudpublicacion.persona
    else:
        persona = coordinador_investigacion()

    # Obtengo la(s) cuenta(s) de correo desde la cual(es) se envía el e-mail
    listacuentascorreo = [29]  # investigacion.dip@unemi.edu.ec
    fechaenvio = datetime.now().date()
    horaenvio = datetime.now().time()

    # E-mail del destinatario
    lista_email_envio = persona.lista_emails_envio()
    # lista_email_envio = ['isaltosm@unemi.edu.ec']
    lista_email_cco = ['ivan_saltos_medina@hotmail.com']
    lista_adjuntos = []

    cuenta = cuenta_email_disponible_para_envio(listacuentascorreo)

    titulo = "Producción Científica"

    if solicitudpublicacion.estado.valor == 2:  # VALIDADO
        tiponotificacion = 'SOLVAL'
        tituloemail = u"Solicitud de Registro de Producción Científica Validada"
    elif solicitudpublicacion.estado.valor == 3:  # NOVEDADES
        tiponotificacion = 'NOVSOL'
        tituloemail = u"Novedades Solicitud de Registro de Producción Científica"
    elif solicitudpublicacion.estado.valor == 4:  # RECHAZADO
        tiponotificacion = 'RECSOL'
        tituloemail = u"Solicitud de Registro de Producción Científica Rechazada"
    elif solicitudpublicacion.estado.valor == 6:  # PRE-APROBADO
        tiponotificacion = 'SOLPREAPRO'
        tituloemail = u"Solicitud de Registro de Producción Científica Pre-Aprobada"
    else:  # RECHAZADO
        tiponotificacion = 'SOLAPRO'
        tituloemail = u"Solicitud de Registro de Producción Científica Aprobada"

    # Notificar por e-mail
    send_html_mail(tituloemail,
                   "emails/solicitudpublicacion.html",
                   {'sistema': u'SGA - UNEMI',
                    'titulo': titulo,
                    'fecha': fechaenvio,
                    'hora': horaenvio,
                    'tiponotificacion': tiponotificacion,
                    'saludo': 'Estimada' if persona.sexo_id == 1 else 'Estimado',
                    'nombrepersona': persona.nombre_completo_inverso(),
                    'solicitudpublicacion': solicitudpublicacion
                    },
                   lista_email_envio,
                   lista_email_cco,
                   lista_adjuntos,
                   cuenta=CUENTAS_CORREOS[cuenta][1]
                   )


def notificar_grupo_investigacion(grupoinvestigacion, tiponotificacion):
    # Obtengo la(s) cuenta(s) de correo desde la cual(es) se envía el e-mail
    if tiponotificacion in ['REGSOL', 'REGDEC', 'REVSOL', 'NOVSOL', 'APRFAC', 'NOTVICE']:
        listacuentascorreo = [0, 8, 9, 10, 11, 12, 13]  # sga@unemi.edu.ec, sga2@unemi.edu.ec, ..., sga7@unemi.edu.ec
    else:
        listacuentascorreo = [29]  # investigacion@unemi.edu.ec

    titulo = "Grupos de Investigación"
    fechaenvio = datetime.now().date()
    horaenvio = datetime.now().time()
    cuenta = cuenta_email_disponible_para_envio(listacuentascorreo)

    if tiponotificacion == 'REGSOL':
        asuntoemail = "Solicitud de Propuesta para Creación de Grupo de Investigación"
        persona = grupoinvestigacion.profesor.persona
    elif tiponotificacion == 'REGDEC':
        asuntoemail = "Solicitud de Propuesta para Creación de Grupo de Investigación"
        persona = responsable_coordinacion(grupoinvestigacion.periodo, grupoinvestigacion.coordinacion).persona
    elif tiponotificacion == 'REVSOL':
        asuntoemail = "Solicitud de Propuesta para Creación de Grupo de Investigación Revisada"
        persona = grupoinvestigacion.profesor.persona
    elif tiponotificacion == 'NOVSOL':
        asuntoemail = "Novedades Solicitud de Propuesta para Creación de Grupo de Investigación"
        persona = grupoinvestigacion.profesor.persona
    elif tiponotificacion == 'APRFAC':
        asuntoemail = "Aprobación Consejo de Facultad para la Propuesta de Creación de Grupo de Investigación"
        persona = grupoinvestigacion.profesor.persona
    elif tiponotificacion == 'NOTVICE':
        asuntoemail = "Aprobación Consejo de Facultad para la Propuesta de Creación de Grupo de Investigación"
        persona = vicerrector_investigacion_posgrado()
    elif tiponotificacion in ['NOTCOORD', 'NOTANL']:
        asuntoemail = "Reasignación para Análisis de Propuesta de Creación de Grupo de Investigación"
        persona = coordinador_investigacion() if tiponotificacion == 'NOTCOORD' else tecnico_revisor_grupoinvestigacion()
    elif tiponotificacion == 'VALSOL':
        asuntoemail = "Solicitud de Propuesta para Creación de Grupo de Investigación Analizada y Validada"
        persona = grupoinvestigacion.profesor.persona
    elif tiponotificacion == 'NOVANLSOL':
        asuntoemail = "Novedades detectadas en la etapa de Análisis de la Solicitud de Propuesta para Creación de Grupo de Investigación"
        persona = coordinador_investigacion()
    elif tiponotificacion in ['DEVVICE', 'DEVSOL']:
        asuntoemail = "Devolución de Requerimiento de Propuesta de Creación de Grupo de Investigación"
        persona = vicerrector_investigacion_posgrado() if tiponotificacion == 'DEVVICE' else grupoinvestigacion.profesor.persona
    elif tiponotificacion == 'INFOELA':
        asuntoemail = "Informe Técnico de Creación de Grupo de Investigación Elaborado"
        persona = experto_investigacion()
    elif tiponotificacion == 'INFONOV':
        asuntoemail = "Novedades en Informe Técnico de Creación de Grupo de Investigación"
        persona = grupoinvestigacion.informe().elabora
    elif tiponotificacion == 'INFOVAL':
        asuntoemail = "Informe Técnico de Creación de Grupo de Investigación Revisado"
        persona = coordinador_investigacion()
    elif tiponotificacion == 'INFOAPR':
        asuntoemail = "Informe Técnico de Creación de Grupo de Investigación Aprobado"
        persona = vicerrector_investigacion_posgrado()
    elif tiponotificacion in ['APROCS', 'NOTVICEOCS', 'NOTCOORDOCS']:
        asuntoemail = "Propuesta de Creación de Grupo de Investigación Aprobada por OCS"
        if tiponotificacion == 'APROCS':
            persona = grupoinvestigacion.profesor.persona
        elif tiponotificacion == 'NOTVICEOCS':
            persona = vicerrector_investigacion_posgrado()
        else:
            persona = coordinador_investigacion()

    # E-mail del destinatario
    lista_email_envio = persona.lista_emails_envio()
    lista_email_cco = ['ivan_saltos_medina@hotmail.com']
    lista_archivos_adjuntos = []

    send_html_mail(asuntoemail,
                   "emails/propuestagrupoinvestigacion.html",
                   {'sistema': u'SGA - UNEMI',
                    'titulo': titulo,
                    'fecha': fechaenvio,
                    'hora': horaenvio,
                    'tiponotificacion': tiponotificacion,
                    'saludo': 'Estimada' if persona.sexo_id == 1 else 'Estimado',
                    'nombrepersona': persona.nombre_completo_inverso(),
                    'grupoinvestigacion': grupoinvestigacion,
                    'nombredocente': grupoinvestigacion.profesor.persona.nombre_completo_inverso(),
                    'saludodocente': 'la docente' if grupoinvestigacion.profesor.persona.sexo_id == 1 else 'el docente',
                    },
                   lista_email_envio,
                   lista_email_cco,
                   lista_archivos_adjuntos,
                   cuenta=CUENTAS_CORREOS[cuenta][1]
                   )
