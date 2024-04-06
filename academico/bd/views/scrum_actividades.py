import xlsxwriter
from django.contrib import messages
import os
import html
import re

from django.contrib.contenttypes.models import ContentType

from automatiza.models import PlanificacionAutomatiza, RequerimientoPlanificacionAutomatiza, PRIORIDAD, DocumentoAdjuntoRequerimiento
from balcon.models import EncuestaProceso, PreguntaEncuestaProceso
from decorators import secure_module, last_access
from datetime import datetime
import json
from django.contrib.auth.decorators import login_required
from django.db import transaction, connection, connections
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import F, ExpressionWrapper, fields

from investigacion.funciones import FORMATOS_CELDAS_EXCEL
from poli.forms import EncuestaPreguntaForm
from sagest.funciones import encrypt_id, crear_editar_encuesta
from sagest.models import Departamento, SeccionDepartamento
from settings import SITE_STORAGE
from sga.commonviews import adduserdata
from bd.forms import ProcesoSCRUMForm, IncidenciaSCRUMForm, CrearActvSecundariaForm, EquipoForm, AsignarActividadForm, \
    PlanificacionForm, RequerimientoForm, CrearComentarioForm
from bd.models import ProcesoSCRUM, IncidenciaSCRUM, PRIORIDAD_REQUERIMIENTO, ESTADO_REQUERIMIENTO, APP_LABEL, \
    IncidenciaSecundariasSCRUM, EquipoSCRUM, ComentarioIncidenciaSCRUM
from sga.models import Persona
from django.template.loader import get_template
from sga.funciones import log, MiPaginador, notificacion, validar_archivo, generar_nombre
from sga.templatetags.sga_extras import encrypt
from django.forms import model_to_dict

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction, connection, connections
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from sga.funciones import log, MiPaginador
from utils.filtros_genericos import filtro_persona_select


@login_required(redirect_field_name='ret', login_url='/loginsga')
@secure_module
@last_access
@transaction.atomic()
def view(request):
    global ex
    data = {}
    adduserdata(request, data)
    persona = request.session['persona']
    hoy = datetime.now().date()
    mi_equipo = EquipoSCRUM.objects.filter(Q(lider=persona) | Q(integrantes=persona), status=True)
    mi_departamento = persona.mi_departamento()
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'addsrumcategoria':
            try:
                f = ProcesoSCRUMForm(request.POST)
                if not f.is_valid():
                    transaction.set_rollback(True)
                    form_error = [{k: v[0]} for k, v in f.errors.items()]
                    return JsonResponse({'result': True, "form": form_error, "mensaje": "Error en el formulario"})
                categoriascrum = ProcesoSCRUM(direccion=f.cleaned_data['direccion'],
                                              gestion_recepta=f.cleaned_data['gestion_recepta'],
                                              descripcion=f.cleaned_data['descripcion'])
                categoriascrum.save(request)

                for pr in f.cleaned_data['equipos']:
                    categoriascrum.equipos.add(pr)

                log(u'Agregó una categoria %s -%s' % (categoriascrum.__str__(), categoriascrum.pk), request, 'add')
                return JsonResponse({'result': False, 'mensaje': u'Registro guardado con éxito!'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': True, 'mensaje': u'Error al procesar los datos! Detalle: %s' % (ex.__str__())})

        elif action == 'addincidenciascrum':
            try:
                f = IncidenciaSCRUMForm(request.POST, request.FILES)
                if f.is_valid():
                    incidencia = IncidenciaSCRUM(categoria=f.cleaned_data['categoria'],
                                                 titulo=f.cleaned_data['titulo'],
                                                 descripcion=f.cleaned_data['descripcion'],
                                                 app=f.cleaned_data['app'],
                                                 prioridad=f.cleaned_data['prioridad'],
                                                 asignadoa=f.cleaned_data['asignadoa'],
                                                 asignadopor=persona,
                                                 finicioactividad=f.cleaned_data['finicioactividad'],
                                                 ffinactividad=f.cleaned_data['ffinactividad'])
                    incidencia.save(request)

                    titulo = f'Nueva actividad asignada para su desarrollo {incidencia}'
                    cuerpo = f'{persona.nombre_completo_minus()} líder de equipo, le asigno una actividad a desarrollar ({incidencia})'
                    notificacion(titulo, cuerpo, incidencia.asignadoa,
                                 None, '/misactividades', incidencia.asignadoa.pk, 1, 'sga-sagest',
                                 IncidenciaSCRUM, request)
                    log(u'Asigno una Incidencia: %s' % incidencia, request, 'add')
                    return JsonResponse({'result': False, 'mensaje': u'Guardado con exito'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in f.errors.items()],
                                         "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': True, 'mensaje': f'Error al guardar los datos. {ex}'})

        elif action == 'editcategoria':
            try:
                id = request.POST['id']
                data['filtro'] = filtro = ProcesoSCRUM.objects.get(pk=int(encrypt(id)), status=True)
                f = ProcesoSCRUMForm(request.POST, instancia=filtro)
                if not f.is_valid():
                    transaction.set_rollback(True)
                    form_error = [{k: v[0]} for k, v in f.errors.items()]
                    return JsonResponse({'result': True, "form": form_error, "mensaje": "Error en el formulario"})
                filtro.direccion = f.cleaned_data['direccion']
                filtro.gestion_recepta = f.cleaned_data['gestion_recepta']
                filtro.descripcion = f.cleaned_data['descripcion']
                filtro.save(request)

                filtro.equipos.clear()
                for pr in f.cleaned_data['equipos']:
                    filtro.equipos.add(pr)
                log(u'Editó una categoria %s -%s' % (filtro, filtro.pk), request, 'edit')
                return JsonResponse({'result': False, 'mensaje': u'Registro guardado con éxito!'})

            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': True, 'mensaje': u'Error al procesar los datos! Detalle: %s' % (ex.__str__())})

        elif action == 'editincidenciascrum':
            try:
                id = (request.POST['id'])
                incidencia = IncidenciaSCRUM.objects.get(pk=int(encrypt(id)))

                f = IncidenciaSCRUMForm(request.POST)
                if f.is_valid():
                    if not incidencia.asignadoa == f.cleaned_data['asignadoa']:
                        titulo = f'Nueva actividad asignada para su desarrollo {incidencia}'
                        cuerpo = f'{persona.nombre_completo_minus()} líder de equipo, le asigno una actividad a desarrollar ({f.cleaned_data["titulo"]})'
                        notificacion(titulo, cuerpo, f.cleaned_data['asignadoa'],
                                     None, '/misactividades', incidencia.asignadoa.pk, 1, 'sga-sagest',
                                     IncidenciaSCRUM, request)
                    incidencia.categoria = f.cleaned_data['categoria']
                    incidencia.titulo = f.cleaned_data['titulo']
                    incidencia.descripcion = f.cleaned_data['descripcion']
                    incidencia.app = f.cleaned_data['app']
                    incidencia.prioridad = f.cleaned_data['prioridad']
                    # incidencia.estado = f.cleaned_data['estado']
                    incidencia.asignadoa = f.cleaned_data['asignadoa']
                    incidencia.asignadopor = persona
                    incidencia.finicioactividad = f.cleaned_data['finicioactividad']
                    incidencia.ffinactividad = f.cleaned_data['ffinactividad']
                    # incidencia.orden = f.cleaned_data['orden']
                    incidencia.save(request)
                    log(u'Editó una categoria %s -%s' % (incidencia, incidencia.pk), request, 'edit')
                    return JsonResponse({'result': False, 'mensaje': 'Edicion Exitosa'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': True, 'mensaje': f'Error al guardar los datos. {ex}'})

        elif action == 'deletescrumcategori':
            try:
                id = encrypt(request.POST['id'])
                categoriascrum = ProcesoSCRUM.objects.filter(pk=int(id), status=True).order_by('-id').first()
                categoriascrum.status = False
                categoriascrum.save(request)
                log(u'Eliminó una categoria scrum_actividades %s -%s' % (categoriascrum.__str__(), categoriascrum.pk),
                    request, 'del')
                return JsonResponse({'error': False, 'mensaje': u'Registro eliminado!'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse(
                    {'error': True, 'mensaje': u'Error al procesar los datos! Detalle: %s' % (ex.__str__())})

        elif action == 'delincidencia':
            try:
                with transaction.atomic():
                    incidencia = IncidenciaSCRUM.objects.get(pk=encrypt(request.POST['id']))
                    if incidencia.requerimiento:
                        incidencia.asignadoa=None
                        incidencia.asignadopor=None
                    else:
                        incidencia.status = False
                    incidencia.save(request)
                    log(f'Elimino una incidencia en {incidencia.__str__()} - {incidencia.get_estado_display()}', request, "del")
                    res_json = {"error": False}
            except Exception as ex:
                res_json = {'error': True, "message": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'addactividadsecundarias':
            try:
                form = CrearActvSecundariaForm(request.POST, request.FILES)
                if form.is_valid():
                    filtro = IncidenciaSecundariasSCRUM(incidencia=form.cleaned_data['incidencia'],
                                                        descripcion=form.cleaned_data['descripcion'],
                                                        asignadoa=form.cleaned_data['asignadoa'],
                                                        prioridad=form.cleaned_data['prioridad'],
                                                        finicioactividad=form.cleaned_data['finicioactividad'])
                    filtro.save(request)
                    log(u'Agrego una Sub incidencia: %s' % filtro, request, 'add')
                    return JsonResponse({'result': False, 'mensaje': u'Guardado con exito'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()],
                                         "mensaje": "Error en el formulario"}, safe=False)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': True, 'mensaje': f'Error al guardar los datos. {ex}'})

        elif action == 'addequipo':
            try:
                form = EquipoForm(request.POST)
                if not form.is_valid():
                    transaction.set_rollback(True)
                    form_error = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({'result': True, "form": form_error, "mensaje": "Error en el formulario"})
                equipo = EquipoSCRUM(nombre=form.cleaned_data['nombre'],
                                     descripcion=form.cleaned_data['descripcion'],
                                     esgestor=form.cleaned_data['esgestor'],
                                     lider=form.cleaned_data['lider'])
                equipo.save(request)
                for integrante in form.cleaned_data['integrantes']:
                    equipo.integrantes.add(integrante)
                log(f'Agrego nuevo equipo', request, 'add')
                return JsonResponse({'result': False, 'mensaje': 'Guardado con éxito'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'results': False, 'mensaje': f'Error: {ex}'})

        elif action == 'editequipo':
            try:
                equipo = EquipoSCRUM.objects.get(id=encrypt_id(request.POST['id']))
                form = EquipoForm(request.POST)
                if not form.is_valid():
                    transaction.set_rollback(True)
                    form_error = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({'result': True, "form": form_error, "mensaje": "Error en el formulario"})

                equipo.nombre = form.cleaned_data['nombre']
                equipo.descripcion = form.cleaned_data['descripcion']
                equipo.lider = form.cleaned_data['lider']
                equipo.esgestor = form.cleaned_data['esgestor']
                equipo.save(request)

                equipo.integrantes.clear()
                for integrante in form.cleaned_data['integrantes']:
                    equipo.integrantes.add(integrante)
                log(f'Edito equipo {equipo}', request, 'edit')
                return JsonResponse({'result': False, 'mensaje': 'Guardado con éxito'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'results': False, 'mensaje': f'Error: {ex}'})

        elif action == 'delequipo':
            try:
                equipo = EquipoSCRUM.objects.get(id=encrypt_id(request.POST['id']))
                equipo.status = False
                equipo.save(request, update_fields=['status'])
                log(f'Elimino equipo: {equipo}', request, 'del')
                res_json = {"error": False}
            except Exception as ex:
                res_json = {'error': True, "message": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'asignar':
            try:
                actividad = IncidenciaSCRUM.objects.get(id=encrypt_id(request.POST['id']))
                form = AsignarActividadForm(request.POST)
                if not form.is_valid():
                    transaction.set_rollback(True)
                    form_error = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({'result': True, "form": form_error, "mensaje": "Error en el formulario"})
                actividad.categoria = form.cleaned_data['categoria']
                actividad.asignadoa = form.cleaned_data['asignadoa']
                actividad.asignadopor = persona
                actividad.finicioactividad = form.cleaned_data['finicioactividad']
                actividad.ffinactividad = form.cleaned_data['ffinactividad']
                actividad.app = form.cleaned_data['app']
                actividad.save(request)
                log(f'Asigno actividad a realizar {actividad} - {actividad.asignadoa}', request, 'edit')

                requerimiento = actividad.requerimiento
                requerimiento.estado = 2
                requerimiento.save(request, update_fields=['estado'])
                log(f'Cambio de estado a asignado en el requerimiento {requerimiento}', request, 'edit')

                titulo = f'Nueva actividad asignada para su desarrollo ({actividad})'
                cuerpo = f'{persona.nombre_completo_minus()} líder de equipo, le asigno una actividad a desarrollar ({actividad})'
                notificacion(titulo, cuerpo, actividad.asignadoa,
                             None, '/misactividades', actividad.asignadoa.pk, 2, 'sga-sagest',
                             IncidenciaSCRUM, request)
                return JsonResponse({'result': False, 'mensaje': 'Guardado con éxito'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'results': False, 'mensaje': f'Error: {ex}'})

        elif action == 'editmostrarrequerimiento':
            try:
                mostrar = eval(request.POST['val'].capitalize())
                registro = PlanificacionAutomatiza.objects.get(pk=int(request.POST['id']))
                registro.mostrar = mostrar
                registro.save(request)
                log(u'%s editó estado mostrar requerimiento : %s (%s)' % (persona, registro, registro.mostrar), request, "edit")
                return JsonResponse({"result": True, 'mensaje': 'Registro actualizado con éxito'})
            except Exception as ex:
                msg = ex.__str__()
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": "Error al guardar los datos. " + msg})

        elif action == 'addplanificacion':
            try:
                f = PlanificacionForm(request.POST)
                if f.is_valid():
                    # Verifico que no exista una planificación con el mismo nombre
                    if PlanificacionAutomatiza.objects.filter(status=True, nombre__iexact=f.cleaned_data['nombre']).exists():
                        return JsonResponse({"result": "bad", "mensaje": u"El nombre de la planificación ya ha sido ingresada anteriormente"})

                    # Valido las fechas
                    if f.cleaned_data['fechafin'] <= f.cleaned_data['fechainicio']:
                        return JsonResponse({"result": "bad", "mensaje": u"La fecha fin debe ser mayor a la fecha inicio"})

                    # Guardo el registro
                    planificacion = PlanificacionAutomatiza(
                        departamento=f.cleaned_data['departamento'],
                        fechainicio=f.cleaned_data['fechainicio'],
                        fechafin=f.cleaned_data['fechafin'],
                        nombre=f.cleaned_data['nombre'],
                        detalle=f.cleaned_data['detalle'],
                        mostrar=f.cleaned_data['mostrar']
                    )
                    planificacion.save(request)

                    log(u'%s adicionó planificación para automatización: %s' % (persona, planificacion), request, "add")
                    return JsonResponse({'result': False, 'mensaje': 'Registro guardado con éxito'})
                else:
                    for k, v in f.errors.items():
                        raise NameError( k + ', ' + v[0])
            except Exception as ex:
                msg = ex.__str__()
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos. [%s]" % msg})

        elif action == 'editplanificacion':
            try:
                f = PlanificacionForm(request.POST)
                if f.is_valid():
                    # Verifico que no exista una planificación con el mismo nombre
                    if PlanificacionAutomatiza.objects.filter(status=True, nombre__iexact=f.cleaned_data['nombre']).exclude(pk=int(encrypt(request.POST['id']))).exists():
                        return JsonResponse({"result": "bad", "mensaje": u"El nombre de la planificación ya ha sido ingresada anteriormente"})

                    # Valido las fechas
                    if f.cleaned_data['fechafin'] <= f.cleaned_data['fechainicio']:
                        return JsonResponse({"result": "bad", "mensaje": u"La fecha fin debe ser mayor a la fecha inicio"})

                    # Consultar la planificación
                    planificacion = PlanificacionAutomatiza.objects.get(pk=int(encrypt(request.POST['id'])))

                    # Actualizar la planificación
                    planificacion.departamento = f.cleaned_data['departamento']
                    planificacion.fechainicio = f.cleaned_data['fechainicio']
                    planificacion.fechafin = f.cleaned_data['fechafin']
                    planificacion.nombre = f.cleaned_data['nombre']
                    planificacion.detalle = f.cleaned_data['detalle']
                    planificacion.mostrar = f.cleaned_data['mostrar']

                    planificacion.save(request)

                    log(u'%s editó planificación para automatización: %s' % (persona, planificacion), request, "edit")
                    return JsonResponse({'result': False, 'mensaje': 'Registro actualizado con éxito'})
                else:
                    for k, v in f.errors.items():
                        raise NameError( k + ', ' + v[0])
            except Exception as ex:
                msg = ex.__str__()
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos. [%s]" % msg})

        elif action == 'delplanificacion':
            try:
                # Consulto la planificación
                planificacion = PlanificacionAutomatiza.objects.get(pk=int(encrypt(request.POST['id'])))

                # Elimino la planificación
                planificacion.status = False
                planificacion.save(request)

                log(u'%s eliminó planificación para automatización: %s' % (persona, planificacion), request, "del")
                return JsonResponse({"error": False})
            except Exception as ex:
                msg = ex.__str__()
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "message": u"Error al eliminar el registro. [%s]" % msg})

        elif action == 'addrequerimiento':
            try:
                planificacion = PlanificacionAutomatiza.objects.get(pk=int(encrypt(request.POST['idp'])))

                f = RequerimientoForm(request.POST)
                if f.is_valid():
                    # Obtiene los valores de los arreglos del detalle de documentos
                    documentos = request.FILES.getlist('adjuntos')
                    lista_items1 = json.loads(request.POST['lista_items1'])

                    # Validar los archivos
                    for d in documentos:
                        items = [item for item in lista_items1 if item['archivo'] == d._name]
                        if len(items) > 1 and all(item['size'] == items[0]['size'] for item in items):
                            raise NameError(f'Error, archivos duplicados {d._name}, remplace uno de los archivos duplicados.')

                        resp = validar_archivo(items[0]['descripcion'], d, ['*'], '4MB')
                        if resp['estado'] != "OK":
                            raise NameError(f"{resp['mensaje']}.")

                    # Guardo el registro
                    requerimiento = RequerimientoPlanificacionAutomatiza(
                        periodo=planificacion,
                        gestion=f.cleaned_data['gestion'],
                        prioridad=f.cleaned_data['prioridad'],
                        tiporequerimiento=f.cleaned_data['tiporequerimiento'],
                        responsable=f.cleaned_data['responsable'],
                        detalle=f.cleaned_data['detalle'],
                        procedimiento=f.cleaned_data['procedimiento']
                    )
                    requerimiento.save(request)

                    # Guardo los documentos
                    for d in documentos:
                        items = [item for item in lista_items1 if item['archivo'] == d._name]
                        d._name = generar_nombre(f"adjunto_{requerimiento.id}_", d._name)
                        doc = DocumentoAdjuntoRequerimiento(
                            requerimiento=requerimiento,
                            leyenda=items[0]['descripcion'],
                            archivo=d)
                        doc.save(request)

                    # Guardo la incidencia
                    actividad = IncidenciaSCRUM(
                        requerimiento=requerimiento,
                        titulo=f.cleaned_data['procedimiento'],
                        descripcion=f.cleaned_data['detalle'],
                        prioridad=requerimiento.prioridad
                    )
                    actividad.save(request)

                    for lider in actividad.lideres_departamento():
                        titulo = 'Nueva incidencia recibida'
                        cuerpo = f'Estimado líder de equipo, se ingresó el requerimiento {actividad}, en caso de no pertenecer a su gestión hacer caso omiso '
                        notificacion(titulo, cuerpo, lider,
                                     None, '/adm_scrum_actividades?action=requerimientos', lider.pk, 2, 'sga-sagest',
                                     IncidenciaSCRUM, request)

                    log(u'%s adicionó requerimiento: %s' % (persona, requerimiento), request, "add")
                    return JsonResponse({'result': False, 'mensaje': 'Registro guardado con éxito'})
                else:
                    for k, v in f.errors.items():
                        raise NameError( k + ', ' + v[0])
            except Exception as ex:
                msg = ex.__str__()
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos. [%s]" % msg})

        elif action == 'editrequerimiento':
            try:
                id = int(encrypt(request.POST['id']))
                idp = int(encrypt(request.POST['idp']))

                f = RequerimientoForm(request.POST)
                if f.is_valid():
                    # Obtiene los valores de los arreglos del detalle de documentos
                    documentos = request.FILES.getlist('adjuntos')
                    lista_items1 = json.loads(request.POST['lista_items1'])
                    ids_excl = [int(item['id_adjunto']) for item in lista_items1 if item['id_adjunto']]

                    # Validar los documentos
                    for d in documentos:
                        items = [item for item in lista_items1 if item['archivo'] == d._name]
                        if len(items) > 1 and all(item['size'] == items[0]['size'] for item in items):
                            raise NameError(f'Error, archivos duplicados {d._name}, remplace uno de los archivos duplicados.')

                        resp = validar_archivo(items[0]['descripcion'], d, ['*'], '4MB')
                        if resp['estado'] != "OK":
                            raise NameError(f"{resp['mensaje']}.")

                    # Consulto el requerimiento
                    requerimiento = RequerimientoPlanificacionAutomatiza.objects.get(id=id)

                    # Actualizo el requerimiento
                    requerimiento.gestion = f.cleaned_data['gestion']
                    requerimiento.prioridad = f.cleaned_data['prioridad']
                    requerimiento.responsable = f.cleaned_data['responsable']
                    requerimiento.tiporequerimiento = f.cleaned_data['tiporequerimiento']
                    requerimiento.detalle = f.cleaned_data['detalle']
                    requerimiento.procedimiento = f.cleaned_data['procedimiento']
                    requerimiento.save(request)

                    actividad = requerimiento.incidenciascrum_set.filter(status=True).first()
                    if actividad:
                        actividad.titulo = f.cleaned_data['procedimiento']
                        actividad.descripcion = f.cleaned_data['detalle']
                        actividad.prioridad = requerimiento.prioridad
                        actividad.save(request)

                    # Guardo y actualizo los documentos
                    for d in documentos:
                        if not items[0]['id_adjunto']:
                            d._name = generar_nombre(f"adjunto_{requerimiento.id}_", d._name)
                            doc = DocumentoAdjuntoRequerimiento(
                                requerimiento=requerimiento,
                                leyenda=items[0]['descripcion'],
                                archivo=d)
                            doc.save(request)
                        else:
                            doc = DocumentoAdjuntoRequerimiento.objects.get(id=items[0]['id_adjunto'])
                            doc.leyenda = items[0]['descripcion']
                            doc.archivo = d
                            doc.save(request)

                        ids_excl.append(doc.id)

                    for items in lista_items1:
                        if items['id_adjunto']:
                            doc = DocumentoAdjuntoRequerimiento.objects.get(id=int(items['id_adjunto']))
                            doc.leyenda = items['descripcion']
                            doc.save(request, update_fields=['leyenda'])

                    requerimiento.documentos().exclude(id__in=ids_excl).update(status=False)

                    log(u'%s editó requerimiento: %s' % (persona, requerimiento), request, "edit")
                    return JsonResponse({'result': False, 'mensaje': 'Registro actualizado con éxito'})
                else:
                    for k, v in f.errors.items():
                        raise NameError( k + ', ' + v[0])
            except Exception as ex:
                msg = ex.__str__()
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos. [%s]" % msg})

        elif action == 'delrequerimiento':
            try:
                # Consulto el requerimiento
                requerimiento = RequerimientoPlanificacionAutomatiza.objects.get(pk=int(encrypt(request.POST['id'])))

                # Elimino el requerimiento
                requerimiento.status = False
                requerimiento.save(request)

                log(u'%s eliminó requerimiento: %s' % (persona, requerimiento), request, "del")
                return JsonResponse({"error": False})
            except Exception as ex:
                msg = ex.__str__()
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "message": u"Error al eliminar el registro. [%s]" % msg})

        elif action == 'addencuesta':
            with transaction.atomic():
                try:
                    id = encrypt_id(request.POST['id'])
                    form = EncuestaPreguntaForm(request.POST)
                    if not form.is_valid():
                        return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()], "message": "Error en el formulario"})

                    eSeccion = SeccionDepartamento.objects.get(id=id)
                    encuesta = crear_editar_encuesta(request, eSeccion, form, 3)
                    preguntas = json.loads(request.POST['lista_items1'])
                    lista = []
                    for p in preguntas:
                        idpregunta = p['id_pregunta']
                        if not idpregunta:
                            pregunta = PreguntaEncuestaProceso(encuesta=encuesta,
                                                               estado=p['activo'],
                                                               descripcion=p['pregunta'])
                            pregunta.save(request)
                            log(u'Agrego pregunta : %s' % pregunta, request, "add")
                        else:
                            pregunta = PreguntaEncuestaProceso.objects.get(id=idpregunta)
                            if not pregunta.en_uso():
                                pregunta.descripcion = p['pregunta']
                            pregunta.estado = p['activo']
                            pregunta.save(request)
                            log(u'Edito pregunta : %s' % pregunta, request, "edit")
                        lista.append(pregunta.id)
                    PreguntaEncuestaProceso.objects.filter(status=True, encuesta=encuesta).exclude(id__in=lista).update(status=False)
                    return JsonResponse({'result': False, 'mensaje': u'Guardado con éxito'})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': True, "mensaje": 'Error: {}'.format(ex)}, safe=False)

        elif action == 'finalizar':
            try:
                form = CrearComentarioForm(request.POST)
                if not form.is_valid():
                    transaction.set_rollback(True)
                    form_error = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({'result': True, "form": form_error, "mensaje": "Error en el formulario"})
                incidencia = form.cleaned_data['incidencia']
                incidencia.estado=3
                incidencia.asignadoa=persona
                incidencia.asignadopor=persona
                incidencia.finicioactividad=datetime.now()
                incidencia.ffinactividad=datetime.now()
                incidencia.save()
                requerimiento = incidencia.requerimiento
                requerimiento.estado=3
                requerimiento.save()

                comentario = ComentarioIncidenciaSCRUM(incidencia = incidencia,
                                                       observacion=form.cleaned_data['observacion'])
                comentario.save()
                if 'archivo' in request.FILES:
                    newfile = request.FILES['archivo']
                    newfile._name = generar_nombre(str(comentario.id), newfile._name)
                    comentario.archivo = newfile
                    comentario.save(request)
                titulo = f'El requerimiento ({requerimiento}) se finalizo.'
                cuerpo = f'El requerimiento {requerimiento} receptado fue finalizado, por favor revisar.'
                notificacion(titulo, cuerpo, requerimiento.responsable, None,
                             f'/adm_ingresarequerimiento?action=requerimientos&idp={encrypt(requerimiento.periodo.id)}&s={requerimiento.procedimiento}',
                             requerimiento.responsable.pk, 1, 'sga-sagest',
                             IncidenciaSCRUM, request)
                log(f'finalizó actividad{incidencia}', request, 'add')
                return JsonResponse({'result': False, 'mensaje': 'Guardado con éxito'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'results': False, 'mensaje': f'Error: {ex}'})


        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:

            data['action'] = action = request.GET['action']

            if action == 'addsrumcategoria':
                try:
                    if not mi_departamento and persona.usuario.is_superuser:
                        mi_departamento = Departamento.objects.get(id=93)
                    elif not mi_departamento:
                        raise NameError('No pertenece a ningún departamento')
                    data['titulo'] = u'Agregar Categoria'
                    form = ProcesoSCRUMForm()
                    form.fields['gestion_recepta'].queryset = mi_departamento.gestiones()
                    data['form'] = form
                    template = get_template('scrum_actividades/Formscrum.html')
                    return JsonResponse({'result': True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'addincidenciascrum':
                try:
                    data['title'] = u'Crear Actividad'
                    incidencia = IncidenciaSCRUMForm()
                    incidencia.fields['finicioactividad'].initial = str(datetime.now().date())
                    incidencia.fields['asignadoa'].queryset = Persona.objects.none()
                    data['form'] = incidencia
                    template = get_template('scrum_actividades/Formscrum.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            elif action == 'buscarpersonas':
                try:
                    q = request.GET['q'].upper().strip()
                    s = q.split(" ")
                    querybase = Persona.objects.filter(status=True, ).order_by('apellido1')
                    if len(s) == 1:
                        per = querybase.filter((Q(nombres__icontains=q) | Q(apellido1__icontains=q) | Q(cedula__icontains=q) | Q(apellido2__icontains=q) | Q(cedula__contains=q)),
                                               Q(status=True)).distinct()[:15]
                    elif len(s) == 2:
                        per = querybase.filter((Q(apellido1__contains=s[0]) & Q(apellido2__contains=s[1])) |
                                               (Q(nombres__icontains=s[0]) & Q(nombres__icontains=s[1])) |
                                               (Q(nombres__icontains=s[0]) & Q(apellido1__contains=s[1]))).filter(status=True).distinct()[:15]
                    else:
                        per = querybase.filter((Q(nombres__contains=s[0]) & Q(apellido1__contains=s[1]) & Q(apellido2__contains=s[2])) |
                                               (Q(nombres__contains=s[0]) & Q(nombres__contains=s[1]) & Q(apellido1__contains=s[2]))).filter(status=True).distinct()[:15]
                    data = {"result": "ok", "results": [{"id": x.id, "name": "{} - {}".format(x.cedula, x.nombre_completo())} for x in per]}
                    return JsonResponse(data)
                except Exception as ex:
                    pass

            elif action == 'editcategoria':
                try:
                    id = encrypt(request.GET['id'])
                    data['filtro'] = filtro = ProcesoSCRUM.objects.filter(pk=int(id), status=True).order_by('-id').first()
                    data['titulo'] = u'Editar categoría'
                    form = ProcesoSCRUMForm(model_to_dict(filtro))
                    if not mi_departamento and persona.usuario.is_superuser:
                        mi_departamento = Departamento.objects.get(id=93)
                    elif not mi_departamento:
                        raise NameError('No pertenece a ningún departamento')
                    form.fields['gestion_recepta'].queryset = mi_departamento.gestiones()
                    data['form'] = form
                    template = get_template('scrum_actividades/Formscrum.html')
                    return JsonResponse({'result': True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'editincidenciascrum':
                try:
                    data['title'] = u'Editar Incidencia de Actividad'
                    data['filtro'] = filtro = IncidenciaSCRUM.objects.get(pk=(request.GET['id']))
                    initial = model_to_dict(filtro)
                    form = IncidenciaSCRUMForm(initial=initial)
                    if filtro.asignadoa:
                        form.fields['asignadoa'].queryset = Persona.objects.filter(id=filtro.asignadoa.id)
                    else:
                        form.fields['asignadoa'].queryset = Persona.objects.none()
                    data['form'] = form
                    template = get_template('scrum_actividades/Formscrum.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'viewcategoria':
                try:
                    url_vars = f'&action={action}'
                    data['title'] = u'Procesos'
                    filtro=Q(status=True)
                    request.session['viewscrum'] = 2
                    if 's' in request.GET:
                        data['s'] = search = request.GET['s']
                        filtro = filtro & (Q(descripcion__icontains=search))
                        url_vars += f"&s={search}"
                    categoria = ProcesoSCRUM.objects.filter(filtro).order_by('descripcion').distinct()
                    paging = MiPaginador(categoria, 15)
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
                    paging.rangos_paginado(p)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['listado'] = page.object_list
                    data['url_vars'] = url_vars
                    return render(request, 'scrum_actividades/viewcategorias.html', data)
                except Exception as ex:
                    pass

            elif action == 'viewincidenciascrum':
                try:
                    url_vars = f'&action={action}'
                    data['title'] = u'Incidencia de Actividades'
                    incidencia = IncidenciaSCRUM.objects.filter(status=True)
                    request.session['viewactivo'] = 2
                    if 's' in request.GET:
                        data['s'] = search = request.GET['s']
                        incidencia = incidencia.filter(Q(descripcion__icontains=search)).distinct()
                        url_vars += f"&s={search}"
                    paging = MiPaginador(incidencia, 10)
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
                    paging.rangos_paginado(p)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['listado'] = page.object_list
                    data['url_vars'] = url_vars
                    return render(request, 'scrum_actividades/viewscrum.html', data)
                except Exception as ex:
                    pass

            elif action == 'listsubincidencia':
                try:
                    data['lista'] = IncidenciaSecundariasSCRUM.objects.filter(status=True, incidencia_id=request.GET['id'])
                    template = get_template('scrum_actividades/listsubincidencias.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'addactividadsecundarias':
                try:
                    data['title'] = u'Ver Actividades Secundaria'
                    data['fkincidencia'] = fkincidencia = request.GET.get('id')
                    form = CrearActvSecundariaForm()
                    form.fields['incidencia'].queryset = IncidenciaSCRUM.objects.filter(pk=fkincidencia)
                    form.fields['finicioactividad'].initial = str(datetime.now().date())
                    form.fields['asignadoa'].queryset = Persona.objects.none()
                    data['form'] = form
                    template = get_template("adm_actividades_scrum/modal/formactividad.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})

            # EQUIPOS
            elif action == 'equipos':
                try:
                    data['title'] = u'Equipos'
                    url_vars, filtro = f'&action={action}', Q(status=True)

                    if 's' in request.GET:
                        data['s'] = search = request.GET['s']
                        filtro = filtro & Q(nombre__icontains=search)
                        url_vars += f"&s={search}"

                    equipos = EquipoSCRUM.objects.filter(filtro)
                    paging = MiPaginador(equipos, 15)
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
                    paging.rangos_paginado(p)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['listado'] = page.object_list
                    data['url_vars'] = url_vars
                    request.session['viewscrum'] = 4
                    return render(request, 'scrum_actividades/viewequipos.html', data)
                except Exception as ex:
                    pass

            elif action == 'addequipo':
                try:
                    form = EquipoForm()
                    form.fields['lider'].queryset = Persona.objects.none()
                    form.fields['integrantes'].queryset = Persona.objects.none()
                    data['switchery']=True
                    data['form'] = form
                    template = get_template('scrum_actividades/modal/formequipo.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'editequipo':
                try:
                    data['id'] = id = encrypt_id(request.GET['id'])
                    equipo = EquipoSCRUM.objects.get(id=id)
                    form = EquipoForm(initial=model_to_dict(equipo))
                    form.fields['lider'].queryset = Persona.objects.filter(id=equipo.lider.id)
                    form.fields['integrantes'].queryset = Persona.objects.filter(id__in=equipo.integrantes.all().values_list('id', flat=True))
                    data['form'] = form
                    data['switchery'] = True
                    template = get_template('scrum_actividades/modal/formequipo.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'buscarresponsables':
                try:
                    resp = filtro_persona_select(request)
                    return HttpResponse(json.dumps({'status': True, 'results': resp}))
                except Exception as ex:
                    pass

            # REQUERIMIENTOS
            elif action == 'requerimientos':
                try:
                    data['title'] = u'Requerimientos'
                    url_vars, desde, hasta, prioridad, filtro, direccion, gestion, search = f'&action={action}', \
                                                                                            request.GET.get('desde', ''), \
                                                                                            request.GET.get('hasta', ''), \
                                                                                            request.GET.get('prioridad', ''), \
                                                                                            Q(status=True, asignadoa__isnull=True, asignadopor__isnull=True), \
                                                                                            request.GET.get('direccion', ''), \
                                                                                            request.GET.get('gestion', ''), \
                                                                                            request.GET.get('s', '')
                    if prioridad:
                        data['prioridad'] = int(prioridad)
                        filtro &= Q(prioridad=prioridad)
                        url_vars += "&prioridad{}".format(prioridad)

                    if desde:
                        data['desde'] = desde
                        filtro &= Q(requerimiento__fecha_creacion__gte=desde)
                        url_vars += '&desde=' + desde

                    if hasta:
                        data['hasta'] = hasta
                        url_vars += "&hasta={}".format(hasta)
                        filtro = filtro & Q(requerimiento__fecha_creacion__lte=hasta)

                    if gestion:
                        data['direccion'] = int(direccion)
                        data['gestion'] = int(gestion)
                        url_vars += "&direccion={}&gestion={}".format(direccion, gestion)
                        filtro = filtro & Q(requerimiento__gestion=gestion)

                    elif direccion:
                        data['direccion'] = int(direccion)
                        url_vars += "&direccion={}".format(direccion)
                        filtro = filtro & Q(requerimiento__gestion__departamento=direccion)

                    if search:
                        data['s'] = search
                        filtro = filtro & Q(titulo__icontains=search)
                        url_vars += f"&s={search}"

                    equipos = IncidenciaSCRUM.objects.filter(filtro).order_by('-id')
                    paging = MiPaginador(equipos, 15)
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
                    paging.rangos_paginado(p)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['listado'] = page.object_list
                    data['url_vars'] = url_vars
                    data['direcciones'] = Departamento.objects.filter(status=True, integrantes__isnull=False).distinct()
                    data['comboprioridad'] = PRIORIDAD_REQUERIMIENTO
                    data['comboestado'] = ESTADO_REQUERIMIENTO
                    request.session['viewscrum'] = 3
                    return render(request, 'scrum_actividades/viewrequerimientos.html', data)
                except Exception as ex:
                    pass

            elif action == 'listgestiones':
                try:
                    lista = []
                    id = int(request.GET['id'])
                    gestiones = SeccionDepartamento.objects.filter(status=True, departamento=id).distinct()
                    for s in gestiones:
                        text = str(s)
                        lista.append({'value': s.id, 'text': text})
                    return JsonResponse({'result': True, 'data': lista})
                except Exception as e:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            elif action == 'asignar':
                try:
                    form = AsignarActividadForm()
                    data['id'] = id = encrypt_id(request.GET['id'])
                    actividad = IncidenciaSCRUM.objects.get(id=id)
                    form.fields['finicioactividad'].initial = str(hoy)
                    form.fields['asignadoa'].queryset = Persona.objects.none()
                    if actividad.requerimiento.tiporequerimiento==1:
                        form.fields['categoria'].queryset = ProcesoSCRUM.objects.filter(direccion=actividad.requerimiento.gestion.departamento)
                    data['form'] = form
                    template = get_template('scrum_actividades/modal/formasignar.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'finalizar':
                try:
                    form = CrearComentarioForm()
                    data ['fkincidencia'] = data['id'] = id = encrypt_id(request.GET['id'])
                    form.fields['incidencia'].queryset = IncidenciaSCRUM.objects.filter(pk=id)
                    data['form'] = form
                    template = get_template("adm_actividades_scrum/modal/formactividad.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'listarequipos':
                try:
                    proceso = ProcesoSCRUM.objects.get(id=int(request.GET['id']))
                    return JsonResponse({'result': True, 'data': proceso.lista_integrantes()})
                except Exception as e:
                    return JsonResponse({"result": False, "mensaje": u"Error al obtener los datos."})

            elif action == 'detallerequerimiento':
                try:
                    data['id'] = id = encrypt_id(request.GET['id'])
                    data['requerimiento'] = IncidenciaSCRUM.objects.get(id=id).requerimiento
                    template = get_template('scrum_actividades/modal/detallerequerimiento.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            #ESTADISTICAS
            elif action == 'estadisticas':
                try:
                    data['title'] = u'Estadísticas'
                    data['accionbtn']= accionbtn = request.GET.get('f') if 'f' in request.GET else  request.GET.get('accionbtn','')
                    planificacion, desde, hasta, filtro, url_vars = request.GET.get('plan', ''), request.GET.get('desde', ''), request.GET.get('hasta', ''), (Q(status=True)), f'&action={action}'

                    data['planificacion'] = planificacion
                    data['desde'] = desde
                    data['hasta'] = hasta

                    if planificacion:
                        data['planificacion'] = int(planificacion)
                        filtro = filtro & Q(requerimiento__periodo_id=planificacion)
                        url_vars += f"&plan={planificacion}"

                    if desde and hasta:
                        filtro = filtro & (Q(finicioactividad__gte=desde, finicioactividad__lte=hasta))
                        url_vars += f"&desde={desde}&hasta={hasta}"

                    incdencias = IncidenciaSCRUM.objects.filter(filtro)
                    data['equipos'] = equipos = EquipoSCRUM.objects.filter(status=True)
                    request.session['viewscrum'] = 5

                    request.session['subviewactivo'] = 1
                    if accionbtn == 'cifras':
                        url_vars += '&f=' + accionbtn
                        request.session['subviewactivo'] = 2
                        desde, hasta = request.GET.get('desde', None), request.GET.get('hasta', None)
                        if desde:
                            data['desde'] = desde
                            filtro = filtro & (Q(finicioactividad__gte=desde))
                            url_vars += '&desde=' + desde
                        if hasta:
                            data['hasta'] = hasta
                            filtro = filtro & Q(ffinactividad__lte=hasta)
                            url_vars += "&hasta={}".format(hasta)
                            data['url_vars'] = url_vars

                        incdencias = incdencias.filter(filtro)

                        # lista.append({'value': ir.id, 'text': ir.nombre_completo_minus()})
                        #
                        # recuentos = [
                        #     {'nombre': 'ActividadUno', 'count': count_actividad_uno},
                        #     {'nombre': 'ActividadDos', 'count': count_actividad_dos},
                        # ]
                        return render(request, 'scrum_actividades/viewcifras.html', data)

                    data['total_incidencias'] = incdencias.count()
                    data['total_sinasignar'] = listpendientes = incdencias.filter(asignadoa__isnull=True).distinct()
                    data['total_pendientes'] = incdencias.filter(estado=1,asignadoa__isnull=False).distinct()
                    data['total_finalizadas'] = listfinalizadas = incdencias.filter(estado=3,asignadoa__isnull=False).distinct()
                    data['total_enproceso'] = listenproceso = incdencias.filter(estado=2,asignadoa__isnull=False).distinct()

                    actividad_con_dias = listfinalizadas.filter(ffinactividad__isnull=False).annotate(duracion=ExpressionWrapper(
                        F('ffinactividad') - F('finicioactividad'), output_field=fields.DurationField())).order_by(
                        'duracion')
                    data['promedio_min_actividad'] = actividad_con_dias.first()
                    data['promedio_max_actividad'] = actividad_con_dias.last()
                    data['planificaciones'] = PlanificacionAutomatiza.objects.filter(status=True).order_by('-id')
                    data['url_vars'] = url_vars
                    return render(request, 'scrum_actividades/viewestadisticas.html', data)
                except Exception as ex:
                    pass

            # PLANIFICACIONES
            elif action == 'planificaciones':
                try:
                    data['title'] = u'Planificaciones'
                    search, url_vars, filtro = request.GET.get('s', ''), f'&action={action}', Q(status=True)

                    if search:
                        data['s'] = search
                        filtro = filtro & Q(nombre__icontains=search)
                        url_vars += f"&s={search}"

                    planificaciones = PlanificacionAutomatiza.objects.filter(filtro).order_by('-id')

                    paging = MiPaginador(planificaciones, 15)
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
                    paging.rangos_paginado(p)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['planificaciones'] = page.object_list
                    data['url_vars'] = url_vars
                    request.session['viewscrum'] = 6
                    return render(request, 'scrum_actividades/viewplanificaciones.html', data)
                except Exception as ex:
                    pass

            elif action == 'addplanificacion':
                try:
                    form = PlanificacionForm()
                    data['switchery'] = True
                    data['form'] = form
                    template = get_template('scrum_actividades/modal/formplanificacion.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'editplanificacion':
                try:
                    data['id'] = id = int(encrypt(request.GET['id']))
                    planificacion = PlanificacionAutomatiza.objects.get(pk=id)

                    form = PlanificacionForm(initial=model_to_dict(planificacion))

                    data['switchery'] = True
                    data['form'] = form
                    template = get_template('scrum_actividades/modal/formplanificacion.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            # REQUERIMIENTOS
            elif action == 'requerimientosplan':
                try:
                    data['plan'] = plan = PlanificacionAutomatiza.objects.get(pk=int(encrypt(request.GET['idp'])))
                    data['title'] = f'Requerimientos: {plan.nombre}'

                    search, prioridad, url_vars, filtro = request.GET.get('s', ''), request.GET.get('prio', ''), f'&action={action}&idp={request.GET["idp"]}', Q(status=True, periodo=plan)

                    if search:
                        data['s'] = search
                        filtro = filtro & Q(procedimiento__icontains=search)
                        url_vars += f"&s={search}"

                    if prioridad:
                        data['prioridad'] = int(prioridad)
                        filtro = filtro & (Q(prioridad=int(prioridad)))
                        url_vars += f'&prio={prioridad}'

                    requerimientos = RequerimientoPlanificacionAutomatiza.objects.filter(filtro).order_by('-id')

                    paging = MiPaginador(requerimientos, 15)
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
                    paging.rangos_paginado(p)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['requerimientos'] = page.object_list
                    data['total'] = len(requerimientos.values_list('id'))
                    data['prioridades'] = PRIORIDAD
                    data['url_vars'] = url_vars
                    request.session['viewscrum'] = 6
                    return render(request, 'scrum_actividades/viewrequerimientosplan.html', data)
                except Exception as ex:
                    pass

            elif action == 'addrequerimiento':
                try:
                    data['idp'] = request.GET['id']

                    form = RequerimientoForm()

                    req = RequerimientoPlanificacionAutomatiza.objects.filter(status=True, periodo_id=int(encrypt(request.GET['id']))).order_by('orden').last()
                    cantidad = req.orden if req else 0
                    cantidad += 1

                    form.fields['responsable'].queryset = Persona.objects.none()
                    form.fields['gestion'].queryset = SeccionDepartamento.objects.none()
                    data['form'] = form
                    data['seccionado'] = True
                    data['cantidad'] = cantidad

                    template = get_template('scrum_actividades/modal/formrequerimiento.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'editrequerimiento':
                try:
                    data['filtro'] = requerimiento = RequerimientoPlanificacionAutomatiza.objects.get(pk=int(encrypt(request.GET['id'])))
                    data['idp'] = encrypt(requerimiento.periodo.id)

                    form = RequerimientoForm(initial=model_to_dict(requerimiento))
                    form.fields['responsable'].queryset = Persona.objects.filter(id=requerimiento.responsable.id)
                    form.fields['gestion'].queryset = SeccionDepartamento.objects.filter(departamento_id=requerimiento.gestion.departamento.id)
                    data['form'] = form
                    data['seccionado'] = True

                    template = get_template('scrum_actividades/modal/formrequerimiento.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'reporteexcel':
                try:
                    pattern = re.compile('<.*?>')

                    plan = PlanificacionAutomatiza.objects.get(pk=int(encrypt(request.GET['idp'])))
                    search, prioridad, filtro = request.GET.get('s', ''), request.GET.get('prio', ''), Q(status=True, periodo=plan)
                    output_folder = os.path.join(os.path.join(SITE_STORAGE, 'media', 'postgrado'))

                    nombrearchivo = "REQUERIMIENTOS_PLANIFICACION_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".xlsx"

                    # Crea un nuevo archivo de excel y le agrega una hoja
                    workbook = xlsxwriter.Workbook(output_folder + '/' + nombrearchivo)
                    ws = workbook.add_worksheet("Listado")

                    fcabeceracolumna = workbook.add_format(FORMATOS_CELDAS_EXCEL["cabeceracolumna"])
                    fceldageneral = workbook.add_format(FORMATOS_CELDAS_EXCEL["celdageneral"])
                    fceldageneralcent = workbook.add_format(FORMATOS_CELDAS_EXCEL["celdageneralcent"])
                    ftitulo1 = workbook.add_format(FORMATOS_CELDAS_EXCEL["titulo1"])
                    fceldafechaDMA = workbook.add_format(FORMATOS_CELDAS_EXCEL["celdafechaDMA"])

                    ws.merge_range(0, 0, 0, 5, 'UNIVERSIDAD ESTATAL DE MILAGRO', ftitulo1)
                    ws.merge_range(1, 0, 1, 5, 'LISTADO GENERAL DE REQUERIMIENTOS', ftitulo1)
                    ws.merge_range(2, 0, 2, 5, 'PLANIFICACIÓN: ' + plan.nombre, ftitulo1)

                    columns = [
                        (u"N°", 3),
                        (u"GESTIÓN", 40),
                        (u"PRIORIDAD", 13),
                        (u"RESPONSABLE", 33),
                        (u"DETALLE", 43),
                        (u"PROCEDIMIENTO", 47)
                    ]

                    row_num = 4
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], fcabeceracolumna)
                        ws.set_column(col_num, col_num, columns[col_num][1])

                    row_num = 5

                    if search:
                        filtro = filtro & Q(procedimiento__icontains=search)

                    if prioridad:
                        filtro = filtro & (Q(prioridad=int(prioridad)))

                    requerimientos = RequerimientoPlanificacionAutomatiza.objects.filter(filtro).order_by('-id')
                    c = 1
                    for requerimiento in requerimientos:
                        ws.write(row_num, 0, c, fceldageneral)
                        ws.write(row_num, 1, requerimiento.gestion.departamento.nombre, fceldageneral)
                        ws.write(row_num, 2, requerimiento.get_prioridad_display(), fceldageneralcent)
                        ws.write(row_num, 3, requerimiento.responsable.nombre_completo_minus(), fceldageneral)
                        ws.write(row_num, 4, re.sub(pattern, '', html.unescape(requerimiento.detalle)), fceldageneral)
                        ws.write(row_num, 5, re.sub(pattern, '', html.unescape(requerimiento.procedimiento)), fceldageneral)

                        row_num += 1
                        c += 1

                    workbook.close()

                    ruta = "media/postgrado/" + nombrearchivo
                    return JsonResponse({'result': 'ok', 'archivo': ruta})
                except Exception as ex:
                    msg = ex.__str__()
                    return JsonResponse({"result": "bad", "titulo": "Error", "mensaje": u"Error al generar el reporte. [%s]" % msg, "showSwal": "True", "swalType": "error"})

            elif action == 'buscarpersonasreq':
                try:
                    resp = filtro_persona_select(request)
                    return HttpResponse(json.dumps({'status': True, 'results': resp}))
                except Exception as ex:
                    pass

            # SECCIONDEPARTAMENTO
            elif action == 'gestiones':
                try:
                    if mi_departamento:
                        iddepartamento = mi_departamento.id
                    elif persona.usuario.is_superuser:
                        iddepartamento = 93
                    else:
                        raise NameError('No pertenece a ningún departamento')
                    data['departamento'] = departamento = Departamento.objects.get(pk=iddepartamento)
                    data['title'] = f'Gestiones'

                    search, url_vars, filtro = request.GET.get('s', ''), \
                                               f'&action={action}', Q(status=True, departamento=departamento)

                    if search:
                        data['s'] = search
                        filtro = filtro & Q(descripcion__icontains=search)
                        url_vars += f"&s={search}"

                    listado = SeccionDepartamento.objects.filter(filtro).order_by('-id')

                    paging = MiPaginador(listado, 15)
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
                    paging.rangos_paginado(p)
                    data['paging'] = paging
                    data['rangospaging'] = paging.rangos_paginado(p)
                    data['page'] = page
                    data['listado'] = page.object_list
                    data['url_vars'] = url_vars
                    request.session['viewscrum'] = 7
                    return render(request, 'scrum_actividades/viewgestiones.html', data)
                except Exception as ex:
                    messages.warning(request, f'!Advertencia!: {ex}')

            elif action == 'addencuesta':
                try:
                    data['id'] = id = encrypt_id(request.GET['id'])
                    eSeccion = SeccionDepartamento.objects.get(id=id)
                    content_type = ContentType.objects.get_for_model(eSeccion)
                    encuesta = EncuestaProceso.objects.filter(object_id=eSeccion.id, content_type=content_type, status=True).first()
                    if encuesta:
                        form = EncuestaPreguntaForm(initial=model_to_dict(encuesta))
                        data['preguntas'] = PreguntaEncuestaProceso.objects.filter(status=True, encuesta=encuesta)
                    else:
                        form = EncuestaPreguntaForm()
                    data['form'] = form
                    data['switchery'] = True
                    template = get_template('formencuesta.html')
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    messages.error(request, f'{ex}')
            return HttpResponseRedirect(request.path)
        else:
            try:
                search, proceso, prioridad, estado, app, desde, hasta, equipo, filtro = request.GET.get('s', ''), \
                                                                                  request.GET.get('proceso', ''), \
                                                                                  request.GET.get('prioridad', ''), \
                                                                                  request.GET.get('estado', ''), \
                                                                                  request.GET.get('app', ''), \
                                                                                  request.GET.get('desde', ''), \
                                                                                  request.GET.get('hasta', ''), \
                                                                                  request.GET.get('equipo', ''), \
                                                                                  Q(status=True, asignadopor__isnull=False, asignadoa__isnull=False)
                url_vars = ""
                data['title'] = u'Incidencia de actividades'
                data['combocategorias'] = ProcesoSCRUM.objects.values('id', 'descripcion').filter(status=True)
                data['comboprioridad'] = PRIORIDAD_REQUERIMIENTO
                data['comboestado'] = ESTADO_REQUERIMIENTO
                data['comboapp'] = APP_LABEL
                # filtro= Q(asignadoa__persona__status=True)

                request.session['viewscrum'] = 1
                if search:
                    url_vars += "&s{}".format(search)
                    data['s'] = search.upper()
                    q = search.split(" ")
                    if len(q) == 1:
                        filtro &= (Q(asignadoa__nombres__icontains=search) | Q(asignadoa__apellido1__icontains=search) |
                                   Q(asignadoa__cedula__icontains=search) | Q(asignadoa__apellido2__icontains=search))

                    elif len(q) == 2:
                        filtro &= ((Q(asignadoa__apellido1__icontains=q[0]) & Q(asignadoa__apellido2__icontains=q[1])) |
                                   (Q(asignadoa__nombres__icontains=q[0]) & Q(asignadoa__nombres__icontains=q[1])) |
                                   (Q(asignadoa__nombres__icontains=q[0]) & Q(asignadoa__apellido1__contains=q[1])))

                if proceso:
                    data['proceso'] = int(proceso)
                    filtro = filtro & Q(categoria__id=proceso)
                    url_vars += "&proceso={}".format(proceso)

                if prioridad:
                    data['prioridad'] = int(prioridad)
                    filtro &= Q(prioridad=prioridad)
                    url_vars += "&prioridad={}".format(prioridad)

                if estado:
                    data['estado'] = int(estado)
                    filtro &= Q(estado=estado)
                    url_vars += "&estado={}".format(estado)

                if app:
                    data['app'] = int(app)
                    filtro &= Q(app=app)
                    url_vars += "&app={}".format(app)

                if desde:
                    data['desde'] = desde
                    filtro = filtro & Q(finicioactividad__gte=desde)
                    url_vars += '&desde=' + desde

                if hasta:
                    data['hasta'] = hasta
                    url_vars += "&hasta={}".format(hasta)
                    filtro = filtro & Q(ffinactividad__lte=hasta)

                if equipo:
                    data['equipo'] = equipo = int(equipo)
                    url_vars += "&equipo={}".format(equipo)
                    equipo = EquipoSCRUM.objects.get(id=equipo)
                    integrantes = list(equipo.integrantes.all().values_list('id',flat=True))
                    integrantes.append(equipo.lider.id)
                    filtro = filtro & Q(asignadoa_id__in=integrantes)

                incidencia = IncidenciaSCRUM.objects.filter(filtro).order_by('-finicioactividad')
                paging = MiPaginador(incidencia, 10)
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
                paging.rangos_paginado(p)
                data['paging'] = paging
                data['equipos'] = EquipoSCRUM.objects.filter(status=True)
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data['listado'] = page.object_list
                data['url_vars'] = url_vars
                return render(request, 'scrum_actividades/viewscrum.html', data)
            except Exception as ex:
                pass
