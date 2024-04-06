# -*- coding: latin-1 -*-
import json
import calendar
import random
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.context import Context
from django.template.loader import get_template
from django.db.models import Q, F, Value, Count, Case, When, ExpressionWrapper, FloatField, Subquery, OuterRef, Exists
from django.db.models.functions import Concat, Coalesce
from django.db import transaction, connections, models
from decorators import secure_module, last_access
from sga.commonviews import adduserdata
from sga.funciones import MiPaginador, log, Round2, convertir_lista
from sga.models import Materia, ProfesorMateria, Profesor, Modulo, Clase, ModuloGrupo, Modalidad, TemaAsistencia, \
    SubTemaAsistencia, SubTemaAdicionalAsistencia, Silabo, SilaboSemanal, ResponsableCoordinacion, Carrera, Malla, \
    NivelMalla, Asignatura, Paralelo, Notificacion, Coordinacion, CoordinadorCarrera, EncuestaGrupoEstudiantes, \
    Inscripcion, Matricula, MateriaAsignada, Encuesta, ProfesorDistributivoHoras
from sga.funcionesxhtml2pdf import conviert_html_to_pdf
from sga.templatetags.sga_extras import encrypt, informe_actividades_mensual_docente_v4_extra
from settings import DEBUG, SITE_STORAGE
from inno.models import EncuestaGrupoEstudianteSeguimientoSilabo, InscripcionEncuestaEstudianteSeguimientoSilabo, \
    PreguntaEncuestaGrupoEstudiantes, RespuestaPreguntaEncuestaSilaboGrupoEstudiantes
from inno.forms import InscripcionEncuestaEstudianteSeguimientoSilaboForm


@login_required(redirect_field_name='ret', login_url='/loginsga')
@transaction.atomic()
# @secure_module
def view(request):
    data = {}
    adduserdata(request, data)
    persona = request.session['persona']
    fechahoy = datetime.now().date()
    perfilprincipal = request.session['perfilprincipal']
    if not perfilprincipal.es_administrativo():
        return HttpResponseRedirect("/?info=Solo los perfiles administrativos pueden ingresar al modulo.")

    data['periodo'] = periodo = request.session['periodo']
    if persona.es_profesor():
        idcoordinacion = persona.profesor().coordinacion.id
        coordinacion = persona.profesor().coordinacion
        data['profesor'] = profesor = persona.profesor()
    es_administrativo = perfilprincipal.es_administrativo()
    dominio_sistema = 'https://sga.unemi.edu.ec'

    if DEBUG:
        dominio_sistema = 'http://localhost:8000'

    data["DOMINIO_DEL_SISTEMA"] = dominio_sistema

    if not es_administrativo:
        return HttpResponseRedirect("/?info=El Módulo está disponible para administrativos.")

    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']
            # if action == 'asignarencuestasilabo':
            #     try:
            #         # Obtener IDs de inscripciones que cumplen con las condiciones dadas
            #         ids_inscripciones = Inscripcion.objects.filter(
            #             status=True,
            #             matricula__retiradomatricula=False,
            #             matricula__nivel__periodo_id=periodo,
            #             coordinacion_id__in=[1, 2, 3, 4, 5]
            #         ).values_list('id', flat=True)
            #         f = InscripcionEncuestaEstudianteSeguimientoSilaboForm(request.POST)
            #         if f.is_valid():
            #             if ids_inscripciones:
            #                 encuesta_estudiante_silabo = EncuestaGrupoEstudianteSeguimientoSilabo(
            #                     encuestagrupoestudiantes=f.cleaned_data['encuesta'],
            #                     fechainicioencuesta=f.cleaned_data['fechainicioencuesta'],
            #                     fechafinencuesta=f.cleaned_data['fechafinencuesta'],
            #                     categoria=True)
            #                 encuesta_estudiante_silabo.save(request)
            #                 for id_ins in ids_inscripciones:
            #                     ids_matriculas = Matricula.objects.values_list('id', flat=True).filter(
            #                         inscripcion_id=id_ins,
            #                         nivel__periodo_id=periodo,
            #                         status=True)
            #                     if ids_matriculas:
            #                         for id_matricula in ids_matriculas:
            #                             ids_materias = MateriaAsignada.objects.values_list('materia_id',
            #                                                                                flat=True).filter(
            #                                 status=True,
            #                                 matricula_id=id_matricula,
            #                                 materia__profesormateria__status=True,
            #                                 materia__profesormateria__tipoprofesor__in=[
            #                                     1, 14],
            #                                 materia__profesormateria__activo=True,
            #                                 materia__profesormateria__hora__gt=0,
            #                                 materia__profesormateria__principal=True,
            #                                 materia__profesormateria__desde__lte=fechahoy,
            #                                 materia__profesormateria__hasta__gte=fechahoy
            #                             )
            #                             encuesta_seguimiento = None
            #                             bandera = False
            #                             if ids_materias:
            #                                 for id_mat in ids_materias:
            #                                     if not InscripcionEncuestaEstudianteSeguimientoSilabo.objects.filter(
            #                                             encuesta=f.cleaned_data['encuesta'],
            #                                             inscripcion_id=id_ins,
            #                                             status=True).exists():
            #                                         encuesta_seguimiento = InscripcionEncuestaEstudianteSeguimientoSilabo(
            #                                             encuesta=f.cleaned_data['encuesta'],
            #                                             inscripcion_id=id_ins,
            #                                             materia_id=id_mat)
            #                                         encuesta_seguimiento.save(request)
            #                                         bandera = True
            #                             if bandera == True:
            #                                 log(u'Adicionó nueva encuesta: %s' % encuesta_seguimiento, request, "add")
            #             return JsonResponse({"result": False, "mensaje": u"Encuesta aplicada."})
            #         else:
            #             transaction.set_rollback(True)
            #             return JsonResponse(
            #                 {'result': "bad", "form": [{k: v[0]} for k, v in f.errors.items()],
            #                  "mensaje": "Error en el formulario"})
            #     except Exception as ex:
            #         transaction.set_rollback(True)
            #         return JsonResponse({"result": "bad", "mensaje": u"Error al asignar la encuesta"})

            if action == 'editencuesta':
                try:
                    f = InscripcionEncuestaEstudianteSeguimientoSilaboForm(request.POST)
                    f.fields['encuesta'].required = False
                    if f.is_valid():
                        encuesta_estudiante_silabo = EncuestaGrupoEstudianteSeguimientoSilabo.objects.get(
                            pk=encrypt(request.POST['id']))
                        # encuesta_estudiante_silabo.encuestagrupoestudiantes = f.cleaned_data['encuesta']
                        encuesta_estudiante_silabo.fechainicioencuesta = f.cleaned_data['fechainicioencuesta']
                        encuesta_estudiante_silabo.fechafinencuesta = f.cleaned_data['fechafinencuesta']
                        encuesta_estudiante_silabo.save(request)
                        log(u'Modificó encuesta : %s' % encuesta_estudiante_silabo, request, "edit")
                        return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {'result': "bad", "form": [{k: v[0]} for k, v in f.errors.items()],
                             "mensaje": "Error en el formulario"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": True, "mensaje": u"Error al guardar los datos."})

            elif action == 'activar_desactivar_encuesta':
                try:
                    encuesta_estudiante_silabo = EncuestaGrupoEstudianteSeguimientoSilabo.objects.values_list(
                        'encuestagrupoestudiantes', flat=True).filter(
                        pk=encrypt(request.POST['id']))
                    encuesta = EncuestaGrupoEstudiantes.objects.get(pk__in=encuesta_estudiante_silabo)
                    if encuesta.activo == True:
                        encuesta.activo = False
                    else:
                        encuesta.activo = True
                    encuesta.save(request)
                    log(u'Modificó encuesta : %s' % encuesta, request, "edit")
                    return JsonResponse({"result": False, 'mensaje': 'Edicion Exitosa'})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": True, "mensaje": u"Error al guardar los datos."})

            elif action == 'traeralumnos':
                try:
                    f = InscripcionEncuestaEstudianteSeguimientoSilaboForm(request.POST)
                    id_encuesta = None
                    if f.is_valid():
                        if EncuestaGrupoEstudianteSeguimientoSilabo.objects.filter(status=True,
                                                                                   fechafinencuesta__gte=fechahoy,
                                                                                   encuestagrupoestudiantes__activo=True).exists():
                            return JsonResponse({"result": True,
                                                 "mensaje": u"No se puede asignar una nueva encuesta mientras otra esté activa."})
                        listaenviar = Inscripcion.objects.values_list('id',
                                      'persona__apellido1',
                                      'persona__apellido2',
                                      'persona__nombres').order_by(
                            'persona__apellido1').filter(
                            status=True,
                            matricula__retiradomatricula=False,
                            matricula__nivel__periodo_id=periodo,
                            coordinacion_id__in=[1, 2, 3, 4, 5]
                        )
                        if listaenviar:
                            id_encuesta = f.cleaned_data['encuesta']
                            id_encuesta_seguimiento_silabo = EncuestaGrupoEstudianteSeguimientoSilabo.objects.values_list('id',flat=True).filter(status = True, encuestagrupoestudiantes_id=id_encuesta.id).order_by('id').last()
                            encuesta_estudiante_silabo = EncuestaGrupoEstudianteSeguimientoSilabo.objects.get(
                                pk=id_encuesta_seguimiento_silabo)
                            encuesta_estudiante_silabo.fechainicioencuesta = f.cleaned_data['fechainicioencuesta']
                            encuesta_estudiante_silabo.fechafinencuesta = f.cleaned_data['fechafinencuesta']
                            encuesta_estudiante_silabo.save(request)
                            # encuesta_estudiante_silabo = EncuestaGrupoEstudianteSeguimientoSilabo(
                            #     encuestagrupoestudiantes=f.cleaned_data['encuesta'],
                            #     fechainicioencuesta=f.cleaned_data['fechainicioencuesta'],
                            #     fechafinencuesta=f.cleaned_data['fechafinencuesta'],
                            #     categoria=True)
                            # encuesta_estudiante_silabo.save(request)
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {'result': "bad", "form": [{k: v[0]} for k, v in f.errors.items()],
                             "mensaje": "Error en el formulario"})
                    return JsonResponse(
                        {"result": "ok", "cantidad": len(listaenviar), "inscritos": convertir_lista(listaenviar), "id_encuesta":id_encuesta.id})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": u"Error al listar los estudiantes."})

            elif action == 'asignar_encuesta_individual':
                try:
                    ids_matriculas = Matricula.objects.values_list('id', flat=True).filter(
                        inscripcion_id=request.POST['id_ins'],
                        nivel__periodo_id=periodo,
                        status=True)
                    if ids_matriculas:
                        for id_matricula in ids_matriculas:
                            ids_materias = MateriaAsignada.objects.values_list('materia_id',
                                                                               flat=True).filter(
                                status=True,
                                matricula_id=id_matricula,
                                materia__profesormateria__status=True,
                                materia__profesormateria__tipoprofesor__in=[
                                    1, 14],
                                materia__profesormateria__activo=True,
                                materia__profesormateria__hora__gt=0,
                                materia__profesormateria__principal=True,
                                materia__profesormateria__desde__lte=fechahoy,
                                materia__profesormateria__hasta__gte=fechahoy
                            )
                            encuesta_seguimiento = None
                            bandera = False
                            if ids_materias:
                                for id_mat in ids_materias:
                                    if not InscripcionEncuestaEstudianteSeguimientoSilabo.objects.filter(
                                            encuesta_id=request.POST['id_encuesta'],
                                            inscripcion_id=request.POST['id_ins'],
                                            materia_id=id_mat,
                                            status=True).exists():
                                        encuesta_seguimiento = InscripcionEncuestaEstudianteSeguimientoSilabo(
                                            encuesta_id=request.POST['id_encuesta'],
                                            inscripcion_id=request.POST['id_ins'],
                                            materia_id=id_mat)
                                        encuesta_seguimiento.save(request)
                                        bandera = True
                            if bandera == True:
                                log(u'Adicionó nueva encuesta: %s' % encuesta_seguimiento, request, "add")
                    return JsonResponse({"result": "ok"})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": u"Error al asignar la encuesta."})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'seguimiento-clases-videos':
                try:
                    if not persona.usuario.has_perm('inno.puede_evaluar_videos_clases_virtuales'):
                        raise NameError(
                            f'Estimad{"a" if persona.es_mujer() else "o"} {persona.nombre_completo().split()[0].title()}, no tiene permisos para visualizar esta pantalla.')

                    data['title'] = u'Detalle de clases sincrónicas y asincrónicas'
                    profesoresmateria = ProfesorMateria.objects.filter(
                        materia__asignaturamalla__malla__carrera__modalidad=3, materia__nivel__periodo=periodo,
                        profesor__activo=True, activo=True, materia__status=True, profesor__status=True,
                        status=True).values_list('profesor', flat=True).distinct()
                    data['profesores'] = Profesor.objects.filter(pk__in=profesoresmateria)
                    return render(request, 'adm_seguimientosilabo/seguimientoclasesvideos.html', data)
                except Exception as ex:
                    return HttpResponseRedirect(request.path + f'?info={ex=}')

            if action == 'asignarrespuestas':
                try:
                    inscripciones = InscripcionEncuestaEstudianteSeguimientoSilabo.objects.filter(status=True)[:240000]
                    preguntas = PreguntaEncuestaGrupoEstudiantes.objects.filter(status=True, encuesta_id=75)

                    # Iterar sobre cada inscripción y cada pregunta para crear registros en inno_respuestapreguntaencuestasilabogrupoestudiantes
                    for inscripcion in inscripciones:
                        for pregunta in preguntas:
                            # Generar valor aleatorio para "respuesta" ('SI' o 'NO')
                            valor_respuesta = random.choice(['SI', 'NO'])

                            # Crear registro en inno_respuestapreguntaencuestasilabogrupoestudiantes
                            if not RespuestaPreguntaEncuestaSilaboGrupoEstudiantes.objects.filter(
                                    inscripcionencuestasilabo_id=inscripcion.id,
                                    pregunta_id=pregunta.id,
                                    status=True).exists():
                                respuesta = RespuestaPreguntaEncuestaSilaboGrupoEstudiantes.objects.create(
                                    inscripcionencuestasilabo_id=inscripcion.id,
                                    pregunta_id=pregunta.id,
                                    respuesta=valor_respuesta,
                                    respuestaporno=''
                                )
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": True, "mensaje": u"Error al guardar los datos."})

            elif action == 'estadistica_encuesta':
                try:
                    data['title'] = u'Resultados estadísticos'
                    data['id'] = id = request.GET.get('id')
                    # filtro = Q(status=True, inscripcionencuestasilabo__materia__nivel__periodo=periodo, inscripcionencuestasilabo__materia__profesormateria__tipoprofesor__in=[1, 14],
                    #            inscripcionencuestasilabo__materia__profesormateria__activo=True, inscripcionencuestasilabo__materia__profesormateria__status=True,
                    #            inscripcionencuestasilabo__materia__profesormateria__principal = True, inscripcionencuestasilabo__materia__profesormateria__hora__gt=0
                    #            )
                    filtro = Q(status=True, inscripcionencuestasilabo__materia__nivel__periodo=periodo, inscripcionencuestasilabo__materia__profesormateria__tipoprofesor__in=[1, 14])
                    url_vars, search = f'&action=estadistica_encuesta&id={id}', ''

                    #-----------DIRECTIVOS-----------#
                    idsdirectivos = [25320, 26985]
                    data['super_directivos'] = super_directivos = False
                    if persona.pk in idsdirectivos or persona.usuario.groups.filter(
                            name__startswith='VICERREC').distinct().exists():
                        data['super_directivos'] = super_directivos = True

                    carreras = 0
                    asignaturaselected = 0
                    nivelselected = 0
                    paraleloselected = '0'
                    carrerasselected = 0
                    if not super_directivos:
                        miscarreras = persona.mis_carreras_tercer_nivel()
                        tiene_carreras_director = True if miscarreras else False
                        querydecano = ResponsableCoordinacion.objects.filter(periodo=periodo, status=True,
                                                                             persona=persona, tipo=1)
                        if not querydecano:
                            if not tiene_carreras_director:
                                return HttpResponseRedirect(f"{request.path}?info=Debe tener carreras asignadas.")
                        es_director_carr = tiene_carreras_director if not querydecano.exists() else False
                        data['es_director_carr'] = es_director_carr
                        data['es_decano'] = es_decano = querydecano.exists()
                        # carreras = carreras_imparte_ids(profesor)
                        carreras_coord = coordinacion.listadocarreras(periodo)
                        carreras = []
                        for carr in carreras_coord:
                            if persona == carr.coordinador(periodo, coordinacion.sede).persona:
                                carreras.append(carr.id)
                        director_car = CoordinadorCarrera.objects.filter(carrera__in=carreras, periodo=periodo,
                                                                         status=True, persona=persona, tipo=3).first()

                        if es_decano:
                            idcoordinacion = ResponsableCoordinacion.objects.values_list('coordinacion_id',
                                                                                         flat=True).filter(
                                periodo=periodo, status=True, persona=persona).first()
                            if idcoordinacion == 2 or idcoordinacion == 3:
                                idcoordinacion = (2, 3)
                            else:
                                idcoordinacion = (idcoordinacion,)
                            contador = querydecano.count()
                            carrerasin = None
                            if contador > 1:
                                carrerasin = querydecano[0].coordinacion.carrera.filter(status=True)
                                for i in range(1, contador):
                                    carrerasin = carrerasin.union(
                                        querydecano[i].coordinacion.carrera.filter(status=True))
                            else:
                                carrerasin = querydecano[0].coordinacion.carrera.filter(status=True)
                            carrerasin_lista = list(carrerasin)
                            mallacarrerasdecano = Malla.objects.filter(status=True, carrera__in=carrerasin_lista)
                            carreras = []
                            for carr in mallacarrerasdecano:
                                if carr.uso_en_periodo(periodo):
                                    carreras.append(carr.carrera.id)
                            data['carreras'] = Carrera.objects.filter(id__in=carreras, status=True)
                            # filtro = filtro & Q(profesor__coordinacion__id__in=idcoordinacion)
                        else:
                        #--------------------FILTROS DIRECTORES-------------------#
                            # ASIGNATURAS
                            data['asignaturas'] = asignaturas = Asignatura.objects.filter(
                                id__in=Materia.objects.values_list('asignatura_id', flat=True).filter(
                                    asignaturamalla__malla__carrera__id__in=carreras,
                                    asignaturamalla__transversal=False,
                                    nivel__periodo=periodo, status=True).distinct().order_by(
                                    'asignaturamalla__nivelmalla__nombre'), status=True)

                            # NIVEL
                            data['nivel'] = nivel = NivelMalla.objects.filter(
                                id__in=Materia.objects.values_list('asignaturamalla__nivelmalla__id',
                                                                   flat=True).filter(
                                    asignaturamalla__malla__carrera__id__in=carreras, status=True,
                                    nivel__periodo=periodo).distinct().order_by(
                                    'asignaturamalla__nivelmalla__nombre'), status=True)

                    else:
                        data['facultades'] = Coordinacion.objects.filter(id__in=(1, 2, 4, 5), status=True)
                        if 'facu' in request.GET and int(request.GET['facu']) > 0:
                            data['facultadeselected'] = facultadeselected = int(request.GET['facu'])
                            url_vars += f'&facu={facultadeselected}'
                            if facultadeselected == 2:
                                idcoordinacion = (2, 3)
                            else:
                                idcoordinacion = (facultadeselected,)
                            # filtro = filtro & Q(profesor__coordinacion__id__in=idcoordinacion)
                            coordinacion = Coordinacion.objects.filter(id__in=idcoordinacion, status=True)
                            contador = coordinacion.count()
                            carrerasin = None
                            if contador > 1:
                                carrerasin = coordinacion[0].carrera.filter(status=True)
                                for i in range(1, contador):
                                    carrerasin = carrerasin.union(coordinacion[i].carrera.filter(status=True))
                            else:
                                carrerasin = coordinacion[0].carrera.filter(status=True)
                            carrerasin_lista = list(carrerasin)
                            mallacarrerasdecano = Malla.objects.filter(status=True, carrera__in=carrerasin_lista)
                            carreras = []
                            for carr in mallacarrerasdecano:
                                if carr.uso_en_periodo(periodo):
                                    carreras.append(carr.carrera.id)
                            data['carreras'] = Carrera.objects.filter(id__in=carreras, status=True)
                        else:
                            filtro = filtro & Q(inscripcionencuestasilabo__materia__profesormateria__profesor__coordinacion__id__in=[1,2,3,4,5])
                            coordinacion = Coordinacion.objects.filter(id__in=[1,2,3,4,5], status=True)
                            contador = coordinacion.count()
                            carrerasin = None
                            if contador > 1:
                                carrerasin = coordinacion[0].carrera.filter(status=True)
                                for i in range(1, contador):
                                    carrerasin = carrerasin.union(coordinacion[i].carrera.filter(status=True))
                            else:
                                carrerasin = coordinacion[0].carrera.filter(status=True)
                            carrerasin_lista = list(carrerasin)
                            mallacarrerasdecano = Malla.objects.filter(status=True, carrera__in=carrerasin_lista)
                            carreras = []
                            for carr in mallacarrerasdecano:
                                if carr.uso_en_periodo(periodo):
                                    carreras.append(carr.carrera.id)


                    #----------------------FILTRADO POR DOCENTE-----------------------------#

                    if 's' in request.GET:
                        search = request.GET['s']
                        ss = search.split(' ')
                        if len(ss) == 1:
                            filtro = filtro & (Q(inscripcionencuestasilabo__materia__profesormateria__profesor__persona__nombres__icontains=search) |
                                               Q(inscripcionencuestasilabo__materia__profesormateria__profesor__persona__apellido1__icontains=search) |
                                               Q(inscripcionencuestasilabo__materia__profesormateria__profesor__persona__apellido2__icontains=search) |
                                               Q(inscripcionencuestasilabo__materia__profesormateria__profesor__persona__cedula__icontains=search) |
                                               Q(inscripcionencuestasilabo__materia__profesormateria__profesor__persona__pasaporte__icontains=search))
                        else:
                            filtro = filtro & (Q(inscripcionencuestasilabo__materia__profesormateria__profesor__persona__apellido1__icontains=ss[0]) &
                                               Q(inscripcionencuestasilabo__materia__profesormateria__profesor__persona__apellido2__icontains=ss[1]))
                        url_vars += f"&s={search}"

                    #----------------------FILTRADO POR CARRERAS-----------------------------#

                    if 'carr' in request.GET and int(request.GET['carr']) > 0:
                        carreras = []
                        data['carrerasselected'] = carrerasselected = int(request.GET['carr'])
                        url_vars += f'&carr={carrerasselected}'
                        carreras.append(carrerasselected)
                        filtro = filtro & Q(inscripcionencuestasilabo__materia__asignaturamalla__malla__carrera__id__in=carreras)
                        ############################
                        # ASIGNATURAS
                        data['asignaturas'] = asignaturas = Asignatura.objects.filter(
                            id__in=Materia.objects.values_list('asignatura_id', flat=True).filter(
                                asignaturamalla__malla__carrera__id__in=carreras,
                                asignaturamalla__transversal=False,
                                nivel__periodo=periodo, status=True).distinct().order_by(
                                'asignaturamalla__nivelmalla__nombre'), status=True)

                        # NIVEL
                        data['nivel'] = nivel = NivelMalla.objects.filter(
                            id__in=Materia.objects.values_list('asignaturamalla__nivelmalla__id',
                                                               flat=True).filter(
                                asignaturamalla__malla__carrera__id__in=carreras, status=True,
                                nivel__periodo=periodo).distinct().order_by(
                                'asignaturamalla__nivelmalla__nombre'), status=True)

                    if 'asig' in request.GET and int(request.GET['asig']) > 0:
                        asignaturaselected = int(request.GET['asig'])
                        url_vars += f'&asig={asignaturaselected}'
                        filtro = filtro & Q(inscripcionencuestasilabo__materia__asignaturamalla__asignatura__id=asignaturaselected)
                        data['nivel'] = nivel = NivelMalla.objects.filter(
                            id__in=Materia.objects.values_list('asignaturamalla__nivelmalla__id',
                                                               flat=True).filter(
                                asignaturamalla__malla__carrera__id__in=carreras,
                                asignaturamalla__asignatura__id=asignaturaselected, status=True,
                                nivel__periodo=periodo).distinct().order_by(
                                'asignaturamalla__nivelmalla__nombre'), status=True)
                    if 'niv' in request.GET and int(request.GET['niv']) > 0:
                        nivelselected = int(request.GET['niv'])
                        url_vars += f'&niv={nivelselected}'
                        filtro = filtro & Q(inscripcionencuestasilabo__materia__asignaturamalla__nivelmalla__id=nivelselected)
                        # PARALELOS
                        data['paralelos'] = Paralelo.objects.filter(
                            nombre__in=Materia.objects.values_list('paralelo', flat=True).filter(status=True,
                                                                                                 asignaturamalla__malla__carrera__id__in=carreras,
                                                                                                 asignaturamalla__nivelmalla__id=nivelselected).distinct(),
                            status=True)
                        if 'par' in request.GET and request.GET['par'] != '0':
                            paraleloselected = request.GET['par']
                            data['paraleloid'] = paraleloselected
                            url_vars += f'&par={paraleloselected}'
                            filtro = filtro & Q(inscripcionencuestasilabo__materia__paralelo=paraleloselected)

                    data['encuesta'] = encuesta = EncuestaGrupoEstudiantes.objects.filter(status=True,encuestagrupoestudianteseguimientosilabo__id=int(encrypt(request.GET['id'])))
                    data['indicadores'] = RespuestaPreguntaEncuestaSilaboGrupoEstudiantes.objects.values(
                        'pregunta__id', 'pregunta__descripcion', 'pregunta__orden'
                    ).annotate(
                        cantidad_si=Coalesce(Count(Case(When(respuesta='SI', then=1))), Value(0)),
                        cantidad_no=Coalesce(Count(Case(When(respuesta='NO', then=1))), Value(0))
                        # cantidad_sinresponder=Coalesce(Count(Case(When(inscripcionencuestasilabo__respondio=False, then=1))), Value(0))
                    ).filter(
                        ~Q(respuesta__isnull=True), filtro, status=True, inscripcionencuestasilabo__respondio=True,
                        inscripcionencuestasilabo__materia__asignaturamalla__malla__carrera_id__in=carreras).distinct().order_by(
                        'pregunta__orden')

                    data['hoy'] = datetime.now().date()

                    data['carrerasselected'] = carrerasselected
                    data['asignaturaselected'] = asignaturaselected
                    data['nivelselected'] = nivelselected
                    data['paraleloselected'] = paraleloselected
                    data['s'] = search if search else ""

                    return render(request, "adm_seguimientosilabo/estadisticas_encuesta.html", data)
                except Exception as ex:
                    pass

            if action == 'verencuestas':
                try:
                    idsdirectivos = [25320, 26985]
                    data['hoy'] = hoy = datetime.now().date()
                    data['super_directivos'] = super_directivos = False
                    if persona.pk in idsdirectivos or persona.usuario.groups.filter(
                            name__startswith='VICERREC').distinct().exists():
                        data['super_directivos'] = super_directivos = True
                    data['title'] = u'Encuestas seguimiento al sílabo'
                    data['encuestas'] = encuestas = EncuestaGrupoEstudiantes.objects.filter(
                        id__in=EncuestaGrupoEstudianteSeguimientoSilabo.objects.values_list(
                            'encuestagrupoestudiantes_id',
                            flat=True).filter(categoria=True, status=True),
                        status=True).order_by('fecha_creacion').distinct()
                    return render(request, 'adm_seguimientosilabo/verencuestas.html', data)
                except Exception as ex:
                    return HttpResponseRedirect(request.path + f'?info={ex=}')

            if action == 'editencuesta':
                try:
                    data['title'] = u'Modificar encuesta'
                    data['action'] = request.GET['action']
                    data['id'] = id = int(encrypt(request.GET['id']))
                    data[
                        'inscripcion_encuesta'] = encuesta_estudiante_silabo = EncuestaGrupoEstudianteSeguimientoSilabo.objects.get(
                        pk=int(encrypt(request.GET['id'])))
                    form = InscripcionEncuestaEstudianteSeguimientoSilaboForm(
                        initial={'encuesta': encuesta_estudiante_silabo.encuestagrupoestudiantes,
                                 'fechainicioencuesta': encuesta_estudiante_silabo.fechainicioencuesta,
                                 'fechafinencuesta': encuesta_estudiante_silabo.fechafinencuesta})
                    form.deshabilitar_campo('encuesta')
                    data['form'] = form
                    template = get_template("adm_seguimientosilabo/modal/encuestaseguimiento.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            if action == 'detalle-clases-videos':
                try:
                    data['title'] = u'Detalle clases sincrónicas y asincrónicas'

                    cursor = connections['default'].cursor()
                    data['hoy'] = hoy = datetime.now().date()
                    data['materia'] = materia = Materia.objects.get(pk=request.GET.get('id'))

                    data_extra = {}
                    profesor = Profesor.objects.get(pk=request.GET.get('profesor'))
                    sql = profesor.get_sql_query_clase_sincronica_y_asincronica(periodo)
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    modalidad, coordinacion = None, None
                    totalsincronica, totalasincronica, totalplansincronica, totalplanasincronica = 0, 0, 0, 0
                    listaasistencias = []
                    silabo = Silabo.objects.filter(profesor=profesor, materia=materia, status=True).first()
                    results = list(filter(lambda x: x[5] == materia.pk, results))
                    for cuentamarcadas in results:
                        clase = Clase.objects.get(pk=cuentamarcadas[0], status=True)
                        unidades_temp = []
                        try:
                            silabosemanal = silabo.silabosemanal_set.filter(semana=cuentamarcadas[24],
                                                                            status=True).first()
                            clase.__setattr__('numsemana', silabosemanal.numsemana)
                            for u in silabosemanal.unidades_silabosemanal():
                                pk = u.temaunidadresultadoprogramaanalitico.unidadresultadoprogramaanalitico.id
                                temas_temp = [(t.temaunidadresultadoprogramaanalitico,
                                               silabosemanal.subtemas_silabosemanal(
                                                   t.temaunidadresultadoprogramaanalitico),
                                               silabosemanal.subtemas_adicionales(t.pk)) for t in
                                              silabosemanal.temas_silabosemanal(pk)]
                                unidades_temp.append({
                                    'unidad': f'UNIDAD {u.temaunidadresultadoprogramaanalitico.unidadresultadoprogramaanalitico.orden} {u.temaunidadresultadoprogramaanalitico.unidadresultadoprogramaanalitico.descripcion}',
                                    'temas': temas_temp})
                        except Exception as ex:
                            ...
                        clase.__setattr__('unidades', unidades_temp)
                        clase.__setattr__('semana', cuentamarcadas[24])
                        clase.__setattr__('rangofecha', cuentamarcadas[8])
                        clase.__setattr__('rangodia', cuentamarcadas[9])
                        clase.__setattr__('sincronica', cuentamarcadas[10])
                        clase.__setattr__('asincronica', cuentamarcadas[11])
                        clase.__setattr__('fecha_feriado', cuentamarcadas[17])
                        clase.__setattr__('observacion_feriado', cuentamarcadas[18])
                        totalsincronica += 1 if cuentamarcadas[7] == 2 else 0
                        totalasincronica += 1 if cuentamarcadas[7] == 7 else 0
                        totalplansincronica += 1
                        totalplanasincronica += 1 if cuentamarcadas[11] else 0
                        coordinacion = clase.materia.coordinacion()
                        sincronica = clase.clasesincronica_set.filter(numerosemana=cuentamarcadas[24],
                                                                      fechaforo=cuentamarcadas[8], status=True)
                        asincronica = clase.claseasincronica_set.filter(numerosemana=cuentamarcadas[24],
                                                                        fechaforo=cuentamarcadas[8], status=True)
                        listaasistencias.append(
                            {'clase': clase, 'sincronicas': sincronica, 'asincronicas': asincronica})

                    data['profesor'] = profesor
                    data['coordinacion'] = coordinacion
                    data['listaasistencias'] = listaasistencias
                    data['totalsincronica'] = totalsincronica
                    data['totalasincronica'] = totalasincronica
                    data['totalplansincronica'] = totalplansincronica
                    data['totalplanasincronica'] = totalplanasincronica
                    template = get_template('adm_seguimientosilabo/detalleclasesvideos.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            if action == 'get-materias':
                try:
                    materias = ProfesorMateria.objects.filter(materia__asignaturamalla__malla__carrera__modalidad=3,
                                                              profesor_id=request.GET.get('pk'),
                                                              materia__nivel__periodo=periodo, profesor__activo=True,
                                                              activo=True, materia__status=True, profesor__status=True,
                                                              status=True).values_list('materia_id',
                                                                                       'materia__asignaturamalla__asignatura__nombre',
                                                                                       'materia__paralelo').distinct()
                    return JsonResponse({'result': 'ok', 'data': list(materias)})
                except Exception as ex:
                    pass

            if action == 'verseguimientosilabo':
                try:
                    idsdirectivos = [25320, 26985]
                    if not persona.usuario.has_perm(
                            'inno.puede_ver_seguimiento_silabo') and not persona.pk in idsdirectivos:
                        raise NameError(
                            f'Estimad{"a" if persona.es_mujer() else "o"} {persona.nombre_completo().split()[0].title()}, no tiene permisos para visualizar esta pantalla.')
                    from sga.excelbackground import reporte_general_seguimiento_silabo
                    data['super_directivos'] = super_directivos = False
                    if persona.pk in idsdirectivos or persona.usuario.groups.filter(
                            name__startswith='VICERREC').distinct().exists():
                        data['super_directivos'] = super_directivos = True
                    carreras = 0
                    asignaturaselected = 0
                    nivelselected = 0
                    paraleloselected = '0'
                    carrerasselected = 0
                    data['title'] = u'Seguimiento al sílabo del docente'
                    filtro = Q(status=True, materia__nivel__periodo=periodo, profesor__persona__real=True) & Q(
                        tipoprofesor__in=(1, 14))
                    url_vars, search = '&action=verseguimientosilabo', ''
                    if not super_directivos:
                        miscarreras = persona.mis_carreras_tercer_nivel()
                        tiene_carreras_director = True if miscarreras else False
                        querydecano = ResponsableCoordinacion.objects.filter(periodo=periodo, status=True,
                                                                             persona=persona, tipo=1)
                        if not querydecano:
                            if not tiene_carreras_director:
                                return HttpResponseRedirect(f"{request.path}?info=Debe tener carreras asignadas.")
                        es_director_carr = tiene_carreras_director if not querydecano.exists() else False
                        data['es_director_carr'] = es_director_carr
                        data['es_decano'] = es_decano = querydecano.exists()
                        # carreras = carreras_imparte_ids(profesor)
                        profesor = persona.profesor()
                        director_car = False
                        if profesor:
                            carreras = []
                            distributivo = ProfesorDistributivoHoras.objects.filter(periodo_id=periodo.pk,
                                                                                    profesor=profesor)
                            if distributivo:
                                carreras_coord = distributivo[0].coordinacion.listadocarreras(periodo)
                                for carr in carreras_coord:
                                    if persona == carr.coordinador(periodo, distributivo[0].coordinacion.sede).persona:
                                        carreras.append(carr.id)
                                if carreras:
                                    director_car = CoordinadorCarrera.objects.filter(carrera__in=carreras,
                                                                                     periodo=periodo,
                                                                                     status=True,
                                                                                     persona=persona,
                                                                                     tipo=3).first()
                        # director_car = CoordinadorCarrera.objects.filter(periodo=periodo,
                        #                                                  status=True, persona=persona, tipo=3).first()
                        if director_car:
                            data['carrera'] = director_car = director_car.carrera
                            data['facultad'] = distributivo[0].coordinacion.nombre
                        # CARRERAS
                        if es_decano:
                            idcoordinacion = ResponsableCoordinacion.objects.values_list('coordinacion_id',
                                                                                         flat=True).filter(
                                periodo=periodo, status=True, persona=persona).first()
                            if idcoordinacion == 2 or idcoordinacion == 3:
                                idcoordinacion = (2, 3)
                            else:
                                idcoordinacion = (idcoordinacion,)
                            contador = querydecano.count()
                            carrerasin = None
                            if contador > 1:
                                carrerasin = querydecano[0].coordinacion.carrera.filter(status=True)
                                for i in range(1, contador):
                                    carrerasin = carrerasin.union(
                                        querydecano[i].coordinacion.carrera.filter(status=True))
                            else:
                                carrerasin = querydecano[0].coordinacion.carrera.filter(status=True)
                            carrerasin_lista = list(carrerasin)
                            mallacarrerasdecano = Malla.objects.filter(status=True, carrera__in=carrerasin_lista)
                            carreras = []
                            for carr in mallacarrerasdecano:
                                if carr.uso_en_periodo(periodo):
                                    carreras.append(carr.carrera.id)
                            data['carreras'] = Carrera.objects.filter(id__in=carreras, status=True)
                            # filtro = filtro & Q(profesor__coordinacion__id__in=idcoordinacion)
                        else:
                            # ASIGNATURAS
                            data['asignaturas'] = asignaturas = Asignatura.objects.filter(
                                id__in=Materia.objects.values_list('asignatura_id', flat=True).filter(
                                    asignaturamalla__malla__carrera__id__in=carreras,
                                    asignaturamalla__transversal=False,
                                    nivel__periodo=periodo, status=True).distinct().order_by(
                                    'asignaturamalla__nivelmalla__nombre'), status=True)

                            # NIVEL
                            data['nivel'] = nivel = NivelMalla.objects.filter(
                                id__in=Materia.objects.values_list('asignaturamalla__nivelmalla__id',
                                                                   flat=True).filter(
                                    asignaturamalla__malla__carrera__id__in=carreras, status=True,
                                    nivel__periodo=periodo).distinct().order_by(
                                    'asignaturamalla__nivelmalla__nombre'), status=True)
                        # filtro = filtro & Q(materia__asignaturamalla__malla__carrera__id__in=carreras)

                    else:
                        data['facultades'] = Coordinacion.objects.filter(id__in=(1, 2, 4, 5), status=True)
                        if 'facu' in request.GET and int(request.GET['facu']) > 0:
                            data['facultadeselected'] = facultadeselected = int(request.GET['facu'])
                            url_vars += f'&facu={facultadeselected}'
                            if facultadeselected == 2:
                                idcoordinacion = (2, 3)
                            else:
                                idcoordinacion = (facultadeselected,)
                            # filtro = filtro & Q(profesor__coordinacion__id__in=idcoordinacion)
                            coordinacion = Coordinacion.objects.filter(id__in=idcoordinacion, status=True)
                            contador = coordinacion.count()
                            carrerasin = None
                            if contador > 1:
                                carrerasin = coordinacion[0].carrera.filter(status=True)
                                for i in range(1, contador):
                                    carrerasin = carrerasin.union(coordinacion[i].carrera.filter(status=True))
                            else:
                                carrerasin = coordinacion[0].carrera.filter(status=True)
                            carrerasin_lista = list(carrerasin)
                            mallacarrerasdecano = Malla.objects.filter(status=True, carrera__in=carrerasin_lista)
                            carreras = []
                            for carr in mallacarrerasdecano:
                                if carr.uso_en_periodo(periodo):
                                    carreras.append(carr.carrera.id)
                            data['carreras'] = Carrera.objects.filter(id__in=carreras, status=True)
                        else:
                            filtro = filtro & Q(profesor__coordinacion__id__in=[1,2,3,4,5])
                            coordinacion = Coordinacion.objects.filter(id__in=[1,2,3,4,5], status=True)
                            contador = coordinacion.count()
                            carrerasin = None
                            if contador > 1:
                                carrerasin = coordinacion[0].carrera.filter(status=True)
                                for i in range(1, contador):
                                    carrerasin = carrerasin.union(coordinacion[i].carrera.filter(status=True))
                            else:
                                carrerasin = coordinacion[0].carrera.filter(status=True)
                            carrerasin_lista = list(carrerasin)
                            mallacarrerasdecano = Malla.objects.filter(status=True, carrera__in=carrerasin_lista)
                            carreras = []
                            for carr in mallacarrerasdecano:
                                if carr.uso_en_periodo(periodo):
                                    carreras.append(carr.carrera.id)
                    filtro = filtro & Q(materia__asignaturamalla__malla__carrera__id__in=carreras)
                        # else:
                        #     filtro = filtro & Q(profesor__coordinacion__id__in=(1,2,3,4,5))
                    if 's' in request.GET:
                        search = request.GET['s']
                        ss = search.split(' ')
                        if len(ss) == 1:
                            filtro = filtro & (Q(profesor__persona__nombres__icontains=search) |
                                               Q(profesor__persona__apellido1__icontains=search) |
                                               Q(profesor__persona__apellido2__icontains=search) |
                                               Q(profesor__persona__cedula__icontains=search) |
                                               Q(profesor__persona__pasaporte__icontains=search))
                        else:
                            filtro = filtro & (Q(profesor__persona__apellido1__icontains=ss[0]) &
                                               Q(profesor__persona__apellido2__icontains=ss[1]))
                        url_vars += f"&s={search}"

                    if 'carr' in request.GET and int(request.GET['carr']) > 0:
                        carreras = []
                        data['carrerasselected'] = carrerasselected = int(request.GET['carr'])
                        url_vars += f'&carr={carrerasselected}'
                        carreras.append(carrerasselected)
                        filtro = filtro & Q(materia__asignaturamalla__malla__carrera__id__in=carreras)
                        ############################
                        # ASIGNATURAS
                        data['asignaturas'] = asignaturas = Asignatura.objects.filter(
                            id__in=Materia.objects.values_list('asignatura_id', flat=True).filter(
                                asignaturamalla__malla__carrera__id__in=carreras,
                                asignaturamalla__transversal=False,
                                nivel__periodo=periodo, status=True).distinct().order_by(
                                'asignaturamalla__nivelmalla__nombre'), status=True)

                        # NIVEL
                        data['nivel'] = nivel = NivelMalla.objects.filter(
                            id__in=Materia.objects.values_list('asignaturamalla__nivelmalla__id',
                                                               flat=True).filter(
                                asignaturamalla__malla__carrera__id__in=carreras, status=True,
                                nivel__periodo=periodo).distinct().order_by(
                                'asignaturamalla__nivelmalla__nombre'), status=True)

                    if 'asig' in request.GET and int(request.GET['asig']) > 0:
                        asignaturaselected = int(request.GET['asig'])
                        url_vars += f'&asig={asignaturaselected}'
                        filtro = filtro & Q(materia__asignaturamalla__asignatura__id=asignaturaselected)
                        data['nivel'] = nivel = NivelMalla.objects.filter(
                            id__in=Materia.objects.values_list('asignaturamalla__nivelmalla__id',
                                                               flat=True).filter(
                                asignaturamalla__malla__carrera__id__in=carreras,
                                asignaturamalla__asignatura__id=asignaturaselected, status=True,
                                nivel__periodo=periodo).distinct().order_by(
                                'asignaturamalla__nivelmalla__nombre'), status=True)
                    if 'niv' in request.GET and int(request.GET['niv']) > 0:
                        nivelselected = int(request.GET['niv'])
                        url_vars += f'&niv={nivelselected}'
                        filtro = filtro & Q(materia__asignaturamalla__nivelmalla__id=nivelselected)
                        # PARALELOS
                        data['paralelos'] = Paralelo.objects.filter(
                            nombre__in=Materia.objects.values_list('paralelo', flat=True).filter(status=True,
                                                                                                 asignaturamalla__malla__carrera__id__in=carreras,
                                                                                                 asignaturamalla__nivelmalla__id=nivelselected).distinct(),
                            status=True)
                        if 'par' in request.GET and request.GET['par'] != '0':
                            paraleloselected = request.GET['par']
                            data['paraleloid'] = paraleloselected
                            url_vars += f'&par={paraleloselected}'
                            filtro = filtro & Q(materia__paralelo=paraleloselected)
                    listado = Profesor.objects.filter(
                        pk__in=ProfesorMateria.objects.values_list('profesor', flat=True).filter(
                            filtro).distinct()).order_by('persona__apellido1', 'persona__apellido2')
                    # PREGUNTAR SI TIENE HORARIO DE ACTIVIDADES APROBADO
                    periodoposgrado = False
                    if periodo.tipo_id in [3, 4]:
                        periodoposgrado = True
                    data['tienehorarioaprobado'] = periodo.claseactividadestado_set.filter(profesor__in=listado,
                                                                                           estadosolicitud=2,
                                                                                           status=True).exists() if not periodoposgrado else True
                    # Inicio paginación
                    data['listado'] = listado
                    paging = MiPaginador(listado, 3)
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
                    data['url_vars'] = url_vars
                    data['profesoresmaterias'] = page.object_list
                    # Fin paginación
                    data['carreras2'] = carreras
                    data['carrerasselected'] = carrerasselected
                    data['asignaturaselected'] = asignaturaselected
                    data['nivelselected'] = nivelselected
                    data['paraleloselected'] = paraleloselected
                    # data['carreras'] = carreras = Carrera.objects.filter(status=True, coordinacion__id=9).order_by(
                    #     'modalidad')

                    # SEGUIMIENTO SILABO - RECURSOS PLANIFICADOS
                    # if 'fechaini' in request.GET:
                    #     fechaini = request.GET['fechaini']
                    #     fechainisplit = fechaini.split('-')
                    #     yearini = int(fechainisplit[0])
                    #     monthini = int(fechainisplit[1])
                    #     dayini = int(fechainisplit[2])
                    #     if 'fechames' in request.GET:
                    #         fechames = request.GET['fechames']
                    #         fechasplit = fechames.split('-')
                    #         year = int(fechasplit[0])
                    #         month = int(fechasplit[1])
                    #         last_day = int(fechasplit[2])
                    # else:
                    data['fechaactual'] = fechaactual = datetime.now().date()

                    ########################### INICIO DE FECHA POR MES #######################################
                    # now = datetime.now()
                    # yearini = now.year
                    # year = now.year
                    # dayini = 1
                    # # month = now.month
                    # dia = int(now.day)
                    # if dia >= 28:
                    #     month = now.month
                    #     monthini = now.month
                    # else:
                    #     if int(now.month) == 1:
                    #         month = int(now.month)
                    #         monthini = int(now.month)
                    #     else:
                    #         month = int(now.month) - 1
                    #         monthini = int(now.month) - 1
                    # last_day = calendar.monthrange(year, month)[1]
                    # calendar.monthrange(year, month)
                    # start = date(yearini, monthini, dayini)
                    # data['fini'] = fini = str(start.day) + '-' + str(start.month) + '-' + str(start.year)
                    # end = date(year, month, last_day)
                    # data['ffin'] = ffin = str(end.day) + '-' + str(end.month) + '-' + str(end.year)
                    ###################################################################################

                    data['fini'] = fini = str(periodo.inicio)
                    data['ffin'] = ffin = str(periodo.fin)

                    data['s'] = search if search else ""

                    # -----EXPORTAR PDF------
                    if 'exportar_seguimiento_pdf' in request.GET:
                        noti = Notificacion(cuerpo='Reporte en proceso', titulo='PDF seguimiento al sílabo del docente',
                                            destinatario=persona,
                                            url="/notificacion",
                                            prioridad=1, app_label='SGA',
                                            fecha_hora_visible=datetime.now() + timedelta(days=1),
                                            tipo=2, en_proceso=True)
                        noti.save(request)
                        reporte_general_seguimiento_silabo(request=request, data=data, notiid=noti.pk,
                                                           periodo=periodo).start()
                        return JsonResponse({'result': True})
                    return render(request, "adm_seguimientosilabo/view.html", data)
                except Exception as ex:
                    return HttpResponseRedirect(f"{request.path}?info=No puede acceder al módulo. {ex}")

            if action == 'verdetallerecursos':
                try:
                    data['id'] = request.GET['id']
                    data['idmateria'] = request.GET['idmateria']
                    data['materia'] = Materia.objects.get(pk=request.GET['idmateria'])
                    profe = Profesor.objects.get(pk=request.GET['id'])
                    # if 'fechaini' in request.GET:
                    #     fechaini = request.GET['fechaini']
                    #     fechainisplit = fechaini.split('-')
                    #     yearini = int(fechainisplit[0])
                    #     monthini = int(fechainisplit[1])
                    #     dayini = int(fechainisplit[2])
                    #     if 'fechames' in request.GET:
                    #         fechames = request.GET['fechames']
                    #         fechasplit = fechames.split('-')
                    #         year = int(fechasplit[0])
                    #         month = int(fechasplit[1])
                    #         last_day = int(fechasplit[2])
                    # else:
                    # fechames = datetime.now().date()
                    # now = datetime.now()
                    # yearini = now.year
                    # year = now.year
                    # dayini = 1
                    # # month = now.month
                    # dia = int(now.day)
                    # if dia >= 28:
                    #     month = now.month
                    #     monthini = now.month
                    # else:
                    #     if int(now.month) == 1:
                    #         month = int(now.month)
                    #         monthini = int(now.month)
                    #     else:
                    #         month = int(now.month) - 1
                    #         monthini = int(now.month) - 1
                    # last_day = calendar.monthrange(year, month)[1]
                    # calendar.monthrange(year, month)
                    # start = date(yearini, monthini, dayini)
                    # fini = str(start.day) + '-' + str(start.month) + '-' + str(start.year)
                    # end = date(year, month, last_day)
                    # ffin = str(end.day) + '-' + str(end.month) + '-' + str(end.year)
                    ##########################################################################

                    fini = str(periodo.inicio)
                    ffin = str(periodo.fin)
                    data['data'] = informe_actividades_mensual_docente_v4_extra(profe, periodo, fini, ffin, 'FACULTAD')
                    template = get_template("adm_seguimientosilabo/modal/verdetallerecursos.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            if action == 'verdetalletemas':
                try:
                    data['idprofe'] = profe = request.GET['id']
                    data['idmateria'] = request.GET['idmateria']
                    data['periodo'] = periodo
                    data['materia'] = materia = Materia.objects.get(pk=request.GET['idmateria'])
                    template = get_template("adm_seguimientosilabo/modal/verdetalletemas.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            if action == 'verdetalleencuestas':
                try:
                    data['idprofe'] = profe = request.GET['id']
                    data['idmateria'] = materia = request.GET['idmateria']

                    preguntas_con_respuestas = RespuestaPreguntaEncuestaSilaboGrupoEstudiantes.objects.values(
                        'pregunta__id', 'pregunta__descripcion'
                    ).annotate(
                        cantidad_si=Coalesce(Count(Case(When(respuesta='SI', then=1))), Value(0)),
                        cantidad_no=Coalesce(Count(Case(When(respuesta='NO', then=1))), Value(0)),
                        cantidad_total=F('cantidad_si') + F('cantidad_no'),
                        porcentaje=Round2(F('cantidad_si') * 100 / F('cantidad_total'))
                    ).filter(
                        ~Q(respuesta__isnull=True), status=True, inscripcionencuestasilabo__materia__id=materia)
                    suma_total = 0
                    porcentaje_total = 0
                    porcentaje_sobre30 = 0
                    cont = 0
                    if preguntas_con_respuestas.exists():
                        data['preguntas'] = preguntas_con_respuestas
                        for pregunta in preguntas_con_respuestas:
                            suma_total += pregunta['porcentaje']
                            cont += 1
                    else:
                        data[
                            'preguntas'] = preguntas_con_respuestas = RespuestaPreguntaEncuestaSilaboGrupoEstudiantes.objects.values(
                            'pregunta__id', 'pregunta__descripcion'
                        ).annotate(
                            cantidad_si=Value('-'),
                            cantidad_no=Value('-'),
                            cantidad_total=Value('-'),
                            porcentaje=Value('-')
                        ).filter(
                            ~Q(respuesta__isnull=True), status=True).distinct()
                    if cont > 0:
                        data['porcentaje_total'] = porcentaje_total = round((suma_total / cont), 2)
                        data['porcentaje_sobre30'] = round(((porcentaje_total * 30) / 100), 2)
                    else:
                        data['porcentaje_total'] = 0
                        data['porcentaje_sobre30'] = 0
                    template = get_template("adm_seguimientosilabo/modal/verdetalleencuestas.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            if action == 'asignarencuestasilabo':
                try:
                    data['title'] = u'Asignar Encuesta'
                    data['action'] = 'traeralumnos'
                    data['form'] = InscripcionEncuestaEstudianteSeguimientoSilaboForm()
                    template = get_template("adm_seguimientosilabo/modal/encuestaseguimiento.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)

        else:
            try:
                data['title'] = u'Seguimiento académico'
                modulos = []
                if es_administrativo:
                    if persona.usuario.has_perm('inno.puede_ver_seguimiento_silabo'):
                        modulos.append(541)

                    if persona.usuario.has_perm('inno.puede_evaluar_videos_clases_virtuales'):
                        modulos.append(539)

                    data['enlaceatras'] = "/"
                    data['modulos2'] = Modulo.objects.filter(id__in=modulos, submodulo=True, status=True)
                return render(request, "adm_seguimientosilabo/panel.html", data)
            except Exception as ex:
                return HttpResponseRedirect(f"/?info=No puede acceder al módulo")


def carreras_imparte_ids(profesor):
    carreras = []
    try:
        materias = profesor.materias_imparte()
        for materia in materias:
            if not materia.asignaturamalla.malla.carrera.id in carreras:
                carreras.append(materia.asignaturamalla.malla.carrera.id)
        return carreras
    except Exception as ex:
        return []