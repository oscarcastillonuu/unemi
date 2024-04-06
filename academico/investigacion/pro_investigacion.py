# -*- coding: UTF-8 -*-
import json
import os
from math import ceil

import PyPDF2
from datetime import time
from decimal import Decimal

import requests
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
import time as pausaparaemail
from xlwt import easyxf, XFStyle, Workbook
import random
from decorators import secure_module
from investigacion.forms import RegistroPropuestaProyectoInvestigacionForm, ContenidoProyectoInvestigacionForm, \
    PresupuestoProyectoInvestigacionForm, CronogramaActividadProyectoInvestigacionForm, ExternoForm, \
    FinalizaEdicionForm, InformeProyectoForm
from investigacion.funciones import coordinador_investigacion, vicerrector_investigacion_posgrado
from investigacion.models import ProyectoInvestigacion, TipoRecursoPresupuesto, ProyectoInvestigacionInstitucion, \
    ProyectoInvestigacionIntegrante, ProyectoInvestigacionRecorrido, ProyectoInvestigacionItemPresupuesto, \
    TIPO_INTEGRANTE, ProyectoInvestigacionObjetivo, TipoResultadoCompromiso, ProyectoInvestigacionResultado, \
    ConvocatoriaProyecto, ConvocatoriaMontoFinanciamiento, ProyectoInvestigacionCronogramaActividad, \
    ProyectoInvestigacionCronogramaResponsable, ProyectoInvestigacionPasajeIntegrante, \
    ProyectoInvestigacionViaticoIntegrante, ProyectoInvestigacionActividadEvidencia, \
    ProyectoInvestigacionCronogramaEntregable, ProyectoInvestigacionHistorialArchivo, \
    ProyectoInvestigacionHistorialActividadEvidencia, ProyectoInvestigacionInforme, \
    ProyectoInvestigacionHistorialInforme, ProyectoInvestigacionInformeActividad, ProyectoInvestigacionInformeAnexo, ESTADO_EVALUACION_INTERNA_EXTERNA, EvaluacionProyecto, EvaluacionProyectoDetalle
from sagest.commonviews import obtener_estado_solicitud
from sagest.models import datetime, Banco, DistributivoPersona, UnidadMedida, ExperienciaLaboral, Producto, SolicitudPublicacion
from settings import SITE_STORAGE, ALUMNOS_GROUP_ID, PROFESORES_GROUP_ID
from sga.commonviews import adduserdata
from sga.funciones import MiPaginador, log, variable_valor, \
    convertir_fecha, remover_caracteres_tildes_unicode, cuenta_email_disponible, generar_nombre, email_valido, \
    validar_archivo, null_to_decimal, cuenta_email_disponible_para_envio, fechaletra_corta
from sga.funcionesxhtml2pdf import conviert_html_to_pdfsaveqrcertificado, convert_html_to_pdf, conviert_html_to_pdf
from sga.models import CUENTAS_CORREOS, ActividadConvalidacionPPV, Profesor, Administrativo, Inscripcion, \
    TituloInstitucion, Externo, miinstitucion, Titulo, InstitucionEducacionSuperior, Pais, NivelTitulacion, \
    AreaConocimientoTitulacion, Persona, Titulacion, ArticuloPersonaExterna, PonenciaPersonaExterna, \
    LibroPersonaExterna, ProyectoInvestigacionPersonaExterna, Coordinacion, MESES_CHOICES, RedPersona, ModuloGrupo, Modulo, ArticuloInvestigacion, Evidencia, PonenciasInvestigacion, CapituloLibroInvestigacion, LibroInvestigacion
from django.template import Context
from django.template.loader import get_template

import time as ET

from sga.tasks import send_html_mail, conectar_cuenta
from sga.templatetags.sga_extras import encrypt

from django.core.cache import cache

IDS_MODULOS_CONVOCATORIAS = [381, 430, 423, 477, 495]
IDS_MODULOS_PRODUCCION_CIENTIFICA = [510]
IDS_MODULOS_NO_AGRUPADOS = [531]

@login_required(redirect_field_name='ret', login_url='/loginsga')
@transaction.atomic()
@secure_module
def view(request):
    data = {}
    adduserdata(request, data)
    data['persona'] = persona = request.session['persona']
    perfilprincipal = request.session['perfilprincipal']

    es_profesor = perfilprincipal.es_profesor()
    es_externo = perfilprincipal.es_externo()
    es_administrativo = perfilprincipal.es_administrativo()

    if es_externo and request.session['tiposistema'] != 'sga':
        request.session['tiposistema'] = 'sga'

    if not es_profesor and not es_externo and not es_administrativo:
        return HttpResponseRedirect("/?info=El Módulo está disponible para docentes y administrativos.")

    permiso_pcientifica = tiene_acceso_produccion_cientifica(persona, es_profesor, es_administrativo, es_externo)
    permiso_convocatorias = tiene_acceso_convocatorias(persona, es_profesor, es_administrativo, es_externo)
    permiso_no_agrupados = tiene_acceso_modulos_no_agrupados(persona, es_profesor, es_administrativo, es_externo)

    if not permiso_pcientifica and not permiso_convocatorias and not permiso_no_agrupados:
        return HttpResponseRedirect("/?info=Usted no tiene asignado permisos a los módulos de la Gestión de Investigación.")

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'subirinforme':
            try:
                if not 'idinforme' in request.POST:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al enviar los datos"})

                informeproyecto = ProyectoInvestigacionInforme.objects.get(pk=int(encrypt(request.POST['idinforme'])))

                archivo = request.FILES['archivoinforme']
                descripcionarchivo = 'Archivo del informe firmado'
                tipoinforme = "avance" if informeproyecto.tipo == 1 else "final"

                # Validar el archivo
                resp = validar_archivo(descripcionarchivo, archivo, ['PDF'], '4MB')
                if resp['estado'] != "OK":
                    return JsonResponse({"result": "bad", "mensaje": resp["mensaje"]})

                archivo._name = generar_nombre("informeproyecto" + tipoinforme, archivo._name)

                # Guardo el archivo del informe
                informeproyecto.archivo = archivo
                informeproyecto.estado = 4
                informeproyecto.save(request)

                log(u'Agregó archivo del informe firmado: %s' % (informeproyecto), request, "add")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                msg = ex.__str__()
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos. [%s]" % msg})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'metricas':
                try:
                    data['title'] = u'Métricas'

                    return render(request, "pro_investigacion/viewcapacitacion.html", data)
                except Exception as ex:
                    pass

            elif action == 'capacitaciones':
                try:
                    data['title'] = u'Capacitaciones Especializadas'

                    return render(request, "pro_investigacion/viewcapacitacion.html", data)
                except Exception as ex:
                    pass

            elif action == 'convocatorias':
                try:
                    data['title'] = u'Convocatorias'
                    modulos = []
                    misgrupos = mis_grupos(persona, es_profesor, es_administrativo, es_externo)

                    for modulo in mis_modulos(misgrupos, IDS_MODULOS_CONVOCATORIAS, True):
                        modulo = {
                            "id": modulo['id'],
                            "url": modulo['url'],
                            "icono": modulo['icono'],
                            "nombre": modulo['nombre'],
                            "descripcion": modulo['descripcion']
                        }
                        modulos.append(modulo)

                    data['modulos2'] = modulos
                    data['enlaceatras'] = "/pro_investigacion"

                    return render(request, "pro_investigacion/panel.html", data)
                except Exception as ex:
                    pass

            elif action == 'asesorias':
                try:
                    data['title'] = u'Asesorías'

                    return render(request, "pro_investigacion/viewcapacitacion.html", data)
                except Exception as ex:
                    pass

            elif action == 'buzon':
                try:
                    data['title'] = u'Buzón de Sugerencias'

                    return render(request, "pro_investigacion/viewcapacitacion.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = u'Investigación'
                modulos = []

                if permiso_pcientifica:
                    modulo = {
                        "id": 510,
                        "url": "pro_produccioncientifica",
                        "icono": "/static/images/iconssga/icon_articulos.svg",
                        "nombre": "Mi Producción Científica",
                        "descripcion": "Artículos, Libros y Ponencias",
                    }
                    modulos.append(modulo)

                if permiso_convocatorias:
                    modulo = {
                        "id": 0,
                        "url": "pro_investigacion?action=convocatorias",
                        "icono": "/static/images/iconssga/icon_articulos.svg",
                        "nombre": "Convocatorias",
                        "descripcion": "Becas, Proyectos y Ponencias",
                    }
                    modulos.append(modulo)

                if permiso_no_agrupados:
                    misgrupos = mis_grupos(persona, es_profesor, es_administrativo, es_externo)

                    for modulo in mis_modulos(misgrupos, IDS_MODULOS_NO_AGRUPADOS, True):
                        modulo = {
                            "id": modulo['id'],
                            "url": modulo['url'],
                            "icono": modulo['icono'],
                            "nombre": modulo['nombre'],
                            "descripcion": modulo['descripcion']
                        }
                        modulos.append(modulo)

                data['modulos2'] = modulos
                data['enlaceatras'] = "/"
                return render(request, "pro_investigacion/panel.html", data)
            except Exception as ex:
                pass


def tiene_acceso_produccion_cientifica(persona, es_profesor, es_administrativo, es_externo):
    if es_profesor or es_administrativo:
        misgrupos = mis_grupos(persona, es_profesor, es_administrativo, es_externo)
        accesomodulos = True if mis_modulos(misgrupos, IDS_MODULOS_PRODUCCION_CIENTIFICA, False) else False
        return accesomodulos
    else:
        return False


def tiene_acceso_convocatorias(persona, es_profesor, es_administrativo, es_externo):
    misgrupos = mis_grupos(persona, es_profesor, es_administrativo, es_externo)
    accesomodulos = True if mis_modulos(misgrupos, IDS_MODULOS_CONVOCATORIAS, True) else False
    return accesomodulos


def tiene_acceso_modulos_no_agrupados(persona, es_profesor, es_administrativo, es_externo):
    misgrupos = mis_grupos(persona, es_profesor, es_administrativo, es_externo)
    accesomodulos = True if mis_modulos(misgrupos, IDS_MODULOS_NO_AGRUPADOS, True) else False
    return accesomodulos


def mis_grupos(persona, es_profesor, es_administrativo, es_externo):
    if es_profesor:
        return ModuloGrupo.objects.filter(grupos__in=[PROFESORES_GROUP_ID]).distinct()
    elif es_administrativo:
        return ModuloGrupo.objects.filter(grupos__in=[13]).distinct()
    else:
        idsgrupos = []
        if persona.es_evaluador_externo_proyectos_investigacion():
            idsgrupos.append(335)
        if persona.es_evaluador_externo_obras_relevancia():
            idsgrupos.append(456)
        if persona.es_integrante_externo_proyecto_investigacion():
            idsgrupos.append(444)
        return ModuloGrupo.objects.filter(grupos__in=idsgrupos).distinct()


def mis_modulos(misgrupos, idsmodulos, es_submodulo):
    return Modulo.objects.values("id", "url", "icono", "nombre", "descripcion").filter(Q(modulogrupo__in=misgrupos), activo=True, submodulo=es_submodulo, pk__in=idsmodulos).distinct().order_by('nombre')


