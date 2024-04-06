# -*- coding: latin-1 -*-
import io
import json
import os
import sys
import pyqrcode
import xlwt
from django.contrib import messages

from django.core.files import File as DjangoFile
from core.firmar_documentos import firmararchivogenerado, obtener_posicion_x_y, firmarmasivo, obtener_posicion_x_y_saltolinea
from sagest.funciones import dominio_sistema_base
from settings import SITE_STORAGE, MEDIA_ROOT
from django.core.paginator import Paginator
from xlwt import *
from django.db import transaction, connection
import random

import sga
from datetime import datetime, timedelta, date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Max, F, Sum
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from decorators import secure_module
from sagest.forms import ActivoFijoForm, ActivoTecnologicoForm, ComponenteActivoForm, GrupoBienForm, \
    ComponenteCatalogoActivoForm, TipoNotificacionForm, NotificacionactivoresponsableForm, InformeBajaATForm, ArchivoActivoBajaForm
from sagest.models import CuentaContable, HistorialTraspaso, SolicitudActivos, EstadoProducto, CLASE_BIEN, \
    ActivoTecnologico, ActivoFijo, \
    TraspasoActivoTecnologico, CatalogoBien, \
    HistorialEstadoActivoTecnologico, DetalleConstatacionFisicaActivoTecnologico, Marca, GruposCategoria, Proveedor, \
    Persona, RangoVidaUtil, InformeActivoBaja, ComponenteActivo, ComponenteCatalogoActivo, HdDetalle_Incidente, \
    TipoNotificacion, Notificacionactivoresponsable, DetalleInformeActivoBaja, DirectorResponsableBaja, PersonaDepartamentoFirmas, HistorialDocumentoInformeBaja,DocumentoFirmaInformeBaja
from settings import DEBUG, SITE_ROOT
from decorators import secure_module
from sga.commonviews import adduserdata, obtener_reporte
from sga.funciones import MiPaginador, log, notificacion, generar_nombre, remover_caracteres_tildes_unicode, remover_caracteres_especiales_unicode
from django.template.loader import get_template
from django.forms import model_to_dict
from sga.models import Notificacion
from sga.templatetags.sga_extras import sumarfecha
from sga.templatetags.sga_extras import encrypt
from sga.funcionesxhtml2pdf import conviert_html_to_pdf, conviert_html_to_pdfsave, \
    conviert_html_to_pdfsaveinformeinventarioactivostecnologicos, \
    conviert_html_to_pdfsaveqrcertificado, conviert_html_to_pdf_name, \
    conviert_html_to_pdfsaveinformeactivo, conviert_html_to_pdfsaveqr_generico
from wpush.models import SubscriptionInfomation
from webpush.utils import _send_notification
unicode = str


@login_required(redirect_field_name='ret', login_url='/loginsga')
@secure_module
@transaction.atomic()

def view(request):
    data = {}
    adduserdata(request, data)
    data['persona'] = persona = request.session['persona']
    perfilprincipal = request.session['perfilprincipal']
    usuario = request.user
    hoy=datetime.now()
    data['DOMINIO_DEL_SISTEMA'] = dominio_sistema = dominio_sistema_base(request)
    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']
            if action == 'add':
                try:
                    f = ActivoTecnologicoForm(request.POST)
                    print(request.POST)
                    if f.is_valid():
                        activofijo = ActivoFijo.objects.select_related('cuentacontable', 'catalogo').get(
                            pk=request.POST['activofijo'])

                        activo = ActivoTecnologico(
                            activotecnologico=activofijo,
                            status=True,
                            responsable_id=request.POST['responsable'],
                            proveedor_id=request.POST['proveedor'],
                            custodio_id=request.POST['custodio'],
                            codigogobierno=activofijo.codigogobierno,
                            codigointerno=activofijo.codigointerno,
                            codigotic=request.POST['codigoticgenerado'],
                            serie=activofijo.serie,
                            modelo=activofijo.modelo,
                            marca=activofijo.marca,
                            cuentacontable_id=activofijo.cuentacontable_id,
                            catalogo_id=activofijo.catalogo_id,
                            fechacompra=activofijo.fechacomprobante,
                            periodogarantiainicio=f.cleaned_data['periodogarantiainicio'],
                            periodogarantiafin=f.cleaned_data['periodogarantiafin'],
                            estado_id=request.POST['estado'],
                            grupocategoria_id=request.POST['gruposcategoria'],
                            observacion=f.cleaned_data['observacion'],
                        )
                        activo.save(request)
                        # if f.cleaned_data['responsable']:
                        #     activo.responsable_id = f.cleaned_data["responsable"]
                        # if f.cleaned_data['proveedor']:
                        #     activo.proveedor_id = f.cleaned_data["proveedor"]
                        # if f.cleaned_data['ubicacion']:
                        #     activo.ubicacion = f.cleaned_data["ubicacion"]
                        # activo.save(request)
                        log(u'Adicion� activo tecnologico: %s' % activo, request, "add")
                        return JsonResponse({"result": "ok"})
                    else:
                        return JsonResponse({"result": True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                             "mensaje": "Complete los datos requeridos."}, safe=False)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

            elif action == 'edit':
                try:
                    f = ActivoTecnologicoForm(request.POST)
                    activo = ActivoTecnologico.objects.get(pk=request.POST['id'])
                    if f.is_valid():
                        activo.codigogobierno = f.cleaned_data['codigogobierno']
                        activo.codigointerno = f.cleaned_data['codigointerno']
                        activo.serie = f.cleaned_data['serie']
                        activo.modelo = f.cleaned_data['modelo']
                        activo.marcaactivo = f.cleaned_data['marca']
                        activo.ubicacion = f.cleaned_data['ubicacion']
                        if f.cleaned_data['responsable'] > 0:
                            activo.responsable_id = f.cleaned_data['responsable']
                        activo.fechacompra = f.cleaned_data['fechacompra']
                        activo.periodogarantiainicio = f.cleaned_data['periodogarantiainicio']
                        activo.periodogarantiafin = f.cleaned_data['periodogarantiafin']
                        try:
                            if int(request.POST['proveedor']) > 0:
                                activo.proveedor_id = request.POST['proveedor']
                        except:
                            pass
                        activo.estado = f.cleaned_data['estado']
                        activo.grupocategoria = f.cleaned_data['gruposcategoria']
                        activo.status = bool(f.cleaned_data['status'])
                        activo.save(request)
                        log(u'Edit� Activo: %s' % activo, request, "edit")
                        return JsonResponse({"result": "ok"})
                    else:
                        raise NameError('Error')

                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

            elif action == 'activocaracteristica':
                try:
                    catalogo = CatalogoBien.objects.get(pk=int(request.POST['id']))
                    return JsonResponse({"result": "ok", "tipo": catalogo.tipobien.id})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos"})

            elif action == 'notificarresponsabledebien':
                try:
                    from bs4 import BeautifulSoup
                    with transaction.atomic():
                        id_activo = int(encrypt(request.POST['id']))
                        persona = Persona.objects.get(pk=int(encrypt(request.POST['idp'])))
                        form = NotificacionactivoresponsableForm(request.POST)
                        if form.is_valid():
                            asunto = form.cleaned_data['asunto']
                            detalle = form.cleaned_data['detalle']
                            html_text = detalle
                            instance = Notificacionactivoresponsable(activo_id=id_activo,
                                                         tipo=form.cleaned_data['tipo'],
                                                         responsable=persona,
                                                         asunto=form.cleaned_data['asunto'],
                                                         detalle=form.cleaned_data['detalle'],
                                                         fecha=datetime.now().date(),
                                                         hora=datetime.now().time(),
                                                         estado=1,)
                                                         # fechaestado=datetime.now().date(),
                                                         # horaestado=datetime.now().time())
                            instance.save(request)
                            log(u'Adiciono Notificacion a responsable: %s' % instance, request, "add")
                            notificacion(
                                form.cleaned_data['asunto'],
                                form.cleaned_data['detalle'],
                                persona,
                                None,
                                '/mis_activos?action=viewlistnotificaciones',
                                instance.id,
                                2,
                                'sga',
                                Notificacionactivoresponsable,
                                request
                            )
                            texto = BeautifulSoup(html_text, 'html.parser')
                            det_sin_html = texto.get_text()

                            subscriptions = persona.usuario.webpush_info.select_related("subscription")
                            push_infos = SubscriptionInfomation.objects.filter(subscription_id__in=subscriptions.values_list('subscription__id', flat=True), app=1,
                                status=True).select_related("subscription")
                            for device in push_infos:
                                payload = {
                                    "head": asunto,
                                    "body": det_sin_html,
                                    "url": "/mis_activos?action=viewlistnotificaciones",
                                    "action": "loadNotifications",
                                }
                                try:
                                    _send_notification(device.subscription, json.dumps(payload), ttl=700)
                                except Exception as exep:
                                    print(f"Fallo de envio del push notification: {exep.__str__()}")

                            return JsonResponse({"result": False})
                        else:
                            return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()],
                                                 "message": "Error en el formulario"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": True, "mensaje": "Intentelo m�s tarde."}, safe=False)

            elif action == 'iniciabaja':
                try:
                    activo = ActivoTecnologico.objects.get(pk=request.POST['id'])

                    if request.POST['val'] == 'y':
                        historial = HistorialEstadoActivoTecnologico(activo=activo, estado=activo.estado)
                        historial.save(request)
                        activo.procesobaja = esta = True
                        activo.estado_id = 3
                    else:
                        activo.procesobaja = esta = False
                        historial = HistorialEstadoActivoTecnologico.objects.filter(activo=activo,
                                                                                    status=True).order_by('-id').last()
                        if historial:
                            activo.estado_id = historial.estado
                            DetalleConstatacionFisicaActivoTecnologico.objects.filter(status=True,
                                                                                      codigoconstatacion__estado=1,
                                                                                      activo=activo).update(
                                estadoactual=historial.estado)
                    activo.save(request)
                    log(u'Inicia proceso de baja : %s (%s)' % (activo, activo.procesobaja), request, "edit")
                    return JsonResponse({"result": "ok"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad"})

            elif action == 'deletenotificacion':
                try:
                    id = request.POST['id']
                    notiresponsable = Notificacionactivoresponsable.objects.get(pk=id)
                    noti = Notificacion.objects.get(status=True, object_id=notiresponsable.id, titulo=notiresponsable.asunto)
                    noti.status = False
                    noti.save(request)
                    log(u'Elimina Notificacion: %s' % (noti), request, "del")
                    notiresponsable.status = False
                    notiresponsable.save(request)
                    log(u'Elimina Notificacion responsable : %s' % (notiresponsable), request, "del")
                    return JsonResponse({"result": "ok"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad"})

            elif action == 'deletiponotificacion':
                try:
                    id = request.POST['id']
                    tipo = TipoNotificacion.objects.get(status=True, pk=id)
                    tipo.status=False
                    tipo.save(request)
                    log(u'Elimina Tipo Notificacion: %s' % (tipo), request, "del")
                    return JsonResponse({"result": "ok"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad"})

            elif action == 'deleteactivotecnologico':
                try:
                    idactivotecnologico = int(request.POST['id'])
                    activotecnologico_delete = ActivoTecnologico.objects.get(id=idactivotecnologico)
                    activotecnologico_delete.status = False
                    activotecnologico_delete.save(request)
                    log(u'Elimina activo tecnologico: %s' % activotecnologico_delete, request, "del")
                    return JsonResponse({"result": "ok"})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u'Error al eliminar el activo tecnol�gico'})

            #INFORME DE BAJA
            elif action == 'addinformebaja':
                try:
                    form =InformeBajaATForm(request.POST)
                    if form.is_valid():
                        informebaja = InformeActivoBaja(activofijo_id=form.cleaned_data['activofijo'],
                                                        solicita=form.cleaned_data['solicita'],
                                                        responsable=form.cleaned_data['responsable_'],
                                                        conclusion=form.cleaned_data['conclusion'],
                                                        estado=form.cleaned_data['estado'],
                                                        estadouso=form.cleaned_data['estadouso'],
                                                        bloque=form.cleaned_data['bloque'],
                                                        detallerevision=form.cleaned_data['detallerevision'],
                                                        tipoinforme=1)
                        informebaja.save(request)
                        if 'actividades' in request.POST:
                            listadetalle = request.POST.getlist('actividades')
                            if listadetalle:
                                for lisdet in listadetalle:
                                    ingresodetalle = DetalleInformeActivoBaja(informebaja=informebaja, detalle=lisdet)
                                    ingresodetalle.save(request)
                        activo=ActivoFijo.objects.get(id=form.cleaned_data['activofijo'])
                        codigo=activo.codigogobierno if activo.codigogobierno else activo.codigointerno
                        log(u'Adiciono informe activo de baja: %s' % informebaja, request, "add")
                        return JsonResponse({"result": False, 'to':f'{request.path}?s={codigo}'},safe=True)
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()],
                                             "mensaje": "Error en el formulario"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": str(ex)})

            elif action == 'editinformebaja':
                try:
                    id=int(encrypt(request.POST['id']))
                    form =InformeBajaATForm(request.POST)
                    if form.is_valid():
                        informebaja = InformeActivoBaja.objects.get(id=id)
                        informebaja.solicita=form.cleaned_data['solicita']
                        informebaja.responsable_id=form.cleaned_data['responsable_']
                        informebaja.conclusion=form.cleaned_data['conclusion']
                        informebaja.estado=form.cleaned_data['estado']
                        informebaja.estadouso=form.cleaned_data['estadouso']
                        informebaja.bloque=form.cleaned_data['bloque']
                        informebaja.detallerevision=form.cleaned_data['detallerevision']
                        informebaja.save(request)
                        if 'actividades' in request.POST:
                            listadetalle = request.POST.getlist('actividades')
                            if listadetalle:
                                informebaja.actividades_informe_baja().filter(informebaja_id=id).update(status=False)
                                for lisdet in listadetalle:
                                    ingresodetalle = DetalleInformeActivoBaja(informebaja=informebaja, detalle=lisdet)
                                    ingresodetalle.save(request)

                        log(u'Edito informe activo de baja: %s' % informebaja, request, "edit")
                        activo = informebaja.activofijo
                        codigo = activo.codigogobierno if activo.codigogobierno else activo.codigointerno
                        return JsonResponse({"result": False,'to':f'{request.path}?s={codigo}'},safe=True)
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()],
                                             "mensaje": "Error en el formulario"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": str(ex)})

            elif action == 'delinformebaja':
                with transaction.atomic():
                    try:
                        instancia = InformeActivoBaja.objects.get(pk=int(encrypt(request.POST['id'])))
                        instancia.status = False
                        instancia.save(request)
                        instancia.documentofirmainformebaja_set.filter(status=True).update(status=False)
                        instancia.activofijo.archivobaja.delete()
                        log(u'Elimino informe de activo baja y sus dependencias: %s' % instancia, request, "del")
                        res_json = {"error": False}
                    except Exception as ex:
                        res_json = {'error': True, "message": "Error: {}".format(ex)}
                    return JsonResponse(res_json, safe=False)

            elif action == 'firmarinformebaja':
                try:
                    # Parametros
                    txtFirmas = json.loads(request.POST['txtFirmas'])
                    firmadirector = request.POST.get('val_extra', '')
                    firma = request.FILES["firma"]
                    passfirma = request.POST['palabraclave']
                    id = int(encrypt(request.POST['id_objeto']))
                    director = DirectorResponsableBaja.objects.filter(status=True, actual=True).first()
                    informe = InformeActivoBaja.objects.get(status=True, activofijo_id=id)

                    #VALIDACIONES
                    if not txtFirmas:
                        raise NameError("Debe seleccionar ubicaci�n de la firma")
                    if firmadirector and not director.responsable.id == persona.id:
                        raise NameError("Para poder firmar tiene que ser el director de departamento")
                    if not firmadirector and not informe.responsable.id == persona.id:
                        raise NameError("Para poder firmar tiene que ser el responsable del informe de baja")

                    x = txtFirmas[-1] #Posiciones
                    url_archivo = (SITE_STORAGE + request.POST["url_archivo"]).replace('\\', '/') #Ubicaci�n exacta donde se encuentra guardado el documento a firmar
                    _name = generar_nombre(f'informebaja_{request.user.username}_{id}_', 'firmada') #Nombre nuevo del documento firmado
                    folder = os.path.join(SITE_STORAGE, 'media', f'archivo_activo_baja\\documento_firma_ib', '') #Ubicaci�n donde se va a guardar el archivo firmado

                    # Firmar y guardar archivo en folder definido.
                    firma = firmararchivogenerado(request, passfirma, firma, url_archivo, folder, _name, x["numPage"], x["x"], x["y"], x["width"], x["height"])
                    if firma != True:
                        raise NameError(firma)
                    #Recuperaci�n del documento guardado.
                    folder_save = os.path.join(f'archivo_activo_baja/documento_firma_ib', '').replace('\\', '/')
                    url_file_generado = f'{folder_save}{_name}.pdf'

                    documento = informe.documento_informe_baja()
                    if not documento:
                        documento=DocumentoFirmaInformeBaja(informe=informe,
                                                            director=director,
                                                            archivo=url_file_generado)
                        documento.save(request)
                        log(u'Guardo archivo firmado: {}'.format(documento), request, "add")
                    else:
                        documento.firmadirector=True if firmadirector else False
                        documento.archivo = url_file_generado
                        documento.save(request)
                        log(u'Edito archivo firmado: {}'.format(documento), request, "edit")
                        if firmadirector:
                            activofijo = informe.activofijo
                            activofijo.archivobaja = url_file_generado
                            activofijo.save(request)
                            experto = Persona.objects.get(id=1204)
                            titulo = f'Informe de baja registrado {activofijo.id}'
                            cuerpo = f'Se registro un nuevo informe de baja del activo {activofijo}'
                            notificacion(titulo, cuerpo + ' a su nombre.', activofijo.responsable, None, f'/mis_activos?s={activofijo.codigogobierno}', activofijo.pk, 2, 'sga-sagest', ActivoFijo, request)
                            notificacion(titulo, cuerpo, experto, None, f'/af_activofijo?s={activofijo.codigogobierno}', activofijo.pk, 2, 'sga-sagest', ActivoFijo, request)
                            log(u'Edito archivo firmado: {}'.format(activofijo), request, "add")
                    historial=HistorialDocumentoInformeBaja(
                        documentoinforme=documento,
                        persona=persona,
                        archivo=url_file_generado
                    )
                    historial.save(request)

                    log(u'Guardo historial de archivo firmado: {}'.format(historial), request, "add")
                    return JsonResponse({"result": False, "mensaje": "Guardado con exito", }, safe=False)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": True, "mensaje": u"Error al guardar. %s" % ex.__str__()}, safe=False)

            elif action == 'firmarinformebajamasivo':
                try:
                    director = DirectorResponsableBaja.objects.filter(status=True, actual=True).first()
                    if not director.responsable.id == persona.id:
                        raise NameError("Para poder firmar tiene que ser el director de departamento")
                    firma = request.FILES["firma"]
                    passfirma = request.POST['palabraclave']
                    documentos=DocumentoFirmaInformeBaja.objects.filter(status=True, firmadirector=False)
                    bandera,p12 = False, None
                    for doc in documentos:
                        archivo_=doc.ultimo_dcoumento().archivo
                        palabras=str(director.cargo)
                        x, y, numpaginafirma = obtener_posicion_x_y_saltolinea(archivo_.url, palabras)
                        if x and y:
                            x=x+35
                            y=y
                            generar_archivo_firmado = io.BytesIO()
                            datau, datas, p12 = firmarmasivo(request,p12,bandera, passfirma, firma, archivo_, numpaginafirma, x, y, 150, 45)
                            bandera = True if p12 else False
                            if not datau:
                                raise NameError(f"{datas}")
                            generar_archivo_firmado.write(datau)
                            generar_archivo_firmado.write(datas)
                            generar_archivo_firmado.seek(0)
                            _name = generar_nombre(f'{request.user.username}_{doc.id}_informebaja', 'firmada')
                            file_obj = DjangoFile(generar_archivo_firmado, name=f"{_name}.pdf")
                            doc.firmadirector = True
                            doc.archivo = file_obj
                            doc.save(request)
                            log(u'Edito archivo firmado: {}'.format(doc), request, "edit")

                            historial = HistorialDocumentoInformeBaja(
                                documentoinforme=doc,
                                persona=persona,
                                archivo=file_obj
                            )
                            historial.save(request)
                            log(u'Guardo historial de informe  firmado: {}'.format(historial), request, "add")
                            activofijo=doc.informe.activofijo
                            activofijo.archivobaja=file_obj
                            activofijo.save(request)

                            # ENVIO DE NOTIFICACI�N
                            experto = Persona.objects.get(id=1204)
                            titulo = f'Informe de baja registrado {activofijo.id}'
                            cuerpo = f'Se registro un nuevo informe de baja del activo {activofijo}'
                            notificacion(titulo, cuerpo + ' a su nombre.', activofijo.responsable, None, f'/mis_activos?s={activofijo.codigogobierno}', activofijo.pk, 2, 'sga-sagest', ActivoFijo, request)
                            notificacion(titulo, cuerpo, experto, None, f'/af_activofijo?s={activofijo.codigogobierno}', activofijo.pk, 2, 'sga-sagest', ActivoFijo, request)

                            log(u'Edito archivo baj de activo fijo: {}'.format(activofijo), request, "edit")
                    return JsonResponse({"result": False, "mensaje": "Guardado con exito", }, safe=False)
                except Exception as ex:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
                    textoerror = '{} Linea:{}'.format(ex, sys.exc_info()[-1].tb_lineno)
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": u"Error: %s" % ex})

            elif action == 'subirinforme':
                try:
                    form = ArchivoActivoBajaForm(request.POST, request.FILES)
                    if form.is_valid():
                        director = DirectorResponsableBaja.objects.filter(status=True, actual=True).first()
                        id=int(encrypt(request.POST['id']))
                        newfile = request.FILES['archivobaja']
                        newfile._name = generar_nombre(f"informe_baja_{usuario.username}_{id}", 'firmado')+".pdf"
                        informe = InformeActivoBaja.objects.get(status=True, activofijo_id=id)
                        documento = informe.documento_informe_baja()
                        if not documento:
                            documento = DocumentoFirmaInformeBaja(informe=informe,
                                                                  firmadirector=True,
                                                                  director=director)
                            documento.save(request)
                            log(u'Adiciono archivo firmado: {}'.format(documento), request, "add")
                        else:
                            documento.firmadirector = True
                            log(u'Edito archivo firmado: {}'.format(documento), request, "edit")

                        documento.archivo = newfile
                        documento.save(request)
                        activofijo = informe.activofijo
                        activofijo.archivobaja = newfile
                        activofijo.save(request)
                        log(u'Edito archivo firmado: {}'.format(activofijo), request, "edit")
                        historial = HistorialDocumentoInformeBaja(
                            documentoinforme=documento,
                            persona=persona,
                            archivo=newfile
                        )
                        historial.save(request)
                        return JsonResponse({"result": False}, safe=False)
                    else:
                        raise NameError('Debe subir archivo pdf con los MG especificado')
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": f"{ex}"})

            elif action == 'delacta':
                with transaction.atomic():
                    try:
                        instancia = DocumentoFirmaInformeBaja.objects.get(pk=int(encrypt(request.POST['id'])))
                        instancia.status = False
                        instancia.save(request)
                        log(u'Elimino acta de constataci�n: %s' % instancia, request, "del")
                        res_json = {"error": False}
                    except Exception as ex:
                        res_json = {'error': True, "message": "Error: {}".format(ex)}
                    return JsonResponse(res_json, safe=False)

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            data['action']= action = request.GET['action']

            if action == 'add':
                try:
                    # puede_realizar_accion(request, 'sagest.puede_ingresar_compras')
                    data['title'] = u'Nuevo activo tecnol�gico'
                    ultimocodigotics = ActivoTecnologico.objects.filter(codigotic__isnull=False).last()
                    codigotics_generado = int(ultimocodigotics.codigotic) + 1
                    form = ActivoTecnologicoForm(
                        initial={'codigotics': codigotics_generado, 'periodogarantiainicio': datetime.now().date(),
                                 'periodogarantiafin': datetime.now().date()})
                    data['codigoticgenerado'] = codigotics_generado
                    form.soloRead(
                        ['codigotics', 'serie', 'cuentacontable', 'catalogodescripcion', 'vidautil', 'fechacompra',
                         'codigogobierno', 'codigointerno', 'modelo', 'marca', ])
                    data['form'] = form
                    plantilla = render(request, 'at_activostecnologicos/add.html', data)
                    return plantilla
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = u'Modificar Activo'
                    data['activo'] = activo = ActivoTecnologico.objects.get(pk=request.GET['id'])
                    form = ActivoTecnologicoForm(initial={
                        'codigogobierno': activo.codigogobierno,
                        'codigointerno': activo.codigointerno,
                        'codigotics': activo.codigotic,
                        'serie': activo.serie,
                        'modelo': activo.modelo,
                        'marca': activo.marcaactivo,
                        'ubicacion': activo.ubicacion,
                        'fechacompra': activo.fechacompra,
                        'periodogarantiainicio': activo.periodogarantiainicio,
                        'periodogarantiafin': activo.periodogarantiafin,
                        'estado': activo.estado,
                        'status': activo.status,
                        'gruposcategoria': activo.grupocategoria
                    })

                    if activo.proveedor:
                        form.editar_proveedor(activo.proveedor)
                    if activo.responsable:
                        form.editar_responsable(activo.responsable)
                    form.ocultar_activo_tecnologico()
                    # form.editar(activo, request.user)
                    data['form'] = form
                    return render(request, 'at_activostecnologicos/edit.html', data)
                except Exception as ex:
                    pass

            elif action == 'historial':
                try:
                    data['title'] = u'Historial del Bien'
                    data['activo'] = activo = ActivoTecnologico.objects.get(pk=int(request.GET['id']))
                    data["detalles"] = activo.detalletraspasoactivotecnologico_set.filter(status=True).order_by(
                        '-codigotraspaso__fecha')
                    data['reporte_0'] = obtener_reporte('historial_activos')
                    data['usuario'] = request.user
                    return render(request, "at_activostecnologicos/historial.html", data)
                except Exception as ex:
                    pass

            elif action == 'constataciones':
                try:
                    data['title'] = u'Constataciones del Bien'
                    data['activo'] = activo = ActivoTecnologico.objects.get(pk=int(request.GET['id']))
                    data["detalles_pert"] = activo.detalleconstatacionfisicaactivotecnologico_set.filter(
                        perteneceusuario=True).order_by('-codigoconstatacion__numero')
                    data['detallenopert'] = activo.detalleconstatacionfisicaactivotecnologico_set.filter(
                        perteneceusuario=False)
                    data['detallenotras'] = activo.detalleconstatacionfisicaactivotecnologico_set.filter(
                        requieretraspaso=True)
                    data['reporte_0'] = obtener_reporte('historial_activos')
                    data['usuario'] = request.user
                    return render(request, "at_activostecnologicos/detalle_constataciones.html", data)
                except Exception as ex:
                    pass

            elif action == 'obteneractivo':
                try:
                    id = request.GET.get('q')
                    activo = ActivoFijo.objects.select_related('responsable', 'estado', 'catalogo', 'ubicacion').get(
                        pk=int(id))

                    data = {
                        'codigogobierno': activo.codigogobierno,
                        'codigointerno': activo.codigointerno,
                        'serie': activo.serie,
                        'modelo': activo.modelo,
                        'marca': activo.marca,
                        'fechacompra': activo.fechacomprobante,
                        'cuentacontable': activo.cuentacontable.__str__(),
                        'ubicacion': {'id': activo.ubicacion_id, 'nombre': activo.ubicacion.nombre},
                        'responsable': {'id': activo.responsable_id, 'name': activo.responsable.__str__()},
                        'estado': {'id': activo.estado_id, 'nombre': activo.estado.nombre},
                        'catalogodescripcion': activo.catalogo.__str__(),
                        'tiempovidautil': activo.fechacomprobante,

                    }

                    return JsonResponse(data)
                except Exception as ex:
                    pass

            elif action == 'buscaractivosdesactivados':
                try:
                    q = request.GET['q'].upper().strip()
                    s = q.split(" ")
                    value = int(s[0])
                    activos = ActivoFijo.objects.filter(
                        Q(codigogobierno=value) | Q(codigointerno=value) | Q(codigogobierno__startswith=value) | Q(
                            codigointerno__startswith=value))
                    data = {"result": "ok",
                            "results": [{"id": x.id, "identificacion": x.__str__(), "name": x.__str__()} for x in
                                        activos]}
                    return JsonResponse(data)
                except Exception as ex:
                    pass

            elif action == 'clasificar':
                try:
                    data['title'] = u'Listado de categor�as por clasificar'
                    data['catalogos'] = CatalogoBien.objects.filter(status=True, clasificado=False)

                    return render(request, 'at_activostecnologicos/clasificar2.html', data)
                except Exception as ex:
                    pass

            elif action == 'chartinventariotecnologico':
                try:
                    recuento_activos = {'vigentes': 0, 'proximos': 0, 'baja': 0, 'archivobaja': 0}
                    data['title'] = u'Equipo Tecnol�gico'
                    data['codigo'] = codigo = int(request.GET['codigo'])
                    data['rangosemaforo'] = anios = RangoVidaUtil.objects.filter(status=True).order_by('anio',
                                                                                                       'descripcion')
                    data['grupocatalogo'] = GruposCategoria.objects.filter(status=True)

                    if codigo == 0:
                        activos1 = ActivoTecnologico.objects.filter(
                            statusactivo=1, status=True,
                        ).order_by('-id').values(
                            'activotecnologico__id',
                            'activotecnologico__archivobaja',
                            'activotecnologico__fechaingreso',
                            'activotecnologico__vidautil',
                        ).distinct()

                    else:
                        activos1 = ActivoTecnologico.objects.filter(
                            statusactivo=1, status=True,
                            activotecnologico__catalogo__grupo__id=codigo
                        ).order_by('-id').values(
                            'activotecnologico__id',
                            'activotecnologico__archivobaja',
                            'activotecnologico__fechaingreso',
                            'activotecnologico__vidautil',
                        ).distinct()

                    for listado in activos1:
                        if listado['activotecnologico__archivobaja']:
                            recuento_activos['archivobaja'] += 1
                        for rangos in anios:
                            sumarfechaingreso = sumarfecha(listado['activotecnologico__fechaingreso'])
                            if rangos.anio == listado[
                                'activotecnologico__vidautil'] and rangos.numeromesdesde <= sumarfechaingreso and rangos.numeromeshasta >= sumarfechaingreso:
                                if rangos.descripcion == 1:
                                    listado['color'] = 'verdes'
                                    listado['totalmeses'] = sumarfechaingreso
                                    recuento_activos['vigentes'] += 1
                                elif rangos.descripcion == 2:
                                    listado['color'] = 'naranjas'
                                    listado['totalmeses'] = sumarfechaingreso
                                    recuento_activos['proximos'] += 1
                                elif rangos.descripcion == 3:
                                    listado['color'] = 'rojos'
                                    listado['totalmeses'] = sumarfechaingreso
                                    recuento_activos['baja'] += 1

                    # paging = MiPaginador(activos1, 50)
                    # p = 1
                    # try:
                    #     paginasesion = 1
                    #     if 'paginador' in request.session:
                    #         paginasesion = int(request.session['paginador'])
                    #     if 'page' in request.GET:
                    #         p = int(request.GET['page'])
                    #     else:
                    #         p = paginasesion
                    #     try:
                    #         page = paging.page(p)
                    #     except:
                    #         p = 1
                    #     page = paging.page(p)
                    # except:
                    #     page = paging.page(p)
                    # request.session['paginador'] = p
                    # data['paging'] = paging
                    # data['rangospaging'] = paging.rangos_paginado(p)
                    # data['page'] = page
                    # data['listadocatalogo1'] = page.object_list
                    # data['listadocatalogo1'] = activos1
                    data['estados'] = recuento_activos
                    data['totales'] = activos1.values('id').count()
                    request.session['viewactivo']=3
                    return render(request, "at_activostecnologicos/chartinventariotecnologico.html", data)
                except Exception as ex:
                    pass

            elif action == 'excellistadoactivos_1':
                try:
                    __author__ = 'Unemi'

                    font_style = XFStyle()
                    font_style.font.bold = True
                    font_style2 = XFStyle()
                    font_style2.font.bold = False
                    wb = Workbook(encoding='utf-8')
                    ws = wb.add_sheet('exp_xls_post_part')
                    # ws.write_merge(0, 0, 0, 10, 'UNIVERSIDAD ESTATAL DE MILAGRO', title)
                    response = HttpResponse(content_type="application/ms-excel")
                    response[
                        'Content-Disposition'] = 'attachment; filename=Listado' + random.randint(1,
                                                                                                 10000).__str__() + '.xls'
                    columns = [

                        (u"RESPONSABLE", 10000),
                        (u"CODIGO INTERNO", 5000),
                        (u"CPDOGP GOBIERNO", 5000),
                        (u"FECHA INGRESO", 4000),
                        (u"DESCRIPCI�N", 10000),
                        (u"MODELO", 6000),
                        (u"MARCA", 6000),
                        (u"ARCHIVO DE BAJA", 5000),
                        (u"UBICACI�N", 17000),
                        (u"ESTADO", 6000),
                        (u"URL ARCHIVO BAJA", 10000),
                        (u"PROCESO BAJA", 5000),
                        (u"FECHA PROCESO BAJA", 5000),
                        (u"CATEGORIA", 10000),
                        (u"DADO DE BAJA", 10000),
                        (u"GARANT�A", 10000),
                    ]
                    row_num = 0
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], font_style)
                        ws.col(col_num).width = columns[col_num][1]
                    date_format = xlwt.XFStyle()
                    date_format.num_format_str = 'yyyy/mm/dd'

                    codigo, estado, search, filtro = request.GET.get('cadenatexto', ''), request.GET.get('estado',
                                                                                                         ''), request.GET.get(
                        's', ''), (Q(status=True))

                    if estado:
                        if not estado == 'informebaja':
                            estado = int(estado)
                            filtro = filtro & (Q(activotecnologico__estado_id=estado))
                            data['estado'] = estado
                        else:
                            ids = DocumentoFirmaInformeBaja.objects.filter(status=True).values_list(
                                'informe__activofijo_id', flat=True)
                            filtro = filtro & (Q(activotecnologico_id__in=ids))
                            data['estado'] = estado

                        # filtro = filtro & (Q(estado_id=estado))

                    if codigo:
                        if int(codigo) != 0:
                            filtro = filtro & Q(activotecnologico__catalogo__grupo__id=codigo)

                    if search:
                        ss = search.split(' ')

                        if len(ss) == 1:
                            filtro = filtro & (Q(descripcion__icontains=search) |
                                               Q(codigogobierno__icontains=search) |
                                               Q(serie__icontains=search) |
                                               Q(codigointerno__icontains=search) |
                                               Q(codigotic__icontains=search) |
                                               Q(modelo__icontains=search) |
                                               Q(codigogobierno__icontains=search) |
                                               Q(responsable__nombres__icontains=search) |
                                               Q(responsable__apellido1__icontains=search) |
                                               Q(responsable__apellido2__icontains=search))
                        else:
                            filtro = filtro & (Q(responsable__apellido1__icontains=ss[0]) &
                                               Q(responsable__apellido2__icontains=ss[1]))


                    # filtro = filtro & (Q(activotecnologico__archivobaja__isnull=True) |
                    #                    Q(activotecnologico__archivobaja='') |
                    #                    Q(activotecnologico__archivobaja__exact=' ')
                    #                    )

                    results = ActivoTecnologico.objects.filter(filtro).select_related(
                                                                'activotecnologico').distinct().order_by('activotecnologico__fechaingreso').order_by('-id')

                    row_num = 1
                    for r in results:
                        tienearchivobaja = r.activotecnologico.archivobaja
                        proccesobaja = r.activotecnologico.procesobaja
                        grupo = r.activotecnologico.catalogo.grupo if r.activotecnologico.catalogo.grupo else ''
                        if proccesobaja:
                            procesobaja = 'SI'
                        else:
                            procesobaja = 'NO'


                        ws.write(row_num, 0, str(r.activotecnologico.responsable), font_style2)
                        ws.write(row_num, 1, str(r.activotecnologico.codigointerno), font_style2)
                        ws.write(row_num, 2, str(r.activotecnologico.codigogobierno), font_style2)
                        ws.write(row_num, 3, r.activotecnologico.fechaingreso, date_format)
                        ws.write(row_num, 4, r.activotecnologico.descripcion, font_style2)
                        ws.write(row_num, 5, r.activotecnologico.modelo, font_style2)
                        ws.write(row_num, 6, r.activotecnologico.marca, font_style2)
                        if not tienearchivobaja or tienearchivobaja == '':
                            archivobaja = 'NO'
                            fechabaja=''
                        else:
                            archivobaja = 'SI'
                            fechabaja = r.activotecnologico.fecha_proceso_baja().fecha_creacion if r.activotecnologico.fecha_proceso_baja() else ''
                            ws.write(row_num, 10, "https://sagest.unemi.edu.ec/media/{}".format(str(tienearchivobaja)),
                                     font_style2)
                        ws.write(row_num, 7, archivobaja, font_style2)
                        ws.write(row_num, 8, str(r.activotecnologico.ubicacion), font_style2)
                        ws.write(row_num, 9, str(r.activotecnologico.estado), font_style2)
                        ws.write(row_num, 11, str(procesobaja), font_style2)
                        ws.write(row_num, 12, str(fechabaja), font_style2)
                        ws.write(row_num, 13, str(grupo), font_style2)
                        ws.write(row_num, 14, str(r.activotecnologico.get_statusactivo_display()), font_style2)
                        ws.write(row_num, 15, 'SI' if r.tiene_garantia() else 'NO', font_style2)


                        row_num += 1
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

            elif action == 'excelcategorias':
                try:
                    __author__ = 'Unemi'

                    font_style = XFStyle()
                    font_style.font.bold = True
                    font_style2 = XFStyle()
                    font_style2.font.bold = False
                    wb = Workbook(encoding='utf-8')
                    ws = wb.add_sheet('exp_xls_post_part')
                    response = HttpResponse(content_type="application/ms-excel")
                    response[
                        'Content-Disposition'] = 'attachment; filename=Listado' + random.randint(1,
                                                                                                 10000).__str__() + '.xls'
                    columns = [

                        (u"CATEGOR�A", 10000),
                        (u"TOTAL DE ACTIVOS", 5000),
                        (u"TOTAL CON INFORME DE BAJA", 5000),
                        (u"TOTAL PROCESO DE BAJA", 4000),
                        (u"TOTAL CON GARANT�A", 10000),
                    ]
                    row_num = 0
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], font_style)
                        ws.col(col_num).width = columns[col_num][1]
                    date_format = xlwt.XFStyle()
                    date_format.num_format_str = 'yyyy/mm/dd'
                    hoy = datetime.now().date()
                    fecha_tope = date(int(hoy.year - 3), int(hoy.month), int(hoy.day))
                    categorias = GruposCategoria.objects.filter(status=True)
                    activos = ActivoTecnologico.objects.filter(status=True,
                                                               activotecnologico__statusactivo=1,
                                                               activotecnologico__status=True)
                    row_num = 1
                    for categoria in categorias:
                        totalactivos = activos.filter(activotecnologico__catalogo__grupo=categoria)
                        totalprocesobaja = len(totalactivos.filter(activotecnologico__procesobaja=True))
                        totalgarantia = len(totalactivos.filter(activotecnologico__fechacomprobante__gte=fecha_tope))
                        ids = DocumentoFirmaInformeBaja.objects.filter(status=True).values_list(
                                'informe__activofijo_id', flat=True)
                        totalinforme = len(totalactivos.filter(Q(activotecnologico_id__in=ids)
                                                               |~Q(activotecnologico__archivobaja='')).distinct())

                        ws.write(row_num, 0, str(categoria), font_style2)
                        ws.write(row_num, 1, str(len(totalactivos)), font_style2)
                        ws.write(row_num, 2, str(totalinforme), font_style2)
                        ws.write(row_num, 3, str(totalprocesobaja), font_style2)
                        ws.write(row_num, 4, str(totalgarantia), font_style2)

                        row_num += 1
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

            elif action == 'pdflistadoactivos':
                try:
                    codigo, estado, search, filtro = request.GET.get('cadenatexto', ''), request.GET.get('estado',
                                                                                                         ''), request.GET.get(
                        's', ''), (Q(status=True))

                    if estado:
                        filtro = filtro & (Q(estado_id=estado))

                    if codigo:
                        if int(codigo) != 0:
                            filtro = filtro & Q(activotecnologico__catalogo__grupo__id=codigo)

                    if search:
                        ss = search.split(' ')

                        if len(ss) == 1:
                            filtro = filtro & (Q(descripcion__icontains=search) |
                                               Q(codigogobierno__icontains=search) |
                                               Q(serie__icontains=search) |
                                               Q(codigointerno__icontains=search) |
                                               Q(codigotic__icontains=search) |
                                               Q(modelo__icontains=search) |
                                               Q(codigogobierno__icontains=search) |
                                               Q(responsable__nombres__icontains=search) |
                                               Q(responsable__apellido1__icontains=search) |
                                               Q(responsable__apellido2__icontains=search))
                        else:
                            filtro = filtro & (Q(responsable__apellido1__icontains=ss[0]) &
                                               Q(responsable__apellido2__icontains=ss[1]))

                    fdesde, fhasta = request.GET.get('fechadesde', ''), request.GET.get('fechahasta', '')
                    data['desde'] = str(fdesde)
                    data['hasta'] = str(fhasta)

                    filtro = filtro & (Q(activotecnologico__archivobaja__isnull=True) |
                                       Q(activotecnologico__archivobaja='') |
                                       Q(activotecnologico__archivobaja__exact=' ')
                                       )

                    results = ActivoTecnologico.objects.filter(filtro & ~Q(activotecnologico__procesobaja=True), activotecnologico__statusactivo=1,
                                                               activotecnologico__fechaingreso__range=[fdesde,
                                                               fhasta]).select_related('activotecnologico').distinct().order_by('activotecnologico__fechaingreso').order_by('-id')

                    data['results'] = results
                    data['hoy'] = str(datetime.now().date())
                    # return conviert_html_to_pdf_name(
                    #     'inventario_activofijo/informes/activotecnologicopdf.html',
                    #     {'pagesize': 'A4', 'data': data,}, nombrearchivo)
                    return conviert_html_to_pdf(
                        'at_activostecnologicos/informes/activotecnologicopdf.html',
                        {
                            'pagesize': 'A4',
                            'data': data,
                        },
                    )
                except Exception as ex:
                    pass

            elif action == 'pdflistadoactivosinactios':
                try:
                    codigo, estado, search, filtro = request.GET.get('cadenatexto', ''), request.GET.get('estado', ''), request.GET.get('s', ''), (Q(status=True))

                    if estado:
                        filtro = filtro & (Q(estado_id=estado))

                    if codigo:
                        if int(codigo) != 0:
                            filtro = filtro & Q(activotecnologico__catalogo__grupo__id=codigo)


                    if search:
                        ss = search.split(' ')

                        if len(ss) == 1:
                            filtro = filtro & (Q(descripcion__icontains=search) |
                                               Q(codigogobierno__icontains=search) |
                                               Q(serie__icontains=search) |
                                               Q(codigointerno__icontains=search) |
                                               Q(codigotic__icontains=search) |
                                               Q(modelo__icontains=search) |
                                               Q(codigogobierno__icontains=search) |
                                               Q(responsable__nombres__icontains=search) |
                                               Q(responsable__apellido1__icontains=search) |
                                               Q(responsable__apellido2__icontains=search))
                        else:
                            filtro = filtro & (Q(responsable__apellido1__icontains=ss[0]) &
                                               Q(responsable__apellido2__icontains=ss[1]))

                    fdesde, fhasta = request.GET.get('fechadesde', ''), request.GET.get('fechahasta', '')
                    data['desde'] = str(fdesde)
                    data['hasta'] = str(fhasta)
                    results = ActivoTecnologico.objects.filter(filtro & ~Q(activotecnologico__archivobaja= '') &
                                                               ~Q(activotecnologico__archivobaja__isnull = True),
                                                               activotecnologico__fechaingreso__range=[fdesde, fhasta]).select_related('activotecnologico'
                                                                                                                                       ).distinct().order_by('-id')

                    data['results'] = results
                    data['hoy'] = str(datetime.now().date())
                    return conviert_html_to_pdf(
                        'at_activostecnologicos/informes/bajasactivotecnologicopdf.html',
                        {
                            'pagesize': 'A4',
                            'data': data,
                        },
                    )
                except Exception as ex:
                    pass

            elif action == 'pdflistadoactivostodos':
                try:
                    data['title'] = nombrearchivo = u'Informe de Activos Tecnol�gicos'
                    lista1 = '0'
                    if 'cadenatexto' in request.GET:
                        lista1 = request.GET['cadenatexto']
                    values_ac = InformeActivoBaja.objects.values('activofijo__id').filter(status=True).values_list(
                        'activofijo__id', flat=True)
                    if lista1 == '0':
                        sql = "select ac.codigointerno,ac.codigogobierno,ac.fechaingreso,age (current_date, ac.fechaingreso) || '' tiempo, " \
                              "cast(extract(year from age (current_date, ac.fechaingreso))*12 + extract(month from age (ac.fechaingreso)) as int)/12 as numanios " \
                              ",cat.descripcion as catalogo,ac.descripcion,ac.modelo,ac.marca," \
                              "(select perso.apellido1 || ' ' || perso.apellido2 || ' ' || perso.nombres from sga_persona perso where id=ac.responsable_id) as responsable , " \
                              "ac.id, (SELECT ubi.nombre AS ubicacion FROM sagest_ubicacion ubi WHERE ubi.id = ac.ubicacion_id)," \
                              "(SELECT est.nombre AS estado FROM sagest_estadoproducto est WHERE est.id = ac.estado_id) " \
                              "from sagest_activofijo ac,sagest_catalogobien cat,sagest_gruposcategoria gru " \
                              "where ac.catalogo_id=cat.id  and cat.equipoelectronico=True and cat.grupo_id=gru.id " \
                              "and ac.statusactivo=1 and cat.clasificado=True and ac.status=True and (ac.archivobaja='' or ac.archivobaja isnull) " \
                              "AND NOT ac.id IN {} ORDER BY ac.fechaingreso ASC".format(str(tuple(values_ac)))
                    else:
                        sql = "select ac.codigointerno,ac.codigogobierno,ac.fechaingreso,age (current_date, ac.fechaingreso) || '' tiempo, " \
                              "cast(extract(year from age (current_date, ac.fechaingreso))*12 + extract(month from age (ac.fechaingreso)) as int)/12 as numanios " \
                              ",cat.descripcion as catalogo,ac.descripcion,ac.modelo,ac.marca," \
                              "(select perso.apellido1 || ' ' || perso.apellido2 || ' ' || perso.nombres from sga_persona perso where id=ac.responsable_id) as responsable , " \
                              "ac.id, (SELECT ubi.nombre AS ubicacion FROM sagest_ubicacion ubi WHERE ubi.id = ac.ubicacion_id)," \
                              "(SELECT est.nombre AS estado FROM sagest_estadoproducto est WHERE est.id = ac.estado_id) " \
                              "from sagest_activofijo ac,sagest_catalogobien cat,sagest_gruposcategoria gru " \
                              "where ac.catalogo_id=cat.id  and cat.equipoelectronico=True and cat.grupo_id=gru.id " \
                              "and ac.statusactivo=1 and ac.status=True and gru.id=" + lista1 + " and (ac.archivobaja='' or ac.archivobaja isnull) " \
                                                                                                "AND NOT ac.id IN {} ORDER BY ac.fechaingreso ASC".format(
                            str(tuple(values_ac)))
                    cursor = connection.cursor()
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    data['results'] = results
                    data['hoy'] = str(datetime.now().date())
                    # return conviert_html_to_pdf_name(
                    #     'inventario_activofijo/informes/activotecnologicopdf.html',
                    #     {'pagesize': 'A4', 'data': data,}, nombrearchivo)
                    return conviert_html_to_pdf(
                        'at_activostecnologicos/informes/activotecnologicopdf.html',
                        {
                            'pagesize': 'A4',
                            'data': data,
                        },
                    )
                except Exception as ex:
                    pass

            elif action == 'solicitudestraspasoresponsable':
                try:
                    search = None
                    ids = None
                    s = None
                    perfil = None
                    data['title'] = u'Pendientes'
                    filtrocatalogo = Q(status=True)
                    if 'id' in request.GET:
                        s = request.GET['id']
                        data['s'] = s
                        search = request.GET['id'].strip()
                        ss = search.split(' ')
                        if len(ss) == 1:
                            filtro = filtrocatalogo & ((Q(responsableasignacion__nombres__icontains=search) |
                                                        Q(responsableasignacion__apellido1__icontains=search) |
                                                        Q(responsableasignacion__apellido2__icontains=search) |
                                                        Q(responsableasignacion__cedula__icontains=search) |
                                                        Q(responsableasignacion__pasaporte__icontains=search)) |
                                                       Q(activo__descripcion__icontains=search) |
                                                       Q(activo__codigogobierno__icontains=search))
                        else:
                            filtro = filtrocatalogo & ((Q(responsableasignacion__apellido1__icontains=ss[0]) &
                                                        Q(responsableasignacion__apellido2__icontains=ss[1])) |
                                                       Q(activo__descripcion__icontains=search) |
                                                       Q(activo__codigogobierno__icontains=search))
                    else:
                        filtro = filtrocatalogo
                    activos = SolicitudActivos.objects.filter(filtro).distinct().order_by('-id')
                    data['totales'] = totales = activos.values('id').count()
                    paging = MiPaginador(activos, 25)
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
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['search'] = search if search else ""
                    data['ids'] = ids if ids else ""
                    data['perfil'] = perfil if perfil else ""
                    data['listadocatalogo'] = page.object_list
                    data['totales'] = totales
                    return render(request, "at_activostecnologicos/solicitudestraspasoresponsable.html", data)
                except Exception as ex:
                    pass

            elif action == 'solicitudespendientesactivos':
                try:
                    search = None
                    ids = None
                    s = None
                    perfil = None
                    data['title'] = u'Pendientes'
                    filtrocatalogo = Q(status=True, estado=4)
                    if 'id' in request.GET:
                        s = request.GET['id']
                        data['s'] = s
                        search = request.GET['id'].strip()
                        ss = search.split(' ')
                        if len(ss) == 1:
                            filtro = filtrocatalogo & ((Q(responsableasignacion__nombres__icontains=search) |
                                                        Q(responsableasignacion__apellido1__icontains=search) |
                                                        Q(responsableasignacion__apellido2__icontains=search) |
                                                        Q(responsableasignacion__cedula__icontains=search) |
                                                        Q(responsableasignacion__pasaporte__icontains=search)) |
                                                       Q(activo__descripcion__icontains=search) |
                                                       Q(activo__codigogobierno__icontains=search))
                        else:
                            filtro = filtrocatalogo & ((Q(responsableasignacion__apellido1__icontains=ss[0]) &
                                                        Q(responsableasignacion__apellido2__icontains=ss[1])) |
                                                       Q(activo__descripcion__icontains=search) |
                                                       Q(activo__codigogobierno__icontains=search))
                    else:
                        filtro = filtrocatalogo
                    activos = SolicitudActivos.objects.filter(filtro).distinct().order_by('-id')
                    data['totales'] = totales = activos.values('id').count()
                    paging = MiPaginador(activos, 25)
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
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['search'] = search if search else ""
                    data['ids'] = ids if ids else ""
                    data['perfil'] = perfil if perfil else ""
                    data['listadocatalogo'] = page.object_list
                    data['totales'] = totales
                    return render(request, "at_activostecnologicos/solicitudesactivos.html", data)
                except Exception as ex:
                    pass

            elif action == 'solicitudespendientestraspasos':
                try:
                    search = None
                    ids = None
                    s = None
                    perfil = None
                    data['title'] = u'Traspasos Pendientes'
                    filtrocatalogo = Q(status=True, estado=2)
                    if 'id' in request.GET:
                        s = request.GET['id']
                        data['s'] = s
                        search = request.GET['id'].strip()
                        ss = search.split(' ')
                        if len(ss) == 1:
                            filtro = filtrocatalogo & ((Q(responsableasignacion__nombres__icontains=search) |
                                                        Q(responsableasignacion__apellido1__icontains=search) |
                                                        Q(responsableasignacion__apellido2__icontains=search) |
                                                        Q(responsableasignacion__cedula__icontains=search) |
                                                        Q(responsableasignacion__pasaporte__icontains=search)) |
                                                       Q(activo__descripcion__icontains=search) |
                                                       Q(activo__codigogobierno__icontains=search))
                        else:
                            filtro = filtrocatalogo & ((Q(responsableasignacion__apellido1__icontains=ss[0]) &
                                                        Q(responsableasignacion__apellido2__icontains=ss[1])) |
                                                       Q(activo__descripcion__icontains=search) |
                                                       Q(activo__codigogobierno__icontains=search))
                    else:
                        filtro = filtrocatalogo
                    activos = SolicitudActivos.objects.filter(filtro).distinct().order_by('-id')
                    data['totales'] = totales = activos.values('id').count()
                    paging = MiPaginador(activos, 25)
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
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['search'] = search if search else ""
                    data['ids'] = ids if ids else ""
                    data['perfil'] = perfil if perfil else ""
                    data['listadocatalogo'] = page.object_list
                    data['totales'] = totales
                    return render(request, "at_activostecnologicos/solicitudestraspasosactivos.html", data)
                except Exception as ex:
                    pass

            elif action == 'historialtraspaso':
                try:
                    if 'id' in request.GET:
                        data['historialtraspaso'] = HistorialTraspaso.objects.filter(activofijo=int(request.GET['id']),
                                                                                     status=True).order_by('-id')
                        data['activofijo'] = ActivoFijo.objects.get(status=True, pk=int(request.GET['id']))
                        #template = get_template("at_activostecnologicos/historialtraspaso.html")
                        #return JsonResponse({"result": 'ok', 'data': template.render(data)})
                        return render(request, "at_activostecnologicos/historialtraspaso.html",data)
                except Exception as ex:
                    pass

            elif action == 'generarcodigoqrtic':

                try:
                    if 'id' in request.GET and 'ids' in request.GET:
                        ruta_carpeta = os.path.join(SITE_STORAGE,'media','activosTecQr')
                        try:
                            os.stat(ruta_carpeta)
                        except:
                            os.mkdir(ruta_carpeta)
                        lista_archivos = os.listdir(ruta_carpeta)
                        for archivo in lista_archivos:
                            os.remove(os.path.join(ruta_carpeta, archivo))
                        data['idm'] = idm = int(request.GET['id'])
                        data['idt'] = idt = int(request.GET['ids'])
                        activo = ActivoTecnologico.objects.get(activotecnologico_id=idm, codigotic=idt, status=True)
                        ruta = 'https://sga.unemi.edu.ec/activodetalleqr?action=qr_presentacion&id=' + str(data['idm'])
                        rutaqr = '/media/activosTecQr/Activo' + str(activo.codigotic) + '.png'
                        url = pyqrcode.create(ruta)
                        data['ruta'] = rutaqr
                        data['detalle'] = str(activo.activotecnologico)
                        url.png(SITE_STORAGE+'/media/activosTecQr/Activo' + str(activo.codigotic) + '.png', 10, '#000000')
                        template = get_template("at_activostecnologicos/codigoqr.html")
                        json_content = template.render(data)
                        return JsonResponse({"result": "ok", 'html': json_content})
                except Exception as ex:
                    pass

            elif action == 'solicitudtraspaso':
                try:
                    if 'id' in request.GET:
                        data['estado'] = True
                        data['activo'] = ActivoFijo.objects.filter(status=True, pk=int(request.GET['id']))
                        data['solicitudactivo'] = SolicitudActivos.objects.filter(activo_id=int(request.GET['id']),
                                                                                  estado=2, status=True).order_by('-id')
                        #template = get_template("inventario_activofijo/solicitudactivo.html")
                        #return JsonResponse({"result": 'ok', 'data': template.render(data)})
                        return render(request, "at_activostecnologicos/solicitudactivo.html", data)
                except Exception as ex:
                    pass

            elif action == 'pdflistadoactivosinactiostodos':
                try:
                    data['title'] = nombrearchivo = u'Informe de Activos Tecnol�gicos'
                    fdesde, fhasta = request.GET.get('fechadesde', ''), request.GET.get('fechahasta', '')
                    data['desde'] = str(fdesde)
                    data['hasta'] = str(fhasta)
                    lista1 = '0'
                    if 'cadenatexto' in request.GET:
                        lista1 = request.GET['cadenatexto']
                    values_ac = InformeActivoBaja.objects.values('activofijo__id').filter(status=True,
                                                                                          activofijo__catalogo__equipoelectronico=True
                                                                                          ).values_list(
                        'activofijo__id', flat=True)
                    if not values_ac:
                        values_ac = [0]
                    if lista1 == '0':
                        sql = "select ac.codigointerno,ac.codigogobierno,ac.fechaingreso,age (current_date, ac.fechaingreso) || '' tiempo, " \
                              "cast(extract(year from age (current_date, ac.fechaingreso))*12 + extract(month from age (ac.fechaingreso)) as int)/12 as numanios " \
                              ",cat.descripcion as catalogo,ac.descripcion,ac.modelo,ac.marca," \
                              "(select perso.apellido1 || ' ' || perso.apellido2 || ' ' || perso.nombres from sga_persona perso where id=ac.responsable_id) as responsable , " \
                              "ac.id, (SELECT ubi.nombre AS ubicacion FROM sagest_ubicacion ubi WHERE ubi.id = ac.ubicacion_id)," \
                              "(SELECT est.nombre AS estado FROM sagest_estadoproducto est WHERE est.id = ac.estado_id), " \
                              "(SELECT DATE(fecha_creacion) FROM sagest_informeactivobaja WHERE activofijo_id=ac.id) AS fecha_salida " \
                              "from sagest_activofijo ac,sagest_catalogobien cat,sagest_gruposcategoria gru " \
                              "where ac.catalogo_id=cat.id  and cat.equipoelectronico=True and cat.grupo_id=gru.id " \
                              "and ac.statusactivo=1 and ac.status=True and (ac.archivobaja='' or ac.archivobaja isnull) " \
                              "AND ac.id IN {} ORDER BY fecha_salida ASC".format(str(tuple(values_ac)))
                    else:
                        sql = "select ac.codigointerno,ac.codigogobierno,ac.fechaingreso,age (current_date, ac.fechaingreso) || '' tiempo, " \
                              "cast(extract(year from age (current_date, ac.fechaingreso))*12 + extract(month from age (ac.fechaingreso)) as int)/12 as numanios " \
                              ",cat.descripcion as catalogo,ac.descripcion,ac.modelo,ac.marca," \
                              "(select perso.apellido1 || ' ' || perso.apellido2 || ' ' || perso.nombres from sga_persona perso where id=ac.responsable_id) as responsable , " \
                              "ac.id, (SELECT ubi.nombre AS ubicacion FROM sagest_ubicacion ubi WHERE ubi.id = ac.ubicacion_id)," \
                              "(SELECT est.nombre AS estado FROM sagest_estadoproducto est WHERE est.id = ac.estado_id), " \
                              "(SELECT DATE(fecha_creacion) FROM sagest_informeactivobaja WHERE activofijo_id=ac.id) AS fecha_salida " \
                              "from sagest_activofijo ac,sagest_catalogobien cat,sagest_gruposcategoria gru " \
                              "where ac.catalogo_id=cat.id  and cat.equipoelectronico=True and cat.grupo_id=gru.id " \
                              "and ac.statusactivo=1 and ac.status=True and gru.id=" + lista1 + " and (ac.archivobaja='' or ac.archivobaja isnull) " \
                                                                                                "AND  ac.id IN {} ORDER BY fecha_salida ASC".format(
                            str(tuple(values_ac)))
                    cursor = connection.cursor()
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    data['results'] = results
                    data['hoy'] = str(datetime.now().date())
                    # return conviert_html_to_pdf_name(
                    #     'inventario_activofijo/informes/activotecnologicopdf.html',
                    #     {'pagesize': 'A4', 'data': data,}, nombrearchivo)
                    return conviert_html_to_pdf(
                        'at_activostecnologicos/informes/bajasactivotecnologicopdf.html',
                        {
                            'pagesize': 'A4',
                            'data': data,
                        },
                    )
                except Exception as ex:
                    pass

            elif action == 'notificarresponsabledebien':
                try:
                    filtro = TipoNotificacion.objects.filter(status=True).first()
                    if filtro:
                        initial_data = {
                            'tipo': filtro.id,
                        }
                    else:
                        initial_data = {}
                    form = NotificacionactivoresponsableForm(initial=initial_data)
                    data['action'] = 'notificarresponsabledebien'
                    data['id'] = request.GET['id']
                    data['idp'] = request.GET['idp']

                    data['form'] = form
                    template = get_template("at_activostecnologicos/formnotificarusuario.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'attecpdf':
                try:
                    data = {}
                    data['fechaactual'] = datetime.now()
                    data['activofijo'] = activofijo = ActivoFijo.objects.get(pk=int(request.GET['id']))
                    data['detallemantenimiento'] = HdDetalle_Incidente.objects.filter(incidente__activo=activofijo,
                                                                                      status=True,
                                                                                      incidente__status=True,
                                                                                      resolucion__isnull=False).exclude(
                        resolucion__exact='')
                    data['mantenimientopreventivo'] = activofijo.mantenimientosactivospreventivos_set.filter(
                        status=True)
                    data[
                        'mantenimientogarantia'] = mantenimientogarantia = activofijo.mantenimientosactivosgarantia_set.filter(
                        status=True)
                    data['costomantenimientogarantia'] = \
                    mantenimientogarantia.filter(status=True).aggregate(cantidad=Sum('valor'))['cantidad']
                    return conviert_html_to_pdf('at_activostecnologicos/informes/histtecnologico_pdf.html',
                                                {'pagesize': 'A4', 'data': data})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Problemas al ejecutar el reporte. %s" % ex})

            elif action == 'buscarpersonasactivos':
                try:
                    q = request.GET['q'].upper().strip()
                    s = q.split(" ")
                    idspersonas=ActivoFijo.objects.filter(status=True).values_list('responsable_id', flat=True).distinct()
                    qspersona = Persona.objects.filter(status=True, distributivopersona__isnull=False, id__in=idspersonas).order_by('apellido1')
                    if len(s) == 1:
                        qspersona = qspersona.filter((Q(nombres__icontains=q) | Q(apellido1__icontains=q) | Q(
                            cedula__icontains=q) | Q(apellido2__icontains=q) | Q(cedula__contains=q)),
                                                     Q(status=True)).distinct()[:15]
                    elif len(s) == 2:
                        qspersona = qspersona.filter((Q(apellido1__contains=s[0]) & Q(apellido2__contains=s[1])) |
                                                     (Q(nombres__icontains=s[0]) & Q(nombres__icontains=s[1])) |
                                                     (Q(nombres__icontains=s[0]) & Q(apellido1__contains=s[1]))).filter(
                            status=True).distinct()[:15]
                    else:
                        qspersona = qspersona.filter(
                            (Q(nombres__contains=s[0]) & Q(apellido1__contains=s[1]) & Q(apellido2__contains=s[2])) |
                            (Q(nombres__contains=s[0]) & Q(nombres__contains=s[1]) & Q(
                                apellido1__contains=s[2]))).filter(status=True).distinct()[:15]
                    resp = [{'id': qs.pk, 'text': f"{qs.nombre_completo_inverso()}",
                             'documento': qs.documento(),
                             'foto': qs.get_foto()} for qs in qspersona]
                    return HttpResponse(json.dumps({'status': True, 'results': resp}))
                except Exception as ex:
                    pass

            if action == 'buscarpersonasdistributivo':
                try:
                    q = request.GET['q'].upper().strip()
                    s = q.split(" ")
                    qspersona = Persona.objects.filter(status=True, distributivopersona__isnull=False).order_by('apellido1')
                    if len(s) == 1:
                        qspersona = qspersona.filter((Q(nombres__icontains=q) | Q(apellido1__icontains=q) | Q(
                            cedula__icontains=q) | Q(apellido2__icontains=q) | Q(cedula__contains=q)),
                                                     Q(status=True)).distinct()[:15]
                    elif len(s) == 2:
                        qspersona = qspersona.filter((Q(apellido1__contains=s[0]) & Q(apellido2__contains=s[1])) |
                                                     (Q(nombres__icontains=s[0]) & Q(nombres__icontains=s[1])) |
                                                     (Q(nombres__icontains=s[0]) & Q(apellido1__contains=s[1]))).filter(
                            status=True).distinct()[:15]
                    else:
                        qspersona = qspersona.filter(
                            (Q(nombres__contains=s[0]) & Q(apellido1__contains=s[1]) & Q(apellido2__contains=s[2])) |
                            (Q(nombres__contains=s[0]) & Q(nombres__contains=s[1]) & Q(
                                apellido1__contains=s[2]))).filter(status=True).distinct()[:15]

                    resp = [{'id': qs.pk, 'text': f"{qs.nombre_completo_inverso()}",
                             'documento': qs.documento(),
                             'foto': qs.get_foto()} for qs in qspersona]
                    return HttpResponse(json.dumps({'status': True, 'results': resp}))
                except Exception as ex:
                    pass
            #INFORME BAJA
            elif action == 'addinformebaja':
                try:
                    data['id']=int(encrypt(request.GET['idp']))
                    id=int(encrypt(request.GET['id']))
                    activo_t=ActivoTecnologico.objects.get(id=id)
                    form = InformeBajaATForm(initial={'solicita': activo_t.activotecnologico.responsable,
                                                      'responsable_': persona,
                                                      'estadouso': 2,
                                                      'estado': 2})
                    form.fields['solicita'].queryset = Persona.objects.filter(id=activo_t.activotecnologico.responsable.id)
                    form.fields['responsable_'].queryset=Persona.objects.filter(id=persona.id)
                    data['form']=form
                    data['actividades']=activo_t.actividades_informe_baja()
                    template=get_template('at_activostecnologicos/modal/forminformebaja.html')
                    return JsonResponse({'result':True,'data':template.render(data)})
                except Exception as ex:
                    messages.error(f'{ex}')
                    return HttpResponseRedirect(request.path)

            elif action == 'editinformebaja':
                try:
                    idp=int(encrypt(request.GET['idp']))
                    id=int(encrypt(request.GET['id']))
                    activo_t=ActivoFijo.objects.get(id=idp)
                    informe=InformeActivoBaja.objects.get(activofijo_id=activo_t.id, status=True)
                    informe_dict=model_to_dict(informe)
                    informe_dict['responsable_']=informe.responsable
                    form = InformeBajaATForm(initial=informe_dict)
                    form.fields['solicita'].queryset = Persona.objects.filter(id=informe.solicita.id)
                    form.fields['responsable_'].queryset=Persona.objects.filter(id=informe.responsable.id)
                    data['form']=form
                    data['informe']=informe
                    data['id'] = informe.id
                    data['actividades']=informe.actividades_informe_baja()
                    template=get_template('at_activostecnologicos/modal/forminformebaja.html')
                    return JsonResponse({'result':True,'data':template.render(data)})
                except Exception as ex:
                    messages.error(f'{ex}')
                    return HttpResponseRedirect(request.path)

            elif action == 'firmarinformebaja':
                try:
                    firmadirector=request.GET.get('tipos','')
                    id=int(encrypt(request.GET['id']))
                    if not firmadirector:
                        directory = os.path.join(MEDIA_ROOT, 'reportes', 'informesbaja')
                        valido = True
                        nombre_archivo = 'Informe_Baja' + str(random.randint(1, 10000)) + '.pdf'
                        try:
                            os.stat(directory)
                        except:
                            os.mkdir(directory)

                        bajaactivo = None
                        detalle = None
                        director = None
                        activofijo = ActivoFijo.objects.get(pk=id)
                        if activofijo.informeactivobaja_set.filter(status=True):
                            bajaactivo = activofijo.informeactivobaja_set.filter(status=True)[0]
                            perso = Persona.objects.get(usuario=bajaactivo.usuario_creacion)
                            detalle = bajaactivo.detalleinformeactivobaja_set.filter(status=True)
                            if DirectorResponsableBaja.objects.filter(actual=True, status=True).exists():
                                director = DirectorResponsableBaja.objects.get(actual=True, status=True)
                                if not bajaactivo.fecha_creacion.date() > director.fechainicio:
                                    if DirectorResponsableBaja.objects.filter(fechainicio__lte=bajaactivo.fecha_creacion.date(),
                                                                              fechafin__gte=bajaactivo.fecha_creacion.date(),
                                                                              status=True).exists():
                                        director = DirectorResponsableBaja.objects.get(
                                            fechainicio__lte=bajaactivo.fecha_creacion.date(),
                                            fechafin__gte=bajaactivo.fecha_creacion.date(), status=True)

                        dir = 'af_activofijo/informebajapdf.html'
                        valido = conviert_html_to_pdfsaveqr_generico(request,dir,
                                                    {'pagesize': 'A4',
                                                     'informe': activofijo, 'perso': perso, 'director': director,
                                                     'bajaactivo': bajaactivo, 'detalle': detalle, 'hoy': datetime.now().date()
                                                     },directory,nombre_archivo)
                        if not valido[0]:
                            raise NameError('Error al generar el informe')
                        archivo = '/media/reportes/informesbaja/' + nombre_archivo
                    else:
                        documento=DocumentoFirmaInformeBaja.objects.get(id=id)
                        archivo=documento.ultimo_dcoumento().archivo.url
                        id=documento.informe.activofijo.id

                    data['archivo'] = archivo
                    data['url_archivo'] = '{}{}'.format(dominio_sistema, archivo)
                    data['id_objeto'] = id
                    data['val_extra'] = firmadirector
                    data['action_firma'] = 'firmarinformebaja'
                    template = get_template("formfirmaelectronica.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(f'{ex}')
                    return HttpResponseRedirect(request.path)

            elif action == 'informesbaja':
                try:
                    data['title'] = u'Informes de baja'
                    search, url_vars,estado = request.GET.get('s', ''), '',request.GET.get('estado','')
                    url_vars = f"&action={action}"
                    filtro = Q(status=True, informe__tipoinforme=1)
                    if search:
                        data['s']=search = request.GET['s']
                        ss = search.split(' ')
                        if len(ss) == 1:
                            filtro = filtro & (Q(informe__activofijo__descripcion=search) |
                                               Q(informe__activofijo__codigogobierno=search) |
                                               Q(informe__activofijo__serie=search) |
                                               Q(informe__activofijo__codigointerno=search) |
                                               Q(informe__activofijo__codigogobierno__icontains=search) |
                                               Q(informe__responsable__nombres__icontains=search) |
                                               Q(informe__responsable__apellido1__icontains=search) |
                                               Q(informe__responsable__apellido2__icontains=search))
                        else:
                            filtro = filtro & (Q(informe__responsable__apellido1__icontains=ss[0]) &
                                               Q(informe__responsable__apellido2__icontains=ss[1]))
                        url_vars += f"&s={search}"
                    if estado:
                        data['estado']=estado=int(estado)
                        url_vars += f"&estado={estado}"
                        if estado == 1:
                            filtro = filtro & (Q(firmadirector=False))
                        elif estado == 2:
                            filtro = filtro & (Q(firmadirector=True))

                    documentos = DocumentoFirmaInformeBaja.objects.filter(filtro).order_by('-id')
                    paging = MiPaginador(documentos, 25)
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
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['search'] = search if search else ""
                    data['listado'] = page.object_list
                    data['url_vars'] = url_vars
                    data['t_firmados']=len(documentos.filter(firmadirector=True, status=True))
                    data['t_pendientes']=len(documentos.filter(firmadirector=False, status=True))
                    request.session['viewactivo']=2
                    return render(request, "at_activostecnologicos/informesbaja.html", data)
                except Exception as ex:
                    messages.error(f'{ex}')
                    return HttpResponseRedirect(request.path)

            elif action == 'firmarinformebajamasivo':
                try:
                    template = get_template("formfirmaelectronicamasiva.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(f'{ex}')
                    return HttpResponseRedirect(request.path)

            elif action == 'historialfirmas':
                try:
                    id = int(encrypt(request.GET['id']))
                    data['documento']=documento=DocumentoFirmaInformeBaja.objects.get(id=id)
                    template = get_template("at_activostecnologicos/modal/historialfirmas.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(f'{ex}')
                    return HttpResponseRedirect(request.path)

            elif action == 'detalle_activo':
                try:
                    data['activo'] = activo = ActivoFijo.objects.get(pk=int(request.GET['id']))
                    template = get_template("at_activostecnologicos/detalleActM.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mensaje": u"Error al obtener los datos."})

            elif action == 'subirinforme':
                try:
                    data['id']=id=int(encrypt(request.GET['id']))
                    data['activo'] = activo = ActivoFijo.objects.get(pk=id)
                    data['form']=ArchivoActivoBajaForm()
                    template = get_template("ajaxformmodal.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mensaje": u"Error al obtener los datos."})

            return HttpResponseRedirect(request.path)

        else:
            try:
                data['title'] = u'Activos tecnol�gicos'
                data['subtitle'] = u'Listado de activos tecnol�gicos'
                ids = None
                responsable, codigo, estado, clase, cuenta, search, filtro, url_vars = request.GET.get('responsable',''),\
                                                                                       request.GET.get('codigo',''), \
                                                                                       request.GET.get('estado',''), \
                                                                                       request.GET.get('clase', ''), \
                                                                                       request.GET.get('cuenta', ''), \
                                                                                       request.GET.get('s', ''), (Q(status=True,activotecnologico__statusactivo=1)), ''
                if responsable:
                    data['responsable'] = responsable
                    data['persona_r']=Persona.objects.get(id=responsable)
                    url_vars += "&responsable={}".format(responsable)
                    filtro = filtro & (Q(responsable_id=responsable)|Q(activotecnologico__responsable_id=responsable))

                if estado:
                    if not estado == 'informebaja':
                        estado = int(estado)
                        filtro = filtro & (Q(activotecnologico__estado_id=estado))
                        data['estado'] = estado
                    else:
                        ids=DocumentoFirmaInformeBaja.objects.filter(status=True).values_list('informe__activofijo_id',flat=True)
                        filtro = filtro & (Q(activotecnologico_id__in=ids))
                        data['estado'] = estado
                    url_vars += "&estado={}".format(estado)

                if codigo:
                    data['codigo'] = c = int(codigo)
                    if c != 0:
                        url_vars += "&codigo={}".format(codigo)
                        filtro = filtro & Q(activotecnologico__catalogo__grupo__id=codigo)

                if clase:
                    data['clase'] = int(clase)
                    url_vars += "&clase={}".format(clase)
                    filtro = filtro & (Q(clasebien=clase))

                if cuenta:
                    data['cuenta'] = int(cuenta)
                    url_vars += "&cuenta={}".format(cuenta)
                    filtro = filtro & (Q(cuentacontable=cuenta))

                if search:
                    data['s'] = search = request.GET['s'].strip()
                    ss = search.split(' ')
                    url_vars += "&s={}".format(search)
                    if len(ss) == 1:
                        filtro = filtro & (Q(descripcion__icontains=search) |
                                           Q(codigogobierno__icontains=search) |
                                           Q(activotecnologico__codigogobierno__icontains=search) |
                                           Q(serie__icontains=search) |
                                           Q(codigointerno__icontains=search) |
                                           Q(activotecnologico__codigointerno__icontains=search) |
                                           Q(codigotic__icontains=search) |
                                           Q(modelo__icontains=search) |
                                           Q(codigogobierno__icontains=search) |
                                           Q(activotecnologico__responsable__nombres__icontains=search) |
                                           Q(activotecnologico__responsable__apellido1__icontains=search) |
                                           Q(activotecnologico__responsable__apellido2__icontains=search))
                    else:
                        filtro = filtro & (Q(activotecnologico__responsable__apellido1__unaccent__icontains=ss[0]) &
                                           Q(activotecnologico__responsable__apellido2__unaccent__icontains=ss[1]))

                if 'id' in request.GET:
                    ids = int(request.GET['id'])
                    filtro = filtro & (Q(status=True))

                activos = ActivoTecnologico.objects.filter(filtro).distinct().order_by('-id')
                paging = MiPaginador(activos, 25)

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

                data['grupocatalogo'] = GruposCategoria.objects.filter(status=True)

                request.session['paginador'] = p
                data['paging'] = paging
                data['rangospaging'] = paging.rangos_paginado(p)
                data['usuario'] = usuario
                data['page'] = page
                data['ids'] = ids if ids else ""
                data['activos'] = page.object_list
                data['totalregistros'] = activos.count()
                hoy = datetime.now().date()

                if  int(hoy.month) == 2 and int(hoy.day)==29:
                    fecha_tope = date(int(hoy.year - 3), int(hoy.month), 28)
                else:
                    fecha_tope = date(int(hoy.year - 3), int(hoy.month), int(hoy.day))
                data['total_infome'] = len(activos.exclude(activotecnologico__archivobaja__isnull=False,activotecnologico__archivobaja='').values_list('id'))
                data['total_garantia'] = len(activos.filter(activotecnologico__fechacomprobante__gte=fecha_tope).values_list('id'))
                data['total_baja'] = len(activos.filter(activotecnologico__procesobaja=True).values_list('id'))
                data['estados'] = EstadoProducto.objects.filter(status=True)
                data['clases'] = CLASE_BIEN
                data['url_vars'] = url_vars
                #data['cuentas'] = CuentaContable.objects.filter(status=True, activosfijos=True)
                data['fecha'] = datetime.now().date()
                request.session['viewactivo']=1
                return render(request, "at_activostecnologicos/view.html", data)
            except Exception as ex:
                pass






