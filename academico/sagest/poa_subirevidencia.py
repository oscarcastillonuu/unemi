# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.context import Context
from django.template.loader import get_template

from decorators import secure_module
from sagest.forms import AccionDocumentoDetalleForm
from sagest.models import AccionDocumentoDetalle, UsuarioEvidencia, AccionDocumentoDetalleRecord, PoaArchivo, \
    AccionDocumento, PeriodoPoa
from sga.commonviews import adduserdata
from sga.funciones import generar_nombre,log
from sga.models import MESES_CHOICES


@login_required(redirect_field_name='ret', login_url='/loginsagest')
@transaction.atomic()
@secure_module
def view(request):
    data = {}
    adduserdata(request, data)
    usuarioevidencia = UsuarioEvidencia.objects.filter(status=True, userpermiso=data['persona'].usuario)
    if not usuarioevidencia.exists():
        return HttpResponseRedirect("/?info=No tiene permisos asignado para este modulo.")
    usuarioevidencia = usuarioevidencia[0]
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'add_evidencia':
            try:
                f = AccionDocumentoDetalleForm(request.POST, request.FILES)
                d = request.FILES['archivo']
                newfilesd = d._name
                ext = newfilesd[newfilesd.rfind("."):]
                if ext == '.pdf':
                    a = 1
                else:
                    return JsonResponse({"result": "bad", "mensaje": u"Error, solo archivos .pdf."})
                if d.size > 10485760:
                    return JsonResponse({"result": "bad", "mensaje": u"Error, archivo mayor a 10 Mb."})
                if f.is_valid():
                    if int(request.POST['record']) == 0:
                        acciondocumentodetallerecord = AccionDocumentoDetalleRecord(acciondocumentodetalle_id=int(request.POST['id']),
                                                                                    observacion_envia=f.cleaned_data['observacion_envia'],
                                                                                    usuario_envia=request.user,
                                                                                    estado_accion_aprobacion=7,
                                                                                    rubrica_aprobacion_id=7,
                                                                                    estado_accion_revisa=7,
                                                                                    rubrica_revisa_id=7,
                                                                                    fecha_envia=datetime.now())
                        acciondocumentodetallerecord.save(request)
                        acciondocumentodetallerecord.acciondocumentodetalle.estado_accion = 7
                        acciondocumentodetallerecord.acciondocumentodetalle.estado_rubrica_id = 7
                        acciondocumentodetallerecord.acciondocumentodetalle.save(request)
                    else:
                        acciondocumentodetallerecord = AccionDocumentoDetalleRecord.objects.get(pk=int(request.POST['record']))
                        acciondocumentodetallerecord.observacion_envia = f.cleaned_data['observacion_envia']
                        acciondocumentodetallerecord.usuario_envia = request.user
                        acciondocumentodetallerecord.estado_accion_aprobacion = 7
                        acciondocumentodetallerecord.rubrica_aprobacion_id = 7
                        acciondocumentodetallerecord.estado_accion_revisa = 7
                        acciondocumentodetallerecord.rubrica_revisa_id = 7
                        acciondocumentodetallerecord.fecha_envia = datetime.now()
                        acciondocumentodetallerecord.save(request)
                        acciondocumentodetallerecord.acciondocumentodetalle.estado_accion = 7
                        acciondocumentodetallerecord.acciondocumentodetalle.estado_rubrica_id = 7
                        acciondocumentodetallerecord.acciondocumentodetalle.save(request)
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        if newfile:
                            newfile._name = generar_nombre("Evidencia", newfile._name)
                            acciondocumentodetallerecord.archivo = newfile
                            acciondocumentodetallerecord.save(request)
                    log(u'añadio evidencia poa: %s' % acciondocumentodetallerecord.id, request,"add")
                    return JsonResponse({"result": "ok"})
                else:
                     raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": "Error al guardar los datos."})

        return JsonResponse({"result": "bad", "mensaje": "Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'ver_observacion':
                try:
                    data = {}
                    acciondocumento = AccionDocumento.objects.get(pk=int(request.GET['iddocumento']))
                    return JsonResponse({"result": "ok", 'data': acciondocumento.observacion})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            if action == 'ver_medio':
                try:
                    data = {}
                    acciondocumento = AccionDocumento.objects.get(pk=int(request.GET['iddocumento']))
                    return JsonResponse({"result": "ok", 'data': acciondocumento.medioverificacion.nombre})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            if action == 'add_evidencia':
                try:
                    data = {}
                    acciondocumentodetalle = AccionDocumentoDetalle.objects.get(pk=int(request.GET['id']))
                    if int(request.GET['record']) == 0:
                        data['form'] = AccionDocumentoDetalleForm
                    else:
                        acciondocumentodetallerecord = AccionDocumentoDetalleRecord.objects.get(pk=int(request.GET['record']))
                        data['form'] = AccionDocumentoDetalleForm(initial={'observacion_envia': acciondocumentodetallerecord.observacion_envia})
                    data['permite_modificar'] = True
                    data['record'] = int(request.GET['record'])
                    data['acciondocumentodetalle'] = acciondocumentodetalle.__str__()
                    data['id'] = acciondocumentodetalle.id
                    template = get_template("poa_subirevidencia/add_evidencia.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": "ok", 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = u'Subir Evidencia'
                if not PeriodoPoa.objects.filter(activo=True,status=True).exists():
                    return HttpResponseRedirect("/?info=No existe periodos activos o dias a evaluar. ")
                diasingreso = PeriodoPoa.objects.filter(activo=True,status=True)
                hoymaxmesanterior = datetime.now().date() - timedelta(days=diasingreso[0].diassubir)
                hoy = datetime.now().date()
                data['mes'] = MESES_CHOICES[hoy.month - 1][1]
                if usuarioevidencia.carrera:
                    acciondocumento = AccionDocumentoDetalle.objects.filter(acciondocumento__status=True, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__periodopoa__ingresar=True, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__departamento=usuarioevidencia.unidadorganica, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__carrera=usuarioevidencia.carrera).filter(mostrar=True, status=True, inicio__lte=hoy, fin__gte=hoy).order_by('acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__orden','acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__orden','acciondocumento__indicadorpoa__objetivooperativo__orden','acciondocumento__indicadorpoa__orden','acciondocumento__orden')
                    acciondocumentoante = AccionDocumentoDetalle.objects.filter(acciondocumento__status=True, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__periodopoa__ingresar=True, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__departamento=usuarioevidencia.unidadorganica, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__carrera=usuarioevidencia.carrera).filter(mostrar=True, status=True, inicio__lte=hoymaxmesanterior, fin__gte=hoymaxmesanterior).order_by('acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__orden','acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__orden','acciondocumento__indicadorpoa__objetivooperativo__orden','acciondocumento__indicadorpoa__orden','acciondocumento__orden')
                else:
                    acciondocumento = AccionDocumentoDetalle.objects.filter(acciondocumento__status=True, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__periodopoa__ingresar=True, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__departamento=usuarioevidencia.unidadorganica, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__carrera__isnull=True).filter(mostrar=True, status=True, inicio__lte=hoy, fin__gte=hoy).order_by('acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__orden','acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__orden','acciondocumento__indicadorpoa__objetivooperativo__orden','acciondocumento__indicadorpoa__orden','acciondocumento__orden')
                    acciondocumentoante = AccionDocumentoDetalle.objects.filter(acciondocumento__status=True, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__periodopoa__ingresar=True, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__departamento=usuarioevidencia.unidadorganica, acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__carrera__isnull=True).filter(mostrar=True, status=True, inicio__lte=hoymaxmesanterior, fin__gte=hoymaxmesanterior).order_by('acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__orden','acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__orden','acciondocumento__indicadorpoa__objetivooperativo__orden','acciondocumento__indicadorpoa__orden','acciondocumento__orden')
                if acciondocumento:
                    if acciondocumentoante:
                        data['acciondocumento'] = (acciondocumento | acciondocumentoante).order_by('acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__orden','acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__orden','acciondocumento__indicadorpoa__objetivooperativo__orden','acciondocumento__indicadorpoa__orden','acciondocumento__orden').distinct()
                    else:
                        data['acciondocumento'] = acciondocumento
                else:
                    if acciondocumentoante:
                        data['acciondocumento'] = acciondocumentoante.order_by('acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__objetivoestrategico__orden','acciondocumento__indicadorpoa__objetivooperativo__objetivotactico__orden','acciondocumento__indicadorpoa__objetivooperativo__orden','acciondocumento__indicadorpoa__orden','acciondocumento__orden').distinct()
                    else:
                        return HttpResponseRedirect("/?info=No existe configuración para este periodo. Verificar en el módulo acciones correctivas. ")
                periodopoa = data['acciondocumento'][0].acciondocumento.indicadorpoa.objetivooperativo.objetivotactico.objetivoestrategico.periodopoa
                records = PoaArchivo.objects.filter(unidadorganica=usuarioevidencia.unidadorganica, status=True, periodopoa=periodopoa).order_by('-fecha')
                if records:
                    data['p'] = records[0]
                return render(request, "poa_subirevidencia/view.html", data)
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})