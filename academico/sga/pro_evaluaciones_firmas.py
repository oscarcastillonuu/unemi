# -*- coding: UTF-8 -*-
import csv
import os

from django.db.models import Q
from django.forms import model_to_dict
from django.template import Context
from django.template.loader import get_template
from googletrans import Translator
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from certi.models import CertificadoAsistenteCertificadora, Certificado
from decorators import secure_module, last_access, inhouse_check, get_client_ip
from settings import DATOS_ESTRICTO, PAGO_ESTRICTO, USA_EVALUACION_INTEGRAL, \
    ARCHIVO_TIPO_NOTAS, SITE_ROOT, VALIDATE_IPS, SERVER_RESPONSE, MEDIA_URL
from sga.commonviews import adduserdata, obtener_reporte, actualizar_nota_docente
from sga.forms import ImportarArchivoCSVForm, AsignacionResponsableForm, SubirActaForm, ValidarActaForm
from sga.funciones import log, generar_nombre, variable_valor, null_to_decimal, ok_json, bad_json, MiPaginador, \
    notificacion
from sga.models import Materia, MateriaAsignada, miinstitucion, LeccionGrupo, Archivo, PlanificacionMateria, \
    ProfesorReemplazo, CUENTAS_CORREOS, DetalleModeloEvaluativo, Reporte, DocumentosFirmadosEvaluaciones, \
    ConfiguracionDocumentoEvaluaciones, Persona, HistorialDocumentoEvaluacion, Coordinacion, ESTADO_SEGUIMIENTO
from sga.reportes import elimina_tildes, run_report_v1
from sga.tasks import send_html_mail, conectar_cuenta
from sga.templatetags.sga_extras import encrypt

unicode = str

@login_required(redirect_field_name='ret', login_url='/loginsga')
# @secure_module
# @last_access
@transaction.atomic()
def view(request):
    data = {}
    hoy=datetime.now()
    adduserdata(request, data)
    persona = request.session['persona']
    perfilprincipal = request.session['perfilprincipal']
    mi_cargo=persona.mi_cargo_administrativo()
    if not mi_cargo and not request.user.is_superuser:
        return HttpResponseRedirect("/?info=Módulo disponible solo a funcionarios con cargo asignado.")

    if mi_cargo and not mi_cargo.id in [16, 30] and not request.user.is_superuser:
        return HttpResponseRedirect("/?info=Solo asistentes de facultad pueden ingresar al módulo.")
    profesor = perfilprincipal.profesor
    data['periodo'] = periodo = request.session['periodo']
    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']

            if action == 'subiractafirmada':
                try:
                    with transaction.atomic():
                        form = SubirActaForm(request.POST, request.FILES)
                        id = int(encrypt(request.POST['id']))
                        if form.is_valid():
                            conf = ConfiguracionDocumentoEvaluaciones.objects.get(id=id)
                            if 'archivo_final' in request.FILES:
                                newfile = request.FILES['archivo_final']
                                newfile._name = 'acta_{}'.format(generar_nombre(conf.nombre_input(), newfile._name))
                                conf.archivo_final = newfile
                                conf.save(request)

                            responsable = DocumentosFirmadosEvaluaciones.objects.get(persona=persona, status=True, configuraciondoc=conf)
                            responsable.subido = True
                            responsable.fecha = hoy
                            if 'archivo_final' in request.FILES:
                                newfile = request.FILES['archivo_final']
                                newfile._name = 'acta_responsable_{}'.format(generar_nombre(conf.nombre_input(), newfile._name))
                                responsable.archivo = newfile
                            responsable.save(request)
                        else:
                            transaction.set_rollback(True)
                            return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()],
                                                 "mensaje": "Error en el formulario"})
                    log(u'Subir acta firmada: %s' % conf, request, "subiractafirmada")
                    return JsonResponse({"result": False}, safe=False)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": True, 'mensaje': str(ex)}, safe=False)

            if action == 'validaracta':
                try:
                    id = int(encrypt(request.POST['id']))
                    form = ValidarActaForm(request.POST)
                    if form.is_valid():
                        documento = DocumentosFirmadosEvaluaciones.objects.get(id=id)
                        documento.fecha_revision=hoy
                        documento.save(request)

                        configuracion=documento.configuraciondoc
                        configuracion.estado=form.cleaned_data['estado']
                        configuracion.observacion=form.cleaned_data['observacion']
                        configuracion.save(request)
                        log(u'Validacion de acta: %s [%s]' % (documento, documento.id), request, "validaracta")

                        historial=HistorialDocumentoEvaluacion(configuraciondoc=configuracion,
                                                               persona=documento.persona,
                                                               responsable=persona,
                                                               estado=configuracion.estado,
                                                               observacion=configuracion.observacion,
                                                               fecha=documento.fecha,
                                                               fecha_revision=hoy)
                        historial.save(request)

                        if int(configuracion.estado) == 2:
                            notificacion('Acta de calificaciones rechazada','Acta de {} fue rechazada'.format(configuracion.materia.nombre_completo()),
                                                      documento.persona, None, '/pro_evaluaciones',
                                                      documento.pk, 1, 'sga', DocumentosFirmadosEvaluaciones, request)
                        log(u'Agrego historial de validacion: %s [%s]' % (historial, historial.id), request, "validaracta")
                        return JsonResponse({"result": False}, safe=False)
                    else:
                        return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()],
                                             "mensaje": "Error en el formulario"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': True, "mensaje": 'Error: {}'.format(ex)}, safe=False)

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            data['action']= action = request.GET['action']
            if action == 'subiractafirmada':
                try:
                    id = int(encrypt(request.GET['id']))
                    data['configuracion'] = ConfiguracionDocumentoEvaluaciones.objects.get(id=id)
                    info=request.GET.get('ext','')
                    if not info:
                        form = SubirActaForm()
                        data['form'] = form
                    else:
                        data['info'] =info
                    template = get_template("pro_evaluaciones/modal/formfirma.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as e:
                    print(e)
                    pass

            if action == 'validaracta':
                try:
                    id = int(encrypt(request.GET['id']))
                    data['documento'] = documento =DocumentosFirmadosEvaluaciones.objects.get(id=id)
                    form = ValidarActaForm(initial=model_to_dict(documento.configuraciondoc))
                    data['form'] = form
                    template = get_template("pro_evaluaciones/modal/formvalidaracta.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as e:
                    print(e)
                    pass


            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = u'Actas de calificaciones'
                lista=[]
                certificado=Certificado.objects.filter(status=True).first()
                asistentes = CertificadoAsistenteCertificadora.objects.filter(status=True, asistente=persona, unidad_certificadora__certificado=certificado)
                for asistente in asistentes:
                    carreras=asistente.unidad_certificadora.coordinacion.carrera.all()
                    for carrera in carreras:
                        lista.append(carrera.id)
                estado, search, filtro, url_vars = request.GET.get('estado', ''), request.GET.get('s', ''), Q(status=True, configuraciondoc__materia__asignaturamalla__malla__carrera_id__in=lista), ''

                if estado:
                    data['est'] = int(estado)
                    filtro = filtro & (Q(configuraciondoc__estado=estado))
                    url_vars += '&est=' + estado

                if search:
                    data['s'] = search
                    s = search.split(' ')
                    if len(s) == 1:
                        filtro = filtro & (Q(persona__nombres__unaccent__icontains=search) |
                                           Q(persona__cedula__unaccent__icontains=search) |
                                           Q(configuraciondoc__materia__asignatura__nombre__unaccent__icontains=search))
                    if len(s) >= 2:
                        filtro = filtro & (Q(persona__nombres__unaccent__icontains=search)|
                                           (Q(persona__apellido1__unaccent__icontains=s[0]) & Q(persona__apellido2__unaccent__icontains=s[1]))|
                                           Q(configuraciondoc__materia__asignatura__nombre__unaccent__icontains=search))
                    url_vars += '&s=' + search

                listado = DocumentosFirmadosEvaluaciones.objects.filter(filtro).order_by('-id')
                # for list in listado:
                #     if list.configuraciondoc.materia.coordinacion_materia()== coordinacion:
                #         lista.append(list)
                paging = MiPaginador(listado, 20)
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
                data['estados']=ESTADO_SEGUIMIENTO
                data["url_vars"] = url_vars
                data['listado'] = page.object_list
                data['listcount'] = len(listado)
                return render(request, 'pro_evaluaciones/actas.html', data)
            except Exception as ex:
                pass