# -*- coding: UTF-8 -*-
import json
import sys
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.context import Context
from django.template.loader import get_template
from decorators import last_access, secure_module
from settings import ESTADO_GESTACION, NOTA_ESTADO_APROBADO
from sga.commonviews import adduserdata
from sga.forms import InscribirTematicaForm, ComplexivoSubirPropuestaForm, ComplexivoEditarArchivoPropuestaForm, \
    CorrecionArchivoFinalSustentacionForm
from sga.funciones import log, generar_nombre, null_to_numeric
from sga.funciones_templatepdf import actatribunalcalificacion
from sga.funcionesxhtml2pdf import conviert_html_to_pdf
from sga.models import MatriculaTitulacion, AlternativaTitulacion, \
    ComplexivoTematica, ComplexivoGrupoTematica, ComplexivoDetalleGrupo, \
    ArchivoTitulacion, TIPO_ARCHIVO_COMPLEXIVO_PROPUESTA, ComplexivoPropuestaPractica, \
    ComplexivoPropuestaPracticaArchivo, ComplexivoExamenDetalle, ComplexivoAcompanamiento, CargoInstitucion, \
    MESES_CHOICES, ComplexivoExamen, TIPO_CELULAR, RecordAcademico, AsignaturaMalla, ParticipantesMatrices, ModuloMalla, \
    PracticasPreprofesionalesInscripcion, RequisitoSustentar, GrupoTitulacion, ComplexivoTematicaGrupoCupo
from sga.templatetags.sga_extras import encrypt


@login_required(redirect_field_name='ret', login_url='/loginsga')
@transaction.atomic()
@secure_module
@last_access
def view(request):
    data = {}
    adduserdata(request, data)
    persona = request.session['persona']
    perfilprincipal = request.session['perfilprincipal']
    data['inscripcion'] = inscripcion = perfilprincipal.inscripcion
    carrera = persona.mis_carreras_inscripcion()


    hoy = datetime.now().date()
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'inscribir':
            try:
                tematica= ComplexivoTematica.objects.get(pk = request.POST['tematica'])
                idgrupo = int(request.POST['id_grupo'])

                if tematica.complexivotematicagrupocupo_set.values("id").filter(status=True, enuso=True, pk=idgrupo).exists():
                    return JsonResponse({'result': 'bad', 'mensaje': u"El grupo ya ha sido seleccionado por otro usuario"})

                if tematica.tiene_cupo():
                    listado = request.POST['otrosintegrantes']
                    participantes = MatriculaTitulacion.objects.filter(pk__in=[int(x) for x in listado.split(',')], status=True)
                    if not ComplexivoDetalleGrupo.objects.values('id').filter(Q(matricula__in = participantes.values_list('id')), Q(status=True), (Q(estado=1) | Q(estado=4))).exists():
                        if participantes.values('id').count() > tematica.cupos_restantes():
                            return JsonResponse({'result': 'bad', 'mensaje':u"La cantidad de integrantes supera el cupo actual."})
                        grupo = ComplexivoGrupoTematica(tematica_id=request.POST['tematica'],
                                                        grupocupo_id=idgrupo)
                        grupo.save(request)

                        ComplexivoTematicaGrupoCupo.objects.filter(pk=idgrupo).update(enuso=True)


                        log(u"Crea grupo %s de propuesta práctica con línea de investigación: %s" % (grupo.id, grupo.tematica), request, "add")
                        for participante in participantes:
                            detalle = ComplexivoDetalleGrupo(grupo=grupo, matricula = participante)
                            if participante.inscripcion.persona != persona:
                                detalle.estado = 4
                            detalle.fechainscripcion = datetime.now()
                            detalle.save(request)
                            log(u"Añade integrante %s a grupo [%s] con línae de investigación: %s" % (detalle.matricula.inscripcion,grupo.id,grupo.tematica), request, "add")
                        return JsonResponse({'result': 'ok'})
                    else:
                        return JsonResponse({'result': 'bad', 'mensaje': u"Ya se encuestran registrados(activo o por confirmar) en grupo de tematica"})
                return JsonResponse({'result': 'bad', 'mensaje': u"Error al aceptar el tema"})

            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result':'bad', 'mensaje': u"Error al aceptar el tema"})

        if action == 'confirmar':
            try:
                detalle = ComplexivoDetalleGrupo.objects.get(status=True, matricula_id=request.POST['id'],grupo__activo=True)
                if request.POST['op']=='t':
                    detalle.estado = 1
                else:
                    detalle.estado = 2
                    detalle.status = False
                detalle.save(request)
                log(u"%s Confirma su participancion en grupo [%s] con línea de investigación: %s" % (detalle.matricula.inscripcion,detalle.grupo.id, detalle.grupo.tematica), request, "confirmar")
                return JsonResponse({'result':'ok'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad'})

        elif action == 'deltematica':
            try:
                grupo = ComplexivoGrupoTematica.objects.get(pk=int(request.POST['id']))
                matricula = MatriculaTitulacion.objects.filter(inscripcion=inscripcion, estado=1)[0]
                if ComplexivoDetalleGrupo.objects.values('id').filter(status=True, grupo=grupo, matricula=matricula).exists():
                    detalle = ComplexivoDetalleGrupo.objects.get(status=True, grupo=grupo, matricula=matricula)
                    detalle.status = False
                    detalle.estado = 2
                    detalle.save(request)
                    log(u"%s se retira del grupo [%s] con línea de investigación: %s" % (detalle.matricula.inscripcion,grupo.id, detalle.grupo.tematica), request, "delete")
                    grupo.eliminar_participantespendientes()

                if not grupo.tiene_participantes():
                    grupo.status = False
                    grupo.save(request)
                    log(u"Se elimina grupo %s con línea de investigación %s por no tener integrantes " % (grupo.id,grupo.tematica), request, "delete")
                return JsonResponse({'result': 'ok'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad'})

        elif action == 'addparticipante':
            try:
                lista = json.loads(request.POST['lista'])
                lista = map(int, lista)

                participantes = MatriculaTitulacion.objects.filter(pk__in=lista)
                for participante in participantes:
                    if not ComplexivoDetalleGrupo.objects.values('id').filter(status=True, matricula=participante).exists():
                        detalle = ComplexivoDetalleGrupo()
                        detalle.grupo = ComplexivoGrupoTematica.objects.get(pk=request.POST['id'])
                        detalle.matricula = participante
                        detalle.estado = 4
                        detalle.fechainscripcion = datetime.now()
                        detalle.save(request)
                        log(u"Añade integrante %s a grupo [%s] con línea de investigación: %s" % (detalle.matricula.inscripcion, detalle.grupo.id, detalle.grupo.tematica), request, "add")
                return JsonResponse({'result': 'ok'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', 'mensaje': u'Ocurrio un problema al añadir integrante'})

        elif action == 'adddoc':
            try:
                f = ComplexivoSubirPropuestaForm(request.POST, request.FILES)
                newfilep = None
                newfilex = None
                if 'propuesta' in request.FILES:
                    newfilep = request.FILES['propuesta']
                    if newfilep:
                        if newfilep.size > 22582912:
                            return JsonResponse({"result": "bad", "mensaje": u"Error, archivo mayor a 12 Mb."})
                        elif newfilep.size <= 0:
                            return JsonResponse({"result": "bad", "mensaje": u"Error, el archivo Propuesta Práctica esta vacío."})
                        else:
                            newfilesd = newfilep._name
                            ext = newfilesd[newfilesd.rfind("."):]
                            if ext == '.doc':
                                newfilep._name = generar_nombre("propuesta_", newfilep._name)
                            elif ext == '.docx':
                                newfilep._name = generar_nombre("propuesta_", newfilep._name)
                            else:
                                return JsonResponse({"result": "bad", "mensaje": u"Error, archivo de Propuesta Práctica solo en .doc, docx."})
                if 'extracto' in request.FILES:
                    newfilex = request.FILES['extracto']
                    if newfilex:
                        if newfilex.size > 22582912:
                            return JsonResponse({"result": "bad", "mensaje": u"Error, archivo mayor a 12 Mb."})
                        elif newfilex.size <= 0:
                            return JsonResponse({"result": "bad", "mensaje": u"Error, el archivo Propuesta Práctica (Desde introducción hasta conclusión) esta vacío."})
                        else:
                            newfilesd = newfilex._name
                            ext = newfilesd[newfilesd.rfind("."):]
                            if ext == '.doc':
                                newfilex._name = generar_nombre("extracto_", newfilex._name)
                            elif ext == '.docx':
                                newfilex._name = generar_nombre("extracto_", newfilex._name)
                            else:
                                return JsonResponse({"result": "bad", "mensaje": u"Error, archivo Propuesta Práctica Antiplagio solo en .doc, docx."})
                if newfilep and newfilex:
                    grupo = ComplexivoGrupoTematica.objects.get(pk=int(request.POST['id']))
                    if f.is_valid():
                        cabecera = ComplexivoPropuestaPractica(grupo=grupo, fecharevision=datetime.now())
                        cabecera.save(request)
                        if newfilep:
                            propuesta = ComplexivoPropuestaPracticaArchivo(propuesta=cabecera, tipo=1, archivo=newfilep, fecha=datetime.now())
                            propuesta.save(request)
                        if newfilex:
                            propuesta = ComplexivoPropuestaPracticaArchivo(propuesta=cabecera, tipo=2, archivo=newfilex,fecha=datetime.now())
                            propuesta.save(request)
                        log(u"Añade archivo propuesta version urkund a  grupo [%s] con línea de investigación: %s" % (grupo.id, grupo.tematica), request, "add")
                        return JsonResponse({'result': 'ok'})
                    else:
                        return JsonResponse({'result': 'bad', 'mensaje': u'Error, al guardar los archivos'})
                else:
                    return JsonResponse({'result': 'bad', 'mensaje': u'Ingrese almenos un archivo'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', 'mensaje': u'Ocurrio un problema al guardar archivos'})

        elif action == 'editdoc':
            try:
                f= ComplexivoEditarArchivoPropuestaForm(request.POST, request.FILES)
                if f.is_valid():
                    archivo = ComplexivoPropuestaPracticaArchivo.objects.get(pk=request.POST['id'])
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        if archivo.tipo==1:
                            nombre="propuesta"
                        else:
                            nombre="propuesta version urkund"
                        newfile._name = generar_nombre(nombre, newfile._name)
                        archivo.archivo = newfile
                        archivo.fecha = datetime.now()
                        archivo.save(request)
                        log(u"Edita archivo %s del grupo [%s] con línea de investigación: %s" % (nombre,archivo.propuesta.grupo.id, archivo.propuesta.grupo.tematica), request, "edit")
                    return JsonResponse({'result': 'ok'})
                else:
                    return JsonResponse({'result': 'bad', 'mensaje': u'Revise la extension del archivos'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', 'mensaje': u'Ocurrió un problema al guardar archivos'})

        elif action == 'deldoc':
            # try:
            #     propuesta = ComplexivoPropuestaPractica.objects.get(pk=request.POST['id'])
            #     archivos = ComplexivoPropuestaPracticaArchivo.objects.filter(status=True,propuesta=propuesta,propuesta__estado=1)
            #     for archivo in archivos:
            #         archivo.delete()
            #         log(u"Elimina archivo %s de propuesta [%s] con grupo: %s" % (archivo.get_tipo_display(),propuesta.id,propuesta.grupo.id),request,"delete")
            #     if  not propuesta.tiene_archivos():
            #         propuesta.delete()
            #         log(u"Elimina propuesta %s del grupo [%s] con línea de investigación: %s"  % (propuesta.id, propuesta.grupo.id,propuesta.grupo.tematica),request,"delete")
            #     return JsonResponse({'result': 'ok'})
            # except Exception as ex:
            #     transaction.set_rollback(True)
            #     return JsonResponse({'result': 'bad'})
            try:
                with transaction.atomic():
                    propuesta = ComplexivoPropuestaPractica.objects.get(pk=request.POST['id'])
                    archivos = ComplexivoPropuestaPracticaArchivo.objects.filter(status=True,propuesta=propuesta,propuesta__estado=1)
                    for archivo in archivos:
                        archivo.delete()
                        log(u"Elimina archivo %s de propuesta [%s] con grupo: %s" % (archivo.get_tipo_display(),propuesta.id,propuesta.grupo.id),request,"delete")
                    if  not propuesta.tiene_archivos():
                        propuesta.delete()
                        log(u"Elimina propuesta %s del grupo [%s] con línea de investigación: %s" % (propuesta.id, propuesta.grupo.id,propuesta.grupo.tematica),request,"delete")

                    res_json = {"error": False}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'error': True, "message": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'actaacompanamiento_pdf':
            try:
                if 'id' in request.POST:
                    data['grupo'] = grupo = ComplexivoGrupoTematica.objects.get(pk=int(request.POST['id']))
                    data['acompanamientos'] = grupo.complexivoacompanamiento_set.filter(status=True, grupo=grupo)
                    # data['integrantes'] = grupo.complexivodetallegrupo_set.filter(Q(status=True), (Q(matricula__estado=1)|Q(matricula__estado=10))).exclude(matricula__complexivoexamendetalle__estado=2).order_by('matricula__inscripcion__persona__apellido1', 'matricula__inscripcion__persona__apellido2')
                    data['integrantes'] = integrantes = grupo.complexivodetallegrupo_set.filter(status=True).order_by('matricula__inscripcion__persona__apellido1', 'matricula__inscripcion__persona__apellido2')
                    # data['integrantes'] = grupo.complexivodetallegrupo_set.filter(Q(status=True), (Q(matricula__estado=1)|Q(matricula__estado=10))).filter(matricula__complexivoexamendetalle__estado__in=[1,3]).order_by('matricula__inscripcion__persona__apellido1', 'matricula__inscripcion__persona__apellido2')
                    valida = 0
                    for listaintegrantes in integrantes:
                        if listaintegrantes.matricula.examen_complexivo():
                            if listaintegrantes.matricula.examen_complexivo().estado == 2 and listaintegrantes.matricula.examen_complexivo().matricula.estado == 9:
                                valida += 1
                    if integrantes.count() <= valida:
                        valida = 1
                    data['valida'] = valida
                    data['facultad'] = grupo.tematica.carrera.coordinaciones()[0]
                    fecha = datetime.today().date()
                    data['fecha'] = str(fecha.day) + " de " + str(MESES_CHOICES[fecha.month - 1][1]).lower() + " del " + str(fecha.year)
                    data['secretariageneral'] = CargoInstitucion.objects.get(pk=1).persona.nombre_completo_inverso() if CargoInstitucion.objects.get(pk=1) else None
                    return conviert_html_to_pdf('pro_complexivotematica/actaacompanamiento_pdf.html',
                                                {
                                                    'pagesize': 'A4',
                                                    'data': data,
                                                }
                                                )
            except Exception as ex:
                pass

        elif action == 'pdfactatribunalcalificacionesnew':
            try:
                iddetallegrupo = request.POST['id']
                actatribunal = actatribunalcalificacion(iddetallegrupo)
                return actatribunal
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'addarchivofinaltitulacion':
            try:
                form = CorrecionArchivoFinalSustentacionForm(request.POST, request.FILES)
                if 'archivo' in request.FILES:
                    d = request.FILES['archivo']
                    newfile = d._name
                    ext = newfile[newfile.rfind("."):]
                    if ext == '.doc' or ext == '.docx':
                        a = 1
                    else:
                        return JsonResponse({"result": "bad", "mensaje": u"Error, solo archivos .doc, .docx."})
                    if d.size > 16728640:
                        return JsonResponse({"result": "bad", "mensaje": u"Error, archivo mayor a 15 Mb."})
                if form.is_valid():
                    complpexivogrupo = ComplexivoGrupoTematica.objects.get(pk=int(encrypt(request.POST['id'])))
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("archivofinal", newfile._name)
                        complpexivogrupo.archivofinalgrupo = newfile
                        complpexivogrupo.fechaarchivofinalgrupo = datetime.now().date()
                        complpexivogrupo.estadoarchivofinalgrupo = 1
                    complpexivogrupo.save(request)
                    log(u"Cargó archivo final de titulación el día %s " % (complpexivogrupo.fechaarchivofinalgrupo), request, "add")
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": "Error al guardar los datos."})

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'elegirtematica':
                try:
                    matricula = MatriculaTitulacion.objects.filter(inscripcion=inscripcion, estado=1)[0]
                    data['title'] = u"Elegir línea de investigación para trabajo titulación"
                    data['periodotitulacion'] = matricula.alternativa.grupotitulacion.periodogrupo.id
                    if not ComplexivoDetalleGrupo.objects.values('id').filter(status=True, matricula=matricula).exists():
                        lista = []
                        for tematica in ComplexivoTematica.objects.filter(status=True, periodo = matricula.alternativa.grupotitulacion.periodogrupo, carrera= matricula.inscripcion.carrera):
                            if tematica.tiene_cupo():
                                lista.append(tematica.id)
                        data['tematicas'] = ComplexivoTematica.objects.filter(pk__in=lista)
                        return render(request, "alu_complexivocurso/listatematicas.html", data)
                    else:
                        pass
                except Exception as ex:
                    pass

            elif action == 'addarchivofinaltitulacion':
                try:
                    data['title'] = u"Evidencias del programa analítico"
                    data['grupo'] = ComplexivoGrupoTematica.objects.get(pk=int(encrypt(request.GET['id_grupo'])))
                    data['form'] = CorrecionArchivoFinalSustentacionForm()
                    return render(request, 'alu_complexivocurso/addarchivofinaltitulacion.html', data)
                except Exception as ex:
                    pass

            elif action == 'addparticipante':
                try:
                    data['grupo']=grupo = ComplexivoGrupoTematica.objects.get(pk=int(request.GET['id']))
                    if grupo.tiene_cupo():
                        data['tematica'] = grupo.tematica
                        restantes = grupo.cupo_restante()
                        template = get_template("alu_complexivocurso/addparticipante.html")
                        json_content = template.render(data)
                        return JsonResponse({"result": "ok", 'data': json_content, 'maxintegrante' :restantes})
                    else:
                        return JsonResponse({"result": "bad", "mensaje": u"Número de participantes completos."})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            elif action == 'inscribir':
                try:
                    data['matricula'] = matricula = MatriculaTitulacion.objects.filter(inscripcion=inscripcion, estado=1)[0]
                    data['title'] = u"Elegir Integrante"
                    data['tematica'] = tematica=ComplexivoTematica.objects.get(pk=request.GET['id'])
                    data['form'] = InscribirTematicaForm(initial={
                        'tematica' : tematica.tematica
                    })
                    gcupos = tematica.complexivotematicagrupocupo_set.filter(status=True, enuso=False).order_by('numerogrupo')
                    grupocupos = [[g.id, g.cupoasignado, 'GRUPO # ' + str(g.numerogrupo) + ' - [ CUPOS: ' + str(g.cupoasignado) + ' ]'] for g in gcupos]
                    data['grupocupo'] = grupocupos
                    return render(request, "alu_complexivocurso/inscribirtematica.html", data)
                except Exception as ex:
                    pass
            elif action == 'busqueda':
                try:
                    matriculado = MatriculaTitulacion.objects.filter(inscripcion=inscripcion, estado=1)[0]
                    inscritos = ComplexivoDetalleGrupo.objects.values_list('matricula__inscripcion').filter(status=True, matricula__alternativa__tipotitulacion=matriculado.alternativa.tipotitulacion)
                    q = request.GET['q'].upper().strip()
                    s = q.split(" ")
                    if s.__len__() == 2:
                        # matri = MatriculaTitulacion.objects.filter(inscripcion__persona__apellido1__icontains=s[0],inscripcion__persona__apellido2__icontains=s[1],inscripcion__carrera=inscripcion.carrera, estado=1, alternativa__tipotitulacion=matriculado.alternativa.tipotitulacion).exclude(inscripcion__id__in=inscritos).exclude(inscripcion=inscripcion).distinct()[:20]
                        matri = MatriculaTitulacion.objects.filter(inscripcion__persona__apellido1__icontains=s[0],inscripcion__persona__apellido2__icontains=s[1],inscripcion__carrera=inscripcion.carrera, estado=1, alternativa__tipotitulacion=matriculado.alternativa.tipotitulacion).exclude(inscripcion=inscripcion).distinct()[:20]
                    else:
                        # matri = MatriculaTitulacion.objects.filter(Q(inscripcion__persona__nombres__contains=s[0]) | Q(inscripcion__persona__apellido1__contains=s[0]) | Q(inscripcion__persona__apellido2__contains=s[0]) | Q(inscripcion__persona__cedula__contains=s[0])).filter(inscripcion__carrera=inscripcion.carrera, estado=1, alternativa__tipotitulacion=matriculado.alternativa.tipotitulacion).exclude(inscripcion__id__in=inscritos).exclude(inscripcion=inscripcion).distinct()[:20]
                        matri = MatriculaTitulacion.objects.filter(Q(inscripcion__persona__nombres__contains=s[0]) | Q(inscripcion__persona__apellido1__contains=s[0]) | Q(inscripcion__persona__apellido2__contains=s[0]) | Q(inscripcion__persona__cedula__contains=s[0])).filter(inscripcion__carrera=inscripcion.carrera, estado=1, alternativa__tipotitulacion=matriculado.alternativa.tipotitulacion).exclude(inscripcion=inscripcion).distinct()[:20]
                    data = {"result": "ok", "results": [{"id": x.id, "name": x.flexbox_repr()}for x in matri]}
                    return JsonResponse(data)
                except Exception as ex:
                    pass

            elif action == 'deltematica':
                try:
                    data['title'] = u"Retiro de grupo"
                    grupo = ComplexivoGrupoTematica.objects.get(pk=request.GET['id'])
                    data['mensaje'] = u"Esta seguro de retirarse de la tematica: %s" %(grupo.tematica)
                    data['grupo'] = grupo
                    return render(request, "alu_complexivocurso/deletetematica.html", data)
                except Exception as ex:
                    pass

            elif action == 'detalle':
                try:
                    grupo = []
                    if 'ida' in request.GET:
                        grupo = ComplexivoGrupoTematica.objects.get(pk=request.GET['ida'], status=True)
                        tematica = grupo.tematica
                    else:
                        tematica = ComplexivoTematica.objects.get(pk=int(request.GET['id']))
                        if tematica.complexivogrupotematica_set.values('id').filter(status=True).exists():
                            grupo = ComplexivoGrupoTematica.objects.filter(tematica_id=int(request.GET['id'])).distinct()[0]
                    data['estadoapto'] = int(request.GET['estadoapto'])
                    data['matri'] = MatriculaTitulacion.objects.get(pk=request.GET['idmatri'])
                    data['grupo'] = grupo
                    puedevertribunal = False
                    if grupo.fechadefensa:
                        fecharestada = grupo.fechadefensa - timedelta(days=10)
                        if fecharestada <= hoy:
                            puedevertribunal = True
                    data['puedevertribunal'] = puedevertribunal
                    data['tematica'] = tematica
                    data['idalum'] = inscripcion.id
                    data['grupos'] = ComplexivoGrupoTematica.objects.filter(pk__in=ComplexivoDetalleGrupo.objects.values_list("grupo__id", flat=False).filter(matricula=inscripcion.proceso_titulacion(), grupo__complexivoacompanamiento__isnull=False).distinct())
                    # data['detalles'] = grupo.complexivoacompanamiento_set.filter(status=True).order_by('id')
                    detalles = []
                    if grupo:
                        detalles = grupo.complexivoacompanamiento_set.filter(status=True).order_by('id')
                    data['detalles'] = detalles

                    if 'mostrarcupos' in request.GET:
                        gcupos = tematica.complexivotematicagrupocupo_set.filter(status=True, enuso=False).order_by('numerogrupo')
                        grupocupos = [[g.numerogrupo, g.cupoasignado] for g in gcupos]
                        data['grupocupos'] = grupocupos

                    template = get_template("alu_complexivocurso/detalle.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": "ok", 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})
            elif action == 'detalle2':
                try:
                    detalles = []
                    if 'idd' in request.GET:
                        detalles = ComplexivoAcompanamiento.objects.get(pk=request.GET['idd'], status=True)
                    data['detalles'] = detalles
                    template = get_template("alu_complexivocurso/detalletutorias.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": "ok", 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})
            elif action == 'confirmar':
                try:
                    data['grupo'] = grupo = ComplexivoGrupoTematica.objects.get(pk=int(request.GET['id']))
                    data['matricula']= matricula = MatriculaTitulacion.objects.filter(inscripcion=inscripcion, estado=1)[0]
                    data['tematica']= grupo.tematica
                    data['idalum'] = inscripcion.id
                    data['companeros'] = grupo.complexivodetallegrupo_set.filter(status=True).exclude(matricula=matricula)
                    template = get_template("alu_complexivocurso/confirmar.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": "ok", 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            elif action == 'adddoc':
                try:
                    data['grupo'] = grupo = ComplexivoGrupoTematica.objects.get(pk=int(request.GET['id']))
                    data['title'] = u"SUBIR DOCUMENTOS DE PROPUESTA PRÁCTICA"
                    data['form'] = ComplexivoSubirPropuestaForm()
                    return render(request, "alu_complexivocurso/adddoc.html", data)
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al cargar formulario."})

            elif action == 'editdoc':
                try:
                    data['archivo']= archivo =ComplexivoPropuestaPracticaArchivo.objects.get(pk=int(request.GET['id']))
                    tipo = archivo.tipo
                    tiparchivo = TIPO_ARCHIVO_COMPLEXIVO_PROPUESTA.__getitem__(tipo - 1)[1]
                    data['title'] = u"MODIFICAR %s" % (tiparchivo)
                    data['form'] = ComplexivoEditarArchivoPropuestaForm()
                    return render(request, "alu_complexivocurso/editdoc.html", data)
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al cargar formulario."})

            elif action == 'deldoc':
                try:
                    data['title'] = u"Eliminar Propuesta Práctica"
                    grupo = ComplexivoGrupoTematica.objects.get(pk=request.GET['id'])
                    data['mensaje'] = u"¿Está seguro que desea eliminar los archivos de la Propuesta Práctica?"
                    data['grupo'] = grupo
                    return render(request, "alu_complexivocurso/deletedoc.html", data)
                except Exception as ex:
                    pass
            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = u'Curso complexivo'
                if not MatriculaTitulacion.objects.values('id').filter(Q(inscripcion=inscripcion), (Q(estado=1)| Q(estado=10)| Q(estado=9))).exists():
                    return HttpResponseRedirect("/?info=No esta matriculado en el examen complexivo.")
                if 'idperiodogrupo' in request.GET:
                    idperiodogrupo = request.GET['idperiodogrupo']
                    matricula = MatriculaTitulacion.objects.get(Q(inscripcion=inscripcion), (Q(estado=1)|Q(estado=10)|Q(estado=9)), alternativa__grupotitulacion__periodogrupo__id=idperiodogrupo)
                else:
                    matricula = MatriculaTitulacion.objects.filter(Q(inscripcion=inscripcion), (Q(estado=1)|Q(estado=10)|Q(estado=9)),status=True).order_by('-id')[0]
                data['matricula'] = matricula
                data['lstadoperiodos'] = MatriculaTitulacion.objects.values_list('alternativa__grupotitulacion__periodogrupo__id', 'alternativa__grupotitulacion__periodogrupo__nombre').filter(Q(inscripcion=inscripcion), (Q(estado=1)|Q(estado=10)|Q(estado=9))).distinct()
                data['alternativa'] = matricula.alternativa
                data['estudiante'] = inscripcion.persona
                data['materias'] = matricula.alternativa.complexivomateria_set.filter(status=True).order_by('fechainicio')
                data['archivos'] = ArchivoTitulacion.objects.filter(vigente=True, status=True).distinct()
                pexamen = 0
                ppropuesta = 0
                if matricula.alternativa.cronogramaexamencomplexivo_set.values('id').exists():
                    data['cronograma'] = cronograma = matricula.alternativa.cronogramaexamencomplexivo_set.all()[0]
                    if matricula.alternativa.cronogramaexamencomplexivo_set.get().fechaeleccionpropuestafin != None and matricula.alternativa.cronogramaexamencomplexivo_set.get().fechaeleccionpropuestainicio != None:
                        if datetime.now().date() <= matricula.alternativa.cronogramaexamencomplexivo_set.get().fechaeleccionpropuestafin and datetime.now().date() >= matricula.alternativa.cronogramaexamencomplexivo_set.get().fechaeleccionpropuestainicio:
                            data['disponible'] = True
                        if datetime.now().date() >= matricula.alternativa.cronogramaexamencomplexivo_set.get().fechaeleccionpropuestainicio:
                            data['disponibleinicio'] = True
                if matricula.alternativa.tiene_examen():
                    # data['examenes'] = ComplexivoExamenDetalle.objects.filter(status=True, matricula=matricula)
                    # if ComplexivoExamenDetalle.objects.filter(status=True, matricula=matricula, estado=3).exclude(examen__examenadicional=True).exists():
                    #     detalle = ComplexivoExamenDetalle.objects.filter(status=True, matricula=matricula, estado=3)[0]
                    #     examenes = ComplexivoExamen.objects.filter(pk=detalle.examen.id)
                    # else:
                    #     examenes = matricula.alternativa.complexivoexamen_set.filter(status=True)
                    if ComplexivoExamenDetalle.objects.filter(status=True, matricula=matricula).exists():
                        listaid = ComplexivoExamenDetalle.objects.values_list('examen_id', flat=True).filter(status=True, matricula=matricula)
                        examenes = ComplexivoExamen.objects.filter(id__in=listaid)
                    else:
                        examenes = matricula.alternativa.complexivoexamen_set.filter(status=True)
                    data['examenes'] = examenes
                    # data['detalleexamen'] = detalle = ComplexivoExamenDetalle.objects.filter(status=True, matricula=matricula)[0]
                    data['detalleexamen'] = detalle = ComplexivoExamenDetalle.objects.filter(status=True, matricula=matricula).order_by('-id')[0]
                    data['examen'] = examen = detalle.examen if detalle else None
                    # data['examen'] = examen = matricula.alternativa.complexivoexamen_set.filter(status=True, aplicaexamen=True)[0]
                    # data['detalleexamen'] = detalle = examen.complexivoexamendetalle_set.filter(matricula=matricula, status=True)
                    if detalle:
                        # data['detalleexamen'] = detalle = detalle.get(matricula=matricula)
                        data['detalleexamen'] = detalle
                    else:
                        detalle = ComplexivoExamenDetalle(examen=examen, matricula=matricula)
                        detalle.save(request)
                        log(u"Se creo un detalle de examen complexivo porque no existia %s - [%s] idalter: %s ---creado: %s" % (matricula,examen, matricula.alternativa.id, detalle), request, "delete")
                    pexamen = detalle.ponderacion()
                listadogrupos = None
                numgrupos = 0
                grupo = None
                idgrupotematica = 0
                miestadogrupo = None
                if ComplexivoGrupoTematica.objects.values('id').filter(status=True, complexivodetallegrupo__status=True, complexivodetallegrupo__matricula=matricula,activo=True).exists():
                    listadogrupos = ComplexivoGrupoTematica.objects.filter(status=True, complexivodetallegrupo__status=True, complexivodetallegrupo__matricula=matricula,activo=True).order_by('id')
                    numgrupos = listadogrupos.count()
                    if 'idgrupotematica' in request.GET:
                        idgrupotematica = int(encrypt(request.GET['idgrupotematica']))
                        data['grupo'] = grupo = ComplexivoGrupoTematica.objects.get(pk=idgrupotematica,activo=True)
                    else:
                        data['grupo'] = grupo = ComplexivoGrupoTematica.objects.filter(status=True, complexivodetallegrupo__status=True, complexivodetallegrupo__matricula=matricula,activo=True).order_by('-id')[0]
                        idgrupotematica = grupo.id
                    data['companeros'] = companeros = grupo.complexivodetallegrupo_set.filter(Q(status=True), (Q(matricula__estado=1) | Q(matricula__estado=10) | Q(matricula__estado=9))).exclude(matricula=matricula)
                    if grupo.complexivodetallegrupo_set.filter(Q(status=True), (Q(matricula__estado=1) | Q(matricula__estado=10) | Q(matricula__estado=9)), matricula=matricula):
                        miestadogrupo = grupo.complexivodetallegrupo_set.get(Q(status=True), (Q(matricula__estado=1) | Q(matricula__estado=10) | Q(matricula__estado=9)), matricula=matricula)
                    data['confirmar'] = grupo.complexivodetallegrupo_set.values('id').filter(status=True, estado=4, matricula = matricula).exists()
                    data['tipoarchivo'] = TIPO_ARCHIVO_COMPLEXIVO_PROPUESTA
                    data['propuestas'] = p = grupo.complexivopropuestapractica_set.filter(status=True).order_by('id')
                    data['tutor'] = grupo.tematica.tutor if not grupo.tiene_tematica_confirmar(matricula.inscripcion_id) else ''
                    nintegrantes = companeros.count() + 1
                    data['numerointegrantes'] = grupo.grupocupo.cupoasignado if grupo.grupocupo else nintegrantes
                    data['grupos'] = ComplexivoGrupoTematica.objects.filter(pk__in=ComplexivoDetalleGrupo.objects.values_list("grupo__id", flat=False).filter(matricula=inscripcion.proceso_titulacion(), grupo__complexivoacompanamiento__isnull=False).distinct())

                    # ppropuesta = matricula.notapropuesta()
                    ppropuesta = matricula.notapropuestagrupo(grupo)
                data['idgrupotematica'] = idgrupotematica
                data['listadogrupos'] = listadogrupos
                data['numgrupos'] = numgrupos
                data['miestadogrupo'] = miestadogrupo
                data['pexamen'] = pexamen
                data['ppropuesta'] = ppropuesta
                # data['ptotal'] = matricula.notafinalcomplexivo()
                data['modelos'] = matricula.alternativa.modelo_alternativatitulacion_set.filter(status=True).order_by('modelo__nombre')
                if matricula.alternativa.tipotitulacion.tipo == 1:
                    data['ptotal'] = ppropuesta
                if matricula.alternativa.tipotitulacion.tipo == 2:
                    data['ptotal'] = matricula.notafinalcomplexivo(grupo)
                # if matricula.alternativa.tipotitulacion.tipo==1:
                #     data['title'] = u'Propuesta de Titulación'
                #     return render(request, "alu_propuestatitulacion/view.html", data)
                data['requisitossustentar'] = RequisitoSustentar.objects.filter(status=True)
                alter = AlternativaTitulacion.objects.get(pk=matricula.alternativa_id)
                data = valida_matricular_estudiante(data, alter, inscripcion, matricula)

                return render(request, "alu_complexivocurso/viewcurso.html", data)
            except Exception as ex:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
                return HttpResponseRedirect("/")


def valida_matricular_estudiante(data, alter, inscripcion, matriculatitulacion):
    vali_alter = 8
    vali_tenido = 0
    data['item'] = alter
    data['grupotitulacion'] = alter.grupotitulacion
    data['inscripcion'] = inscripcion
    malla = inscripcion.inscripcionmalla_set.filter(status=True)[0].malla
    perfil = inscripcion.persona.mi_perfil()
    fechainicioprimernivel = inscripcion.fechainicioprimernivel if inscripcion.fechainicioprimernivel else datetime.now().date()
    excluiralumnos = datetime(2009, 1, 21, 23, 59, 59).date()
    data['esexonerado'] = fechainicioprimernivel <= excluiralumnos

    data['tiene_discapidad'] = perfil.tienediscapacidad
    # if alter.estadofichaestudiantil:
    #     vali_alter += 1
    ficha = 0
    if inscripcion.persona.nombres and inscripcion.persona.apellido1 and inscripcion.persona.nacimiento and  inscripcion.persona.nacionalidad and inscripcion.persona.email and inscripcion.persona.estado_civil and inscripcion.persona.sexo:
        data['datospersonales'] = True
        ficha += 1
    if inscripcion.persona.paisnacimiento and inscripcion.persona.provincianacimiento and inscripcion.persona.cantonnacimiento and inscripcion.persona.parroquianacimiento:
        data['datosnacimientos'] = True
        ficha += 1
    examenfisico = inscripcion.persona.datos_examen_fisico()
    if inscripcion.persona.sangre and examenfisico.peso and examenfisico.talla:
        data['datosmedicos'] = True
        ficha += 1
    if inscripcion.persona.pais and inscripcion.persona.provincia and inscripcion.persona.canton and inscripcion.persona.parroquia and inscripcion.persona.direccion and inscripcion.persona.direccion2 and inscripcion.persona.num_direccion and inscripcion.persona.telefono_conv or inscripcion.persona.telefono:
        data['datosdomicilio'] = True
        ficha += 1
    if perfil.raza:
        data['etnia'] = True
        ficha += 1
    if ficha == 5:
        vali_tenido += 1
    # if alter.estadopracticaspreprofesionales:
    #     vali_alter += 1
    totalhoras = 0
    practicaspreprofesionalesinscripcion = PracticasPreprofesionalesInscripcion.objects.filter(inscripcion=inscripcion, status=True, culminada=True)
    data['malla_horas_practicas'] = malla.horas_practicas
    if fechainicioprimernivel > excluiralumnos:
        if practicaspreprofesionalesinscripcion.exists():
            for practicas in practicaspreprofesionalesinscripcion:
                if practicas.tiposolicitud == 3:
                    totalhoras += practicas.horahomologacion if practicas.horahomologacion else 0
                else:
                    totalhoras += practicas.numerohora
            if totalhoras >= malla.horas_practicas:
                data['practicaspreprofesionales'] = True
                vali_tenido += 1
        data['practicaspreprofesionalesvalor'] = totalhoras
    else:
        data['practicaspreprofesionales'] = True
        vali_tenido += 1
        data['practicaspreprofesionalesvalor'] = malla.horas_practicas
    # if alter.estadocredito:
    #     vali_alter += 1
    data['creditos'] = inscripcion.aprobo_asta_penultimo_malla()
    if inscripcion.aprobo_asta_penultimo_malla() and inscripcion.esta_matriculado_ultimo_nivel():
        vali_tenido += 1
    data['cantasigaprobadas'] = inscripcion.cantidad_asig_aprobada_penultimo_malla()
    data['cantasigaprobar'] = inscripcion.cantidad_asig_aprobar_penultimo_malla()
    data['esta_mat_ultimo_nivel'] = inscripcion.esta_matriculado_ultimo_nivel()
    # if alter.estadoadeudar:
    #     vali_alter += 1
    if inscripcion.adeuda_a_la_fecha() == 0:
        data['deudas'] = True
        vali_tenido += 1
    data['deudasvalor'] = inscripcion.adeuda_a_la_fecha()
    # if alter.estadoingles:
    #     vali_alter += 1
    modulo_ingles = ModuloMalla.objects.filter(malla=malla, status=True).exclude(asignatura_id=782)
    numero_modulo_ingles = modulo_ingles.count()
    lista = []
    listaid = []
    for modulo in modulo_ingles:
        if inscripcion.estado_asignatura(modulo.asignatura) == NOTA_ESTADO_APROBADO:
            lista.append(modulo.asignatura.nombre)
            listaid.append(modulo.asignatura.id)
    data['modulo_ingles_aprobados'] = lista
    data['modulo_ingles_faltante'] = modulo_ingles.exclude(asignatura_id__in=[int(i) for i in listaid])
    if numero_modulo_ingles == len(listaid):
        data['modulo_ingles'] = True
        vali_tenido += 1
    # if alter.estadonivel:
    #     vali_alter += 1
    #total_materias_malla = malla.cantidad_materiasaprobadas()
    #cantidad_materias_aprobadas_record = inscripcion.recordacademico_set.filter(aprobada=True, status=True,asignatura__in=[x.asignatura for x in malla.asignaturamalla_set.filter(status=True)]).count()
    #poraprobacion = round(cantidad_materias_aprobadas_record * 100 / total_materias_malla, 0)
    data['mi_nivel'] = nivel = inscripcion.mi_nivel()
    inscripcionmalla = inscripcion.malla_inscripcion()
    niveles_maximos = inscripcionmalla.malla.niveles_regulares
    # MOMENTANEO EL AUMENTO DE VALI_TENIDO
    # vali_tenido += 1

    asignaturas_malla = AsignaturaMalla.objects.filter(Q(status=True,malla=malla,opcional=False)| Q(itinerario__in=[1,2,3],status=True,malla=malla,opcional=False))
    xyz = [1, 2, 3]
    if inscripcion.itinerario and inscripcion.itinerario > 0:
        xyz.remove(inscripcion.itinerario)
        asignaturas_malla = asignaturas_malla.exclude(itinerario__in=xyz)
    materia_aprobada = True
    for asignatura in asignaturas_malla:
        existe_asignatura =RecordAcademico.objects.filter(status=True,asignaturamalla=asignatura, inscripcion= inscripcion).exists()
        if existe_asignatura:
            asignatura_record =RecordAcademico.objects.get(status=True,asignaturamalla=asignatura, inscripcion= inscripcion)
            if not asignatura_record.aprobada:
                materia_aprobada = False
                break
        else:
            materia_aprobada = False
            break


    # if poraprobacion >= 100 :
    #     data['nivel'] = True
    #     vali_tenido += 1

    if materia_aprobada:
        data['nivel'] = True
        vali_tenido += 1

    else:
        if niveles_maximos == nivel.nivel.id:
            data['septimo'] = True
    if perfil.tienediscapacidad:
        data['discapacidad'] = perfil
    if inscripcion.persona.sexo.id == ESTADO_GESTACION:
        data['femenino'] = True
    # if alter.estadovinculacion:
    #     vali_alter += 1
    data['malla_horas_vinculacion'] = malla.horas_vinculacion
    # horastotal = ParticipantesMatrices.objects.filter(matrizevidencia_id=2, status=True, proyecto__status=True, inscripcion_id=inscripcion.id, actividad__isnull=True).aggregate(horastotal=Sum('horas'))['horastotal']
    horastotal = null_to_numeric(ParticipantesMatrices.objects.filter(matrizevidencia_id=2, status=True, proyecto__status=True, inscripcion_id=inscripcion.id, actividad__isnull=True).aggregate(horastotal=Sum('horas'))['horastotal'])
    horasconvalidadas = null_to_numeric(inscripcion.participantesmatrices_set.filter(matrizevidencia_id=2, status=True, actividad__isnull=False).aggregate(horas=Sum('horas'))['horas'])

    # horastotal = horastotal if horastotal else 0
    horastotal += horasconvalidadas
    if fechainicioprimernivel > excluiralumnos:
        if horastotal >= malla.horas_vinculacion:
            data['vinculacion'] = True
            vali_tenido += 1
        data['horas_vinculacion'] = horastotal
    else:
        data['horas_vinculacion'] = malla.horas_vinculacion
        data['vinculacion'] = True
        vali_tenido += 1
    # if alter.estadocomputacion:
    #     vali_alter += 1
    asignatura = AsignaturaMalla.objects.values_list('asignatura__id', flat=True).filter(malla__id=32)
    data['record_computacion'] = record = RecordAcademico.objects.filter(inscripcion__id=inscripcion.id, asignatura__id__in=asignatura, aprobada=True)
    creditos_computacion = 0
    data['malla_creditos_computacion'] = malla.creditos_computacion
    for comp in record:
        creditos_computacion += comp.creditos
    if creditos_computacion >= malla.creditos_computacion:
        data['computacion'] = True
        vali_tenido += 1
    data['creditos_computacion'] = creditos_computacion
    if vali_alter == vali_tenido:
        data['aprueba'] = True
        matriculatitulacion.cumplerequisitos = 2
        matriculatitulacion.save()
    else:
        matriculatitulacion.cumplerequisitos = 3
        matriculatitulacion.save()
    if inscripcion.persona.tipocelular == 0:
        data['tipocelular'] = '-'
    else:
        data['tipocelular'] = TIPO_CELULAR[int(inscripcion.persona.tipocelular) - 1][1]
    return data