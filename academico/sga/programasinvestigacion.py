# -*- coding: UTF-8 -*-
import random
from datetime import datetime
import xlwt
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.aggregates import Sum
from django.http import JsonResponse, request
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.context import Context
from django.template.loader import get_template
from xlwt import *
from decorators import secure_module, last_access
from sga.commonviews import adduserdata
from sga.forms import ProgramasInvestigacionForm, EvidenciaForm, ProyectoInvestigacionForm, \
    ParticipanteProfesorForm, ParticipanteEstudianteForm, ParticipanteAdministrativoForm, PresupuestoProyectoForm
from sga.funciones import log, generar_nombre, MiPaginador
from sga.models import Inscripcion, ProgramasInvestigacion, DetalleEvidencias, ProyectosInvestigacion, \
    ParticipantesMatrices, PresupuestosProyecto, CarrerasProyecto, Graduado, Evidencia, ParticipantesTipo, Carrera


@login_required(redirect_field_name='ret', login_url='/loginsga')
@secure_module
@last_access
@transaction.atomic()
def view(request):
    data = {}
    adduserdata(request, data)
    persona = request.session['persona']
    miscarreras = persona.mis_carreras()
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'add':
            try:
                f = ProgramasInvestigacionForm(request.POST)
                if f.is_valid():
                    if not ProgramasInvestigacion.objects.filter(nombre=f.cleaned_data['nombre']).exists():
                        programas = ProgramasInvestigacion(nombre=f.cleaned_data['nombre'],
                                                           fechainicio=f.cleaned_data['fechainicio'],
                                                           fechaplaneado=f.cleaned_data['fechaplaneado'],
                                                           # fechareal=f.cleaned_data['fechaFin'],
                                                           lineainvestigacion=f.cleaned_data['lineainvestigacion'],
                                                           alcanceterritorial=f.cleaned_data['alcanceterritorial'],
                                                           areaconocimiento=f.cleaned_data['areaconocimiento'],
                                                           subareaconocimiento=f.cleaned_data['subareaconocimiento'],
                                                           subareaespecificaconocimiento=f.cleaned_data['subareaespecificaconocimiento']
                                                           )
                        programas.save(request)
                        log(u'Adiciono programa de investigación: %s' % programas, request, "add")
                        return JsonResponse({"result": "ok"})
                    else:
                        return JsonResponse({"result": "bad", "mensaje": u"Ya el estudiante esta graduado."})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        if action == 'addproyecto':
            try:
                f = ProyectoInvestigacionForm(request.POST)
                if f.is_valid():
                    if not ProyectosInvestigacion.objects.filter(nombre=f.cleaned_data['nombre'],tipo=2).exists():
                        proyecto = ProyectosInvestigacion(nombre=f.cleaned_data['nombre'],
                                                          fechainicio=f.cleaned_data['fechainicio'],
                                                          fechaplaneado=f.cleaned_data['fechaplaneado'],
                                                          # fechareal=f.cleaned_data['fechafin'],
                                                          programa=f.cleaned_data['programa'],
                                                          tipo=2,
                                                          tipoproinstitucion=f.cleaned_data['tipoproinstitucion'],
                                                          alcanceterritorial=f.cleaned_data['alcanceterritorial'],
                                                          areaconocimiento=f.cleaned_data['areaconocimiento'],
                                                          subareaconocimiento=f.cleaned_data['subareaconocimiento'],
                                                          subareaespecificaconocimiento=f.cleaned_data['subareaespecificaconocimiento']
                                                          )
                        proyecto.save(request)
                        log(u'Adiciono proyecto de investigación: %s' % proyecto, request, "add")
                        return JsonResponse({"result": "ok"})
                    else:
                        return JsonResponse({"result": "bad", "mensaje": u"Ya el estudiante esta graduado."})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'editprograma':
            try:
                f = ProgramasInvestigacionForm(request.POST)
                programas = ProgramasInvestigacion.objects.get(pk=request.POST['id'])
                if f.is_valid():
                    programas.fechainicio = f.cleaned_data['fechainicio']
                    programas.fechaplaneado = f.cleaned_data['fechaplaneado']
                    programas.fechareal = f.cleaned_data['fechareal']
                    programas.nombre = f.cleaned_data['nombre']
                    programas.lineainvestigacion = f.cleaned_data['lineainvestigacion']
                    programas.alcanceterritorial = f.cleaned_data['alcanceterritorial']
                    programas.areaconocimiento = f.cleaned_data['areaconocimiento']
                    programas.subareaconocimiento = f.cleaned_data['subareaconocimiento']
                    programas.subareaespecificaconocimiento = f.cleaned_data['subareaespecificaconocimiento']
                    programas.save(request)
                    log(u'Editó programa de investigación: %s' % programas, request, "edit")
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'addevidenciasprogramas':
            try:
                f = EvidenciaForm(request.POST, request.FILES)
                if f.is_valid():
                    newfile = None
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("programa_", newfile._name)
                    if DetalleEvidencias.objects.filter(evidencia_id=request.POST['idevidencia'], programa_id=request.POST['id']).exists():
                        detalle = DetalleEvidencias.objects.get(evidencia_id=request.POST['idevidencia'], programa_id=request.POST['id'])
                        detalle.descripcion = f.cleaned_data['descripcion']
                        detalle.archivo = newfile
                        detalle.save(request)
                        log(u'Editó detalle de evidencia de investigación: %s' % detalle, request, "edit")
                    else:
                        evidencia = DetalleEvidencias(evidencia_id=request.POST['idevidencia'],
                                                      programa_id=request.POST['id'],
                                                      descripcion=f.cleaned_data['descripcion'],
                                                      archivo=newfile)
                        evidencia.save(request)
                        log(u'Adiciono evidencia de investigación: %s' % evidencia, request, "add")
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'deleteprograma':
            try:
                programa = ProgramasInvestigacion.objects.get(pk=request.POST['id'])
                programa.status = False
                log(u'Elimino programa de investigación: %s' % programa, request, "del")
                programa.save(request)
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al eliminar los datos."})

        elif action == 'deleteparticipanteproyecto':
            try:
                participante = ParticipantesMatrices.objects.get(pk=request.POST['id'])
                participante.status = False
                log(u'Elimino practicipante de investigación: %s' % participante, request, "del")
                participante.save(request)
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al eliminar los datos."})

        elif action == 'deletepresupuestoproyecto':
            try:
                presupuesto = PresupuestosProyecto.objects.get(pk=request.POST['id'])
                presupuesto.status = False
                log(u'Elimino presupuesto de proyecto de investigación: %s' % presupuesto, request, "del")
                presupuesto.save(request)
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al eliminar los datos."})

        elif action == 'editproyecto':
            try:
                f = ProyectoInvestigacionForm(request.POST)
                proyectos = ProyectosInvestigacion.objects.select_related().get(pk=request.POST['id'],tipo=2)
                if f.is_valid():
                    proyectos.fechainicio = f.cleaned_data['fechainicio']
                    proyectos.fechaplaneado = f.cleaned_data['fechaplaneado']
                    proyectos.fechareal = f.cleaned_data['fechareal']
                    proyectos.nombre = f.cleaned_data['nombre']
                    proyectos.programa = f.cleaned_data['programa']
                    proyectos.tipo = 2
                    proyectos.tipoproinstitucion = f.cleaned_data['tipoproinstitucion']
                    proyectos.alcanceterritorial = f.cleaned_data['alcanceterritorial']
                    proyectos.areaconocimiento = f.cleaned_data['areaconocimiento']
                    proyectos.subareaconocimiento = f.cleaned_data['subareaconocimiento']
                    proyectos.subareaespecificaconocimiento = f.cleaned_data['subareaespecificaconocimiento']
                    proyectos.save(request)
                    log(u'Editó proyecto de investigación: %s' % proyectos, request, "del")
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'addevidenciasproyectos':
            try:
                f = EvidenciaForm(request.POST, request.FILES)
                # 2.5MB - 2621440
                # 5MB - 5242880
                # 10MB - 10485760
                # 20MB - 20971520
                # 50MB - 5242880
                # 100MB 104857600
                # 250MB - 214958080
                # 500MB - 429916160
                d = request.FILES['archivo']
                if d.size > 10485760:
                    return JsonResponse({"result": "bad", "mensaje": u"Error, archivo mayor a 10 Mb."})
                if f.is_valid():
                    newfile = None
                    if 'archivo' in request.FILES:
                        newfile = request.FILES['archivo']
                        newfile._name = generar_nombre("proyecto_", newfile._name)
                    if DetalleEvidencias.objects.filter(evidencia_id=request.POST['idevidencia'], proyecto_id=request.POST['id']).exists():
                        detalle = DetalleEvidencias.objects.get(evidencia_id=request.POST['idevidencia'], proyecto_id=request.POST['id'])
                        detalle.descripcion = f.cleaned_data['descripcion']
                        detalle.archivo = newfile
                        detalle.save(request)
                        log(u'Adiciono evidencia proyecto de investigación: %s' % detalle, request, "add")
                    else:
                        evidencia = DetalleEvidencias(evidencia_id=request.POST['idevidencia'],
                                                      proyecto_id=request.POST['id'],
                                                      descripcion=f.cleaned_data['descripcion'],
                                                      archivo=newfile)
                        evidencia.save(request)
                        log(u'Adiciono evidencia proyecto de investigación: %s' % evidencia, request, "add")
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'deleteproyecto':
            try:
                proyecto = ProyectosInvestigacion.objects.get(pk=request.POST['id'],tipo=2)
                # proyecto.status = False
                log(u'Eliminó proyecto de investigación: %s' % proyecto, request, "add")
                proyecto.delete()
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al eliminar los datos."})

        if action == 'addparticipantesdocentes':
            try:
                f = ParticipanteProfesorForm(request.POST)
                if f.is_valid():
                    if ParticipantesMatrices.objects.filter(proyecto_id=request.POST['id'],profesor_id=f.cleaned_data['profesor'],status=True).exists():
                        return JsonResponse({"result": "r","mensaje": u"Error el docente ya se encuentra inscrito en el proyecto."})
                    programas = ParticipantesMatrices(matrizevidencia_id=2,
                                                      proyecto_id=request.POST['id'],
                                                      profesor_id=f.cleaned_data['profesor'],
                                                      horas=f.cleaned_data['horas'],
                                                      tipoparticipante=f.cleaned_data['tipoparticipante']
                                                      )
                    programas.save(request)
                    log(u'Adiciono Participante Docente: %s' % programas, request, "add")
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        if action == 'addparticipantesestudiantes':
            try:
                f = ParticipanteEstudianteForm(request.POST)
                if f.is_valid():
                    datainscripcion = Inscripcion.objects.get(pk=int(f.cleaned_data['inscripcion']))
                    if ParticipantesMatrices.objects.filter(proyecto_id=request.POST['id'], inscripcion__persona=datainscripcion.persona, status=True).exists():
                        return JsonResponse({"result": "r", "mensaje": u"Error el estudiante ya se encuentra inscrito en el proyecto."})
                    programas = ParticipantesMatrices(matrizevidencia_id=2,
                                                      proyecto_id=request.POST['id'],
                                                      inscripcion_id=f.cleaned_data['inscripcion'],
                                                      horas=f.cleaned_data['horas']
                                                      )
                    programas.save(request)
                    log(u'Adiciono participante estudiante proyecto de investigación: %s' % programas, request, "add")
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        if action == 'delparticipantesproyectos':
            try:
                nompersona = ''
                proyecto = ProyectosInvestigacion.objects.get(pk=request.POST['idproyecto'],tipo=2,status=True)
                participantes = ParticipantesMatrices.objects.filter(proyecto=proyecto,status=True)
                for participante in participantes:
                    participante.status = False
                    if participante.inscripcion:
                        nompersona = ' ESTUDIANTE ' + participante.inscripcion.persona.apellido1 + ' ' + participante.inscripcion.persona.apellido2 + ' ' + participante.inscripcion.persona.nombres
                    if participante.profesor:
                        nompersona = ' DOCENTE ' + participante.profesor.persona.apellido1 + ' ' + participante.profesor.persona.apellido2 + ' ' + participante.profesor.persona.nombres
                    if participante.administrativo:
                        nompersona = ' ADMINISTRATIVO ' + participante.administrativo.persona.apellido1 + ' ' + participante.administrativo.persona.apellido2 + ' ' + participante.administrativo.persona.nombres
                    participante.save(request)
                    log(u'Eliminación masiva de participantes de proyectos: %s - %s' % (proyecto, nompersona), request, "del")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al solicitar cupo."})

        if action == 'addparticipantesadministrativos':
            try:
                f = ParticipanteAdministrativoForm(request.POST)
                if f.is_valid():
                    if ParticipantesMatrices.objects.filter(proyecto_id=request.POST['id'],administrativo_id=f.cleaned_data['administrativo'],status=True).exists():
                        return JsonResponse({"result": "r","mensaje": u"Error personal administrativo ya se encuentra inscrito en el proyecto."})
                    programas = ParticipantesMatrices(matrizevidencia_id=2,
                                                      proyecto_id=request.POST['id'],
                                                      administrativo_id=f.cleaned_data['administrativo'],
                                                      horas=f.cleaned_data['horas']
                                                      )
                    programas.save(request)
                    log(u'Adiciono participante Administrativo programa de investigación: %s' % programas, request, "add")
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'updatehoras':
            try:
                participantes = ParticipantesMatrices.objects.get(pk=request.POST['indi'])
                valor = int(request.POST['valor'])
                cupoanterior = participantes.horas
                participantes.horas = valor
                participantes.save(request)
                return JsonResponse({'result': 'ok', 'valor': participantes.horas})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad'})

        elif action == 'updatetipoparticipante':
            try:
                participantes = ParticipantesMatrices.objects.get(pk=request.POST['idparticipante'])
                tipopar = request.POST['tipoparticipante']
                tipoparanterior = participantes.tipoparticipante_id
                participantes.tipoparticipante_id = tipopar
                participantes.save(request)
                log(u'Editó tipo de participante de investigación: %s' % participantes, request, "add")
                return JsonResponse({'result': 'ok', 'valor': participantes.tipoparticipante_id})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad'})

        if action == 'addcarrerasproyectos':
            try:
                idproyecto = request.POST['idproyecto']
                carrerasproyectos = CarrerasProyecto.objects.filter(proyecto_id=int(idproyecto))
                carrerasproyectos.delete()
                lista = request.POST['listacarrerasproyecto']
                if lista:
                    elementos = lista.split(',')
                    for elemento in elementos:
                        addcarrera = CarrerasProyecto(carrera_id=int(elemento),proyecto_id=int(idproyecto))
                        addcarrera.save(request)
                        log(u'Adiciono carreras de proyecto de investigación: %s' % addcarrera, request, "add")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        if action == 'addpresupuestoproyectos':
            try:
                idproyecto = request.POST['idproyecto']
                presupuesto = PresupuestosProyecto(anioejecucion=int(request.POST['anioejecucion']),
                                                   planificado=float(request.POST['planificado']),
                                                   ejecutado=float(request.POST['ejecutado']),
                                                   proyecto_id=int(idproyecto))
                presupuesto.save(request)
                log(u'Adiciono presupuesto de  proyectos de investigación: %s' % presupuesto, request, "add")
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'excelprograma':
                try:
                    __author__ = 'Unemi'
                    style0 = easyxf('font: name Times New Roman, color-index blue, bold off', num_format_str='#,##0.00')
                    style_nb = easyxf('font: name Times New Roman, color-index blue, bold on', num_format_str='#,##0.00')
                    style_sb = easyxf('font: name Times New Roman, color-index blue, bold on')
                    title = easyxf('font: name Times New Roman, color-index blue, bold on , height 350; alignment: horiz centre')
                    style1 = easyxf(num_format_str='D-MMM-YY')
                    font_style = XFStyle()
                    font_style.font.bold = True
                    font_style2 = XFStyle()
                    font_style2.font.bold = False
                    wb = Workbook(encoding='utf-8')
                    ws = wb.add_sheet('exp_xls_post_part')
                    ws.write_merge(0, 0, 0, 10, 'UNIVERSIDAD ESTATAL DE MILAGRO', title)
                    response = HttpResponse(content_type="application/ms-excel")
                    response[
                        'Content-Disposition'] = 'attachment; filename=Matriz_Programas' + random.randint(1, 10000).__str__() + '.xls'

                    columns = [
                        (u"NUM", 2000),
                        (u"NOMBRE", 10000),
                        (u"LINEA", 10000),
                        (u"FECHA INICIO", 3000),
                        (u"FECHA PLANEADA", 3000),
                        (u"FECHA REAL", 3000),
                        (u"AREA CONOCIMIENTO", 10000),
                        (u"SUBAREA CONOCIMIENTO", 10000),
                        (u"SUBAREA ESPECIFICA", 10000),
                        (u"ALCANCE TERRITORIAL", 3000),
                    ]
                    row_num = 3
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], font_style)
                        ws.col(col_num).width = columns[col_num][1]
                    date_format = xlwt.XFStyle()
                    date_format.num_format_str = 'yyyy/mm/dd'
                    listaprogramas = ProgramasInvestigacion.objects.filter(status=True).order_by('nombre')
                    row_num = 4
                    for programa in listaprogramas:
                        i = 0
                        campo1 = programa.id
                        campo2 = programa.nombre
                        campo3 = ''
                        if programa.lineainvestigacion:
                            campo3 = programa.lineainvestigacion.nombre
                        campo4 = programa.fechainicio
                        campo5 = programa.fechaplaneado
                        campo6 = programa.fechareal
                        campo7 = ''
                        campo8 = ''
                        campo9 = ''
                        campo10 = ''
                        if programa.areaconocimiento:
                            campo7 = programa.areaconocimiento.nombre
                        if programa.subareaconocimiento:
                            campo8 = programa.subareaconocimiento.nombre
                        if programa.subareaespecificaconocimiento:
                            campo9 = programa.subareaespecificaconocimiento.nombre
                        if programa.alcanceterritorial:
                            campo10 = programa.alcanceterritorial.nombre
                        ws.write(row_num, 0, campo1, font_style2)
                        ws.write(row_num, 1, campo2, font_style2)
                        ws.write(row_num, 2, campo3, font_style2)
                        ws.write(row_num, 3, campo4, date_format)
                        ws.write(row_num, 4, campo5, date_format)
                        ws.write(row_num, 5, campo6, date_format)
                        ws.write(row_num, 6, campo7, font_style2)
                        ws.write(row_num, 7, campo8, font_style2)
                        ws.write(row_num, 8, campo9, font_style2)
                        ws.write(row_num, 9, campo10, font_style2)
                        row_num += 1
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

            if action == 'excelparticipanteproyecto':
                try:
                    idproyecto = request.GET['idproyecto']
                    __author__ = 'Unemi'
                    style0 = easyxf('font: name Times New Roman, color-index blue, bold off', num_format_str='#,##0.00')
                    style_nb = easyxf('font: name Times New Roman, color-index blue, bold on', num_format_str='#,##0.00')
                    style_sb = easyxf('font: name Times New Roman, color-index blue, bold on')
                    title = easyxf('font: name Times New Roman, color-index blue, bold on , height 350; alignment: horiz centre')
                    style1 = easyxf(num_format_str='D-MMM-YY')
                    font_style = XFStyle()
                    font_style.font.bold = True
                    font_style2 = XFStyle()
                    font_style2.font.bold = False
                    wb = Workbook(encoding='utf-8')
                    ws = wb.add_sheet('exp_xls_post_part')
                    ws.write_merge(0, 0, 0, 10, 'UNIVERSIDAD ESTATAL DE MILAGRO', title)
                    response = HttpResponse(content_type="application/ms-excel")
                    response[
                        'Content-Disposition'] = 'attachment; filename=Matriz_Participantes_Proyectos' + random.randint(
                        1, 10000).__str__() + '.xls'

                    columns = [
                        (u"NUM", 2000),
                        (u"PROGRAMA", 10000),
                        (u"PROYECTO", 10000),
                        (u"CEDULA", 10000),
                        (u"APELLIDOS", 10000),
                        (u"HORAS", 2000),
                        (u"TIPO", 2000),
                    ]
                    row_num = 3
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], font_style)
                        ws.col(col_num).width = columns[col_num][1]
                    date_format = xlwt.XFStyle()
                    date_format.num_format_str = 'yyyy/mm/dd'
                    listaparticipantes = ParticipantesMatrices.objects.filter(status=True, matrizevidencia_id=2, proyecto_id=idproyecto).order_by('inscripcion__persona__apellido1', 'inscripcion__persona__apellido2')
                    row_num = 4
                    for participantes in listaparticipantes:
                        i = 0
                        campo1 = participantes.id
                        campo2 = participantes.proyecto.programa.nombre
                        campo3 = participantes.proyecto.nombre
                        if participantes.profesor:
                            campo4 = participantes.profesor.persona.cedula
                        if participantes.inscripcion:
                            campo4 = participantes.inscripcion.persona.cedula
                        if participantes.administrativo:
                            campo4 = participantes.administrativo.persona.cedula
                        if participantes.profesor:
                            campo5 = participantes.profesor.persona.nombre_completo_inverso()
                        if participantes.inscripcion:
                            campo5 = participantes.inscripcion.persona.nombre_completo_inverso()
                        if participantes.administrativo:
                            campo5 = participantes.administrativo.persona.nombre_completo_inverso()
                        campo6 = participantes.horas
                        if participantes.profesor:
                            campo7 = participantes.tipoparticipante.nombre
                        if participantes.inscripcion:
                            campo7 = 'ESTUDIANTE'
                        if participantes.administrativo:
                            campo7 = 'ADMINISTRATIVO'
                        ws.write(row_num, 0, campo1, font_style2)
                        ws.write(row_num, 1, campo2, font_style2)
                        ws.write(row_num, 2, campo3, font_style2)
                        ws.write(row_num, 3, campo4, font_style2)
                        ws.write(row_num, 4, campo5, font_style2)
                        ws.write(row_num, 5, campo6, font_style2)
                        ws.write(row_num, 6, campo7, font_style2)
                        row_num += 1
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

            if action == 'excelparticipanteproyectototal':
                try:
                    tipoproyectos = request.GET['tipo']
                    __author__ = 'Unemi'
                    style0 = easyxf('font: name Times New Roman, color-index blue, bold off', num_format_str='#,##0.00')
                    style_nb = easyxf('font: name Times New Roman, color-index blue, bold on', num_format_str='#,##0.00')
                    style_sb = easyxf('font: name Times New Roman, color-index blue, bold on')
                    title = easyxf('font: name Times New Roman, color-index blue, bold on , height 350; alignment: horiz centre')
                    style1 = easyxf(num_format_str='D-MMM-YY')
                    font_style = XFStyle()
                    font_style.font.bold = True
                    font_style2 = XFStyle()
                    font_style2.font.bold = False
                    wb = Workbook(encoding='utf-8')
                    ws = wb.add_sheet('exp_xls_post_part')
                    ws.write_merge(0, 0, 0, 10, 'UNIVERSIDAD ESTATAL DE MILAGRO', title)
                    response = HttpResponse(content_type="application/ms-excel")
                    response[
                        'Content-Disposition'] = 'attachment; filename=Matriz_Participantes_Proyectos' + random.randint(
                        1, 10000).__str__() + '.xls'

                    columns = [
                        (u"NUM", 2000),
                        (u"PROGRAMA", 10000),
                        (u"PROYECTO", 10000),
                        (u"CEDULA", 4000),
                        (u"APELLIDOS", 10000),
                        (u"HORAS", 2000),
                        (u"TIPO", 2000),
                        (u"LINEA", 20000),
                        (u"FECHA INICIO", 3000),
                        (u"FECHA FINAL", 3000),
                        (u"FECHA REAL", 3000),
                    ]
                    row_num = 3
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], font_style)
                        ws.col(col_num).width = columns[col_num][1]
                    date_format = xlwt.XFStyle()
                    date_format.num_format_str = 'yyyy/mm/dd'
                    listaparticipantes = ParticipantesMatrices.objects.filter(status=True, matrizevidencia_id=2, proyecto__tipo=tipoproyectos)
                    row_num = 4
                    for participantes in listaparticipantes:
                        i = 0
                        campo1 = participantes.id
                        campo2 = participantes.proyecto.programa.nombre
                        campo3 = participantes.proyecto.nombre
                        if participantes.profesor:
                            campo4 = participantes.profesor.persona.cedula
                        if participantes.inscripcion:
                            campo4 = participantes.inscripcion.persona.cedula
                        if participantes.administrativo:
                            campo4 = participantes.administrativo.persona.cedula
                        if participantes.profesor:
                            campo5 = participantes.profesor.persona.nombre_completo()
                        if participantes.inscripcion:
                            campo5 = participantes.inscripcion.persona.nombre_completo()
                        if participantes.administrativo:
                            campo5 = participantes.administrativo.persona.nombre_completo()
                        campo6 = participantes.horas
                        if participantes.profesor:
                            campo7 = participantes.tipoparticipante.nombre
                        if participantes.inscripcion:
                            campo7 = 'ESTUDIANTE'
                        if participantes.administrativo:
                            campo7 = 'ADMINISTRATIVO'
                        if participantes.proyecto.programa.lineainvestigacion:
                            campo8 = participantes.proyecto.programa.lineainvestigacion.nombre
                        campo9 = participantes.proyecto.fechainicio
                        campo10 = participantes.proyecto.fechaplaneado
                        campo11 = participantes.proyecto.fechareal
                        ws.write(row_num, 0, campo1, font_style2)
                        ws.write(row_num, 1, campo2, font_style2)
                        ws.write(row_num, 2, campo3, font_style2)
                        ws.write(row_num, 3, campo4, font_style2)
                        ws.write(row_num, 4, campo5, font_style2)
                        ws.write(row_num, 5, campo6, font_style2)
                        ws.write(row_num, 6, campo7, font_style2)
                        ws.write(row_num, 7, campo8, font_style2)
                        ws.write(row_num, 8, campo9, date_format)
                        ws.write(row_num, 9, campo10, date_format)
                        ws.write(row_num, 10, campo11, date_format)
                        row_num += 1
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

            if action == 'excelparticipantevinculacion':
                try:
                    tipoproyectos = request.GET['tipo']
                    __author__ = 'Unemi'
                    style0 = easyxf('font: name Times New Roman, color-index blue, bold off', num_format_str='#,##0.00')
                    style_nb = easyxf('font: name Times New Roman, color-index blue, bold on', num_format_str='#,##0.00')
                    style_sb = easyxf('font: name Times New Roman, color-index blue, bold on')
                    title = easyxf('font: name Times New Roman, color-index blue, bold on , height 350; alignment: horiz centre')
                    style1 = easyxf(num_format_str='D-MMM-YY')
                    font_style = XFStyle()
                    font_style.font.bold = True
                    font_style2 = XFStyle()
                    font_style2.font.bold = False
                    wb = Workbook(encoding='utf-8')
                    ws = wb.add_sheet('exp_xls_post_part')
                    ws.write_merge(0, 0, 0, 10, 'UNIVERSIDAD ESTATAL DE MILAGRO', title)
                    response = HttpResponse(content_type="application/ms-excel")
                    response[
                        'Content-Disposition'] = 'attachment; filename=Matriz_Participantes_Proyectos' + random.randint(
                        1, 10000).__str__() + '.xls'

                    columns = [
                        (u"NUM", 2000),
                        (u"PROGRAMA", 10000),
                        (u"PROYECTO", 10000),
                        (u"ANIO", 2000),
                        (u"CARRERAS PROYECTO", 10000),
                        (u"CEDULA", 3000),
                        (u"APELLIDOS", 10000),
                        (u"CARRERAS ESTUDIANTE", 10000),
                        (u"HORAS", 2000),
                        (u"TIPO", 2000),
                    ]
                    row_num = 3
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], font_style)
                        ws.col(col_num).width = columns[col_num][1]
                    date_format = xlwt.XFStyle()
                    date_format.num_format_str = 'yyyy/mm/dd'
                    listaparticipantes = ParticipantesMatrices.objects.filter(status=True, matrizevidencia_id=2, proyecto__tipo=tipoproyectos).order_by('inscripcion__persona__apellido1','inscripcion__persona__apellido2')
                    row_num = 4
                    for participantes in listaparticipantes:
                        lista = []
                        i = 0
                        campo1 = participantes.id
                        campo2 = participantes.proyecto.programa.nombre
                        campo3 = participantes.proyecto.nombre
                        campocarrera = ''
                        anio = str(participantes.proyecto.fechainicio)
                        anio = anio.split('-')
                        if participantes.profesor:
                            campo4 = participantes.profesor.persona.cedula
                        if participantes.inscripcion:
                            campo4 = participantes.inscripcion.persona.cedula
                            campocarrera = participantes.inscripcion.carrera.nombre + ' ' + participantes.inscripcion.carrera.alias
                        if participantes.administrativo:
                            campo4 = participantes.administrativo.persona.cedula
                        if participantes.profesor:
                            campo5 = participantes.profesor.persona.nombre_completo_inverso()
                        if participantes.inscripcion:
                            campo5 = participantes.inscripcion.persona.nombre_completo_inverso()
                        if participantes.administrativo:
                            campo5 = participantes.administrativo.persona.nombre_completo_inverso()
                        campo6 = participantes.horas
                        if participantes.profesor:
                            campo7 = participantes.tipoparticipante.nombre
                        if participantes.inscripcion:
                            campo7 = 'ESTUDIANTE'
                        if participantes.administrativo:
                            campo7 = 'ADMINISTRATIVO'

                        ws.write(row_num, 0, campo1, font_style2)
                        ws.write(row_num, 1, campo2, font_style2)
                        ws.write(row_num, 2, campo3, font_style2)
                        if participantes.inscripcion:
                            if participantes.proyecto.carrerasproyecto_set.filter(status=True).exists():
                                carrerasproyectos = participantes.proyecto.carrerasproyecto_set.filter(status=True)
                                for carrerasproy in carrerasproyectos:
                                    lista.append(carrerasproy.carrera.nombre + ',')
                        ws.write(row_num, 3, anio[0], font_style2)
                        ws.write(row_num, 4, str(lista), font_style2)
                        ws.write(row_num, 5, campo4, font_style2)
                        ws.write(row_num, 6, campo5, font_style2)
                        ws.write(row_num, 7, campocarrera, font_style2)
                        ws.write(row_num, 8, campo6, font_style2)
                        ws.write(row_num, 9, campo7, font_style2)
                        row_num += 1
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Programa'
                    form = ProgramasInvestigacionForm(initial={"fechainicio": datetime.now().date()})
                    data['form'] = form
                    return render(request, "inv_programas/add.html", data)
                except Exception as ex:
                    pass

            if action == 'addproyecto':
                try:
                    data['title'] = u'Adicionar Proyecto'
                    form = ProyectoInvestigacionForm
                    data['form'] = form
                    return render(request, "inv_programas/addproyecto.html", data)
                except Exception as ex:
                    pass

            if action == 'editprograma':
                try:
                    data['title'] = u'Editar Programa'
                    data['programas'] = programas = ProgramasInvestigacion.objects.get(pk=request.GET['id'])

                    form = ProgramasInvestigacionForm(initial={'nombre': programas.nombre,
                                                               'fechainicio': programas.fechainicio,
                                                               'fechaplaneado': programas.fechaplaneado,
                                                               'fechareal': programas.fechareal,
                                                               'lineainvestigacion': programas.lineainvestigacion,
                                                               'alcanceterritorial': programas.alcanceterritorial,
                                                               'areaconocimiento': programas.areaconocimiento,
                                                               'subareaconocimiento': programas.subareaconocimiento,
                                                               'subareaespecificaconocimiento': programas.subareaespecificaconocimiento})
                    form.editar(programas)
                    data['form'] = form
                    return render(request, "inv_programas/editprograma.html", data)
                except Exception as ex:
                    pass

            if action == 'editproyecto':
                try:
                    data['title'] = u'Editar Proyecto'
                    data['proyectos'] = proyectos = ProyectosInvestigacion.objects.get(pk=request.GET['id'],tipo=2)

                    form = ProyectoInvestigacionForm(initial={'nombre': proyectos.nombre,
                                                              'fechainicio': proyectos.fechainicio,
                                                              'fechaplaneado': proyectos.fechaplaneado,
                                                              'fechareal': proyectos.fechareal,
                                                              'programa': proyectos.programa,
                                                              # 'tipo': proyectos.tipo,
                                                              'tipoproinstitucion': proyectos.tipoproinstitucion,
                                                              'alcanceterritorial': proyectos.alcanceterritorial,
                                                              'areaconocimiento': proyectos.areaconocimiento,
                                                              'subareaconocimiento': proyectos.subareaconocimiento,
                                                              'subareaespecificaconocimiento': proyectos.subareaespecificaconocimiento})
                    form.editar(proyectos)
                    data['form'] = form
                    return render(request, "inv_programas/editproyecto.html", data)
                except Exception as ex:
                    pass

            if action == 'addevidenciasprogramas':
                try:
                    data['title'] = u'Evidencia Programa'
                    data['form'] = EvidenciaForm
                    data['id'] = request.GET['id']
                    data['idevidencia'] = request.GET['idevidencia']
                    template = get_template("inv_programas/add_evidencia.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": "ok", 'data': json_content})
                except Exception as ex:
                    pass

            if action == 'evidenciasprogramas':
                try:
                    data['title'] = u'Evidencia Programa'
                    data['programas'] = programas = ProgramasInvestigacion.objects.get(pk=request.GET['id'])
                    data['evidencias'] = Evidencia.objects.filter(status=True, matrizevidencia_id=1)
                    data['formevidencias'] = EvidenciaForm()
                    return render(request, "inv_programas/evidenciasprogramas.html", data)
                except Exception as ex:
                    pass

            if action == 'deleteprograma':
                try:
                    data['title'] = u'Eliminar Programa'
                    data['programa'] = ProgramasInvestigacion.objects.get(pk=request.GET['id'])
                    return render(request, "inv_programas/deleteprograma.html", data)
                except Exception as ex:
                    pass

            if action == 'deleteparticipanteproyecto':
                try:
                    data['title'] = u'Eliminar Participante'
                    tipo = request.GET['tipo']
                    data['participante'] = participante = ParticipantesMatrices.objects.get(pk=request.GET['id'])
                    if tipo == '1':
                        data['nombres'] = participante.profesor.persona.nombre_completo()
                    if tipo == '2':
                        data['nombres'] = participante.inscripcion.persona.nombre_completo()
                    if tipo == '3':
                        data['nombres'] = participante.administrativo.persona.nombre_completo()
                    return render(request, "inv_programas/deleteparticipanteproyecto.html", data)
                except Exception as ex:
                    pass

            if action == 'deletepresupuestoproyecto':
                try:
                    data['title'] = u'Eliminar Presupuesto'
                    data['presupuesto'] = PresupuestosProyecto.objects.get(pk=request.GET['id'])
                    return render(request, "inv_programas/deletepresupuestoproyecto.html", data)
                except Exception as ex:
                    pass

            if action == 'listadoproyectos':
                try:
                    data['title'] = u'Listado de Proyectos'
                    # data['proyectos'] = ProyectosInvestigacion.objects.filter(status=True)
                    search = None
                    ids = None
                    tipobus = None
                    inscripcionid = None
                    if 'id' in request.GET:
                        ids = request.GET['id']
                        programasinvestigacion = ProyectosInvestigacion.objects.select_related().filter(pk=ids,tipo=2).order_by('nombre')
                    elif 'inscripcionid' in request.GET:
                        inscripcionid = request.GET['inscripcionid']
                        programasinvestigacion = Graduado.objects.filter(inscripcion__carrera__in=miscarreras).filter(inscripcion__id=inscripcionid)
                    elif 's' in request.GET:
                        search = request.GET['s']
                        tipobus = int(request.GET['tipobus'])
                        data['tipobus'] = tipobus
                        if tipobus == 1:
                            data['tipobus'] = 1
                            programasinvestigacion = ProyectosInvestigacion.objects.select_related().filter(nombre__icontains=search,tipo=2,status=True)
                        if tipobus == 2:
                            data['tipobus'] = 2
                            programasinvestigacion = ProyectosInvestigacion.objects.select_related().filter(fechainicio__year=search,tipo=2,status=True)
                        if tipobus == 3:
                            if ' ' in search:
                                s = search.split(" ")
                                participantematri = ParticipantesMatrices.objects.filter(tipoparticipante__tipo=2, status=True).filter(
                                    Q(profesor__persona__apellido1__contains=s[0]) & Q(
                                        profesor__persona__apellido2__contains=s[1])).distinct()
                                programasinvestigacion = ProyectosInvestigacion.objects.select_related().filter(tipo=2,pk__in=participantematri.values_list('proyecto_id'), status=True)
                            else:
                                participantematri = ParticipantesMatrices.objects.filter(tipoparticipante__tipo=2, status=True).filter(
                                    Q(profesor__persona__nombres__icontains=search) |
                                    Q(profesor__persona__apellido1__icontains=search) |
                                    Q(profesor__persona__apellido2__icontains=search)).distinct()
                                programasinvestigacion = ProyectosInvestigacion.objects.select_related().filter(tipo=2,pk__in=participantematri.values_list('proyecto_id'), status=True)
                    else:
                        data['tipobus'] = 1
                        programasinvestigacion = ProyectosInvestigacion.objects.select_related().filter(status=True,tipo=2).order_by('programa__nombre', 'nombre')
                    paging = MiPaginador(programasinvestigacion, 25)
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
                    data['proyectos'] = page.object_list
                    data['search'] = search if search else ""
                    data['ids'] = ids if ids else ""
                    return render(request, "inv_programas/listaproyectos.html", data)
                except Exception as ex:
                    pass

            if action == 'evidenciasproyectos':
                try:
                    data['title'] = u'Evidencia Proyectos'
                    data['proyectos'] = ProyectosInvestigacion.objects.get(pk=request.GET['id'],tipo=2)
                    data['evidencias'] = Evidencia.objects.filter(status=True, matrizevidencia_id=2)
                    data['formevidencias'] = EvidenciaForm()
                    return render(request, "inv_programas/evidenciasproyectos.html", data)
                except Exception as ex:
                    pass

            if action == 'addevidenciasproyectos':
                try:
                    data['title'] = u'Evidencia Programa'
                    data['form'] = EvidenciaForm
                    data['id'] = request.GET['id']
                    data['idevidencia'] = request.GET['idevidencia']
                    template = get_template("inv_programas/add_evidenciaproyectos.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": "ok", 'data': json_content})
                except Exception as ex:
                    pass

            if action == 'addparticipantesdocentes':
                try:
                    data['title'] = u'Participante Docente'
                    form = ParticipanteProfesorForm()
                    var = request.GET['tipoparticipante']
                    form.adicionar(var)
                    data['form'] = form
                    data['id'] = request.GET['idproyecto']
                    return render(request, "inv_programas/addparticipantedocente.html", data)
                except Exception as ex:
                    pass

            if action == 'addparticipantesestudiantes':
                try:
                    data['title'] = u'Participante Estudiante'
                    data['form'] = ParticipanteEstudianteForm
                    data['id'] = request.GET['idproyecto']
                    return render(request, "inv_programas/addparticipanteestudiante.html", data)
                except Exception as ex:
                    pass

            if action == 'addparticipantesadministrativos':
                try:
                    data['title'] = u'Participante Administrativo'
                    data['form'] = ParticipanteAdministrativoForm
                    data['id'] = request.GET['idproyecto']
                    return render(request, "inv_programas/addparticipanteadministrativo.html", data)
                except Exception as ex:
                    pass

            if action == 'deleteproyecto':
                try:
                    data['title'] = u'Eliminar Proyecto'
                    data['proyecto'] = ProyectosInvestigacion.objects.get(pk=request.GET['id'],tipo=2)
                    return render(request, "inv_programas/deleteproyecto.html", data)
                except Exception as ex:
                    pass

            if action == 'participantesproyectos':
                try:
                    data['title'] = u'Participantes de Proyectos'
                    search = None
                    ids = None
                    inscripcionid = None
                    data['proyecto'] = proyectos = ProyectosInvestigacion.objects.get(pk=request.GET['id'],tipo=2)
                    data['tipoparticipante'] =  ParticipantesTipo.objects.filter(tipo=proyectos.tipo)
                    if 's' in request.GET:
                        search = request.GET['s']
                        if ' ' in search:
                            s = search.split(" ")
                            participantes = ParticipantesMatrices.objects.filter((Q(inscripcion__persona__apellido1__contains=s[0]) &
                                                                                  Q(inscripcion__persona__apellido2__contains=s[1])) |
                                                                                 (Q(profesor__persona__apellido1__contains=s[0]) &
                                                                                  Q(profesor__persona__apellido2__contains=s[1])) |
                                                                                 (Q(administrativo__persona__apellido1__contains=s[0]) &
                                                                                  Q(administrativo__persona__apellido1__contains=s[0])),
                                                                                 status=True, matrizevidencia_id=2, proyecto=proyectos).order_by('inscripcion__persona__apellido1')
                        else:
                            participantes = ParticipantesMatrices.objects.filter(Q(inscripcion__persona__nombres__contains=search) |
                                                                                 Q(inscripcion__persona__apellido1__contains=search) |
                                                                                 Q(inscripcion__persona__apellido2__contains=search) |
                                                                                 Q(inscripcion__persona__cedula__contains=search) |
                                                                                 Q(profesor__persona__nombres__contains=search) |
                                                                                 Q(profesor__persona__apellido1__contains=search) |
                                                                                 Q(profesor__persona__apellido2__contains=search) |
                                                                                 Q(profesor__persona__cedula__contains=search) |
                                                                                 Q(administrativo__persona__nombres__contains=search) |
                                                                                 Q(administrativo__persona__apellido1__contains=search) |
                                                                                 Q(administrativo__persona__apellido2__contains=search) |
                                                                                 Q(administrativo__persona__cedula__contains=search),
                                                                                 status=True, matrizevidencia_id=2, proyecto=proyectos).order_by('inscripcion__persona__apellido1')
                    else:
                        participantes = proyectos.participantesmatrices_set.filter(status=True, matrizevidencia_id=2).order_by('-tipoparticipante', 'inscripcion__persona__apellido1')
                    paging = MiPaginador(participantes, 25)
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
                    data['participantes'] = page.object_list
                    data['search'] = search if search else ""
                    data['ids'] = ids if ids else ""
                    return render(request, "inv_programas/participantesproyectos.html", data)
                except Exception as ex:
                    pass

            if action == 'carrerasproyectos':
                try:
                    data['title'] = u'Carreras de Proyecto'
                    data['proyecto'] = proyectos = ProyectosInvestigacion.objects.get(pk=request.GET['id'],tipo=2)
                    data['carreras'] = Carrera.objects.order_by('nombre')
                    data['carrerasproyecto'] = CarrerasProyecto.objects.filter(status=True, proyecto=proyectos)
                    return render(request, "inv_programas/carrerasproyectos.html", data)
                except Exception as ex:
                    pass

            if action == 'presupuestoproyectos':
                try:
                    data['title'] = u'Presupuesto de Proyecto'
                    data['proyecto'] = proyectos = ProyectosInvestigacion.objects.get(pk=request.GET['id'],tipo=2)
                    data['presupuestoproyecto'] = presupuesto = proyectos.presupuestosproyecto_set.filter(status=True) #PresupuestosProyecto.objects.filter(status=True, proyecto=proyectos)
                    data['totalplanificado'] = presupuesto.aggregate(totoplanificado=Sum('planificado'))['totoplanificado']
                    data['totalejecutado'] = presupuesto.aggregate(totejecutado=Sum('ejecutado'))['totejecutado']
                    data['formpresupuesto'] = PresupuestoProyectoForm
                    return render(request, "inv_programas/presupuestoproyectos.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)
        else:
            data['title'] = u'Listado de Programas'
            search = None
            ids = None
            inscripcionid = None
            if 'id' in request.GET:
                ids = request.GET['id']
                programasinvestigacion = ProgramasInvestigacion.objects.filter(inscripcion__carrera__in=miscarreras).filter(pk=ids).order_by('nombre')
            # elif 'inscripcionid' in request.GET:
            #     inscripcionid = request.GET['inscripcionid']
            #     programasinvestigacion = Graduado.objects.filter(inscripcion__carrera__in=miscarreras).filter(inscripcion__id=inscripcionid)
            elif 's' in request.GET:
                search = request.GET['s']
                if search.isdigit():
                    programasinvestigacion = ProgramasInvestigacion.objects.select_related().filter(pk=search, status=True)
                else:
                    programasinvestigacion = ProgramasInvestigacion.objects.select_related().filter(nombre__icontains=search, status=True)
            else:
                programasinvestigacion = ProgramasInvestigacion.objects.select_related().filter(status=True).order_by('nombre')
            paging = MiPaginador(programasinvestigacion, 25)
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
            data['programas'] = page.object_list
            data['search'] = search if search else ""
            data['ids'] = ids if ids else ""
            data['inscripcionid'] = inscripcionid if inscripcionid else ""
            data['carreras'] = Carrera.objects.all().order_by('nombre')
            return render(request, "inv_programas/view.html", data)