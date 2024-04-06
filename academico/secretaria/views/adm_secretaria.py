# -*- coding: latin-1 -*-
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from decorators import last_access, secure_module
from inno.funciones import enviar_notificacion_aceptar_rechazar_solicitud_asistencia_pro
from sagest.models import Rubro
from secretaria.models import Solicitud, Servicio, HistorialSolicitud, CategoriaServicio, FormatoCertificado, SolicitudAsignatura
from settings import SOLICITUD_PREPROYECTO_ESTADO_APROBADO_ID, \
    SOLICITUD_PREPROYECTO_ESTADO_RECHAZADO_ID
from sga.commonviews import adduserdata
from sga.funciones import MiPaginador, log, generar_nombre, notificacion2, notificacion4
from sga.models import SolicitudAperturaClase, Carrera, Profesor, ESTADOS_PREPROYECTO
from sga.templatetags.sga_extras import encrypt
from django.template.loader import get_template
from secretaria.forms import EntregaCertificadoForm, SubirCertificadoPersonalizadoForm, SubirFormatoCertificadoForm, \
    AprobarRechazarInformePertinenciaForm, AdicionarActividadCronogramaForm, ActividadCronogramaTitulacionForm, \
    SubirInformeTecnicoPertinenciaForm, SubirCronogramaTitulacionForm, NotificarCronogramaTitulacionForm
from sga.tasks import send_html_mail
from sga.models import CUENTAS_CORREOS, PerfilAccesoUsuario, Persona, FirmaCertificadoSecretaria, InscripcionMalla, AsignaturaMalla, \
    RecordAcademico, Inscripcion, Malla
from django.forms import model_to_dict
from sga.funciones import notificacion3, remover_caracteres_tildes_unicode, remover_caracteres_especiales_unicode, generar_nombre, notificacion
from pdip.models import ContratoDip, ContratoCarrera
from posgrado.models import ActividadCronogramaTitulacion, DetalleActividadCronogramaTitulacion, CohorteMaestria
from sga.funciones_templatepdf import cronogramatituex
from sga.funciones import variable_valor
import os
from core.firmar_documentos import firmar, firmarmasivo, obtener_posicion_y, obtener_posicion_x_y
from core.firmar_documentos_ec import JavaFirmaEc
import io
import time
from django.core.files import File as DjangoFile

@login_required(redirect_field_name='ret', login_url='/loginsga')
@secure_module
@last_access
@transaction.atomic()
def view(request):
    data = {}
    adduserdata(request, data)
    persona = request.session['persona']
    periodo = request.session['periodo']
    miscarreras = persona.mis_carreras()
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'delete':
            try:
                eSolicitud = delete = Solicitud.objects.get(pk=int(encrypt(request.POST['id'])))
                if not eSolicitud.puede_eliminar():
                    raise NameError(u"Solicitud se esta utilizando")
                eRubros = Rubro.objects.filter(solicitud=eSolicitud, status=True)
                historial = False
                observacion = ''
                if eRubros.values("id").exists():
                    eRubro = eRubros.first()
                    if not eRubro.tiene_pagos():
                        #eSolicitud.delete()
                        #eSolicitud.anular_solicitud()
                        eRubro.delete()
                        observacion = u'Elimino solicitud'
                        historial = True
                        log(u'Eliminó solicitud de secretaría: %s' % delete, request, "del")
                    else:
                        observacion= u'Solicitud cuenta con pagos realizados'
                        historial = True

                if historial:
                    eSolicitud.estado = 8
                    eSolicitud.en_proceso = False
                    eSolicitud.save(request)
                    log(u'Eliminó solicitud de secretaría: %s' % delete, request, "del")
                    eHistorialSolicitud = HistorialSolicitud(solicitud=eSolicitud,
                                                             observacion=observacion,
                                                             fecha=datetime.now().date(),
                                                             hora=datetime.now().time(),
                                                             estado=eSolicitud.estado,
                                                             responsable=eSolicitud.perfil.persona,
                                                             )
                    eHistorialSolicitud.save(request)
                return JsonResponse({"result": 'ok', "mensaje": u"Solicitud eliminada correctamente"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al eliminar: {ex.__str__()}"})

        if action == 'validarfirmaec':
            try:
                eSolicitud = Solicitud.objects.get(pk=int(encrypt(request.POST['id'])))

                eSolicitud.firmadoec = True
                eSolicitud.save(request)
                observacion = 'Archivo de solicitud de homologación interna validado correctamente.'
                log(u'Validó archivo de solicitud de homologación: %s' % eSolicitud, request, "del")
                eHistorialSolicitud = HistorialSolicitud(solicitud=eSolicitud,
                                                         observacion=observacion,
                                                         fecha=datetime.now().date(),
                                                         hora=datetime.now().time(),
                                                         estado=eSolicitud.estado,
                                                         archivo=eSolicitud.archivo_respuesta,
                                                         responsable=persona
                                                         )
                eHistorialSolicitud.save(request)
                return JsonResponse({"result": 'ok', "mensaje": u"Archivo de solicitud de homologación interna validado correctamente."})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al eliminar: {ex.__str__()}"})

        if action == 'rechazarfirmaec':
            try:
                eSolicitud = Solicitud.objects.get(pk=int(request.POST['id']))

                observacionf = request.POST['observacion']

                eSolicitud.firmadoec = False
                eSolicitud.estado = 7
                eSolicitud.save(request)
                observacion = f'Su archivo de solicitud de homologación ha sido rechazado. - {observacionf}.'

                log(u'Rechazó archivo de solicitud de homologación: %s' % eSolicitud, request, "edit")

                eHistorialSolicitud = HistorialSolicitud(solicitud=eSolicitud,
                                                         observacion=observacion,
                                                         fecha=datetime.now().date(),
                                                         hora=datetime.now().time(),
                                                         estado=eSolicitud.estado,
                                                         archivo=eSolicitud.archivo_respuesta,
                                                         responsable=persona)
                eHistorialSolicitud.save(request)

                titulo = 'SOLICITUD DE HOMOLOGACIÓN RECHAZADA'

                notificacion4(titulo, observacionf, eSolicitud.perfil.persona, None, '/alu_secretaria/service/asignaturashomologa', eSolicitud.pk, 1, 'SIE', eSolicitud, eSolicitud.perfil)
                return JsonResponse({"result": False, 'mensaje': 'Solicitud Rechazada'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al eliminar: {ex.__str__()}"})

        if action == 'seleccionarcarreraho':
            try:
                eSolicitud = Solicitud.objects.get(pk=int(request.POST['id']))
                carrera = Carrera.objects.get(pk=int(request.POST['carrera']))

                nombre_carrera = carrera.nombre
                if carrera.mencion:
                    nombre_carrera = f'{carrera.nombre} CON MENCIÓN EN {carrera.mencion}'

                eSolicitud.carrera_homologada = carrera
                eSolicitud.save(request)

                log(u'Seleccionó carrera comparativa: %s' % eSolicitud, request, "edit")

                eHistorialSolicitud = HistorialSolicitud(solicitud=eSolicitud,
                                                         observacion=f'Seleccionó como carrera comparativa: {nombre_carrera}',
                                                         fecha=datetime.now().date(),
                                                         hora=datetime.now().time(),
                                                         estado=eSolicitud.estado,
                                                         # archivo=eSolicitud.archivo_respuesta,
                                                         responsable=persona)
                eHistorialSolicitud.save(request)
                return JsonResponse({"result": False, 'mensaje': 'Solicitud Rechazada'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al eliminar: {ex.__str__()}"})

        if action == 'deleteformat':
            try:
                eFormat = FormatoCertificado.objects.get(pk=int(request.POST['id']))
                eFormat.status = False
                eFormat.save(request)
                log(u'Eliminó el formato de certificado: %s' % eFormat, request, "del")
                return JsonResponse({"result": 'ok', "mensaje": u"Solicitud eliminada correctamente"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al eliminar: {ex.__str__()}"})

        if action == 'deleteactividad':
            try:
                eActividad = ActividadCronogramaTitulacion.objects.get(pk=int(request.POST['id']))
                eActividad.status = False
                eActividad.save(request)
                log(u'Eliminó el actividad de cronograma de titulación: %s' % eActividad, request, "del")
                return JsonResponse({"result": 'ok', "mensaje": u"Solicitud eliminada correctamente"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al eliminar: {ex.__str__()}"})

        if action == 'deleteactividaddetalle':
            try:
                eActividad = DetalleActividadCronogramaTitulacion.objects.get(pk=int(request.POST['id']))
                eActividad.status = False
                eActividad.save(request)
                log(u'Eliminó el actividad de cronograma de titulación del maestrante: %s' % eActividad.solicitud, request, "del")
                return JsonResponse({"result": 'ok', "mensaje": u"Solicitud eliminada correctamente"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al eliminar: {ex.__str__()}"})

        if action == 'procesarCertificado':
            try:
                eSolicitud = Solicitud.objects.get(pk=int(encrypt(request.POST['id'])))
                eSolicitud = eSolicitud.generar_certificado()
                return JsonResponse({"result": 'ok', "mensaje": u"Certificado generaddo correctamente"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al generar certificado: {ex.__str__()}"})

        elif action == 'addentrega':
            try:
                f = EntregaCertificadoForm(request.POST)
                if f.is_valid():
                    solicitud = Solicitud.objects.get(pk=int(request.POST['id']))
                    solicitud.estado = 2
                    solicitud.save(request)

                    eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                             observacion=f.cleaned_data['observacion'],
                                                             fecha=datetime.now().date(),
                                                             hora=datetime.now().time(),
                                                             estado=solicitud.estado,
                                                             responsable=persona)
                    eHistorialSolicitud.save(request)
                    log(u'Entregó certificado físico: %s' % solicitud, request, "edit")
                    return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": True, "mensaje": u"Error al guardar los datos."})

        elif action == 'marcaratendido':
            try:
                solicitud = Solicitud.objects.get(status=True, pk=int(encrypt(request.POST['id'])))
                # solicitud.atendido = True
                # solicitud.save(request)

                fechaasi = datetime.now().date()
                horaasi = str(datetime.now().time().strftime('%H:%M'))

                eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                         observacion= f"Está siendo atendido por {persona}",
                                                         fecha=fechaasi,
                                                         hora=horaasi,
                                                         estado=solicitud.estado,
                                                         responsable=persona,
                                                         atendido=True)
                eHistorialSolicitud.save(request)
                log(u'Atendió las solicitud del maestrante: %s' % solicitud.perfil.persona, request, "edit")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'aprobarrechazar':
            try:
                solicitud = Solicitud.objects.get(status=True, pk=int(request.POST['id']))
                director = ''

                if 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                    director = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN'
                if 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                    director = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD'
                if 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                    director = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO'

                f = AprobarRechazarInformePertinenciaForm(request.POST)
                if f.is_valid():
                    if int(f.cleaned_data['estado']) == 1:
                        solicitud.estado = 12
                        solicitud.save(request)
                    else:
                        solicitud.estado = 13
                        solicitud.save(request)

                    fechaasi = datetime.now().date()
                    horaasi = str(datetime.now().time().strftime('%H:%M'))

                    eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                             observacion=f.cleaned_data['observacion'],
                                                             fecha=fechaasi,
                                                             hora=horaasi,
                                                             estado=solicitud.estado,
                                                             responsable=persona,
                                                             archivo = solicitud.respaldo if solicitud.respaldo else '',
                                                             atendido=True)
                    eHistorialSolicitud.save(request)

                    secretarias = Persona.objects.filter(id__in=variable_valor('PERSONAL_SECRETARIA'), status=True)

                    coordinadores = ContratoDip.objects.filter(status=True, cargo__nombre__icontains='COORDINADOR', contratocarrera__carrera=solicitud.perfil.inscripcion.carrera, fechainicio__lte=datetime.now().date(), fechafin__gte=datetime.now().date()).exclude(persona=persona)

                    if 'clave' in request.POST and request.POST['clave'] == 'homolog':
                        if int(f.cleaned_data['estado']) == 1:
                            titulo = 'INFORME TÉCNICO DE PERTINENCIA APROBADO'
                            cuerpo = f'Saludos cordiales, se comunica al maestrante {solicitud.perfil.persona} que su informe técnico de pertinencia ha sido APROBADO por el {director}. Se le comunicará en estos días las asignaturas favorables para el proceso de homologación junto con la opción pra confirmar la generación del rubro.'

                            notificacion4(titulo, cuerpo, solicitud.perfil.persona, None, '/alu_secretaria/service/asignaturashomologa', solicitud.pk, 1, 'SIE', solicitud, solicitud.perfil)
                        else:
                            titulo = 'INFORME TÉCNICO DE PERTINENCIA RECHAZADO'
                            cuerpo = f'Saludos cordiales, se comunica al maestrante {solicitud.perfil.persona} que su informe técnico de pertinencia ha sido RECHAZADO por el {director}. Agradecemos su compresión.'

                            notificacion4(titulo, cuerpo, solicitud.perfil.persona, None, '/alu_secretaria/service/asignaturashomologa', solicitud.pk, 1, 'SIE', solicitud, solicitud.perfil)

                        if int(f.cleaned_data['estado']) == 1:
                            titulo = "INFORME TÉCNICO DE PERTINENCIA APROBADO"
                            cuerpo = f'Se informa al coordinador del programa de {solicitud.perfil.inscripcion.carrera} que el informe técnico de pertinencia del maestrante {solicitud.perfil.persona}  ha sido aprobado por el {director}.'
                        else:
                            titulo = "INFORME TÉCNICO DE PERTINENCIA RECHAZADO"
                            cuerpo = f'Se informa al coordinador del programa de {solicitud.perfil.inscripcion.carrera} que el informe técnico de pertinencia del maestrante {solicitud.perfil.persona}  ha sido rechazado por el {director}.'
                        coordinadores1 = []
                        if ContratoDip.objects.filter(status=True, cargo__nombre__icontains='COORDINADOR', contratocarrera__carrera=solicitud.perfil.inscripcion.carrera, fechainicio__lte=datetime.now().date(), fechafin__gte=datetime.now().date()).exclude(persona=persona).exists():
                            coordinators = coordinadores.append(ContratoDip.objects.filter(status=True, cargo__nombre__icontains='COORDINADOR', contratocarrera__carrera=solicitud.perfil.inscripcion.carrera, fechainicio__lte=datetime.now().date(), fechafin__gte=datetime.now().date()).exclude(persona=persona).values_list('persona_id', flat=True))
                            for idpersona in coordinators:
                                coordinadores1.append(idpersona)
                        coordinadores1.append(solicitud.inscripcioncohorte.cohortes.coordinador.id)

                        for idp in coordinadores1:
                            coordinador = Persona.objects.get(status=True, pk=idp)
                            notificacion2(titulo, cuerpo, coordinador, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo), coordinador.id, 1, 'sga', coordinador)
                    else:
                        if int(f.cleaned_data['estado']) == 1:
                            titulo = 'INFORME TÉCNICO DE PERTINENCIA APROBADO'
                            cuerpo = 'Saludos cordiales, se comunica al maestrante ' + str(solicitud.perfil.persona) + ' que su informe técnico de pertinencia ha sido APROBADO por el ' + director +', por esta razón se ha habilitado la opción en la ventana de Mis pedidos representada mediante un ícono de dólar, la cual confirmará la creación del rubro para ingresar al proceso de titulación extraordinaria.'

                            notificacion4(titulo, cuerpo, solicitud.perfil.persona, None, '/alu_secretaria/mis_pedidos', solicitud.pk, 1, 'SIE', solicitud, solicitud.perfil)
                        else:
                            titulo = 'INFORME TÉCNICO DE PERTINENCIA RECHAZADO'
                            cuerpo = 'Saludos cordiales, se comunica al maestrante ' + str(solicitud.perfil.persona) + ' que su informe técnico de pertinencia ha sido RECHAZADO por el ' + director + '. Agradecemos su compresión.'

                            notificacion4(titulo, cuerpo, solicitud.perfil.persona, None, '/alu_secretaria/mis_pedidos', solicitud.pk, 1, 'SIE',
                                          solicitud, solicitud.perfil)

                        for secretaria in secretarias:
                            if int(f.cleaned_data['estado']) == 1:
                                titulo = "INFORME TÉCNICO DE PERTINENCIA APROBADO"
                                cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.persona) + ' ha sido aprobado por el ' + director +'.'
                            else:
                                titulo = "INFORME TÉCNICO DE PERTINENCIA RECHAZADO"
                                cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.persona) + ' ha sido rechazado por el ' + director +'.'

                            notificacion2(titulo,
                                          cuerpo, secretaria, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                          secretaria.pk, 1, 'sga', secretaria)

                        for coordinador in coordinadores:
                            if int(f.cleaned_data['estado']) == 1:
                                titulo = "INFORME TÉCNICO DE PERTINENCIA APROBADO"
                                cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.persona) + ' ha sido aprobado por el ' + director +'.'
                            else:
                                titulo = "INFORME TÉCNICO DE PERTINENCIA RECHAZADO"
                                cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.persona) + ' ha sido rechzado por el ' + director +'.'

                            notificacion2(titulo,
                                          cuerpo, coordinador.persona, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                          coordinador.persona.pk, 1, 'sga', coordinador.persona)

                    log(u'Aprobó el informe técnico de pertinencia del maestrante: %s' % solicitud.perfil.persona, request, "edit")
                    return JsonResponse({"result": False, 'mensaje': 'Aprobación Existosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'revisarinforme':
            try:
                solicitud = Solicitud.objects.get(status=True, pk=int(request.POST['id']))

                f = AprobarRechazarInformePertinenciaForm(request.POST)
                if f.is_valid():
                    if int(f.cleaned_data['estado']) == 1:
                        solicitud.estado = 17
                        solicitud.save(request)
                    else:
                        solicitud.estado = 13
                        solicitud.save(request)

                    fechaasi = datetime.now().date()
                    horaasi = str(datetime.now().time().strftime('%H:%M'))

                    eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                             observacion=f.cleaned_data['observacion'],
                                                             fecha=fechaasi,
                                                             hora=horaasi,
                                                             estado=solicitud.estado,
                                                             responsable=persona)
                    eHistorialSolicitud.save(request)

                    secretarias = Persona.objects.filter(id__in=variable_valor('PERSONAL_SECRETARIA'), status=True)

                    coordinadores = ContratoDip.objects.filter(status=True, cargo__nombre__icontains='COORDINADOR', contratocarrera__carrera=solicitud.perfil.inscripcion.carrera, fechainicio__lte=datetime.now().date(), fechafin__gte=datetime.now().date()).exclude(persona=persona)

                    if int(f.cleaned_data['estado']) == 1:
                        if solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN').values_list('carrera_id', flat=True):
                            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN'
                            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                            titulo = "REVISIÓN DE INFORME TÉCNICO DE PERTINENCIA"
                            cuerpo = 'Se informa a ' + str(dir) + ' que la experta de Secretaría Técnica de Posgrado ha aprobado el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.inscripcion.persona) + '. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

                            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                          dir.pk, 1, 'sga', dir)
                        elif solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD').values_list('carrera_id', flat=True):
                            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD'
                            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                            titulo = "REVISIÓN DE INFORME TÉCNICO DE PERTINENCIA"
                            cuerpo = 'Se informa a ' + str(dir) + ' que la experta de Secretaría Técnica de Posgrado ha aprobado el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.inscripcion.persona) + '. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

                            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                          dir.pk, 1, 'sga', dir)
                        elif solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO').values_list('carrera_id', flat=True):
                            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO'
                            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                            titulo = "REVISIÓN DE INFORME TÉCNICO DE PERTINENCIA"
                            cuerpo = 'Se informa a ' + str(dir) + ' que la experta de Secretaría Técnica de Posgrado ha aprobado el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.inscripcion.persona) + '. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

                            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                          dir.pk, 1, 'sga', dir)

                    for secretaria in secretarias:
                        if int(f.cleaned_data['estado']) == 1:
                            titulo = "INFORME TÉCNICO DE PERTINENCIA APROBADO"
                            cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.persona) + ' ha sido aprobado por la EXPERTA de Secretaría Técnica de Posgrado'
                        else:
                            titulo = "INFORME TÉCNICO DE PERTINENCIA RECHAZADO"
                            cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.persona) + ' ha sido rechazado por la EXPERTA de Secretaría Técnica de Posgrado'

                        notificacion2(titulo,
                                      cuerpo, secretaria, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.perfil.persona.cedula),
                                      secretaria.pk, 1, 'sga', secretaria)

                    for coordinador in coordinadores:
                        if int(f.cleaned_data['estado']) == 1:
                            titulo = "INFORME TÉCNICO DE PERTINENCIA APROBADO"
                            cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.persona) + ' ha sido aprobado por la EXPERTA de Secretaría Técnica de Posgrado'
                        else:
                            titulo = "INFORME TÉCNICO DE PERTINENCIA RECHAZADO"
                            cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el informe técnico de pertinencia del maestrante ' + str(solicitud.perfil.persona) + ' ha sido rechazado por la EXPERTA de Secretaría Técnica de Posgrado'

                        notificacion2(titulo,
                                      cuerpo, coordinador.persona, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.perfil.persona.cedula),
                                      coordinador.persona.pk, 1, 'sga', coordinador.persona)

                    log(u'Revisó el informe técnico de pertinencia del maestrante: %s' % solicitud.perfil.persona, request, "edit")
                    return JsonResponse({"result": False, 'mensaje': 'Aprobación Existosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'revisarcronograma':
            try:
                solicitud = Solicitud.objects.get(status=True, pk=int(request.POST['id']))

                f = AprobarRechazarInformePertinenciaForm(request.POST)
                if f.is_valid():
                    if int(f.cleaned_data['estado']) == 1:
                        solicitud.estado = 18
                        solicitud.save(request)
                    else:
                        solicitud.estado = 21
                        solicitud.save(request)

                    fechaasi = datetime.now().date()
                    horaasi = str(datetime.now().time().strftime('%H:%M'))

                    eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                             observacion=f.cleaned_data['observacion'],
                                                             fecha=fechaasi,
                                                             hora=horaasi,
                                                             estado=solicitud.estado,
                                                             responsable=persona)
                    eHistorialSolicitud.save(request)

                    secretarias = Persona.objects.filter(id__in=variable_valor('PERSONAL_SECRETARIA'), status=True)

                    if int(f.cleaned_data['estado']) == 1:
                        if solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN').values_list('carrera_id', flat=True):
                            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN'
                            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                            titulo = "REVISIÓN DE CRONOGRAMA DE TITULACIÓN EXTRAORDINARIA"
                            cuerpo = 'Se informa a ' + str(dir) + ' que la experta de Secretaría Técnica de Posgrado ha aprobado el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + '. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

                            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                          dir.pk, 1, 'sga', dir)
                        elif solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD').values_list('carrera_id', flat=True):
                            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD'
                            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                            titulo = "REVISIÓN DE CRONOGRAMA DE TITULACIÓN EXTRAORDINARIA"
                            cuerpo = 'Se informa a ' + str(dir) + ' que la experta de Secretaría Técnica de Posgrado ha aprobado el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + '. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

                            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                          dir.pk, 1, 'sga', dir)
                        elif solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO').values_list('carrera_id', flat=True):
                            cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO'
                            dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                            titulo = "REVISIÓN DE CRONOGRAMA DE TITULACIÓN EXTRAORDINARIA"
                            cuerpo = 'Se informa a ' + str(dir) + ' que la experta de Secretaría Técnica de Posgrado ha aprobado el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + '. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo para continuar con el proceso.'

                            notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                          dir.pk, 1, 'sga', dir)

                    for secretaria in secretarias:
                        if int(f.cleaned_data['estado']) == 1:
                            titulo = "CRONOGRAMA DE TITULACIÓN EX. APROBADO"
                            cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.persona) + ' ha sido aprobado por la EXPERTA de Secretaría Técnica de Posgrado'
                        else:
                            titulo = "CRONOGRAMA DE TITULACIÓN EX. RECHAZADO"
                            cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.persona) + ' ha sido rechazado por la EXPERTA de Secretaría Técnica de Posgrado'

                        notificacion2(titulo,
                                      cuerpo, secretaria, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                      secretaria.pk, 1, 'sga', secretaria)

                    log(u'Revisó el cronograma de titulación extraordinaria del maestrante: %s' % solicitud.perfil.persona, request, "edit")
                    return JsonResponse({"result": False, 'mensaje': 'Aprobación Existosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'aprobarrechazarcronograma':
            try:
                solicitud = Solicitud.objects.get(status=True, pk=int(request.POST['id']))

                f = AprobarRechazarInformePertinenciaForm(request.POST)
                if f.is_valid():
                    if int(f.cleaned_data['estado']) == 1:
                        solicitud.estado = 20
                        solicitud.save(request)
                    else:
                        solicitud.estado = 21
                        solicitud.save(request)

                    fechaasi = datetime.now().date()
                    horaasi = str(datetime.now().time().strftime('%H:%M'))

                    eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                             observacion=f.cleaned_data['observacion'],
                                                             fecha=fechaasi,
                                                             hora=horaasi,
                                                             estado=solicitud.estado,
                                                             responsable=persona)
                    eHistorialSolicitud.save(request)

                    secretarias = Persona.objects.filter(id__in=variable_valor('PERSONAL_SECRETARIA'), status=True)

                    for secretaria in secretarias:
                        if int(f.cleaned_data['estado']) == 1:
                            titulo = "CRONOGRAMA DE TITULACIÓN EX. APROBADO"
                            cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.persona) + ' ha sido aprobado por el Director de Escuela'
                        else:
                            titulo = "CRONOGRAMA DE TITULACIÓN EX. RECHAZADO"
                            cuerpo = 'Se informa a todo el personal de Secretaría Técnica Posgrado que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.persona) + ' ha sido rechazado por el Director de Escuela'

                        notificacion2(titulo,
                                      cuerpo, secretaria, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                      secretaria.pk, 1, 'sga', secretaria)

                    log(u'Aprobó o rechazó el cronograma de titulación extraordinaria del maestrante: %s' % solicitud.perfil.persona, request, "edit")
                    return JsonResponse({"result": False, 'mensaje': 'Aprobación Existosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'subircertificado':
            try:
                if 'archivo' in request.FILES:
                    newfile = request.FILES['archivo']
                    if newfile.size > 10485760:
                        return JsonResponse({"result": "bad", "mensaje": u"Error, Tamaño de archivo Maximo permitido es de 10Mb"})
                    else:
                        newfiles = request.FILES['archivo']
                        newfilesd = newfiles._name
                        ext = newfilesd[newfilesd.rfind("."):]
                        if not ext.lower() == '.pdf':
                            return JsonResponse({"result": "bad", "mensaje": u"Error, solo archivos .pdf."})

                f = SubirCertificadoPersonalizadoForm(request.POST, request.FILES)
                if f.is_valid():
                    solicitud = Solicitud.objects.get(pk=int(request.POST['id']))
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("resultado", newfile._name)
                        solicitud.archivo_respuesta = newfile
                        solicitud.estado = 2
                        solicitud.save(request)

                        eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                                 observacion=f.cleaned_data['observacion'],
                                                                 fecha=datetime.now().date(),
                                                                 hora=datetime.now().time(),
                                                                 estado=solicitud.estado,
                                                                 responsable=persona)
                        eHistorialSolicitud.save(request)

                        if solicitud.servicio.categoria.roles == '3':
                            send_html_mail(u"Certificado personalizado habilitado para descarga, Secretaría Técnica Posgrado.",
                                "emails/entrega_certificado_posgrado.html",
                                {'sistema': u'SGA', 'fecha': solicitud.fecha_retiro,
                                 'hora': solicitud.hora_retiro, 'solicitud': solicitud,
                                 'persona': solicitud.perfil.persona, 'lugar': solicitud.lugar_retiro},
                                solicitud.perfil.persona.lista_emails_envio(), [], [], cuenta=CUENTAS_CORREOS[34][1])
                        else:
                            send_html_mail(u"Certificado personalizado habilitado para descarga, Secretaría General.",
                                "emails/entrega_certificado_posgrado.html",
                                {'sistema': u'SGA', 'fecha': solicitud.fecha_retiro,
                                 'hora': solicitud.hora_retiro, 'solicitud': solicitud,
                                 'persona': solicitud.perfil.persona, 'lugar': solicitud.lugar_retiro},
                                solicitud.perfil.persona.lista_emails_envio(), [], [], cuenta=CUENTAS_CORREOS[35][1])
                        log(u'Subió certificado personalizado: %s' % solicitud, request, "edit")
                        return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'subirinformetecnico':
            try:
                if 'archivo' in request.FILES:
                    newfile = request.FILES['archivo']
                    if newfile.size > 10485760:
                        return JsonResponse({"result": "bad", "mensaje": u"Error, Tamaño de archivo Maximo permitido es de 10Mb"})
                    else:
                        newfiles = request.FILES['archivo']
                        newfilesd = newfiles._name
                        ext = newfilesd[newfilesd.rfind("."):]
                        if not ext.lower() in ['.pdf', '.doc', '.docx']:
                            return JsonResponse({"result": "bad", "mensaje": u"Error, solo archivos .doc o .docx"})

                clave = None
                f = SubirInformeTecnicoPertinenciaForm(request.POST, request.FILES)
                if f.is_valid():
                    solicitud = Solicitud.objects.get(pk=int(request.POST['id']))
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("informe_tecnico_pertinencia", newfile._name)

                        if request.POST['clave'] == '':
                            solicitud.archivo_respuesta = newfile
                            solicitud.estado = 11
                            solicitud.save(request)

                            eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                                     observacion=f.cleaned_data['observacion'],
                                                                     fecha=datetime.now().date(),
                                                                     hora=datetime.now().time(),
                                                                     estado=solicitud.estado,
                                                                     responsable=persona,
                                                                     archivo=solicitud.archivo_respuesta)
                            eHistorialSolicitud.save(request)
                        else:
                            solicitud.respaldo = newfile
                            solicitud.estado = 11
                            solicitud.save(request)

                            eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                                     observacion=f.cleaned_data['observacion'],
                                                                     fecha=datetime.now().date(),
                                                                     hora=datetime.now().time(),
                                                                     estado=solicitud.estado,
                                                                     responsable=persona,
                                                                     archivo=solicitud.respaldo)
                            eHistorialSolicitud.save(request)

                        if 'clave' in request.POST and request.POST['clave'] == 'homolog':
                            solicitud.notificar_escuela()
                        log(u'Subió informe técnico de pertinencia: %s' % solicitud, request, "edit")
                        return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'subircronograma':
            try:
                if 'archivo' in request.FILES:
                    newfile = request.FILES['archivo']
                    if newfile.size > 10485760:
                        return JsonResponse({"result": "bad", "mensaje": u"Error, Tamaño de archivo Maximo permitido es de 10Mb"})
                    else:
                        newfiles = request.FILES['archivo']
                        newfilesd = newfiles._name
                        ext = newfilesd[newfilesd.rfind("."):]
                        if not ext.lower() == '.pdf':
                            return JsonResponse({"result": "bad", "mensaje": u"Error, solo archivos .pdf"})

                f = SubirCronogramaTitulacionForm(request.POST, request.FILES)
                if f.is_valid():
                    solicitud = Solicitud.objects.get(pk=int(request.POST['id']))
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("cronograma_titulacion", newfile._name)
                        solicitud.archivo_solicitud = newfile
                        solicitud.estado = 19
                        solicitud.save(request)

                        eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                                 observacion=f.cleaned_data['observacion'],
                                                                 fecha=datetime.now().date(),
                                                                 hora=datetime.now().time(),
                                                                 estado=solicitud.estado,
                                                                 responsable=persona,
                                                                 archivo=solicitud.archivo_solicitud)
                        eHistorialSolicitud.save(request)

                        experta = Persona.objects.get(status=True, pk=int(variable_valor('EXPERTA_SECRETARÍA')))

                        titulo = "REVISIÓN DE CRONOGRAMA DE TITULACIÓN EX."
                        cuerpo = 'Se informa a ' + str(experta) + ' que el personal administrativo ha subido el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + '. Por favor, realizar la respectiva revisión y la posterior aprobación o rechazo.'

                        notificacion2(titulo, cuerpo, experta, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.codigo),
                                      experta.pk, 1, 'sga', experta)

                        # if 'notificar' in request.POST:
                        #     titulo = 'CRONOGRAMA ENTREGADO'
                        #     cuerpo = 'Saludos cordiales, se comunica al maestrante ' + str(solicitud.perfil.persona) + ' que su cronograma de titulación ha sido enviado vía correo electrónico. Al dar clic en esta notificación será redirigido al módulo de Proceso de Titulación.'
                        #
                        #     notificacion4(titulo, cuerpo, solicitud.perfil.persona, None, '/alu_secretaria/mis_pedidos', solicitud.pk, 1, 'SIE', solicitud, solicitud.perfil)
                        #
                        #     send_html_mail(
                        #         u"Cronograma de Titulación Extraordinaria, Secretaría Técnica Posgrado.",
                        #         "emails/entrega_cronograma_tit_ex.html",
                        #         {'sistema': u'SGA', 'fecha': datetime.now().date(),
                        #          'hora': datetime.now().time(), 'solicitud': solicitud,
                        #          'persona': solicitud.perfil.persona},
                        #         solicitud.perfil.persona.lista_emails_envio(), [], [solicitud.archivo_solicitud], cuenta=CUENTAS_CORREOS[34][1])
                        #
                        #     if solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN').values_list('carrera_id', flat=True):
                        #         cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN'
                        #         dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                        #         titulo = "CRONOGRAMA ENTREGADO"
                        #         cuerpo = 'Se informa a ' + str(dir) + ' que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + ' ha sido entregado.'
                        #
                        #         notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.perfil.inscripcion.persona.cedula),
                        #                       dir.pk, 1, 'sga', dir)
                        #     elif solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD').values_list('carrera_id', flat=True):
                        #         cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD'
                        #         dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                        #         titulo = "CRONOGRAMA ENTREGADO"
                        #         cuerpo = 'Se informa a ' + str(dir) + ' que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + ' ha sido entregado.'
                        #
                        #         notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.perfil.inscripcion.persona.cedula),
                        #                       dir.pk, 1, 'sga', dir)
                        #     elif solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO').values_list('carrera_id', flat=True):
                        #         cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO'
                        #         dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                        #         titulo = "CRONOGRAMA ENTREGADO"
                        #         cuerpo = 'Se informa a ' + str(dir) + ' que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + ' ha sido entregado.'
                        #
                        #         notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.perfil.inscripcion.persona.cedula),
                        #                       dir.pk, 1, 'sga', dir)
                        log(u'Subió informe técnico de pertinencia: %s' % solicitud, request, "edit")
                        return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'notificarcronograma':
            try:
                f = NotificarCronogramaTitulacionForm(request.POST)
                if f.is_valid():
                    solicitud = Solicitud.objects.get(pk=int(request.POST['id']))
                    solicitud.estado = 16
                    solicitud.save(request)

                    eHistorialSolicitud = HistorialSolicitud(solicitud=solicitud,
                                                             observacion=f.cleaned_data['observacion'],
                                                             fecha=datetime.now().date(),
                                                             hora=datetime.now().time(),
                                                             estado=solicitud.estado,
                                                             responsable=persona,
                                                             archivo=solicitud.archivo_solicitud,
                                                             urldrive=f.cleaned_data['url'])
                    eHistorialSolicitud.save(request)

                    titulo = 'CRONOGRAMA ENTREGADO'
                    cuerpo = 'Saludos cordiales, se comunica al maestrante ' + str(solicitud.perfil.persona) + ' que su cronograma de titulación extraordinaria ha sido subido al SGA en el módulo Servicios de secretaría en la ventana de Mis pediddos, y también ha sido enviado vía correo electrónico. Al dar clic en esta notificación será redirigido al módulo de Proceso de Titulación.'

                    notificacion4(titulo, cuerpo, solicitud.perfil.persona, None, '/alu_tematitulacionposgrado', solicitud.pk, 1, 'SIE', solicitud, solicitud.perfil)

                    send_html_mail(
                        u"Cronograma de Titulación Extraordinaria, Secretaría Técnica Posgrado.",
                        "emails/entrega_cronograma_tit_ex.html",
                        {'sistema': u'SGA', 'fecha': datetime.now().date(),
                         'hora': datetime.now().time(), 'solicitud': solicitud,
                         'persona': solicitud.perfil.persona, 'observacion': f.cleaned_data['observacion'],
                         'url':f.cleaned_data['url']},
                        solicitud.perfil.persona.lista_emails_envio(), [], [solicitud.archivo_solicitud], cuenta=CUENTAS_CORREOS[34][1])

                    if solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN').values_list('carrera_id', flat=True):
                        cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN'
                        dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                        titulo = "CRONOGRAMA ENTREGADO"
                        cuerpo = 'Se informa a ' + str(dir) + ' que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + ' ha sido entregado.'

                        notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.perfil.inscripcion.persona.cedula),
                                      dir.pk, 1, 'sga', dir)
                    elif solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD').values_list('carrera_id', flat=True):
                        cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD'
                        dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                        titulo = "CRONOGRAMA ENTREGADO"
                        cuerpo = 'Se informa a ' + str(dir) + ' que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + ' ha sido entregado.'

                        notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.perfil.inscripcion.persona.cedula),
                                      dir.pk, 1, 'sga', dir)
                    elif solicitud.perfil.inscripcion.carrera.id in PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO').values_list('carrera_id', flat=True):
                        cargo = 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO'
                        dir = Persona.objects.filter(usuario__groups__name=cargo).order_by('id').first()
                        titulo = "CRONOGRAMA ENTREGADO"
                        cuerpo = 'Se informa a ' + str(dir) + ' que el cronograma de titulación extraordinaria del maestrante ' + str(solicitud.perfil.inscripcion.persona) + ' ha sido entregado.'

                        notificacion2(titulo, cuerpo, dir, None, '/adm_secretaria?action=versolicitudes&id=' + str(solicitud.servicio.categoria.id) + '&ids=0&s=' + str(solicitud.perfil.inscripcion.persona.cedula),
                                      dir.pk, 1, 'sga', dir)
                    log(u'Notificó el cronograma de titulación extraordinaria del maestrante: %s' % solicitud, request, "edit")
                    return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'addformato':
            try:
                lista = ''
                if 'archivo' in request.FILES:
                    newfile = request.FILES['archivo']
                    if newfile.size > 10485760:
                        return JsonResponse({"result": "bad", "mensaje": u"Error, Tamaño de archivo Maximo permitido es de 10Mb"})
                    else:
                        newfiles = request.FILES['archivo']
                        newfilesd = newfiles._name
                        ext = newfilesd[newfilesd.rfind("."):]
                        if not ext.lower() in ['.doc', '.docx']:
                            return JsonResponse({"result": "bad", "mensaje": u"Error, solo archivos .doc o .docx"})

                if request.POST['idc'] == '1':
                    lista = '3'
                elif request.POST['idc'] == '4':
                    lista = '2'
                elif request.POST['idc'] == '5':
                    lista = '1'

                f = SubirFormatoCertificadoForm(request.POST, request.FILES)
                if f.is_valid():
                    formato = FormatoCertificado(certificacion=f.cleaned_data['certificacion'],
                                                 tipo_origen=f.cleaned_data['tipo'],
                                                 roles=lista)
                    formato.save(request)

                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("resultado", newfile._name)
                        formato.formato = newfile
                        formato.save(request)

                        log(u'Adicionó formato de certificado: %s' % formato, request, "add")
                        return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'addactividad':
            try:
                f = AdicionarActividadCronogramaForm(request.POST)
                if f.is_valid():
                    actividad = ActividadCronogramaTitulacion(nombre=f.cleaned_data['nombre'],
                                                            descripcion=f.cleaned_data['descripcion'])
                    actividad.save(request)
                    log(u'Adicionó actividad de cronograma de titulación: %s' % actividad, request, "add")
                    return JsonResponse({"result": False, 'mensaje': 'Adición Exitosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'addactividadtituex':
            try:
                solicitante = Solicitud.objects.get(status=True, pk=int(request.GET['id']))
                f = ActividadCronogramaTitulacionForm(request.POST)
                if f.is_valid():
                    if not DetalleActividadCronogramaTitulacion.objects.filter(status=True, solicitud=solicitante, actividad=f.cleaned_data['actividad']).exists():
                        if f.cleaned_data['inicio'] <= f.cleaned_data['fin']:
                            deta = DetalleActividadCronogramaTitulacion(solicitud=solicitante,
                                                                       periodo=f.cleaned_data['periodo'],
                                                                       actividad=f.cleaned_data['actividad'],
                                                                       inicio=f.cleaned_data['inicio'],
                                                                       fin=f.cleaned_data['fin'],
                                                                       observacion=f.cleaned_data['observacion'])
                            deta.save(request)
                            log(u'Adicionó actividad de cronograma de titulación del maestrante: %s' % deta.solicitud, request, "add")
                            return JsonResponse({"result": False, 'mensaje': 'Adición Exitosa'})
                        else:
                            return JsonResponse({"result": "bad", "mensaje": u"La fecha de inicio debe ser menor o igual a la de fin"})
                    else:
                        return JsonResponse({"result": "bad", "mensaje": u"Esta actividad ya ha sido ingresada"})
                        # raise NameError(u"Esta actividad ya ha sido ingresada")
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'editactividad':
            try:
                actividad = ActividadCronogramaTitulacion.objects.get(pk=int(request.POST['id']))
                f = AdicionarActividadCronogramaForm(request.POST, request.FILES)
                if f.is_valid():
                    actividad.nombre = f.cleaned_data['nombre']
                    actividad.descripcion = f.cleaned_data['descripcion']
                    actividad.save(request)
                    log(u'Editó actividad de cronograma de titulación: %s' % actividad, request, "edit")
                    return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'editactividadtituex':
            try:
                detalle = DetalleActividadCronogramaTitulacion.objects.get(pk=int(request.POST['id']))
                f = ActividadCronogramaTitulacionForm(request.POST)
                if f.is_valid():
                    if not DetalleActividadCronogramaTitulacion.objects.filter(status=True, solicitud=detalle.solicitud, actividad=f.cleaned_data['actividad']).exclude(pk=detalle.id).exists():
                        detalle.periodo = f.cleaned_data['periodo']
                        detalle.actividad = f.cleaned_data['actividad']
                        detalle.inicio = f.cleaned_data['inicio']
                        detalle.fin = f.cleaned_data['fin']
                        detalle.observacion = f.cleaned_data['observacion']
                        detalle.save(request)
                        log(u'Editó actividad de cronograma de titulación del maestrante: %s' % detalle.solicitud.perfil.inscripcion.persona, request, "edit")
                        return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                    else:
                        return JsonResponse({"result": "bad", "mensaje": u"Esta actividad ya ha sido ingresada"})
                else:
                    return JsonResponse({'error': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'pdfcronogramatituex':
            try:
                result = cronogramatituex(request.POST['id'])
                return JsonResponse({"result": "ok", 'url': result})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'firmarcertificadomasivo':
            try:
                firma = request.FILES["firma"]
                passfirma = request.POST['palabraclave']
                certificadoselect = request.POST['ids'].split(',')
                bandera = False
                p12 = None
                certificado = None
                listainscripcion = []
                nombresmae = ''
                conterrornombre = 0
                conteoerror = 0
                bytes_certificado = firma.read()
                extension_certificado = os.path.splitext(firma.name)[1][1:]
                palabras = FirmaCertificadoSecretaria.objects.get(status=True, activo=True).nombrefirma
                # palabras = 'Abg. Stefania Velasco Neira, Mgtr.'

                secretaria = Persona.objects.get(pk=variable_valor('SECRETARIA_G'))
                for certi in certificadoselect:
                    certificado = Solicitud.objects.get(pk=certi)
                    if not certificado.respaldo:
                        certificado.respaldo = certificado.archivo_respuesta
                        certificado.save(request)
                    documento_a_firmar = certificado.archivo_respuesta
                    # obtener la posicion xy de la firma del doctor en el pdf
                    y, numpaginafirma = obtener_posicion_y(documento_a_firmar.url, palabras)
                    # FIN obtener la posicion y
                    if y:
                        datau = JavaFirmaEc(
                            archivo_a_firmar=documento_a_firmar, archivo_certificado=bytes_certificado,
                            extension_certificado=extension_certificado,
                            password_certificado=passfirma,
                            page=numpaginafirma, reason='Certificado firmado', lx=260, ly=y)
                        if datau:
                            if datau.datos_del_certificado['cedula'] == secretaria.cedula:
                                generar_archivo_firmado = io.BytesIO()
                                generar_archivo_firmado.write(datau.sign_and_get_content_bytes())
                                generar_archivo_firmado.seek(0)
                                extension = documento_a_firmar.name.split('.')
                                tam = len(extension)
                                exte = extension[tam - 1]
                                nombrefile_ = remover_caracteres_tildes_unicode(
                                    remover_caracteres_especiales_unicode(documento_a_firmar.name)).replace('-', '_').replace('.pdf', '')
                                _name = 'rpt_certificado' + str(certificado.id)
                                file_obj = DjangoFile(generar_archivo_firmado, name=f"{remover_caracteres_especiales_unicode(_name)}_firmado.pdf")
                                certificado.archivo_respuesta = file_obj
                                certificado.certificadofirmado = True
                                certificado.estado = 2
                                certificado.save(request)
                                detalleevidencia = HistorialSolicitud(solicitud_id=certificado.id)
                                detalleevidencia.save(request)
                                detalleevidencia.observacion = 'Certificado firmado'
                                detalleevidencia.responsable = persona
                                detalleevidencia.estado = 2
                                detalleevidencia.fecha = datetime.now().date()
                                detalleevidencia.hora = datetime.now().time()
                                detalleevidencia.save(request)
                                log(u'Masivo Firmó Documento: {}'.format(nombrefile_), request, "add")
                                listainscripcion.append(certificado.perfil.inscripcion.id)
                                nombresmae += '%s, ' % certificado.perfil.inscripcion.persona

                                integrante = Persona.objects.get(status=True, pk=certificado.perfil.inscripcion.persona.id)

                                asunto = u"CERTIFICADO FIRMADO"
                                cuerpo = f'Se le comunica que su certificado ha sido firmado y entregado correctamente. Clic aqu[i, para ser redirigido a la venta mis pedidos.'

                                notificacion3(asunto,
                                              cuerpo, certificado.perfil.persona, None,
                                              '/alu_secretaria/mis_pedidos',
                                              certificado.pk, 1, 'SIE', certificado, certificado.perfil, request)
                            else:
                                return JsonResponse({"result": "bad", "mensaje": f"La firma ingresada no pertenece a la Secretaria General {secretaria} con número de cédula {secretaria.cedula}."})
                        else:
                            conteoerror += 1
                            if certificado.certificadofirmado:
                                certificado.certificadofirmado = False
                            certificado.estado = 7
                            certificado.save(request)

                            detalleevidencia = HistorialSolicitud(solicitud_id=certificado.id)
                            detalleevidencia.save(request)
                            detalleevidencia.observacion = 'Certificado con inconsistencia en la firma'
                            detalleevidencia.responsable = persona
                            detalleevidencia.estado = 7
                            detalleevidencia.fecha = datetime.now().date()
                            detalleevidencia.hora = datetime.now().time()
                            detalleevidencia.save(request)
                    else:
                        conteoerror += 1
                        conterrornombre += 1
                        if certificado.certificadofirmado:
                            certificado.certificadofirmado = False
                        certificado.estado = 7
                        certificado.save(request)

                        detalleevidencia = HistorialSolicitud(solicitud_id=certificado.id)
                        detalleevidencia.save(request)
                        detalleevidencia.observacion = 'El nombre de la secretaria general en la firma no es el correcto.'
                        detalleevidencia.responsable = persona
                        detalleevidencia.estado = 7
                        detalleevidencia.fecha = datetime.now().date()
                        detalleevidencia.hora = datetime.now().time()
                        detalleevidencia.save(request)
                    time.sleep(2)
                if listainscripcion:
                    cuerpo = ('Documentos firmados con éxito: %s' % nombresmae)
                    notificacion('Firma electrónica SGA', cuerpo, persona, None,
                                 '/adm_secretaria?action=listadoafirmar&id=1', None, 1, 'sga', certificado,
                                 request)
                    if conteoerror > 0:
                        messages.success(request, f'Documentos firmados con éxito. %s' % (
                            'Existieron %s contratos con inconsistencia que no fueron firmados. Enviados a comercialización: %s' % (
                            conteoerror, conterrornombre) if conterrornombre > 0 else ''))
                    else:
                        messages.success(request, f'Documentos firmados con éxito')
                else:
                    if conteoerror > 0:
                        messages.warning(request, f'%s' % (
                            'Existieron %s certificados(s) con inconsistencia que no fueron firmados.' % conteoerror if conteoerror > 0 else ''))
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error: %s" % ex})

        elif action == 'firmarcertificadoindividual':
            try:
                firma = request.FILES["firma"]
                passfirma = request.POST['palabraclave']
                bandera = False
                p12 = None
                certificado = None
                listainscripcion = []
                nombresmae = ''
                conterrornombre = 0
                conteoerror = 0
                bytes_certificado = firma.read()
                extension_certificado = os.path.splitext(firma.name)[1][1:]
                palabras = FirmaCertificadoSecretaria.objects.get(status=True, activo=True).nombrefirma
                # palabras = 'Abg. Stefania Velasco Neira, Mgtr.'

                secretaria = Persona.objects.get(pk=variable_valor('SECRETARIA_G'))
                certificado = Solicitud.objects.get(pk=int(request.POST['id']))
                if not certificado.respaldo:
                    certificado.respaldo = certificado.archivo_respuesta
                    certificado.save(request)
                documento_a_firmar = certificado.archivo_respuesta
                # obtener la posicion xy de la firma del doctor en el pdf
                y, numpaginafirma = obtener_posicion_y(documento_a_firmar.url, palabras)
                # FIN obtener la posicion y
                if y:
                    datau = JavaFirmaEc(
                        archivo_a_firmar=documento_a_firmar, archivo_certificado=bytes_certificado,
                        extension_certificado=extension_certificado,
                        password_certificado=passfirma,
                        page=numpaginafirma, reason='Certificado firmado', lx=260, ly=y)
                    if datau:
                        if datau.datos_del_certificado['cedula'] == secretaria.cedula:
                            generar_archivo_firmado = io.BytesIO()
                            generar_archivo_firmado.write(datau.sign_and_get_content_bytes())
                            generar_archivo_firmado.seek(0)
                            extension = documento_a_firmar.name.split('.')
                            tam = len(extension)
                            exte = extension[tam - 1]
                            nombrefile_ = remover_caracteres_tildes_unicode(
                                remover_caracteres_especiales_unicode(documento_a_firmar.name)).replace('-', '_').replace('.pdf', '')
                            _name = 'rpt_certificado' + str(certificado.id)
                            file_obj = DjangoFile(generar_archivo_firmado, name=f"{remover_caracteres_especiales_unicode(_name)}_firmado.pdf")
                            certificado.archivo_respuesta = file_obj
                            certificado.certificadofirmado = True
                            certificado.estado = 2
                            certificado.save(request)
                            detalleevidencia = HistorialSolicitud(solicitud_id=certificado.id)
                            detalleevidencia.save(request)
                            detalleevidencia.observacion = 'Certificado firmado'
                            detalleevidencia.responsable = persona
                            detalleevidencia.estado = 2
                            detalleevidencia.fecha = datetime.now().date()
                            detalleevidencia.hora = datetime.now().time()
                            detalleevidencia.save(request)
                            log(u'Masivo Firmó Documento: {}'.format(nombrefile_), request, "add")
                            listainscripcion.append(certificado.perfil.inscripcion.id)
                            nombresmae += '%s, ' % certificado.perfil.inscripcion.persona

                            integrante = Persona.objects.get(status=True, pk=certificado.perfil.inscripcion.persona.id)

                            asunto = u"CERTIFICADO FIRMADO"
                            cuerpo = f'Se le comunica que su certificado ha sido firmado y entregado correctamente. Clic aqu[i, para ser redirigido a la venta mis pedidos.'

                            notificacion3(asunto,
                                          cuerpo, certificado.perfil.persona, None,
                                          '/alu_secretaria/mis_pedidos',
                                          certificado.pk, 1, 'SIE', certificado, certificado.perfil, request)
                        else:
                            return JsonResponse({"result": "bad", "mensaje": f"La firma ingresada no pertenece a la Secretaria General {secretaria} con número de cédula {secretaria.cedula}."})
                    else:
                        conteoerror += 1
                        if certificado.certificadofirmado:
                            certificado.certificadofirmado = False
                        certificado.estado = 7
                        certificado.save(request)

                        detalleevidencia = HistorialSolicitud(solicitud_id=certificado.id)
                        detalleevidencia.save(request)
                        detalleevidencia.observacion = 'Certificado con inconsistencia en la firma'
                        detalleevidencia.responsable = persona
                        detalleevidencia.estado = 7
                        detalleevidencia.fecha = datetime.now().date()
                        detalleevidencia.hora = datetime.now().time()
                        detalleevidencia.save(request)
                else:
                    conteoerror += 1
                    conterrornombre += 1
                    if certificado.certificadofirmado:
                        certificado.certificadofirmado = False
                    certificado.estado = 7
                    certificado.save(request)

                    detalleevidencia = HistorialSolicitud(solicitud_id=certificado.id)
                    detalleevidencia.save(request)
                    detalleevidencia.observacion = 'El nombre de la secretaria general en la firma no es el correcto.'
                    detalleevidencia.responsable = persona
                    detalleevidencia.estado = 7
                    detalleevidencia.fecha = datetime.now().date()
                    detalleevidencia.hora = datetime.now().time()
                    detalleevidencia.save(request)
                    time.sleep(2)
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error: %s" % ex})

        elif action == 'informarasignaturas':
            try:
                eSolicitud = Solicitud.objects.get(pk=int(request.POST['id']))

                eSolicitudAsignaturas = SolicitudAsignatura.objects.filter(status=True, solicitud=eSolicitud)

                idam = request.POST['ids'].split(',')

                lisid = []
                for id in idam:
                    if int(id) in eSolicitudAsignaturas.values_list('asignaturamalla__id', flat=True):
                        soli = SolicitudAsignatura.objects.filter(status=True, asignaturamalla__id=id, solicitud=eSolicitud).first()
                        soli.estado = 2
                        soli.save(request)
                        lisid.append(soli.id)

                        log(u'Marcó como favorable la asignatura: %s' % SolicitudAsignatura, request, "edit")
                    else:
                        asigma = AsignaturaMalla.objects.get(pk=id)
                        soli = SolicitudAsignatura(solicitud=eSolicitud,
                                                   asignaturamalla=asigma,
                                                   estado=2)
                        soli.save(request)
                        lisid.append(soli.id)

                        log(u'Marcó como favorable la asignatura: %s' % SolicitudAsignatura, request, "add")

                for eSoli in eSolicitudAsignaturas.exclude(id__in=lisid):
                    eSoli.estado = 3
                    eSoli.save(request)

                    log(u'Marcó como NO favorable la asignatura: %s' % SolicitudAsignatura, request, "edit")

                obs = f'Ha marcadado como favorables las asignaturas: {eSolicitud.lista_asignaturas_favorables()} y como NO favorable las asignaturas: {eSolicitud.lista_asignaturas_no_favorables()}'
                if not HistorialSolicitud.objects.filter(status=True, solicitud=eSolicitud, estado=24):
                    eHistorialSolicitud = HistorialSolicitud(solicitud=eSolicitud,
                                                             observacion=obs,
                                                             fecha=datetime.now().date(),
                                                             hora=datetime.now().time(),
                                                             estado=24,
                                                             responsable=persona,
                                                             archivo=eSolicitud.archivo_solicitud)
                    eHistorialSolicitud.save(request)
                else:
                    histo = HistorialSolicitud.objects.filter(status=True, solicitud=eSolicitud).first()
                    histo.fecha = datetime.now().date()
                    histo.hora = datetime.now().time()
                    histo.observacion = obs
                    histo.archivo = eSolicitud.archivo_solicitud
                    histo.save(request)

                eSolicitud.estado = 24
                eSolicitud.visible = True
                eSolicitud.save(request)

                titulo = 'RESULTADOS DE SU SOLICITUD DE HOMOLOGACIÓN INTERNA POSGRADO'
                notificacion4(titulo, obs, eSolicitud.perfil.persona, None, '/alu_secretaria/service/asignaturashomologa', eSolicitud.pk, 1, 'SIE', eSolicitud, eSolicitud.perfil)
                return JsonResponse({"result": 'ok', "mensaje": u"Asignaturas procesadas"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": 'bad', "mensaje": f"Ocurrio un error al eliminar: {ex.__str__()}"})

        elif action == 'changeesfavorable':
            try:
                eSolicitudAsignatura = SolicitudAsignatura.objects.get(status=True, pk=request.POST['idreq'])
                if eSolicitudAsignatura.estado == 2:
                    eSolicitudAsignatura.estado = 3
                    log(u'Marcó como NO favorable la asignatura: %s' % eSolicitudAsignatura, request, "edit")
                else:
                    eSolicitudAsignatura.estado = 2
                    log(u'Marcó como favorable la asignatura: %s' % eSolicitudAsignatura, request, "edit")

                eSolicitudAsignatura.save(request)
                eSolicitudAsignatura.solicitud.visible = True
                eSolicitudAsignatura.solicitud.save(request)
                return JsonResponse({'result': 'ok', 'valor': eSolicitudAsignatura.estado})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'versolicitudes':
                try:
                    data['title'] = u'Gestión de solicitudes'
                    es_director = False
                    es_coordi = False
                    es_secretaria = False
                    es_experta = False

                    experta = Persona.objects.get(status=True, pk=int(variable_valor('EXPERTA_SECRETARÍA')))

                    if persona.id == experta.id:
                        es_experta = True

                    cate = CategoriaServicio.objects.get(status=True, id=int(request.GET['id']))

                    if persona.id in Persona.objects.filter(id__in=variable_valor('PERSONAL_SECRETARIA'), status=True).values_list('id', flat=True):
                        es_secretaria = True

                    es_coordinador = ContratoDip.objects.filter(status=True, cargo__nombre__icontains='COORDINADOR',
                                                               persona=persona,
                                                               fechainicio__lte=datetime.now().date(),
                                                               fechafin__gte=datetime.now().date()).values_list('id', flat=True)

                    if 'SOLO_TITULACION_EX' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        if CohorteMaestria.objects.filter(status=True, coordinador=persona).exists():
                            idcarreras = CohorteMaestria.objects.filter(status=True, coordinador=persona).values_list('maestriaadmision__carrera__id', flat=True).order_by('maestriaadmision__carrera__id').distinct()
                            filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']), perfil__inscripcion__carrera__id__in=idcarreras)
                            es_coordi = True
                        else:
                            if es_coordinador:
                                es_coordi = True
                                carrreras = ContratoCarrera.objects.filter(status=True, contrato__id__in=es_coordinador).values_list('carrera_id', flat=True)
                                filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']), perfil__inscripcion__carrera__id__in=carrreras)
                            else:
                                filtros = Q(pk=0)

                    elif 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        es_director = True
                        carreras = PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN').values_list('carrera_id', flat=True)
                        filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']),
                                    perfil__inscripcion__carrera__id__in=carreras, estado__in=[11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
                        data['eCarreras'] = carreras
                    elif 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        es_director = True
                        carreras = PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD').values_list('carrera_id', flat=True)
                        filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']),
                                    perfil__inscripcion__carrera__id__in=carreras, estado__in=[11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
                        data['eCarreras'] = carreras
                    elif 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        es_director = True
                        carreras = PerfilAccesoUsuario.objects.filter(status=True, grupo__name__exact='DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO').values_list('carrera_id', flat=True)
                        filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']),
                                    perfil__inscripcion__carrera__id__in=carreras, estado__in=[11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
                        data['eCarreras'] = carreras
                    elif 'SOLICITUDES_FACI' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        if cate.roles == '1':
                            carreras = Carrera.objects.filter(status=True, coordinacionvalida__id=4)
                        else:
                          carreras = Carrera.objects.filter(status=True, coordinacion__id=4)
                        filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']), perfil__inscripcion__carrera__id__in=carreras.values_list('id', flat=True))
                        data['eCarreras'] = carreras
                    elif 'SOLICITUDES_FASO' in persona.usuario.groups.all().distinct().values_list('name', flat=True) and 'SOLICITUDES_FACAC' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        if cate.roles == '1':
                            carreras = Carrera.objects.filter(status=True, coordinacionvalida__id__in=[3, 2])
                        else:
                            if 'SOLICITUDES_ASISTENTE_1' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                                carreras = Carrera.objects.filter(status=True, id__in=[134, 138, 244, 7, 130, 160, 246, 89, 190, 161, 6, 162,
                                                                    92, 141, 95, 225, 140, 61])
                            if 'SOLICITUDES_ASISTENTE_2' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                                carreras = Carrera.objects.filter(status=True, id__in=[188, 9, 145, 91, 164, 8, 43, 165, 11, 128, 158, 245,
                                                                    248, 10, 88, 144, 16, 12, 126, 242, 163, 93])
                            if 'SOLICITUDES_ASISTENTE_3' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                                carreras = Carrera.objects.filter(status=True, id__in=[132, 136, 243, 18, 137, 58, 152, 5, 159, 15, 131, 143,
                                                                    247, 80])
                        filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']), perfil__inscripcion__carrera__id__in=carreras.values_list('id', flat=True))
                        data['eCarreras'] = carreras
                    elif 'SOLICITUDES_FACE' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        if cate.roles == '1':
                            carreras = Carrera.objects.filter(status=True, coordinacionvalida__id=5)
                        else:
                            carreras = Carrera.objects.filter(status=True, coordinacion__id=5)
                        filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']), perfil__inscripcion__carrera__id__in=carreras.values_list('id', flat=True))
                        data['eCarreras'] = carreras
                    elif 'SOLICITUDES_FACS' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        if cate.roles == '1':
                            carreras = Carrera.objects.filter(status=True, coordinacionvalida__id=1)
                        else:
                            carreras = Carrera.objects.filter(status=True, coordinacion__id=1)
                        filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']), perfil__inscripcion__carrera__id__in=carreras.values_list('id', flat=True))
                        data['eCarreras'] = carreras
                    else:
                        filtros = Q(pk__gte=0, servicio__categoria__id=int(request.GET['id']))
                        if cate.roles == '3':
                            data['eCarreras'] = Carrera.objects.filter(status=True, coordinacion__id=7).order_by('-id').distinct()
                        elif cate.roles == '1':
                            data['eCarreras'] = Carrera.objects.filter(status=True, coordinacion__id=9).order_by('-id').distinct()
                        else:
                            data['eCarreras'] = Carrera.objects.filter(status=True).exclude(coordinacion__id=7).order_by('-id').distinct()

                    s = request.GET.get('s', '')
                    ids = request.GET.get('ids', '0')
                    idc = request.GET.get('idc', '0')
                    ide = request.GET.get('ide', '0')
                    url_vars = '&action=versolicitudes&id=' + request.GET['id']

                    if s:
                        filtros = filtros & (Q(servicio__nombre__icontains=s) | Q(perfil__persona__nombres__contains=s) | Q(perfil__persona__apellido1__contains=s) | Q(perfil__persona__apellido2__contains=s) | Q(perfil__persona__cedula__contains=s) | Q(perfil__persona__pasaporte__contains=s) | Q(codigo__contains=s))
                        ss = s.split(" ")
                        if ss.__len__() == 2:
                            filtros = filtros & (Q(perfil__persona__apellido1__contains=ss[0]) & Q(perfil__persona__apellido2__contains=ss[1]))
                        data['s'] = f"{s}"
                        url_vars += f"&s={s}"

                    if int(ids):
                        filtros = filtros & (Q(servicio_id=ids))
                        data['ids'] = f"{ids}"
                        url_vars += f"&ids={ids}"

                    if int(idc):
                        filtros = filtros & (Q(perfil__inscripcion__carrera__id=idc))
                        data['idc'] = f"{idc}"
                        url_vars += f"&idc={idc}"

                    if int(ide):
                        if int(ide) == 30:
                            filtros = filtros & (Q(firmadoec=False))
                            data['ide'] = f"{ide}"
                            url_vars += f"&ide={ide}"
                        else:
                            filtros = filtros & (Q(estado=ide))
                            data['ide'] = f"{ide}"
                            url_vars += f"&ide={ide}"

                    eSolicitudes = Solicitud.objects.filter(filtros).order_by('-fecha', '-hora')
                    paging = MiPaginador(eSolicitudes, 25)
                    p = 1
                    try:
                        paginasesion = 1
                        if 'paginador' in request.session:
                            paginasesion = int(request.session['paginador'])
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        else:
                            p = paginasesion
                        try:
                            page = paging.page(p)
                        except:
                            p = 1
                        page = paging.page(p)
                    except:
                        page = paging.page(p)
                    request.session['paginador'] = p
                    data['paging'] = paging
                    data['page'] = page
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['eSolicitudes'] = page.object_list
                    data['url_vars'] = url_vars
                    data['eServicios'] = Servicio.objects.values_list('id', 'nombre').filter(status=True, categoria__id=int(request.GET['id'])).distinct()
                    data['id'] = int(request.GET['id'])
                    data['eTotal'] = eSolicitudes.count()
                    data['eSolicitados'] = eSolicitudes.filter(estado=1).count()
                    data['eEntregados'] = eSolicitudes.filter(estado=2).count()
                    data['ePendientes'] = eSolicitudes.filter(estado=3).count()
                    data['ePagados'] = eSolicitudes.filter(estado=4).count()
                    data['eReasignados'] = eSolicitudes.filter(estado=5).count()
                    data['eAsignados'] = eSolicitudes.filter(estado=6).count()
                    data['eRechazados'] = eSolicitudes.filter(estado=7).count()
                    data['eVencidos'] = eSolicitudes.filter(estado=9).count()
                    data['eEliminados'] = eSolicitudes.filter(estado=8).count()
                    data['cate'] = cate
                    data['es_director'] = es_director
                    data['es_coordinador'] = es_coordi
                    data['es_secretaria'] = es_secretaria
                    data['es_experta'] = es_experta

                    if cate.id == 7:
                        return render(request, "adm_secretaria/solicitudeshomoi.html", data)
                    else:
                        return render(request, "adm_secretaria/versolicitudes.html", data)
                except Exception as ex:
                    pass

            elif action == 'verformatoscertificados':
                try:
                    data['title'] = u'Formatos de certificados'
                    if int(request.GET['id']) == 1:
                        filtros = Q(status=True, roles=3)
                    elif int(request.GET['id']) == 4:
                        filtros = Q(status=True, roles=2)
                    elif int(request.GET['id']) == 5:
                        filtros = Q(status=True, roles=1)
                    else:
                        filtros = Q(status=True)

                    s = request.GET.get('s', '')
                    idt = request.GET.get('idt', '0')
                    url_vars = '&action=verformatoscertificados&id=' + request.GET['id']

                    if s:
                        filtros = filtros & (Q(certificacion__icontains=s))
                        data['s'] = f"{s}"
                        url_vars += f"&s={s}"

                    if int(idt):
                        filtros = filtros & (Q(tipo_origen=idt))
                        data['idt'] = f"{idt}"
                        url_vars += f"&idt={idt}"

                    eFormatos = FormatoCertificado.objects.filter(filtros).order_by('-id')
                    paging = MiPaginador(eFormatos, 25)
                    p = 1
                    try:
                        paginasesion = 1
                        if 'paginador' in request.session:
                            paginasesion = int(request.session['paginador'])
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        else:
                            p = paginasesion
                        try:
                            page = paging.page(p)
                        except:
                            p = 1
                        page = paging.page(p)
                    except:
                        page = paging.page(p)
                    request.session['paginador'] = p
                    data['paging'] = paging
                    data['page'] = page
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['eFormatos'] = page.object_list
                    data['url_vars'] = url_vars
                    data['id'] = int(request.GET['id'])
                    return render(request, "adm_secretaria/verformatoscertificados.html", data)
                except Exception as ex:
                    pass

            elif action == 'listadoafirmar':
                try:
                    data['title'] = u'Certificaciones a firmar'

                    search = request.GET.get('s', None)
                    ide = request.GET.get('ide', '0')
                    idt = request.GET.get('idt', '0')
                    url_vars = '&action=listadoafirmar'

                    filtro = Q(status=True, estado__in=[22, 7]) | Q(status=True, certificadofirmado=True)
                    # filtro = Q(status=True, servicio__categoria__id=int(request.GET['id']), estado__in=[22, 7]) | Q(status=True, servicio__categoria__id=int(request.GET['id']), certificadofirmado=True)

                    if search:
                        data['search'] = search
                        ss = search.split(' ')
                        if len(ss) == 1:
                            filtro = filtro & (Q(perfil__inscripcion__persona__apellido1__icontains=search) |
                                                     Q(perfil__inscripcion__persona__apellido2__icontains=search) |
                                                     Q(perfil__inscripcion__persona__nombres__icontains=search) |
                                                     Q(perfil__inscripcion__persona__cedula__icontains=search))
                            url_vars += "&s={}".format(search)
                        elif len(ss) == 2:
                            filtro = filtro & (Q(perfil__inscripcion__persona__apellido1__icontains=ss[0]) &
                                                     Q(perfil__inscripcion__persona__apellido2__icontains=ss[1]))
                            url_vars += "&s={}".format(ss)
                        else:
                            filtro = filtro & (Q(perfil__inscripcion__persona__apellido1__icontains=ss[0]) &
                                                Q(perfil__inscripcion__persona__apellido2__icontains=ss[1]) &
                                               Q(perfil__inscripcion__persona__nombres__icontains=ss[2]))
                            url_vars += "&s={}".format(ss)

                    if int(ide):
                        if int(ide) == 1:
                            filtro = filtro & (Q(certificadofirmado=True))
                            data['ide'] = f"{ide}"
                            url_vars += f"&ide={ide}"
                        elif int(ide) == 2:
                            filtro = filtro & (Q(certificadofirmado=False))
                            data['ide'] = f"{ide}"
                            url_vars += f"&ide={ide}"

                    if int(idt):
                        cor = [1, 2, 3, 4, 5, 7]
                        if int(idt) == 1:
                            cor = [7]
                        elif int(idt) == 2:
                            cor = [1, 2, 3, 4, 5]
                        filtro = filtro & (Q(perfil__inscripcion__carrera__coordinacion__in=cor))
                        data['idt'] = f"{idt}"
                        url_vars += f"&idt={idt}"

                    eSolicitudes = Solicitud.objects.filter(filtro).order_by('-id')
                    paging = MiPaginador(eSolicitudes, 25)
                    p = 1
                    try:
                        paginasesion = 1
                        if 'paginador' in request.session:
                            paginasesion = int(request.session['paginador'])
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        else:
                            p = paginasesion
                        try:
                            page = paging.page(p)
                        except:
                            p = 1
                        page = paging.page(p)
                    except:
                        page = paging.page(p)
                    request.session['paginador'] = p
                    data['paging'] = paging
                    data['page'] = page
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['eSolicitudes'] = page.object_list
                    data['url_vars'] = url_vars
                    # data['id'] = int(request.GET['id'])
                    data['Total'] = eSolicitudes.count()
                    data['Firmados'] = eSolicitudes.filter(certificadofirmado=True).count()
                    data['Nofirmados'] = eSolicitudes.filter(certificadofirmado=False).count()
                    return render(request, "adm_secretaria/listadoafirmar.html", data)
                except Exception as ex:
                    pass

            elif action == 'cronogramatitulacion':
                try:
                    data['title'] = u'Actividades de cronograma de titulación extraordinaria'
                    filtros = Q(status=True)

                    s = request.GET.get('s', '')
                    idt = request.GET.get('idt', '0')
                    url_vars = '&action=cronogramatitulacion'

                    if s:
                        filtros = filtros & (Q(nombre__icontains=s) | Q(descripcion__icontains=s))
                        data['s'] = f"{s}"
                        url_vars += f"&s={s}"

                    eActividades = ActividadCronogramaTitulacion.objects.filter(filtros).order_by('-id')
                    paging = MiPaginador(eActividades, 25)
                    p = 1
                    try:
                        paginasesion = 1
                        if 'paginador' in request.session:
                            paginasesion = int(request.session['paginador'])
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        else:
                            p = paginasesion
                        try:
                            page = paging.page(p)
                        except:
                            p = 1
                        page = paging.page(p)
                    except:
                        page = paging.page(p)
                    request.session['paginador'] = p
                    data['paging'] = paging
                    data['page'] = page
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['eActividades'] = page.object_list
                    data['url_vars'] = url_vars
                    return render(request, "adm_secretaria/cronogramatitulacion.html", data)
                except Exception as ex:
                    pass

            elif action == 'vercronogramatitulacion':
                try:
                    id = request.GET.get('id', '0')
                    eSolicitud = Solicitud.objects.get(status=True, pk=int(id))
                    data['title'] = u'Cronograma de titulación extraordinaria de ' + str(eSolicitud.perfil.inscripcion.persona)

                    eActividades = DetalleActividadCronogramaTitulacion.objects.filter(status=True, solicitud=eSolicitud).order_by('inicio')
                    paging = MiPaginador(eActividades, 25)
                    p = 1
                    try:
                        paginasesion = 1
                        if 'paginador' in request.session:
                            paginasesion = int(request.session['paginador'])
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
                        else:
                            p = paginasesion
                        try:
                            page = paging.page(p)
                        except:
                            p = 1
                        page = paging.page(p)
                    except:
                        page = paging.page(p)
                    request.session['paginador'] = p
                    data['paging'] = paging
                    data['page'] = page
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['eActividades'] = page.object_list
                    data['solicitante'] = eSolicitud
                    return render(request, "adm_secretaria/vercronogramaex.html", data)
                except Exception as ex:
                    pass

            elif action == 'infoservicios':
                try:
                    id= int(request.GET['id'])
                    data['categoria'] = categoria = CategoriaServicio.objects.get(pk=id, status=True)
                    data['servicios'] = Servicio.objects.filter(status=True, categoria=categoria).order_by('id')
                    template=get_template('adm_secretaria/modales/infoservicios.html')
                    return JsonResponse({'result':'ok','data':template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'infoobservacion':
                try:
                    id= int(encrypt(request.GET['id']))
                    solicitud = Solicitud.objects.get(pk=id)
                    data['historiales'] = HistorialSolicitud.objects.filter(status=True, solicitud=solicitud).order_by('id')
                    data['solicitante'] = solicitud
                    template=get_template('adm_secretaria/modales/infoobservacion.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'addentrega':
                try:
                    data['title'] = u'Asignar horario de retiro'
                    data['action'] = request.GET['action']
                    data['id'] = id = int(request.GET['id'])
                    solicitud = Solicitud.objects.get(pk=id)
                    form = EntregaCertificadoForm(initial={'postulante': solicitud.perfil.persona.nombre_completo_inverso(),
                                                      'maestria': solicitud.perfil.inscripcion.carrera,
                                                      'periodo': solicitud.perfil.inscripcion.matricula_posgrado(),
                                                      'observacion': 'Ninguna'})
                    data['form'] = form
                    template = get_template("adm_secretaria/modales/addhorarioretiro.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'addformato':
                try:
                    data['title'] = u'Adicionar formato de certificado'
                    data['action'] = request.GET['action']
                    data['idc'] = request.GET['idc']
                    form = SubirFormatoCertificadoForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/addformato.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'addactividad':
                try:
                    data['title'] = u'Adicionar actividad de cronograma'
                    data['action'] = request.GET['action']
                    form = AdicionarActividadCronogramaForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/addactividad.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'addactividadtituex':
                try:
                    data['title'] = u'Adicionar actividad de cronograma de titulación'
                    data['action'] = request.GET['action']
                    solicitante = Solicitud.objects.get(status=True, pk=int(request.GET['id']))
                    detalle = DetalleActividadCronogramaTitulacion.objects.filter(status=True, solicitud=solicitante)
                    if detalle:
                        form = ActividadCronogramaTitulacionForm(initial={'solicitante':solicitante.perfil.inscripcion.persona,
                                                                          'periodo':detalle[0].periodo})
                    else:
                        form = ActividadCronogramaTitulacionForm(initial={'solicitante':solicitante.perfil.inscripcion.persona})
                    data['form2'] = form
                    data['id'] = solicitante.id
                    template = get_template("adm_secretaria/modales/addactividad.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'editformato':
                try:
                    data['title'] = u'Adicionar formato de certificado'
                    data['id'] = request.GET['id']
                    data['filtro'] = filtro = FormatoCertificado.objects.get(status=True, pk=int(request.GET['id']))
                    data['action'] = request.GET['action']
                    form = SubirFormatoCertificadoForm(initial=model_to_dict(filtro))
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/addformato.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'editactividad':
                try:
                    data['title'] = u'Adicionar formato de certificado'
                    data['id'] = request.GET['id']
                    data['filtro'] = filtro = ActividadCronogramaTitulacion.objects.get(status=True, pk=int(request.GET['id']))
                    data['action'] = request.GET['action']
                    form = AdicionarActividadCronogramaForm(initial=model_to_dict(filtro))
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/addactividad.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'editactividadtituex':
                try:
                    data['title'] = u'Adicionar formato de certificado'
                    data['id'] = request.GET['id']
                    data['filtro'] = filtro = DetalleActividadCronogramaTitulacion.objects.get(status=True, pk=int(request.GET['id']))
                    data['action'] = request.GET['action']
                    form = ActividadCronogramaTitulacionForm(initial={'solicitante': filtro.solicitud.perfil.inscripcion.persona,
                                                                      'periodo':filtro.periodo,
                                                                      'actividad':filtro.actividad,
                                                                      'inicio':filtro.inicio,
                                                                      'fin':filtro.fin,
                                                                      'observacion':filtro.observacion})
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/addactividad.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'subircertificado':
                try:
                    data['title'] = u'Subir archivo de certificado personalizado'
                    data['action'] = 'subircertificado'
                    data['id'] = id = int(request.GET['id'])
                    form = SubirCertificadoPersonalizadoForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'subirinformetecnico':
                try:
                    data['title'] = u'Subir archivo de certificado personalizado'
                    data['action'] = 'subirinformetecnico'
                    data['id'] = id = int(request.GET['id'])

                    if 'clave' in request.GET:
                        data['clave'] = request.GET['clave']

                    form = SubirInformeTecnicoPertinenciaForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'rechazarfirmaec':
                try:
                    data['title'] = u'Subir archivo de certificado personalizado'
                    data['action'] = 'rechazarfirmaec'
                    data['id'] = id = int(request.GET['id'])
                    data['eSolicitud'] = Solicitud.objects.get(pk=id)

                    form = SubirInformeTecnicoPertinenciaForm()
                    data['form2'] = form

                    if 'clave' in request.GET and request.GET['clave'] == 'rechazo':
                        data['clave'] = request.GET['clave']
                        form.sin_archivo()

                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'seleccionarcarreraho':
                try:
                    data['title'] = u'Subir archivo de certificado personalizado'
                    data['action'] = 'seleccionarcarreraho'
                    data['id'] = id = int(request.GET['id'])
                    data['eSolicitud'] = eSolicitud =Solicitud.objects.get(pk=id)

                    form = SubirInformeTecnicoPertinenciaForm()
                    data['form2'] = form

                    if 'clave' in request.GET and request.GET['clave'] == 'selectcarreraho':
                        data['clave'] = request.GET['clave']
                        form.solo_carrera()

                    idcarreras = RecordAcademico.objects.filter(status=True, inscripcion__carrera__coordinacion__id=7,
                                                       inscripcion__persona=eSolicitud.perfil.inscripcion.persona, asignaturamalla__isnull=False).values_list('inscripcion__carrera__id', flat=True).order_by('inscripcion__carrera__id').distinct()

                    form.fields['carrera'].queryset = Carrera.objects.filter(id__in=idcarreras)
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'subircronograma':
                try:
                    data['title'] = u'Subir archivo de certificado personalizado'
                    data['action'] = 'subircronograma'
                    data['id'] = id = int(request.GET['id'])
                    form = SubirCronogramaTitulacionForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'aprobarrechazar':
                try:
                    data['title'] = u'Aprobar/Rechazar informe técnico de pertinecia'
                    data['action'] = 'aprobarrechazar'
                    data['id'] = id = int(request.GET['id'])
                    data['eSolicitud'] = Solicitud.objects.get(status=True, pk=id)
                    es_director = False
                    if 'clave' in request.GET and request.GET['clave'] == 'homolog':
                        data['clave'] = request.GET['clave']

                        if 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                            es_director = True
                        elif 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                            es_director = True
                        elif 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                            es_director = True
                    data['es_director'] = es_director
                    form = AprobarRechazarInformePertinenciaForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'revisarinforme':
                try:
                    data['title'] = u'Aprobar/Rechazar informe técnico de pertinecia'
                    data['action'] = 'revisarinforme'
                    data['id'] = id = int(request.GET['id'])
                    form = AprobarRechazarInformePertinenciaForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'revisarcronograma':
                try:
                    data['title'] = u'Aprobar/Rechazar cronograma de titulación'
                    data['action'] = 'revisarcronograma'
                    data['id'] = id = int(request.GET['id'])
                    form = AprobarRechazarInformePertinenciaForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'aprobarrechazarcronograma':
                try:
                    data['title'] = u'Aprobar/Rechazar cronograma de titulación'
                    data['action'] = 'aprobarrechazarcronograma'
                    data['id'] = id = int(request.GET['id'])
                    form = AprobarRechazarInformePertinenciaForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'notificarcronograma':
                try:
                    data['title'] = u'Aprobar/Rechazar informe técnico de pertinecia'
                    data['action'] = 'notificarcronograma'
                    data['id'] = id = int(request.GET['id'])
                    form = NotificarCronogramaTitulacionForm()
                    data['form2'] = form
                    template = get_template("adm_secretaria/modales/subircertificado.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'firmarcertificadomasivo':
                try:
                    ids = None

                    if 'ids' in request.GET:
                        ids = request.GET['ids']

                    leadsselect = ids
                    data['listadoseleccion'] = leadsselect

                    template = get_template("adm_secretaria/firmarcertificados.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'html': json_content})
                except Exception as ex:
                    mensaje = 'Intentelo más tarde'
                    return JsonResponse({"result": False, "mensaje": mensaje})

            elif action == 'firmarcertificadoindividual':
                try:
                    id = None
                    if 'id' in request.GET:
                        id = int(request.GET['id'])
                    data['eSolicitud'] = Solicitud.objects.get(status=True, pk=id)
                    data['valor'] = 1
                    template = get_template("adm_secretaria/firmarcertificados.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": "ok", 'html': json_content})
                except Exception as ex:
                    mensaje = 'Intentelo más tarde'
                    return JsonResponse({"result": False, "mensaje": mensaje})

            elif action == 'fichahomologacion':
                try:
                    data['title'] = u'Ficha de homologación interna Posgrado'
                    idex = []
                    eSolicitud = Solicitud.objects.get(pk=int(request.GET['ids']))
                    eInscripcion = Inscripcion.objects.get(status=True, carrera=eSolicitud.carrera_homologada, persona=eSolicitud.perfil.persona)
                    eInscripcionMalla = InscripcionMalla.objects.get(status=True, inscripcion=eInscripcion)
                    idasigma = AsignaturaMalla.objects.filter(status=True, malla=eInscripcionMalla.malla).values_list('id', flat=True)
                    eRecords = RecordAcademico.objects.filter(status=True, aprobada=True, inscripcion=eInscripcion, asignaturamalla__id__in=idasigma).order_by('asignaturamalla__asignatura__nombre').distinct()

                    for eR in eRecords:
                        if eSolicitud.solicitud_asignatura(eR.asignaturamalla.asignatura):
                            idex.append(eR.asignaturamalla.asignatura.id)

                    asignaturasca = AsignaturaMalla.objects.filter(status=True, malla__carrera=eSolicitud.perfil.inscripcion.carrera).exclude(asignatura__id__in=idex).order_by('asignatura__nombre').distinct()

                    eRecordsLi = []
                    c = id = 0
                    eSolicitudA = eSolicitudB = eSolicitudC = None
                    tienefavorable = 0
                    for eRecord in eRecords:
                        solasi = None
                        nota = horas = creditos = porcentaje = orden = 0
                        asignatura = ''
                        color = color2 = ''
                        colorfont = nos = ''

                        if eSolicitud.solicitud_asignatura(eRecord.asignaturamalla.asignatura):
                            solasi = eSolicitud.solicitud_asignatura(eRecord.asignaturamalla.asignatura)

                        if eSolicitud.solicitud_asignatura(eRecord.asignaturamalla.asignatura):
                            eSolicitudA = eSolicitud.solicitud_asignatura(eRecord.asignaturamalla.asignatura)
                            asignatura = eSolicitudA.asignaturamalla.asignatura.nombre
                            horas = eSolicitudA.asignaturamalla.horas
                            creditos = eSolicitudA.asignaturamalla.creditos
                            nota = eRecord.nota
                            color = '#198754'
                            porcentaje = 100
                            color2 = '#124076'
                            colorfont = 'white'
                            id = eSolicitudA.asignaturamalla.id
                            orden = 3
                            tienefavorable = 1
                        elif eSolicitud.solicitud_asignatura_matches(eRecord.asignaturamalla):
                            eSolicitudB = eSolicitud.solicitud_asignatura_matches(eRecord.asignaturamalla)
                            asignatura = eSolicitudB.asignatura.nombre
                            horas = eSolicitudB.horas
                            creditos = eSolicitudB.creditos
                            nota = eRecord.nota
                            color = '#FE9900'
                            color2 = '#FE9900'
                            porcentaje = 100
                            colorfont = 'white'
                            nos = "no"
                            id = eSolicitudB.id
                            orden = 2
                            tienefavorable = 1
                        else:
                            if c <= asignaturasca.count() - 1:
                                eSolicitudC = asignaturasca[c]
                                asignatura = eSolicitudC.asignatura.nombre
                                horas = eSolicitudC.horas
                                creditos = eSolicitudC.creditos
                                nota = 0
                                color = '#00000000'
                                porcentaje = 0
                                if eSolicitud.solicitud_asignatura(eSolicitudC.asignatura):
                                    color2 = '#124076'
                                    colorfont = 'white'
                                    orden = 1

                                c += 1

                        eRecordsLi.append({
                            "asignatura": eRecord.asignaturamalla.asignatura.nombre,
                            "nota": eRecord.nota,
                            "horas": eRecord.horas,
                            "creditos": eRecord.creditos,
                            "asignatura2": asignatura,
                            "nota2": nota,
                            "horas2": horas,
                            "creditos2": creditos,
                            "color": color,
                            "porcentaje": porcentaje,
                            "color2": color2,
                            "colorfont": colorfont,
                            "nos": nos,
                            "id": id,
                            "orden": orden,
                            "solasi": solasi
                        })

                    eRecordsLi_ordenada = sorted(eRecordsLi, key=lambda x: x["orden"], reverse=True)
                    data['eRecords'] = eRecordsLi_ordenada
                    data['eSolicitud'] = eSolicitud
                    data['tienefavorable'] = tienefavorable
                    return render(request, "adm_secretaria/fichahomologacion.html", data)
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = u'Gestión de categorías de servicios'
                search = None
                if persona.usuario.is_superuser:
                    filtros = Q(status=True, pk__gte=0)
                elif persona.coordinacion_pertenece() == 7:
                    if 'SOLO_TITULACION_EX' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        filtros = Q(status=True, id__in=[6, 7])
                    elif 'DIRECTOR DE LA ESCUELA DE POSGRADO DE EDUCACIÓN' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        filtros = Q(status=True, id__in=[6, 7])
                    elif 'DIRECTOR DE LA ESCUELA DE POSGRADO DE CIENCIAS DE LA SALUD' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        filtros = Q(status=True, id__in=[6, 7])
                    elif 'DIRECTOR DE LA ESCUELA DE POSGRADO DE NEGOCIOS Y DERECHO' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                        filtros = Q(status=True, id__in=[6, 7])
                    else:
                        filtros = Q(status=True, pk__gte=0, roles=3)
                elif any(y in [434, 435, 436, 437, 438] for y in persona.usuario.groups.all().distinct().values_list('id', flat=True)):
                    filtros = Q(status=True, pk=4)
                elif 'SOLICITUDES_NIVELACION' in persona.usuario.groups.all().distinct().values_list('name', flat=True):
                    filtros = Q(status=True, pk=5)
                else:
                    filtros = Q(status=True, pk__gte=0, roles__in=[1,2])

                url_vars = ' '
                ids = 0

                if 's' in request.GET:
                    search = request.GET['s']

                if 'ids' in request.GET:
                    ids = int(request.GET['ids'])

                if search:
                    data['search'] = search
                    filtros = filtros & (Q(nombre__icontains=search)| Q(descripcion__icontains=search))
                    url_vars += "&s={}".format(search)

                if ids:
                    data['ids'] = ids
                    filtros = filtros & (Q(roles=ids))
                    url_vars += "&ids={}".format(search)

                categorias = CategoriaServicio.objects.filter(filtros).order_by('nombre')

                paging = MiPaginador(categorias, 20)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session:
                        paginasesion = int(request.session['paginador'])
                    if 'page' in request.GET:
                        p = int(request.GET['page'])
                    else:
                        p = paginasesion
                    try:
                        page = paging.page(p)
                    except:
                        p = 1
                    page = paging.page(p)
                except:
                    page = paging.page(p)

                request.session['paginador'] = p
                data['paging'] = paging
                data['page'] = page
                data['rangospaging'] = paging.rangos_paginado(p)
                data['categorias'] = page.object_list
                data['s'] = search if search else ""
                data['url_vars'] = url_vars
                return render(request, "adm_secretaria/view.html", data)
            except Exception as ex:
                HttpResponseRedirect(f"/?info={ex.__str__()}")
