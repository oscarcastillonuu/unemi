# -*- coding: UTF-8 -*-

import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import get_template

from datetime import datetime
from decorators import secure_module
from sagest.forms import PeriodoPoaForm, EvaluacionPoaForm
from sagest.models import PeriodoPoa, InformeGenerado, EvaluacionPeriodoPoa
from sga.commonviews import adduserdata
from sga.funciones import MiPaginador, generar_nombre,log
from sga.templatetags.sga_extras import encrypt


@login_required(redirect_field_name='ret', login_url='/loginsagest')
@transaction.atomic()
@secure_module
def view(request):
    data = {}
    adduserdata(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            try:
                f = PeriodoPoaForm(request.POST, request.FILES)
                if f.is_valid():
                    if PeriodoPoa.objects.filter(anio=f.cleaned_data['anio'], status=True).exists():
                        # return JsonResponse({"result": False , "mensaje": u"Periodo existente."})
                        return redirect('/poa_periodos?info=Periodo existente')

                    newfile = None
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("periodopoa_", newfile._name)
                    periodopoa = PeriodoPoa(anio=f.cleaned_data['anio'],
                                            descripcion=f.cleaned_data['descripcion'],
                                            diassubir=f.cleaned_data['diassubir'],
                                            mostrar=f.cleaned_data['mostrar'],
                                            archivo=newfile)
                    periodopoa.save(request)
                    log(u'añadio periodo poa: %s' % periodopoa, request, "add")
                    return redirect('/poa_periodos')
                else:
                     raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        if action == 'edit':
            try:
                periodopoa = PeriodoPoa.objects.get(pk=request.POST['id'])
                f = PeriodoPoaForm(request.POST, request.FILES)
                if f.is_valid():
                    newfile = None
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("periodopoa_", newfile._name)
                        periodopoa.archivo = newfile
                    periodopoa.anio = f.cleaned_data['anio']
                    periodopoa.diassubir = f.cleaned_data['diassubir']
                    periodopoa.mostrar = f.cleaned_data['mostrar']
                    periodopoa.descripcion = f.cleaned_data['descripcion']
                    periodopoa.save(request)
                    log(u'edito periodo poa: %s' % periodopoa, request, "edit")
                    return redirect('/poa_periodos')
                    #return JsonResponse({"result": "ok"})
                else:
                     raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        if action == 'delete':
            try:
                periodopoa = PeriodoPoa.objects.get(pk=request.POST['id'])
                periodopoa.status = False
                periodopoa.save(request)
                log(u'cambio estado de periodo poa: %s' % periodopoa, request, "edit")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al eliminar los datos."})

        if action == 'activar':
            try:
                periodopoa = PeriodoPoa.objects.get(pk=request.POST['id'])
                periodopoa.edicion = not periodopoa.edicion
                periodopoa.save(request)
                log(u'activo periodo poa: %s' % periodopoa, request, "edit")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al activar el periodo."})

        if action == 'cambiaestado':
            try:
                periodopoa = PeriodoPoa.objects.get(pk=request.POST['periodoid'])
                PeriodoPoa.objects.filter(status=True).update(activo=False)
                if periodopoa.activo:
                    periodopoa.activo = False
                else:
                    periodopoa.activo = True
                periodopoa.save()
                log(u'cambio estado periodo poa: %s' % periodopoa, request, "edit")
                return JsonResponse({'result': 'ok', 'valor': periodopoa.activo})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        if action == 'duplicar':
            try:
                periodopoa = PeriodoPoa.objects.get(pk=request.POST['id'])
                periodopoa.ingresar = False
                periodopoa.save(request)
                periodopoa.id = None
                periodopoa.mostrar = False
                periodopoa.archivo = None
                periodopoa.ingresar = True
                periodopoa.edicion = True
                periodopoa.descripcion = 'TRASPASO, EDITE LA DESCRIPCION'
                periodopoa.save(request)
                a = PeriodoPoa.objects.get(pk=request.POST['id'])
                for i in InformeGenerado.objects.filter(periodopoa=a):
                    i.id = None
                    i.periodopoa = periodopoa
                    i.save(request)
                for p in PeriodoPoa.objects.filter(pk=request.POST['id']):
                    for oe in p.objetivoestrategico_set.all():
                        aux_oe = oe.objetivotactico_set.all()
                        oe.id = None
                        oe.periodopoa = periodopoa
                        oe.save(request)
                        for ot in aux_oe:
                            aux_ot = ot.objetivooperativo_set.all()
                            ot.id = None
                            ot.objetivoestrategico = oe
                            ot.save(request)
                            for oo in aux_ot:
                                aux_oo = oo.indicadorpoa_set.all()
                                oo.id = None
                                oo.objetivotactico = ot
                                oo.save(request)
                                for i in aux_oo:
                                    aux_i = i.acciondocumento_set.all()
                                    i.id = None
                                    i.objetivooperativo = oo
                                    i.save(request)
                                    for ad in aux_i:
                                        aux_ad = ad.acciondocumentodetalle_set.all()
                                        ad.id = None
                                        ad.indicadorpoa = i
                                        ad.save(request)
                                        for acd in aux_ad:
                                            aux_acd = acd.acciondocumentodetallerecord_set.all()
                                            acd.id = None
                                            acd.acciondocumento = ad
                                            acd.save(request)
                                            for adr in aux_acd:
                                                adr.id = None
                                                adr.acciondocumentodetalle = acd
                                                adr.save(request)
                log(u'duplico periodo poa: %s' % periodopoa, request, "edit")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al procesar el traspaso."})

        if action == 'editarperiodoevaluacion':
            try:
                f = EvaluacionPoaForm(request.POST)
                evaluacionpoa = EvaluacionPeriodoPoa.objects.get(pk=encrypt(request.POST['id']))
                if f.is_valid():
                    evaluacionpoa.descripcion = f.cleaned_data['descripcion']
                    evaluacionpoa.fechainicio = f.cleaned_data['fechainicio']
                    evaluacionpoa.fechafin = f.cleaned_data['fechafin']
                    evaluacionpoa.informeanual = f.cleaned_data['informeanual']
                    evaluacionpoa.porcentajedesempeno = f.cleaned_data['porcentajedesempeno']
                    evaluacionpoa.porcentajemeta = f.cleaned_data['porcentajemeta']
                    evaluacionpoa.save(request)
                    log(u'Editó evaluacion periodo poa: %s' % evaluacionpoa, request, "edit")
                    return JsonResponse({"result": False })
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": True, "mensaje": u"Error al guardar los datos."})

        if action == 'addperiodoevaluacion':
            try:
                f = EvaluacionPoaForm(request.POST)
                f.data['fechainicio'].replace("-", "/")
                f.data['fechafin'].replace("-", "/")
                if f.is_valid():
                    periodopoa = PeriodoPoa.objects.get(pk=int(encrypt(request.POST['idperiodopoa'])))
                    evaluacionpoa = EvaluacionPeriodoPoa(periodopoa=periodopoa,
                                                         descripcion=f.cleaned_data['descripcion'].upper(),
                                                         fechainicio=f.cleaned_data['fechainicio'],
                                                         fechafin=f.cleaned_data['fechafin'],
                                                         porcentajedesempeno=f.cleaned_data['porcentajedesempeno'],
                                                         porcentajemeta=f.cleaned_data['porcentajemeta'],
                                                         informeanual=f.cleaned_data['informeanual']
                    )
                    evaluacionpoa.save(request)
                    log(u'Añadió evaluación periodo poa: %s' % evaluacionpoa, request, "add")
                    return JsonResponse({"result": False})
                else:
                    raise NameError('Error')
            except Exception as ex:
                print([{k: v[0]} for k, v in f.errors.items()])
                transaction.set_rollback(True)
                return JsonResponse({"result": True, "mensaje": u"Error al guardar los datos."})

        if action == 'deleteperiodopoa':
            try:
                evaluacionperiodopoa = evaluacion = EvaluacionPeriodoPoa.objects.get(pk=int(request.POST['id']))
                evaluacionperiodopoa.delete()
                log(u'Eliminó evaluación periodo poa: %s' % evaluacion, request, "delete")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": "Error al guardar los datos."})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Periodo POA'
                    data['action'] = 'add'
                    data['form'] = PeriodoPoaForm()
                    template = get_template('poa_periodos/add.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['title'] = u'Modificar Periodo POA'
                    data['action'] = 'edit'
                    data['periodo'] = periodo = PeriodoPoa.objects.get(pk=request.GET['id'])
                    data['form'] = PeriodoPoaForm(initial={'descripcion': periodo.descripcion,
                                                           'anio': periodo.anio,
                                                           'diassubir': periodo.diassubir,
                                                           'mostrar': periodo.mostrar})
                    template = get_template('poa_periodos/edit.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            if action == 'delete':
                try:
                    data['title'] = u'Eliminar Periodo POA'
                    data['periodo'] = PeriodoPoa.objects.get(pk=request.GET['id'])
                    return render(request, 'poa_periodos/delete.html', data)
                except Exception as ex:
                    pass

            if action == 'activar':
                try:
                    data['title'] = u'Edición Total POA'
                    data['periodo'] = PeriodoPoa.objects.get(pk=int(request.GET['id']))
                    return render(request, 'poa_periodos/ediciontotal.html', data)
                except Exception as ex:
                    pass

            if action == 'listadoevaluacion':

                try:
                    data['title'] = u'Listado Evaluación POA'
                    data['periodo'] = periodopoa = PeriodoPoa.objects.get(pk=int(request.GET['idperiodopoa']))
                    search= request.GET.get('s', '')
                    url_vars = f"&action=listadoevaluacion&idperiodopoa="+str(periodopoa.id)
                    search = None
                    tipo = None
                    if 's' in request.GET:
                        search = request.GET['s']
                        # if search:
                        listadoevaluacion = periodopoa.evaluacionperiodopoa_set.filter(descripcion__icontains=search, status=True).order_by('id')
                        url_vars += "&s={}".format(search)
                    else:
                        listadoevaluacion= periodopoa.evaluacionperiodopoa_set.filter(status=True).order_by('id')

                    paging = MiPaginador(listadoevaluacion, 25)
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
                    data['fechaactual'] = datetime.now().date().year
                    data['search'] = search if search else ""
                    data['listadoevaluacion'] = page.object_list
                    data['url_vars'] = url_vars

                    return render(request, 'poa_periodos/listadoevaluacion.html', data)
                except Exception as ex:
                    pass

            if action == 'editarperiodoevaluacion':
                try:
                    data['title'] = u'Editar Evaluación POA'
                    data['action'] = 'editarperiodoevaluacion'
                    data['id'] = (encrypt(request.GET['id']))
                    data['evaluacionperiodopoa'] = evaluacionperiodopoa = EvaluacionPeriodoPoa.objects.get(pk=int(encrypt(request.GET['id'])))
                    data['form'] = EvaluacionPoaForm(initial={'descripcion': evaluacionperiodopoa.descripcion,
                                                              'fechainicio': evaluacionperiodopoa.fechainicio,
                                                              'fechafin': evaluacionperiodopoa.fechafin,
                                                              'porcentajedesempeno': evaluacionperiodopoa.porcentajedesempeno,
                                                              'porcentajemeta': evaluacionperiodopoa.porcentajemeta,
                                                              'informeanual':evaluacionperiodopoa.informeanual})
                    template = get_template('poa_periodos/editarperiodoevaluacion.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})

                    # return render(request, 'poa_periodos/editarperiodoevaluacion.html', data)
                except Exception as ex:
                    pass

            if action == 'duplicar':
                try:
                    data['title'] = u'Traspaso POA'
                    data['periodo'] = PeriodoPoa.objects.get(pk=int(request.GET['id']))
                    return render(request, 'poa_periodos/traspaso.html', data)
                except Exception as ex:
                    pass

            if action == 'addperiodoevaluacion':
                try:
                    data['title'] = u'Adicionar Evaluación Periodo POA'
                    data['action'] = 'addperiodoevaluacion'
                    data['idperiodo'] = int(request.GET['id'])
                    data['periodopoa'] = PeriodoPoa.objects.get(pk=int(request.GET['id']))
                    form = EvaluacionPoaForm()
                    data['form'] = form
                    template = get_template('poa_periodos/addevaluacionpoa.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})

                    #return render(request, 'poa_periodos/addevaluacionpoa.html', data)
                except Exception as ex:
                    pass

            if action == 'deleteperiodopoa':
                try:
                    data['title'] = u'Eliminar Evaluación POA'
                    data['evaluacionperiodopoa'] = EvaluacionPeriodoPoa.objects.get(pk=request.GET['id'])
                    return render(request, 'poa_periodos/deleteevaluacionpoa.html', data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)
        else:
            data['title'] = u'Periodos POA'
            search, url_vars = request.GET.get('s', ''),''
            search = None
            tipo = None
            if 's' in request.GET:
                search = request.GET['s']
            #if search:
                periodos = PeriodoPoa.objects.filter(descripcion__icontains=search, status=True).order_by('-id')
                url_vars += "&s={}".format(search)

            else:
                periodos = PeriodoPoa.objects.filter(status=True).order_by('-id')
            paging = MiPaginador(periodos, 25)
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
            data['fechaactual'] = datetime.now().date().year
            data['search'] = search if search else ""
            data['periodos'] = page.object_list
            data['url_vars'] = url_vars
            return render(request, "poa_periodos/view.html", data)
