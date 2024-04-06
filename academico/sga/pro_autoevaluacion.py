# -*- coding: latin-1 -*-
import io as StringIO
import os
from datetime import datetime
from time import strftime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
import settings
from decorators import secure_module, last_access
from sga.commonviews import adduserdata, obtener_reporte
from sga.funciones import log
from sga.models import RespuestaEvaluacionAcreditacion, Rubrica, RespuestaRubrica, DetalleRespuestaRubrica, \
    miinstitucion, RubricaPreguntas, ProfesorDistributivoHoras, ResumenFinalEvaluacionAcreditacion, \
    null_to_numeric, PermisoPeriodo, CriterioTipoObservacionEvaluacion, ResumenEvaluacionAcreditacion
from sga.tasks import send_html_mail

def link_callback(uri, rel):
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri                  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))

    return path

def conviert_html_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict).encode(encoding="UTF-8")
    result = StringIO.BytesIO()
    pisaStatus = pisa.CreatePDF(StringIO.BytesIO(html), result, link_callback=link_callback)
    if not pisaStatus.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return JsonResponse({"result": "bad", "mensaje": u"Problemas al ejecutar el reporte."})


def pdf_listaevaluacion(request):
    data = {}
    data['fechaactual'] = strftime('%Y-%m-%d')
    adduserdata(request, data)
    persona = request.session['persona']
    perfilprincipal = request.session['perfilprincipal']
    data['profesor'] = profesor = perfilprincipal.profesor
    periodo = request.session['periodo']
    data['periodo'] = periodo
    data['periodonombre'] = periodo.nombre
    data['proceso'] = proceso = periodo.proceso_evaluativo()
    data['materias'] = materias = profesor.materias_imparte_periodo_autores(periodo)
    data['title'] = u'Resultados de la evaluación integral del desempeño docente'
    data['distributivo'] = distributivo = profesor.distributivohoraseval(periodo)
    data['rubricapreguntas'] = RubricaPreguntas.objects.filter(detallerespuestarubrica__respuestarubrica__respuestaevaluacion__proceso__periodo=periodo, rubrica__informativa=False, detallerespuestarubrica__respuestarubrica__respuestaevaluacion__profesor=profesor, detallerespuestarubrica__respuestarubrica__respuestaevaluacion__tipoinstrumento=1).distinct().order_by('preguntacaracteristica__caracteristica__orden')
    data['resumenfinalevaluacion'] = resumen = ResumenFinalEvaluacionAcreditacion.objects.get(distributivo__periodo=periodo, distributivo__profesor=profesor)
    data['promescalacien'] = 0
    if resumen:
        data['promescalacien'] = (resumen.resultado_total * 100) / 5
    # evaluacion autoevaluacion
    data['rubricaautodocente'] = autodocente = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=2, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=1).distinct().order_by('rubrica__tipo_criterio')
    data['promautodocente'] = round(null_to_numeric(autodocente.aggregate(prom=Avg('valor'))['prom']), 2)
    data['rubricaautoinves'] = autoinve = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=2, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=2).distinct().order_by('rubrica__tipo_criterio')
    data['promautoinvestigacion'] = round(null_to_numeric(autoinve.aggregate(prom=Avg('valor'))['prom']), 2)
    data['rubricaautogestion'] = autogestion = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=2, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=3).distinct().order_by('rubrica__tipo_criterio')
    data['promautogestion'] = round(null_to_numeric(autogestion.aggregate(prom=Avg('valor'))['prom']), 2)
    data['rubricaparesdocente'] = paresdocente = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=3, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=1).distinct().order_by('rubrica__tipo_criterio')
    data['promparesdocente'] = round(null_to_numeric(paresdocente.aggregate(prom=Avg('valor'))['prom']), 2)
    data['rubricaparesinves'] = paresinves = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=3, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=2).distinct().order_by('rubrica__tipo_criterio')
    data['promparesinves'] = round(null_to_numeric(paresinves.aggregate(prom=Avg('valor'))['prom']), 2)
    data['rubricaparesgestion'] = paresgestion = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=3, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=3).distinct().order_by('rubrica__tipo_criterio')
    data['promparesgestion'] = round(null_to_numeric(paresgestion.aggregate(prom=Avg('valor'))['prom']), 2)
    data['rubricadirdocente'] = dirdocente = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=4, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=1).distinct().order_by('rubrica__tipo_criterio')
    data['promdirdocente'] = round(null_to_numeric(dirdocente.aggregate(prom=Avg('valor'))['prom']), 2)
    data['rubricadirinves'] = dirinve = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=4, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=2).distinct().order_by('rubrica__tipo_criterio')
    data['promdirinve'] = round(null_to_numeric(dirinve.aggregate(prom=Avg('valor'))['prom']), 2)
    data['rubricadirgestion'] = dirgestion = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo=periodo, respuestaevaluacion__tipoinstrumento=4, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=3).distinct().order_by('rubrica__tipo_criterio')
    data['promdirgestion'] = round(null_to_numeric(dirgestion.aggregate(prom=Avg('valor'))['prom']), 2)
    data['mejorasforauto'] = RespuestaEvaluacionAcreditacion.objects.filter(proceso__periodo=periodo, profesor_id=profesor, tipoinstrumento=2).distinct()
    data['mejorasforpares'] = RespuestaEvaluacionAcreditacion.objects.filter(proceso__periodo=periodo, profesor_id=profesor, tipoinstrumento=3).distinct()
    data['mejorasfordirectivos'] = RespuestaEvaluacionAcreditacion.objects.filter(proceso__periodo=periodo, profesor_id=profesor, tipoinstrumento=4).distinct()
    # data['rubricapreguntasinformativas'] = RubricaPreguntas.objects.filter(detallerespuestarubrica__respuestarubrica__respuestaevaluacion__proceso__periodo=periodo, rubrica__informativa=True, detallerespuestarubrica__respuestarubrica__respuestaevaluacion__profesor=profesor, detallerespuestarubrica__respuestarubrica__respuestaevaluacion__tipoinstrumento=1).distinct().order_by('rubrica__tipo_criterio')
    data['resumenesevaluacion'] = ResumenEvaluacionAcreditacion.objects.filter(periodo=periodo, profesor=profesor).distinct()
    data['distributivos'] = ProfesorDistributivoHoras.objects.filter(periodo_id=periodo, profesor_id=profesor)
    return conviert_html_to_pdf(
        'pro_autoevaluacion/resultados_evaluaciones_pdf.html',
        {
            'pagesize': 'A4',
            'listadoevaluaciones': data,
        }
    )


@login_required(redirect_field_name='ret', login_url='/loginsga')
@secure_module
@last_access
@transaction.atomic()
def view(request):
    data = {}
    adduserdata(request, data)
    data['title'] = u'Autoevaluación del docente'
    persona = request.session['persona']
    perfilprincipal = request.session['perfilprincipal']
    if not perfilprincipal.es_profesor():
        return HttpResponseRedirect("/?info=Solo los perfiles de profesores pueden ingresar al modulo.")
    data['profesor'] = profesor = perfilprincipal.profesor
    data['periodo'] = periodo = request.session['periodo']
    data['proceso'] = proceso = periodo.proceso_evaluativo()
    if periodo.ocultarmateria:
        data['materias'] = False
    else:
        data['materias'] = materias = profesor.materias_imparte_periodo_autores(periodo)
    data['evaluacion'] = None
    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']

            if action == 'evaluar':
                try:
                    coordinaciondistributivo = ProfesorDistributivoHoras.objects.get(periodo=proceso.periodo, profesor=profesor, status=True)
                    if RespuestaEvaluacionAcreditacion.objects.filter(proceso__periodo=periodo, profesor=profesor,tipoinstrumento=2).exists():
                        return JsonResponse({"result": "bad", 'mensaje': u'Evaluación ya existe.'})
                    evaluacion = RespuestaEvaluacionAcreditacion(proceso=proceso,
                                                                 tipoinstrumento=2,
                                                                 profesor=profesor,
                                                                 fecha=datetime.now(),
                                                                 # coordinacion=profesor.coordinacion,
                                                                 coordinacion=coordinaciondistributivo.coordinacion,
                                                                 carrera=coordinaciondistributivo.carrera,
                                                                 # carrera=profesor.carrera_principal_periodo(periodo),
                                                                 accionmejoras=request.POST['accionmejoras'],
                                                                 tipomejoras_id=request.POST['nommejoras'],
                                                                 tipocontinua_id=request.POST['nomcontinua'],
                                                                 formacioncontinua=request.POST['formacioncontinua'])
                    evaluacion.save(request)
                    listarespuesta = []
                    for elemento in request.POST['lista'].split(';'):
                        individuales = elemento.split(':')
                        rubricapregunta = RubricaPreguntas.objects.get(pk=int(individuales[0]))
                        rubrica = rubricapregunta.rubrica
                        if not RespuestaRubrica.objects.filter(respuestaevaluacion=evaluacion, rubrica=rubrica).exists():
                            respuestarubrica = RespuestaRubrica(respuestaevaluacion=evaluacion,
                                                                rubrica=rubrica,
                                                                valor=0)
                            respuestarubrica.save(request)
                        else:
                            respuestarubrica = RespuestaRubrica.objects.filter(respuestaevaluacion=evaluacion, rubrica=rubrica)[0]
                        listarespuesta.append(respuestarubrica.id)
                        detalle = DetalleRespuestaRubrica(respuestarubrica=respuestarubrica,
                                                          rubricapregunta=rubricapregunta,
                                                          valor=float(individuales[1]))
                        detalle.save(request)
                        respuestarubrica.save()
                    # for elemento in request.POST['lista'].split(';'):
                    #     individuales = elemento.split(':')
                    #     rubrica = Rubrica.objects.get(pk=int(individuales[0]))
                    #     respuestarubrica = RespuestaRubrica(respuestaevaluacion=evaluacion,
                    #                                         rubrica=rubrica,
                    #                                         valor=float(individuales[1]))
                    #     respuestarubrica.save(request)
                    #     for rubricapregunta in rubrica.mis_preguntas():
                    #         detalle = DetalleRespuestaRubrica(respuestarubrica=respuestarubrica,
                    #                                           rubricapregunta=rubricapregunta,
                    #                                           valor=respuestarubrica.valor)
                    #         detalle.save(request)
                    #     respuestarubrica.save(request)
                    # evaluacion.save(request)
                    distributivo = profesor.distributivohoraseval(periodo)
                    resumen = distributivo.resumen_evaluacion_acreditacion()
                    resumen.actualizar_resumen()
                    log(u'Autoevaluacion de profesores: %s' % profesor, request, "add")
                    send_html_mail("Autoevaluación docente realizada.", "emails/evaluaciondocente.html", {'sistema': request.session['nombresistema'], 'd': evaluacion, 't': miinstitucion(), 'tituloemail': "Autoevaluación docente realizada"}, profesor.persona.lista_emails_envio(), [])
                    return JsonResponse({"result": "ok"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

            if action == 'listasubmejoras':
                try:
                    combomejoras = CriterioTipoObservacionEvaluacion.objects.get(pk=request.POST['id'])
                    tipoinstrumento = request.POST['tipoins']
                    lista = []
                    for detmejoras in combomejoras.tipoobservacionevaluacion_set.filter(tipoinstrumento=tipoinstrumento, tipo=1, status=True,activo=True).order_by('nombre'):
                        lista.append([detmejoras.id, detmejoras.nombre.upper()])
                    return JsonResponse({'result': 'ok', 'lista': lista})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            if action == 'listacontinua':
                try:
                    combomejoras = CriterioTipoObservacionEvaluacion.objects.get(pk=request.POST['id'])
                    tipoinstrumento = request.POST['tipoins']
                    lista = []
                    for detmejoras in combomejoras.tipoobservacionevaluacion_set.filter(tipoinstrumento=tipoinstrumento, tipo=2, status=True,activo=True).order_by('nombre'):
                        lista.append([detmejoras.id, detmejoras.nombre.upper()])
                    return JsonResponse({'result': 'ok', 'lista': lista})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'evaluar':
                try:
                    data['title'] = u'Autoevaluacion del periodo'
                    # data['rubricas'] = rubricas = profesor.mis_rubricas(periodo)
                    data['rubricas'] = rubricas = profesor.mis_rubricasauto(periodo)
                    # data['combomejoras'] = TipoObservacionEvaluacion.objects.filter(tipoinstrumento=2, tipo=1, status=True).order_by('nombre')
                    data['combomejoras'] = CriterioTipoObservacionEvaluacion.objects.filter(tipoobservacionevaluacion__tipoinstrumento=2, tipoobservacionevaluacion__tipo=1, tipoobservacionevaluacion__status=True, tipoobservacionevaluacion__activo=True).order_by('nombre').distinct()
                    # data['combocontinuas'] = TipoObservacionEvaluacion.objects.filter(tipoinstrumento=2, tipo=2, status=True).order_by('nombre')
                    data['combocontinuas'] = CriterioTipoObservacionEvaluacion.objects.filter(tipoobservacionevaluacion__tipoinstrumento=2, tipoobservacionevaluacion__tipo=2, tipoobservacionevaluacion__status=True, tipoobservacionevaluacion__activo=True).order_by('nombre').distinct()
                    data['tiene_docencia'] = rubricas.filter(tipo_criterio=1).exists()
                    data['tiene_investigacion'] = rubricas.filter(tipo_criterio=2).exists()
                    data['tiene_gestion'] = rubricas.filter(tipo_criterio=3).exists()
                    return render(request, "pro_autoevaluacion/evaluar.html", data)
                except Exception as ex:
                    pass

            if action == 'consultar':
                try:
                    data['title'] = u'Consulta de Autoevaluacion en el periodo'
                    # data['rubricas'] = rubricas = profesor.mis_rubricas(periodo)
                    data['rubricas'] = rubricas = profesor.mis_rubricasauto(periodo)
                    data['tiene_docencia'] = rubricas.filter(tipo_criterio=1).exists()
                    data['tiene_investigacion'] = rubricas.filter(tipo_criterio=2).exists()
                    data['tiene_gestion'] = rubricas.filter(tipo_criterio=3).exists()
                    data['evaluacion'] = profesor.dato_autoevaluado_periodo(periodo)
                    return render(request, "pro_autoevaluacion/consultar.html", data)
                except Exception as ex:
                    pass

            if action == 'resultados_evaluaciones':
                try:
                    data['title'] = u'Resultados de la evaluación integral del desempeño docente'
                    data['distributivo'] = distributivo = profesor.distributivohoraseval(periodo)
                    data['rubricapreguntas'] = RubricaPreguntas.objects.filter(detallerespuestarubrica__respuestarubrica__respuestaevaluacion__proceso__periodo_id=periodo, rubrica__informativa=False, detallerespuestarubrica__respuestarubrica__respuestaevaluacion__profesor=profesor, detallerespuestarubrica__respuestarubrica__respuestaevaluacion__tipoinstrumento=1).distinct().order_by('preguntacaracteristica__caracteristica__orden')
                    data['mejorasforauto'] = RespuestaEvaluacionAcreditacion.objects.values('id', 'respuestarubrica__rubrica__tipo_criterio', 'accionmejoras', 'formacioncontinua').filter(profesor=profesor, tipoinstrumento=2, proceso__periodo=periodo).distinct()
                    # evaluacion autoevaluacion
                    data['rubricaautodocente'] = autodocente = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=2, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=1, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promautodocente'] = round(null_to_numeric(autodocente.aggregate(prom=Avg('valor'))['prom']), 2)
                    data['rubricaautoinves'] = autoinve = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=2, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=2, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promautoinvestigacion'] = round(null_to_numeric(autoinve.aggregate(prom=Avg('valor'))['prom']), 2)
                    data['rubricaautogestion'] = autogestion = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=2, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=3, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promautogestion'] = round(null_to_numeric(autogestion.aggregate(prom=Avg('valor'))['prom']), 2)
                    # evaluacion pares
                    data['rubricaparesdocente'] = paresdocente = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=3, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=1, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promparesdocente'] = round(null_to_numeric(paresdocente.aggregate(prom=Avg('valor'))['prom']), 2)
                    data['rubricaparesinves'] = paresinves = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=3, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=2, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promparesinves'] = round(null_to_numeric(paresinves.aggregate(prom=Avg('valor'))['prom']), 2)
                    data['rubricaparesgestion'] = paresgestion = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=3, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=3, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promparesgestion'] = round(null_to_numeric(paresgestion.aggregate(prom=Avg('valor'))['prom']), 2)
                    data['resumenfinalevaluacion'] = resumen = ResumenFinalEvaluacionAcreditacion.objects.get(distributivo__periodo=periodo, distributivo__profesor=profesor)
                    data['promescalacien'] = 0
                    if resumen:
                        data['promescalacien'] = (resumen.resultado_total * 100) / 5
                    data['mejorasforpares'] = RespuestaEvaluacionAcreditacion.objects.values('id', 'respuestarubrica__rubrica__tipo_criterio', 'accionmejoras', 'formacioncontinua').filter(profesor=profesor, tipoinstrumento=3, proceso__periodo=periodo).distinct()
                    # evaluacion directivos
                    data['rubricadirdocente'] = dirdocente = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=4, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=1, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promdirdocente'] = round(null_to_numeric(dirdocente.aggregate(prom=Avg('valor'))['prom']), 2)
                    data['rubricadirinves'] = dirinve = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=4, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=2, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promdirinve'] = round(null_to_numeric(dirinve.aggregate(prom=Avg('valor'))['prom']), 2)
                    data['rubricadirgestion'] = dirgestion = RespuestaRubrica.objects.filter(respuestaevaluacion__proceso__periodo_id=periodo, respuestaevaluacion__tipoinstrumento=4, respuestaevaluacion__profesor_id=profesor, rubrica__informativa=False, rubrica__tipo_criterio=3, respuestaevaluacion__proceso__periodo=periodo).distinct().order_by('rubrica__tipo_criterio')
                    data['promdirgestion'] = round(null_to_numeric(dirgestion.aggregate(prom=Avg('valor'))['prom']), 2)
                    data['mejorasfordirectivos'] = RespuestaEvaluacionAcreditacion.objects.values('id', 'respuestarubrica__rubrica__tipo_criterio', 'accionmejoras', 'formacioncontinua').filter(profesor=profesor, tipoinstrumento=4, proceso__periodo=periodo).distinct()
                    # data['rubricapreguntasinformativas'] = RubricaPreguntas.objects.filter(detallerespuestarubrica__respuestarubrica__respuestaevaluacion__proceso__periodo_id=periodo, rubrica__informativa=True, detallerespuestarubrica__respuestarubrica__respuestaevaluacion__profesor=profesor, detallerespuestarubrica__respuestarubrica__respuestaevaluacion__tipoinstrumento=1).distinct().order_by('rubrica__tipo_criterio')
                    data['resumenesevaluacion'] = ResumenEvaluacionAcreditacion.objects.filter(periodo=periodo, profesor=profesor, nivelmalla__isnull=True).distinct()
                    data['resumenesevaluacionasignatura'] = ResumenEvaluacionAcreditacion.objects.filter(periodo=periodo, profesor=profesor, nivelmalla__isnull=False).distinct()
                    data['distributivos'] = ProfesorDistributivoHoras.objects.filter(periodo_id=periodo, profesor_id=profesor)
                    return render(request, "pro_autoevaluacion/resultados_evaluaciones.html", data)
                except Exception as ex:
                    pass
                
            return HttpResponseRedirect(request.path)
        else:
            try:
                # if not PermisoPeriodo.objects.filter(periodo=periodo).exists():
                #     return HttpResponseRedirect("/?info=No tiene asignado profesor a evaluar.")
                data['distributivo'] = distributivo = profesor.distributivohoraseval(periodo)
                data['detalledistributivo'] = distributivo.detalledistributivo_set.all()
                data['autoevaluacion'] = profesor.dato_autoevaluado_periodo(periodo)
                data['reporte_0'] = obtener_reporte('resultado_evaluacion')
                return render(request, "pro_autoevaluacion/view.html", data)
            except Exception as ex:
                return HttpResponseRedirect(f"/?info=No puede acceder al módulo")