import io
import json
import random
import sys
import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db import transaction
import xlwt
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import Context
from django.template.loader import get_template
from xlwt import *
from django.shortcuts import render, redirect

from core.firmar_documentos import obtener_posicion_x_y_saltolinea
from core.firmar_documentos_ec import JavaFirmaEc
from decorators import secure_module
from settings import EMAIL_DOMAIN
from sga.commonviews import adduserdata
from sga.templatetags.sga_extras import encrypt
from sga.funciones import MiPaginador, log, generar_nombre, remover_caracteres_especiales_unicode, notificacion
from sagest.models import BitacoraActividadDiaria
from .models import *
from .forms import *
from django.db.models import Sum, Q, F, FloatField
from django.db.models.functions import Coalesce


def validarDiasSolicitud(request, fecha, data):
    try:
        diasemana, dias = fecha.strftime('%A'), 0
        if diasemana == 'Friday' or diasemana == 'friday':
            dias = 3
        if diasemana == 'Saturday' or diasemana == 'saturday':
            dias = 2
        if diasemana == 'Sunday' or diasemana == 'sunday':
            dias = 1
        return {'result': True, 'dias': dias}
    except Exception as ex:
        return {'result': False, 'ex': str(ex)}


def registroHistorial(request, solicitud, paso, estado, persona, observacion, tipo, falerta=None):
    try:
        historial = HistorialProcesoSolicitud(solicitud=solicitud, estado=estado, persona=persona, observacion=observacion, accion=tipo)
        if paso:
            historial.paso = paso
        if falerta:
            historial.fecha_maxima = falerta
        historial.save(request)
        return {'resp': True}
    except Exception as ex:
        return {'resp': False, 'ex': str(ex)}


@login_required(redirect_field_name='ret', login_url='/loginsga')
# @secure_module
@transaction.atomic()
def view(request):
    data = {}
    adduserdata(request, data)
    usuario = request.user
    persona = request.session['persona']
    perfilprincipal = request.session['perfilprincipal']
    periodo = request.session['periodo']

    if request.method == 'POST':
        res_json = []
        action = request.POST['action']

        if action == 'validarrequisito':
            try:
                instance = RequisitoPasoSolicitudPagos.objects.get(id=int(request.POST['id']))
                instance.estado = request.POST['est']
                instance.observacion = request.POST['obs']
                instance.save(request)
                log(u'{} : Validación de Requisito Individual - {}'.format(instance.paso.paso.descripcion, instance), request, "edit")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'validarpaso':
            try:
                with transaction.atomic():
                    filtro = PasoSolicitudPagos.objects.get(pk=int(request.POST['id']))
                    filtro.estado = request.POST['estado']
                    filtro.observacion = request.POST['observacion'].upper()
                    filtro.fecha_revision = datetime.now()
                    filtro.persona_revision = persona
                    filtro.save(request)
                    solicitud = SolicitudPago.objects.get(pk=filtro.solicitud.pk)
                    pasoanterior = solicitud.traer_ultimo_historial()
                    pasoanterior.estado = 3
                    pasoanterior.fecha_ejecucion = datetime.now()
                    pasoanterior.persona_ejecucion = persona
                    pasoanterior.save(request)
                    respmensaje = ''
                    if filtro.estado == '1':
                        pasosiguiente = PasoSolicitudPagos.objects.filter(solicitud=filtro.solicitud, paso__pasoanterior=filtro.paso)
                        if pasosiguiente.exists():
                            filtropaso = pasosiguiente.first()
                            filtropaso.estado = 2
                            fechaactual, fechalimite = datetime.now(), datetime.now()
                            validar = validarDiasSolicitud(request, fechaactual, data)
                            if validar['result']:
                                dias, horas = validar['dias'], filtropaso.paso.tiempoalerta_carga
                                fechalimite = fechaactual + timedelta(days=dias) + timedelta(hours=filtropaso.paso.tiempoalerta_carga)
                            filtropaso.save(request)
                            registroHistorial(request, filtropaso.solicitud, filtropaso, 2, persona, filtropaso.paso.descripcion, 1, fechalimite)
                            respmensaje = 'Validación guardada, se habilitó un lapso de {} horas para la generación del informe.'.format(filtro.paso.tiempoalerta_carga)
                        else:
                            if filtro.paso.finaliza:
                                respmensaje = 'Validación del proceso para la solcitiud del pago finalizada.'
                        messages.success(request, '{} APROBADO'.format(filtro.paso.descripcion))
                    else:
                        messages.success(request, '{} RECHAZADO'.format(filtro.paso.descripcion))
                        fechaactual, fechalimite = datetime.now(), datetime.now()
                        validar = validarDiasSolicitud(request, fechaactual, data)
                        if validar['result']:
                            dias, horas = validar['dias'], filtro.paso.tiempoalerta_validacion
                            fechalimite = fechaactual + timedelta(days=dias) + timedelta(hours=filtro.paso.tiempoalerta_validacion)
                        registroHistorial(request, filtro.solicitud, filtro, 2, persona, 'CORREGIR DOCUMENTOS SOPORTE', 1, fechalimite)
                        respmensaje = 'Validación guardada, se habilitó un lapso de {} horas para corregir la información.'.format(filtro.paso.tiempoalerta_carga)
                    log(u'{} : Validación de Requisitos - {}'.format(filtro.paso.descripcion, filtro), request, "edit")
                    return JsonResponse({"result": False, 'modalsuccess': True, 'mensaje': respmensaje}, safe=False)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": True, "mensaje": "Intentelo más tarde."}, safe=False)

        elif action == 'cargarrequisitos':
            try:
                with transaction.atomic():
                    filtro = PasoSolicitudPagos.objects.get(pk=int(request.POST['id']))
                    filtro.estado = 6
                    filtro.fecha_revision = datetime.now()
                    filtro.persona_revision = persona
                    filtro.save(request)
                    solicitud = SolicitudPago.objects.get(pk=filtro.solicitud.pk)
                    pasoanterior = solicitud.traer_ultimo_historial()
                    pasoanterior.estado = 3
                    pasoanterior.fecha_ejecucion = datetime.now()
                    pasoanterior.persona_ejecucion = persona
                    pasoanterior.save(request)
                    respmensaje = ''
                    for dr in filtro.requisito_paso():
                        if 'req{}'.format(dr.pk) in request.FILES:
                            newfile = request.FILES['req{}'.format(dr.pk)]
                            extension = newfile._name.split('.')
                            tam = len(extension)
                            exte = extension[tam - 1]
                            if newfile.size > 15194304:
                                transaction.set_rollback(True)
                                return JsonResponse({"result": True, "mensaje": u"Error, el tamaño del archivo es mayor a 10 Mb."})
                            if not exte in ['pdf', 'jpg', 'jpeg', 'png', 'jpeg', 'peg']:
                                transaction.set_rollback(True)
                                return JsonResponse({"result": True, "mensaje": u"Error, solo archivos .pdf,.jpg, .jpeg"})
                            nombre_persona = remover_caracteres_especiales_unicode(persona.apellido1).lower().replace(' ','_')
                            newfile._name = generar_nombre("{}__{}".format(nombre_persona, dr.requisito.nombre_input()), newfile._name)
                            dr.archivo = newfile
                            dr.save(request)
                        else:
                            transaction.set_rollback(True)
                            return JsonResponse({"result": True, "mensaje": "Suba todo los requisitos, {}.".format(dr.requisito.nombre)}, safe=False)
                    fechaactual, fechalimite = datetime.now(), datetime.now()
                    validar = validarDiasSolicitud(request, fechaactual, data)
                    if validar['result']:
                        dias, horas = validar['dias'], filtro.paso.tiempoalerta_validacion
                        fechalimite = fechaactual + timedelta(days=dias) + timedelta(hours=filtro.paso.tiempoalerta_validacion)
                    registroHistorial(request, filtro.solicitud, filtro, 2, persona, 'VALIDACIÓN DE {}'.format(filtro.paso.descripcion), 2, fechalimite)
                    respmensaje = 'Documentación cargada, se habilitó un lapso de {} horas para la validación de la información.'.format(filtro.paso.tiempoalerta_validacion)
                    log(u'Valido Paso de Solicitud de Pago: {}'.format(filtro), request, "edit")
                    return JsonResponse({"result": False, 'modalsuccess': True, 'mensaje': respmensaje}, safe=False)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": True, "mensaje": "Intentelo más tarde."}, safe=False)

        elif action == 'informe-administrativo-posgrado-masivo':
            try:
                data['hoy'] = hoy = datetime.now()
                ids = request.POST.get('contrato_posgrado',None).split(',')
                certificado = request.FILES["firma"]
                contrasenaCertificado = request.POST['palabraclave']
                extension_certificado = os.path.splitext(certificado.name)[1][1:]
                bytes_certificado = certificado.read()
                for id in ids:
                    reg = HistorialProcesoSolicitud.objects.get(status=True,id=int(encrypt(id)))
                    requi = reg.requisito
                    if HistorialProcesoSolicitud.objects.filter(status=True, persona_ejecucion=persona,requisito=reg.requisito):
                        hist_= HistorialProcesoSolicitud.objects.filter(status=True, persona_ejecucion=persona,requisito=reg.requisito).order_by('-id').first()
                        hist_.fecha_ejecucion=hoy
                    else:
                        hist_ = HistorialProcesoSolicitud(
                            observacion=f'Informe firmado por {persona.__str__()}',
                            fecha_ejecucion=hoy,
                            persona_ejecucion=persona,
                            requisito=requi,
                            estado=1
                        )
                        hist_.save(request)
                    palabras = f'{persona}'
                    x, y, numpaginafirma = obtener_posicion_x_y_saltolinea(reg.archivo.url, palabras)
                    datau = JavaFirmaEc(
                        archivo_a_firmar=reg.archivo, archivo_certificado=bytes_certificado,
                        extension_certificado=extension_certificado,
                        password_certificado=contrasenaCertificado,
                        page=int(numpaginafirma), reason='', lx=x+50, ly=y+20
                    ).sign_and_get_content_bytes()
                    documento_a_firmar = io.BytesIO()
                    documento_a_firmar.write(datau)
                    documento_a_firmar.seek(0)
                    hist_.archivo.save(f'{reg.archivo.name.split("/")[-1].replace(".pdf", "")}_firmado.pdf',ContentFile(documento_a_firmar.read()))
                    requi.estado = 1
                    requi.save(request)
                    cuerpo = f"Informe mensual para pago de posgrado validado y firmado por {persona}"
                    persona_notificacion = None
                    redirect_mod = f'/adm_solicitudpago'
                    estado_solicitud = 7
                    requisito = hist_.requisito
                    solicitud = requisito.solicitud
                    contrato = solicitud.contrato
                    if contrato.validadorgp:
                        persona_notificacion = contrato.validadorgp
                        redirect_mod = f'/adm_solicitudpago?action=viewinformesmen'
                    else:
                        persona_notificacion = contrato.persona
                    solicitud.estado = estado_solicitud
                    solicitud.save(request)
                    cuerpo = f"Informe mensual de posgrado validado y firmado por {persona}"
                    notificacion(
                        "Informe mensual de posgrado validado por %s" % persona,
                        cuerpo, requi.solicitud.contrato.persona, None, f'/pro_solicitudpago',
                        requi.solicitud.id,
                        1, 'sga', requi, request)
                    persona_gestionposgrado = Persona.objects.get(status=True, id=2356)
                    notificacion(
                        "Solicitud de pago de %s firmado por su jefe inmediato" % hist_.requisito.solicitud.contrato.persona,
                        cuerpo, persona_notificacion, None, f'https://sga.unemi.edu.ec{hist_.archivo.url}',
                        hist_.id,
                        1, 'sga', hist_, request)
                    obshisto = HistorialObseracionSolicitudPago(
                        solicitud=solicitud,
                        observacion=cuerpo,
                        persona=persona,
                        estado=estado_solicitud,
                        fecha=hoy
                    )
                    obshisto.save(request)
                    log(f'Firma jefe inmediato el informe mensual de la solicitud: {solicitud}', request, 'change')
                res_json = {"result": False}
            except Exception as ex:
                err_ = f"Ocurrio un error: {ex.__str__()}. En la linea {sys.exc_info()[-1].tb_lineno}"
                transaction.set_rollback(True)
                res_json = {"result": True, "mensaje": err_}
            return JsonResponse(res_json)

        elif action == 'informe-administrativo-posgrado':
            try:
                data['hoy'] = hoy = datetime.now()
                id = request.POST.get('contrato_posgrado',None)
                certificado = request.FILES["firma"]
                contrasenaCertificado = request.POST['palabraclave']
                extension_certificado = os.path.splitext(certificado.name)[1][1:]
                bytes_certificado = certificado.read()

                reg = HistorialProcesoSolicitud.objects.get(status=True,id=int(encrypt(id)))
                requi = reg.requisito
                if HistorialProcesoSolicitud.objects.filter(status=True, persona_ejecucion=persona,requisito=reg.requisito):
                    hist_= HistorialProcesoSolicitud.objects.filter(status=True, persona_ejecucion=persona,requisito=reg.requisito).order_by('-id').first()
                    hist_.fecha_ejecucion=hoy
                else:
                    hist_ = HistorialProcesoSolicitud(
                        observacion=f'Informe firmado por {persona.__str__()}',
                        fecha_ejecucion=hoy,
                        persona_ejecucion=persona,
                        requisito=requi,
                        estado=1
                    )
                    hist_.save(request)
                palabras = f'{persona}'
                x, y, numpaginafirma = obtener_posicion_x_y_saltolinea(reg.archivo.url, palabras)
                datau = JavaFirmaEc(
                    archivo_a_firmar=reg.archivo, archivo_certificado=bytes_certificado,
                    extension_certificado=extension_certificado,
                    password_certificado=contrasenaCertificado,
                    page=int(numpaginafirma), reason='', lx=x+50, ly=y+20
                ).sign_and_get_content_bytes()
                documento_a_firmar = io.BytesIO()
                documento_a_firmar.write(datau)
                documento_a_firmar.seek(0)
                hist_.archivo.save(f'{reg.archivo.name.split("/")[-1].replace(".pdf", "")}_firmado.pdf',ContentFile(documento_a_firmar.read()))
                requi.estado = 1
                requi.save(request)
                cuerpo = f"Informe mensual para pago de posgrado validado y firmado por {persona}"
                persona_notificacion = None
                redirect_mod = f'/adm_solicitudpago'
                estado_solicitud = 7
                requisito = hist_.requisito
                solicitud = requisito.solicitud
                contrato = solicitud.contrato
                if contrato.validadorgp:
                    persona_notificacion = contrato.validadorgp
                    redirect_mod = f'/adm_solicitudpago?action=viewinformesmen'
                else:
                    persona_notificacion = contrato.persona
                solicitud.estado = estado_solicitud
                solicitud.save(request)
                notificacion(
                    "Informe mensual de posgrado validado por %s" % persona,
                    cuerpo, requi.solicitud.contrato.persona, None, f'/pro_solicitudpago',
                    requi.solicitud.id,
                    1, 'sga', requi, request)
                notificacion(
                    "Solicitud de pago de %s firmado por su jefe inmediato" % hist_.requisito.solicitud.contrato.persona,
                    cuerpo, persona_notificacion, None, f'https://sga.unemi.edu.ec{hist_.archivo.url}',
                    hist_.id,
                    1, 'sga', hist_, request)
                obshisto = HistorialObseracionSolicitudPago(
                    solicitud=solicitud,
                    observacion=cuerpo,
                    persona=persona,
                    estado=estado_solicitud,
                    fecha=hoy
                )
                obshisto.save(request)
                log(f'Firma jefe inmediato el informe mensual de la solicitud: {solicitud}', request, 'change')
                res_json = {"result": False}
            except Exception as ex:
                err_ = f"Ocurrio un error: {ex.__str__()}. En la linea {sys.exc_info()[-1].tb_lineno}"
                transaction.set_rollback(True)
                res_json = {"result": True, "mensaje": err_}
            return JsonResponse(res_json)

        elif action == 'notificarcambios':
            try:
                id = request.POST['id']
                numero = int(request.POST.get('numero'))
                obse = request.POST.get('obs')
                soli = SolicitudPago.objects.get(status=True, id=int(encrypt(id)))
                if numero==1:
                    soli.estado = 6
                    soli.save(request)
                    notificacion(f'Se aprobó el informe de pago de {soli.contrato.persona}.',f'El informe ha sido aprobado. {obse}',soli.contrato.gestion.responsable,None,'/adm_solicitudpago',soli.id,1,'sga',soli,request)
                    obshisto = HistorialObseracionSolicitudPago(
                        solicitud=soli,
                        observacion=f'El informe ha sido aprobado. {obse}',
                        persona=persona,
                        estado=6,
                        fecha=datetime.now()
                    )
                    obshisto.save(request)
                elif numero==2:
                    soli.estado = 0
                    soli.save(request)
                    notificacion(f'Se devolvió el informe de pago.', f'El informe se ha devuelto el informe {soli} por el motivo: {obse}', soli.contrato.persona, None, '/pro_solicitudpago', soli.id, 1, 'sga', soli,request)
                    obshisto = HistorialObseracionSolicitudPago(
                        solicitud=soli,
                        observacion=f'El informe se ha devuelto el informe {soli} por el motivo: {obse}',
                        persona=persona,
                        estado=0,
                        fecha=datetime.now()
                    )
                    obshisto.save(request)
                res_js = {'result':True}
            except Exception as ex:
                err_ = f'{ex} ({sys.exc_info()[-1].tb_lineno})'
                res_js = {'result':False, 'mensaje':err_}
            return JsonResponse(res_js)

        elif action == 'notificarcambiosfinal':
            try:
                id = request.POST['id']
                numero = int(request.POST.get('numero'))
                obse = request.POST.get('obs')
                requisito = RequisitoSolicitudPago.objects.get(status=True, id=int(encrypt(id)))
                soli = requisito.solicitud
                if numero == 1:
                    requisito.estado = 2
                    requisito.save(request)
                    soli.estado = 8
                    soli.save(request)
                    log(f'Aprobo el informe validado por el jefe inmediato: {soli}', request, 'change')
                    notificacion(f'Se aprobó el informe de pago de {soli.contrato.persona}.',
                                 f'El informe ha sido aprobado. {obse}', soli.contrato.persona, None,
                                 '/adm_solicitudpago', soli.id, 1, 'sga', soli, request)
                    obshisto = HistorialObseracionSolicitudPago(
                        solicitud=soli,
                        observacion=f'El informe ha sido aprobado. {obse}',
                        persona=persona,
                        estado=8,
                        fecha=datetime.now()
                    )
                    obshisto.save(request)
                elif numero == 2:
                    requisito.estado = 5
                    requisito.save(request)
                    soli.estado = 0
                    soli.save(request)
                    log(f'Rechazo el informe validado por el jefe inmediato: {soli}', request, 'change')
                    notificacion(f'Se devolvió el informe de pago.',
                                 f'El informe se ha devuelto el informe {soli} por el motivo: {obse}',
                                 soli.contrato.persona, None, '/pro_solicitudpago', soli.id, 1, 'sga', soli, request)
                    obshisto = HistorialObseracionSolicitudPago(
                        solicitud=soli,
                        observacion=f'El informe se ha devuelto el informe {soli} por el motivo: {obse}',
                        persona=persona,
                        estado=0,
                        fecha=datetime.now()
                    )
                    obshisto.save(request)

                res_js = {'result': True}
            except Exception as ex:
                err_ = f'{ex} ({sys.exc_info()[-1].tb_lineno})'
                res_js = {'result': False, 'mensaje': ''}
            return JsonResponse(res_js)

        elif action == 'aprobar_actividade_ind':
            try:
                datos = json.loads(request.POST.get('datos', []))
                id = request.POST.get('id_soli', None)
                soli = SolicitudPago.objects.get(status=True, id=int(encrypt(id)))
                soli.estado = 6
                soli.save(request)
                requisito = RequisitoSolicitudPago.objects.filter(status=True, solicitud=soli, requisito_id=14).order_by('id').first()
                requisito.estado = 2
                requisito.save(request)
                notificacion(f'Se aprobó el informe de pago de {soli.contrato.persona}.',
                             f'El informe ha sido aprobado.', soli.contrato.gestion.responsable, None,
                             '/adm_solicitudpago', soli.id, 1, 'sga', soli, request)
                obshisto = HistorialObseracionSolicitudPago(
                    solicitud=soli,
                    observacion=f'El informe ha sido aprobado.',
                    persona=persona,
                    estado=6,
                    fecha=datetime.now()
                )
                obshisto.save(request)
                res_js = {'result': True}
            except Exception as ex:
                transaction.set_rollback(True)
                msg_err = f'{ex} ({sys.exc_info()[-1].tb_lineno})'
                res_js = {'result': False, 'mensaje': msg_err}
            return JsonResponse(res_js)

        elif action == 'rechazar_actividades_ind':
            try:
                datos = json.loads(request.POST.get('datos',[]))
                id = request.POST.get('id_soli',None)
                soli = SolicitudPago.objects.get(status=True, id=int(encrypt(id)))
                if len(datos) <= 0: raise NameError("Debe haber realizado al menos una observación a un registro.")
                for registro in datos:
                    bitacora = BitacoraActividadDiaria.objects.get(status=True, id=int(encrypt(registro['id'])))
                    bitacora.observacion = registro['observacion']
                    bitacora.corregida = False
                    bitacora.save(request)
                soli.estado = 0
                soli.save(request)
                requisito = RequisitoSolicitudPago.objects.filter(status=True, solicitud=soli, requisito_id=14).order_by('-id').first()
                requisito.estado = 5
                requisito.save(request)
                notificacion(f'Se devolvió el informe de pago.',
                             f'El informe se ha devuelto el informe {soli}',
                             soli.contrato.persona, None, f'/pro_solicitudpago?action=viewrevisionactividades&id={encrypt(soli.id)}', soli.id, 1, 'sga', soli, request)
                obshisto = HistorialObseracionSolicitudPago(
                    solicitud=soli,
                    observacion=f'El informe se ha devuelto el informe {soli}',
                    persona=persona,
                    estado=0,
                    fecha=datetime.now()
                )
                obshisto.save(request)
                log(f"Actualizo las actividades de la bitacora: {datos}", request, "change")
                res_js = {'result':True}
            except Exception as ex:
                transaction.set_rollback(True)
                msg_err = f'{ex} ({sys.exc_info()[-1].tb_lineno})'
                res_js = {'result':False,'mensaje':msg_err}
            return JsonResponse(res_js)

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})

    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'validarrequisito':
                try:
                    data['paso'] = paso = PasoSolicitudPagos.objects.get(pk=int(request.GET['id']))
                    ESTADOS_PASOS_SOLICITUD = ((1, u'APROBADO'), (4, u'RECHAZADO'))
                    ESTADOS_DOCUMENTOS = ((1, u'APROBADO'), (4, u'CORREGIR'))
                    data['estados'] = ESTADOS_PASOS_SOLICITUD
                    data['estados_documentos'] = ESTADOS_DOCUMENTOS
                    data['documentos'] = paso.requisito_paso()
                    template = get_template('adm_solicitudpago/modal/validardocumento.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, "mensaje": ex})

            if action == 'cargarrequisitos':
                try:
                    data['paso'] = paso = PasoSolicitudPagos.objects.get(pk=int(request.GET['id']))
                    ESTADOS_PASOS_SOLICITUD = ((1, u'APROBADO'), (4, u'RECHAZADO'))
                    ESTADOS_DOCUMENTOS = ((1, u'APROBADO'), (4, u'CORREGIR'))
                    data['estados'] = ESTADOS_PASOS_SOLICITUD
                    data['estados_documentos'] = ESTADOS_DOCUMENTOS
                    data['documentos'] = paso.requisito_paso()
                    template = get_template('adm_solicitudpago/modal/cargarrequisitos.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, "mensaje": ex})

            if action == 'estverificacionrequisitos':
                id, ESTADOS_PASOS_SOLICITUD, resp = request.GET['id'], (), []
                filtro = PasoSolicitudPagos.objects.get(pk=id)
                totaldocumentos = RequisitoPasoSolicitudPagos.objects.filter(status=True, paso=filtro).exists()
                totalaprobados = RequisitoPasoSolicitudPagos.objects.filter(status=True, paso=filtro, estado=1).exists()
                if RequisitoPasoSolicitudPagos.objects.filter(status=True, paso=filtro, estado=4).exists():
                    resp = [{'id': 4, 'text': 'RECHAZADO'}]
                else:
                    if totaldocumentos == totalaprobados:
                        ESTADOS_PASOS_SOLICITUD = ((1, u'APROBADO'), (4, u'RECHAZADO'))
                        resp = [{'id': cr[0], 'text': cr[1]} for cr in ESTADOS_PASOS_SOLICITUD]
                return HttpResponse(json.dumps({'state': True, 'result': resp}))

            if action == 'verhistorial':
                try:
                    data['title'] = u'Ver Historial'
                    data['id'] = id = request.GET['id']
                    data['filtro'] = filtro = SolicitudPago.objects.get(pk=int(id))
                    data['detalle'] = HistorialProcesoSolicitud.objects.filter(status=True, solicitud=filtro).order_by('-pk')
                    template = get_template("adm_solicitudpago/modal/verhistorial.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            if action == 'verproceso':
                id = int(encrypt(request.GET['id']))
                data['filtro'] = filtro = SolicitudPago.objects.get(pk=id)
                data['title'] = 'SOLICITUD DE PAGO #{}'.format(filtro.numero)
                return render(request, 'pro_solicitudpago/verprocesosolicitud.html', data)

            elif action == 'viewhistorialrequisito':
                try:
                    id = encrypt(request.GET['id'])
                    reg = HistorialProcesoSolicitud.objects.filter(status=True,requisito_id=int(id))
                    data['lista'] = reg
                    template = get_template('th_hojavida/informacionlaboral/modal/viewhistoryrequiposgrado.html')
                    res_js = {'result':True,'data':template.render(data)}
                except Exception as ex:
                    err_ = f'Ocurrio un error: {ex.__str__()}. En la linea {sys.exc_info()[-1].tb_lineno}'
                    res_js = {'result':False,'mensaje':err_}
                return JsonResponse(res_js)

            elif action == 'viewinformesmen':
                try:
                    data['title'] = u'Solicitudes de Pagos'
                    estsolicitud, search, desde, hasta, filtro, url_vars = request.GET.get('estsolicitud',''), request.GET.get('search',''), request.GET.get('desde', ''), request.GET.get('hasta', ''), Q(status=True), '&action=viewinformesmen'
                    id = request.GET.get('id',None)

                    gruporevision = ContratoDip.objects.values_list('persona_id', flat=True).filter(status=True,validadorgp=persona)
                    filtro = filtro & Q(contrato__persona__id__in=gruporevision) & Q(Q(estado=3)|Q(estado=7)|Q(estado=8))
                    # if estsolicitud:
                    #     data['estsolicitud'] = estsolicitud = int(estsolicitud)
                    #     url_vars += "&estsolicitud={}".format(estsolicitud)
                    #     filtro = filtro & Q(estado=estsolicitud)

                    if desde:
                        data['desde'] = desde
                        url_vars += "&desde={}".format(desde)
                        filtro = filtro & Q(fecha_creacion__gte=desde)

                    if hasta:
                        data['hasta'] = hasta
                        url_vars += "&hasta={}".format(hasta)
                        filtro = filtro & Q(fecha_creacion__lte=hasta)

                    if search:
                        data['search'] = search
                        s = search.split()
                        if len(s) == 1:
                            filtro = filtro & (Q(contrato__persona__apellido2__icontains=search) | Q(
                                contrato__persona__cedula__icontains=search) | Q(contrato__persona__apellido1__icontains=search))
                        else:
                            filtro = filtro & (
                                        Q(contrato__persona__apellido1__icontains=s[0]) & Q(contrato__persona__apellido2__icontains=s[1]))
                        url_vars += '&search={}'.format(search)
                    if id:
                        filtro = filtro & Q(id=int(encrypt(id)))
                    listado = SolicitudPago.objects.filter(filtro).order_by('-id')
                    paging = MiPaginador(listado, 20)
                    p = 1
                    try:
                        paginasesion = 1
                        if 'paginador' in request.session:
                            paginasesion = int(request.session['paginador'])
                        if 'page' in request.GET:
                            p = int(request.GET['page'])
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
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data["url_vars"] = url_vars
                    data['listado'] = page.object_list
                    data['totcount'] = listado.count()
                    data['email_domain'] = EMAIL_DOMAIN
                    data['estado_solicitud'] = ESTADOS_PAGO_SOLICITUD
                    return render(request, 'adm_solicitudpago/viewgest.html', data)
                except Exception as ex:
                    pass

            elif action == 'loadhisotryobser':
                try:
                    id = request.GET.get('id', None)
                    hsitobs = HistorialObseracionSolicitudPago.objects.filter(status=True, solicitud_id = int(encrypt(id)))
                    data['listado'] = hsitobs
                    template = get_template('pro_solicitudpago/modal/viewhistoryobservacion.html')
                    res_js = {'result': True, 'data': template.render(data)}
                except Exception as ex:
                    err_ = f'Ocurrio un error: {ex.__str__()}. En la linea {sys.exc_info()[-1].tb_lineno}'
                    res_js = {'result': False, 'mensaje': err_}
                return JsonResponse(res_js)

            elif action == 'reviewactivities':
                try:
                    id = request.GET.get('id')
                    solicitud = SolicitudPago.objects.get(status=True, id=int(encrypt(id)))
                    fil_bitacora = Q(fecha__date__gte=solicitud.fechainicio.date(), fecha__date__lte=solicitud.fechaifin.date(), persona=solicitud.contrato.persona, status=True)
                    fecha_actual = solicitud.fechainicio
                    data['fechas'] = [fecha_actual + timedelta(days=d) for d in range((solicitud.fechaifin - solicitud.fechainicio).days + 1)]
                    actividades = BitacoraActividadDiaria.objects.filter(fil_bitacora).order_by('fecha')
                    data['title'] = f'Revisión de actividades intividuales - {solicitud.contrato.persona}'
                    data['soli'] = solicitud
                    data['actividades'] = actividades
                    return render(request,'adm_solicitudpago/viewactivities.html', data)
                except Exception as ex:
                    msg_err = f'{ex} ({sys.exc_info()[-1].tb_lineno})'
                    return HttpResponseRedirect(f'{request.path}?info={msg_err}')

        else:
            try:
                data['title'] = u'Solicitudes de Pagos'
                estsolicitud, search, desde, hasta, filtro, url_vars = request.GET.get('estsolicitud', ''), request.GET.get('search', ''), request.GET.get('desde', ''), request.GET.get('hasta', ''), Q(status=True,contrato__gestion__responsable=persona, estado=6), ''
                gruporevision = ContratoDip.objects.values_list('persona_id', flat=True).filter(status=True,validadorgp=persona).exists()
                data['gruporevision'] = gruporevision

                if estsolicitud:
                    data['estsolicitud'] = estsolicitud = int(estsolicitud)
                    url_vars += "&estsolicitud={}".format(estsolicitud)
                    filtro = filtro & Q(estado=estsolicitud)

                if desde:
                    data['desde'] = desde
                    url_vars += "&desde={}".format(desde)
                    filtro = filtro & Q(fecha_creacion__gte=desde)

                if hasta:
                    data['hasta'] = hasta
                    url_vars += "&hasta={}".format(hasta)
                    filtro = filtro & Q(fecha_creacion__lte=hasta)

                if search:
                    data['search'] = search
                    s = search.split()
                    if len(s) == 1:
                        filtro = filtro & (Q(persona__apellido2__icontains=search) | Q(persona__cedula__icontains=search) | Q(persona__apellido1__icontains=search))
                    else:
                        filtro = filtro & (Q(persona__apellido1__icontains=s[0]) & Q(persona__apellido2__icontains=s[1]))
                    url_vars += '&search={}'.format(search)

                listado = SolicitudPago.objects.filter(filtro).order_by('-id')
                paging = MiPaginador(listado, 20)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session:
                        paginasesion = int(request.session['paginador'])
                    if 'page' in request.GET:
                        p = int(request.GET['page'])
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
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data["url_vars"] = url_vars
                data['listado'] = page.object_list
                data['totcount'] = listado.count()
                data['email_domain'] = EMAIL_DOMAIN
                data['estado_solicitud'] = ESTADOS_PAGO_SOLICITUD
                # data['total_pagado'] = total_pagado = listado.filter(estado=3).aggregate(total=Coalesce(Sum(F('total_pagado'), output_field=FloatField()), 0)).get('total')
                return render(request, 'adm_solicitudpago/view.html', data)
            except Exception as ex:
                print(ex)
                print(sys.exc_info()[-1].tb_lineno)
