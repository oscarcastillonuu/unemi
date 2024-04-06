# -*- coding: UTF-8 -*-
from _decimal import Decimal

from django import template
from django.core.files.storage import default_storage
from django.db.models import Q,  F, Value, Count, Case, When, ExpressionWrapper, FloatField
from django.db.models.functions import Concat, Coalesce
import settings
from inno.models import MateriaGrupoTitulacion, TipoActaFirma
from sga.funciones import fechaletra_corta, fields_model, field_default_value_model, trimestre, null_to_decimal, \
    convertir_fecha, convertir_fecha_invertida
from sga.models import MESES_CHOICES, Persona, Sesion, Carrera, PracticasTutoria, PracticasPreprofesionalesInscripcion, \
    AgendaPracticasTutoria, ActividadConvenio, Modulo, DIAS_CHOICES, Clase, AsignaturaMallaPredecesora, MateriaAsignada, \
    MateriaTitulacion
from datetime import datetime, timedelta, date

register = template.Library()


def existe_validacion(pk, dia):
    from sagest.models import RecaudacionBanco
    incorrecto = False
    qs = RecaudacionBanco.objects.filter(cuentabanco_id=int(pk), fecha=convertir_fecha(dia))
    if qs.exists():
        incorrecto = qs[0].incorrecto
    return incorrecto


@register.simple_tag
def ver_valor_dict(diccionario, llave):
    return diccionario[llave]


@register.simple_tag
def ver_total_tutorias(mes, dia, anio, profesor):
    fecha = convertir_fecha(str(dia) + '-' + str(mes) + '-' + str(anio))
    return PracticasTutoria.objects.select_related('practica').filter(fechainicio=fecha, fechafin=fecha,
                                                                      practica__tutorunemi=profesor,
                                                                      status=True).count()


@register.simple_tag
def ver_total_tutorias_agendadas(mes, dia, anio, profesor):
    fecha = convertir_fecha(str(dia) + '-' + str(mes) + '-' + str(anio))
    return AgendaPracticasTutoria.objects.select_related('docente').filter(fecha=fecha, docente=profesor,
                                                                           status=True).count()


@register.simple_tag
def ver_total_actividad_convenio(mes, dia, anio, convenio):
    fecha = convertir_fecha(str(dia) + '-' + str(mes) + '-' + str(anio))
    return ActividadConvenio.objects.select_related('actividad').filter(fecha=fecha, status=True,
                                                                        convenioempresa=convenio).count()


def callmethod(obj, methodname):
    method = getattr(obj, methodname)
    if "__callArg" in obj.__dict__:
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()


def args(obj, arg):
    if "__callArg" not in obj.__dict__:
        obj.__callArg = []
    obj.__callArg.append(arg)
    return obj


def suma(var, value=1):
    try:
        return var + value
    except Exception as ex:
        pass


def resta(var, value=1):
    return var - value


def restanumeros(var, value):
    return var - value

def cincoacien(valor):
    return round((valor * 100 / 5), 2)

def multiplicanumeros(var, value):
    return Decimal(Decimal(var).quantize(Decimal('.01')) * Decimal(value).quantize(Decimal('.01'))).quantize(
        Decimal('.01'))


def divide(value, arg):
    return int(value) / int(arg) if arg else 0


def porciento(value, arg):
    return round(value * 100 / float(arg), 2) if arg else 0


def calendarbox(var, dia):
    return var[dia]


def barraporciento(var, total):
    if int(total) == 0:
        return 0
    else:
        if settings.TIPO_RESPUESTA_EVALUACION == 3:
            return int((int(var) / 3) * total)
        elif settings.TIPO_RESPUESTA_EVALUACION == 1:
            return int((int(var) / 5) * total)
        elif settings.TIPO_RESPUESTA_EVALUACION == 2:
            return int((int(var) / 10) * total)


def calendarboxdetails(var, dia):
    lista = var[dia]
    result = []
    for x in lista:
        b = [x.split(',')[0], x.split(',')[1]]
        result.append(b)
    return result


@register.simple_tag
def traducir_mes(value):
    return ' '.join(str(value).lower().replace('january', 'Enero') \
                    .replace('february', 'Febrero') \
                    .replace('march', 'Marzo') \
                    .replace('april', 'Abril') \
                    .replace('may', 'Mayo') \
                    .replace('june', 'Junio') \
                    .replace('july', 'Julio') \
                    .replace('august', 'Agosto') \
                    .replace('september', 'Septiembre') \
                    .replace('october', 'Octubre') \
                    .replace('november', 'Noviembre') \
                    .replace('december', 'Diciembre').split(' ')[0:2])


@register.simple_tag
def traducir_dia(value):
    return ' '.join(str(value).lower().replace('monday', 'Lunes') \
                    .replace('tuesday', 'Martes') \
                    .replace('wednesday', 'Miercoles') \
                    .replace('thursday', 'Jueves') \
                    .replace('friday', 'Viernes') \
                    .replace('saturday', 'Sabado').split(' ')[0:2])


@register.simple_tag
def gedc_texto_universidad(value):
    return str(value).replace('UNIVERSIDAD', 'UNI.').replace('INSTITUTO', 'INST.')


def calmodeloevaluaciondocente2015(periodo, docente):
    try:
        from django.db.models import Avg
        from sga.models import ResumenParcialEvaluacionIntegral, null_to_numeric
        notaporcentaje = ResumenParcialEvaluacionIntegral.objects.filter(profesor=docente, proceso=periodo).order_by(
            'materia__asignaturamalla__malla__carrera__id', 'materia__asignaturamalla__nivelmalla__id')
        return round(null_to_numeric(notaporcentaje.aggregate(prom=Avg('totalmateriadocencia'))['prom']), 2)
    except Exception as ex:
        return 0


def calmodeloevaluaciondocente(periodoid, docente):
    try:
        from sga.models import ResumenFinalEvaluacionAcreditacion
        porcentaje = ResumenFinalEvaluacionAcreditacion.objects.get(distributivo__profesor=docente,
                                                                    distributivo__periodo=periodoid)
        return round(((porcentaje.resultado_total * 100) / 5), 2)
    except Exception as ex:
        return 0


def calevaluaciondocente(periodoid, docente):
    try:
        from django.db.models import Avg
        from sga.models import MigracionEvaluacionDocente, null_to_numeric
        migra = MigracionEvaluacionDocente.objects.filter(idprofesor=docente, idperiodo=periodoid).order_by('tipoeval',
                                                                                                            'idperiodo',
                                                                                                            'carrera',
                                                                                                            'semestre',
                                                                                                            'materia')
        return round(null_to_numeric(migra.filter(modulo=0).aggregate(prom=Avg('promedioasignatura'))['prom']), 2)
    except Exception as ex:
        return 0


def gedc_calculos(row, filtro):
    from sga.models import GEDCRespuestas, GEDC_GRUPO, GENEROS_ENCUESTAS
    import statistics as stats
    grupoid = row['cab__cab__grupo'] if 'cab__cab__grupo' in row else None
    paisid = row['cab__pais__id'] if 'cab__pais__id' in row else None
    universidad_nombre = row['cab__universidad__nombre'] if 'cab__universidad__nombre' in row else ''
    generoid = row['cab__genero'] if 'cab__genero' in row else None
    preguntaid = row['indicador__id'] if 'indicador__id' in row else None
    frespuesta = Q(status=True) & Q(respcalificacion_inversa__isnull=False)
    if grupoid:
        frespuesta = frespuesta & Q(cab__cab__grupo=grupoid)
    if paisid:
        frespuesta = frespuesta & Q(cab__pais__id=paisid)
    if universidad_nombre:
        frespuesta = frespuesta & Q(cab__universidad__nombre=universidad_nombre)
    if generoid:
        frespuesta = frespuesta & Q(cab__genero=generoid)
    if preguntaid:
        frespuesta = frespuesta & Q(indicador__id=preguntaid)
    listaRespuestas = GEDCRespuestas.objects.filter(cab__cab__publicar=True, cab__pais__isnull=False,
                                                    cab__universidad__isnull=False).filter(
        frespuesta & filtro).values_list('respcalificacion_inversa', flat=True)
    totpreguntas = listaRespuestas.count()
    media = round(stats.mean(list(listaRespuestas)), 2)
    desvestandar = round(stats.pstdev(list(listaRespuestas)), 2)
    return [totpreguntas, media, desvestandar]


def gedc_calculos_grafica(row, filtro):
    try:
        from sga.models import GEDCRespuestas, GEDC_GRUPO, GENEROS_ENCUESTAS
        import statistics as stats
        grupoid = filtro['cab__grupo'] if 'cab__grupo' in filtro else None
        paisid = filtro['pais__id'] if 'pais__id' in filtro else None
        universidad_nombre = filtro['universidad__nombre'] if 'universidad__nombre' in filtro else ''
        generoid = filtro['genero'] if 'genero' in filtro else None
        frespuesta = Q(status=True) & Q(respcalificacion_inversa__isnull=False)
        if grupoid:
            frespuesta = frespuesta & Q(cab__cab__grupo=grupoid)
        if paisid:
            frespuesta = frespuesta & Q(cab__pais__id=paisid)
        if universidad_nombre:
            frespuesta = frespuesta & Q(cab__universidad__nombre=universidad_nombre)
        if generoid:
            frespuesta = frespuesta & Q(cab__genero=generoid)
        listaRespuestas = GEDCRespuestas.objects.filter(cab__cab__publicar=True, cab__pais__isnull=False,
                                                        cab__universidad__isnull=False,
                                                        indicador__factores_id=row.pk).filter(frespuesta).values_list(
            'respcalificacion_inversa', flat=True)
        totpreguntas = listaRespuestas.count()
        if totpreguntas > 0:
            media = round(stats.mean(list(listaRespuestas)), 2)
            desvestandar = round(stats.pstdev(list(listaRespuestas)), 2)
            return [totpreguntas, media, desvestandar]
        else:
            return [0, 0, 0]
    except Exception as ex:
        return [0, 0, 0]


def calendarboxdetailsmostrar(var, dia):
    return var[dia]


def calendarboxdetails2(var, dia):
    lista = var[dia]
    result = []
    b = []
    for x in lista:
        b.append(x[0])
        b.append(x[1])
        b.append(x[2])
        b.append(x[3])
        result.append(b)
    return result


def calendarboxdetailspracticas(var, dia):
    lista = var[dia]
    result = []
    b = []
    for x in lista:
        b.append(x[0])
        b.append(x[1])
        b.append(x[2])
        b.append(x[3])
        b.append(x[4])
        b.append(x[5])
        b.append(x[6])
        result.append(b)
    return result


def predecesoratitulacion(idasignaturamalla):
    listaprodecesoratitulacion = AsignaturaMallaPredecesora.objects.filter(asignaturamalla_id=idasignaturamalla,
                                                                           predecesora__validarequisitograduacion=True,
                                                                           status=True)
    return listaprodecesoratitulacion


def pertenecepredecesoratitulacion(idasignaturamalla):
    listaprodecesoratitulacion = AsignaturaMallaPredecesora.objects.filter(predecesora_id=idasignaturamalla,
                                                                           status=True)
    return listaprodecesoratitulacion


def actasgradopendiente(idpersona):
    faltantes = TipoActaFirma.objects.values('id').filter(persona_id=idpersona, tipoacta__tipo=5, turnofirmar=True,
                                                          firmado=False, status=True).count()
    return faltantes


def actasconsolidadaspendientes(idpersona):
    faltantes = TipoActaFirma.objects.values('id').filter(persona_id=idpersona, tipoacta__tipo=6, turnofirmar=True,
                                                          firmado=False, status=True).count()
    return faltantes


def firmaactagradosistema(idgraduado):
    return TipoActaFirma.objects.values('id').filter(tipoacta__graduado_id=idgraduado, tipoacta__tipo=5,
                                                     status=True).exists()


def notafinalmateriatitulacion(idmateriatitulacion, idmate):
    lista = []
    listanotas = []
    sumatoria = 0
    estadonota = 1
    matetitulacion = MateriaTitulacion.objects.get(pk=idmateriatitulacion)
    listadomateriagrupo = MateriaGrupoTitulacion.objects.filter(
        grupo__materia_id=matetitulacion.materiaasignada.materia.id, status=True).order_by('orden')
    for materiagrupo in listadomateriagrupo:
        listaprodecesoratitulacion = MateriaAsignada.objects.filter(
            matricula__inscripcion_id=matetitulacion.materiaasignada.matricula.inscripcion.id,
            materia__asignaturamalla_id=materiagrupo.asignaturamalla.id, status=True).order_by('-id')
        if MateriaAsignada.objects.filter(
                matricula__inscripcion_id=matetitulacion.materiaasignada.matricula.inscripcion.id,
                materia__asignaturamalla_id=materiagrupo.asignaturamalla.id, status=True):
            calculanota = round((listaprodecesoratitulacion[0].notafinal * materiagrupo.puntaje) / 100, 0)
            sumatoria = sumatoria + calculanota
            lista.append([calculanota, materiagrupo.nombre])
    if sumatoria >= 70:
        estadonota = 2
    listanotas.append([lista, 'NOTA FINAL', sumatoria, estadonota])
    return listanotas


def listar_campos_tabla(modelo, dbname, schema='public'):
    from django.db import connections
    query = "SELECT column_name FROM information_schema.columns WHERE table_schema = '{}' AND table_name   = '{}';".format(
        schema, modelo)
    cursor = connections[dbname].cursor()
    cursor.execute(query)
    campos = list([c[0] for c in cursor.fetchall()])
    return campos


def tieneestudiantepracticas(detalle, dis_docente):
    resp = False
    if detalle.criteriodocenciaperiodo.criterio.pk == 6:
        dis_periodo = detalle.distributivo.periodo
        # practicas = PracticasPreprofesionalesInscripcion.objects.values_list('id').filter(Q(tutorunemi=dis_docente),
        #                                                                                 ((Q(fechadesde__gte=dis_periodo.inicio) & Q(fechadesde__lte=dis_periodo.fin)) |
        #                                                                                 (Q(fechahasta__gte=dis_periodo.inicio) & Q(fechahasta__lte=dis_periodo.fin))),
        #                                                                                 Q(estadosolicitud=2)).distinct()
        practicas = PracticasPreprofesionalesInscripcion.objects.values_list('id').filter(
            preinscripcion__preinscripcion__periodo__isnull=False, preinscripcion__preinscripcion__periodo=dis_periodo,
            tutorunemi=dis_docente, estadosolicitud=2).distinct()
        resp = practicas.exists()
    return resp


@register.filter
def contar_estado_solicitud(practica, estadosolicitud):
    return PracticasPreprofesionalesInscripcion.objects.filter(
        supervisor=practica.supervisor,
        preinscripcion__preinscripcion__periodo=practica.preinscripcion.preinscripcion.periodo,
        inscripcion__carrera=practica.inscripcion.carrera, estadosolicitud=estadosolicitud).count()


def times(number):
    return range(number)


def multipilca(number):
    return number * 5


def llevaraporcentaje(number):
    valor = (number * 100) / 5
    return null_to_decimal(valor, 2)


def nombremescorto(fecha):
    if type(fecha) is str:
        return "%s" % fecha[:3].capitalize()
    else:
        return "%s %s" % (fecha.day, MESES_CHOICES[fecha.month - 1][1][:3].capitalize())


def numerotemas(numero):
    num = ''
    num = numero * 2;
    if num == 1:
        num = 2;
    return str(num - 1) + '-' + str(num)


def numerotemasdiv(numero):
    num = ''
    num = numero * 2;
    return int(num)


def substraer(value, rmostrar):
    return "%s" % value[:rmostrar]


def substraerconpunto(value, rmostrar):
    if len(value) > int(rmostrar):
        return "%s..." % value[:rmostrar]
    else:
        return "%s" % value[:rmostrar]


def substraersinpuntohasta(value, rmostrar):
    if len(value) > int(rmostrar):
        return "%s" % value[:rmostrar]
    else:
        return "%s" % value[:rmostrar]


def substraersinpuntodesde(value, rmostrar):
    if len(value) > int(rmostrar):
        return "%s" % value[rmostrar:]
    else:
        return ""


def cambiarlinea(value, cant):
    cadena = ''
    c = 0
    for caracter in value:
        c = c + 1
        if c > cant:
            cadena = cadena + '<br />' + caracter
            c = 0
        else:
            cadena = cadena + "" + caracter
    return cadena


def contarcaracter(texto, cantidad):
    return len(texto) >= cantidad


def extraer(campo, cantidad):
    return campo[0:cantidad]


def nombremes(fecha):
    if type(fecha) is int:
        return "%s" % MESES_CHOICES[fecha - 1][1]
    elif type(fecha) is str:
        return ""
    else:
        return "%s" % MESES_CHOICES[fecha.month - 1][1]


def title2(texto=''):
    return " ".join([x.capitalize() if x.__len__() > 3 else x.lower() for x in f"{texto}".lower().split(' ')])


def numero_a_letras(numero):
    from sga.funciones import numero_a_letras
    return numero_a_letras(numero)


def numeromes(fecha):
    return trimestre(int(fecha.strftime("%m")))


def fechapermiso(fecha):
    if datetime.now().date() >= fecha:
        return True
    else:
        return False


def entrefechas(finicio, ffin):
    if datetime.now().date() >= finicio and datetime.now().date() <= ffin:
        return True
    else:
        return False


def datename(fecha):
    return u"%s de %s de %s" % (str(fecha.day).rjust(2, "0"), nombremes(fecha=fecha).capitalize(), fecha.year)


def datetimename(dt):
    return u"%s de %s del %s %s:%s" % (
        str(dt.day).rjust(2, "0"), nombremes(fecha=dt).capitalize(), dt.year, str(dt.hour).rjust(2, "0"),
        str(dt.minute).rjust(2, "0"))


def sumarfecha(fecha):
    meses = int(round((((datetime.now().date() - fecha).days) / 30), 0))
    return meses


def sumarvalores(n1, n2):
    suma = int(n1) + int(n2)
    return suma


def nombrepersona(usuario):
    if Persona.objects.filter(usuario=usuario).exists():
        return Persona.objects.filter(usuario=usuario)[0]
    return None


def encrypt(value):
    if value == None:
        return value
    myencrip = ""
    if type(value) != str:
        value = str(value)
    i = 1
    for c in value.zfill(20):
        myencrip = myencrip + chr(int(44450 / 350) - ord(c) + int(i / int(9800 / 4900)))
        i = i + 1
    return myencrip


def encrypt_alu(value):
    if value == None:
        return value
    myencrip = ""
    if type(value) != str:
        value = str(value)
    i = 1
    for c in value.zfill(20):
        myencrip = myencrip + chr(int(44450 / 350) - ord(c) + int(i / int(14700 / 4900)))
        i = i + 1
    return myencrip


def solo_caracteres(texto):
    acentos = [u'á', u'é', u'í', u'ó', u'ú', u'Á', u'É', u'Í', u'Ó', u'Ú', u'ñ', u'Ñ']
    alfabeto = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F',
                'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '.',
                '/', '#', ',', ' ']
    resultado = ''
    for letra in texto:
        if letra in alfabeto:
            resultado += letra
        elif letra in acentos:
            if letra == u'á':
                resultado += 'a'
            elif letra == u'é':
                resultado += 'e'
            elif letra == u'í':
                resultado += 'i'
            elif letra == u'ó':
                resultado += 'o'
            elif letra == u'ú':
                resultado += 'u'
            elif letra == u'Á':
                resultado += 'A'
            elif letra == u'É':
                resultado += 'E'
            elif letra == u'Í':
                resultado += 'I'
            elif letra == u'Ó':
                resultado += 'O'
            elif letra == u'Ú':
                resultado += 'U'
            elif letra == u'Ñ':
                resultado += 'N'
            elif letra == u'ñ':
                resultado += 'n'
        else:
            resultado += '?'
    return resultado


def ceros(numero, cantidad):
    return str(numero).zfill(cantidad)


def fechamayor(fecha1, fecha2):
    if fecha1.date() > fecha2:
        return True
    else:
        return False


def fechamayor_aux(fecha1, fecha2):
    if convertir_fecha(fecha1) > fecha2:
        return True
    else:
        return False

def calculaedad(fecha1, fecha_actual):
    return fecha_actual.year - fecha1.year - ((fecha_actual.month, fecha_actual.day) < (fecha1.month, fecha1.day))


def transformar_n_l(n):
    arreglo = ['PRIMERO', 'SEGUNDO', 'TERCERO', 'CUARTO', 'QUINTO', 'SEXTO', 'SEPTIMO', 'OCTAVO', 'NOVENO']
    return arreglo[n - 1] if n else ""


def sumauno(numero):
    return numero + 1


def transformar_mes(n):
    arreglo = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
               "Noviembre", "Diciembre"]
    return arreglo[n - 1] if n else "SIN MES"


def diaenletra(dia):
    arreglo = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
    return arreglo[int(dia) - 1]


def diaenletra_fecha(fecha):
    dia = fecha.isoweekday()
    return DIAS_CHOICES[dia - 1][1]


def diaisoweekday(fecha):
    return fecha.isoweekday()


def traernombre(idsesion):
    nombresesion = Sesion.objects.get(pk=idsesion)
    return nombresesion.nombre


def traernombrecarrera(idcarrera):
    nombre = Carrera.objects.get(pk=idcarrera)
    return nombre.nombre


# NO TUVE MAS REMEDIO QUE HACER FUNCIONES MUERTAS PARA UN SOLO REPORTE PIDO MIL DISCULPAS A MIS ADMIRADORES ATT. CLOCKEM
def sumar_fm(value, lista):
    su = 0
    for l in lista:
        if value == l[0]:
            su += l[3]
    return su


def sumar_fh(value, lista):
    su = 0
    for l in lista:
        if value == l[0]:
            su += l[4]
    return su


def sumar_cm(value, lista):
    su = 0
    for l in lista:
        if value[1] == l[1] and value[0] == l[0]:
            su += l[3]
    return su


def sumar_ch(value, lista):
    su = 0
    for l in lista:
        if value[1] == l[1] and value[0] == l[0]:
            su += l[4]
    return su


def sumar_th(value, lista):
    su = 0
    for l in lista:
        su += l[4]
    return su


def sumar_tm(value, lista):
    su = 0
    for l in lista:
        su += l[3]
    return su


def sumar_pagineo(totalpagina, contador):
    suma = totalpagina + contador
    return suma


def colores(colores, indice):
    color = colores[indice]
    return color


# AQUI TERMINA LAS FUNCIONES NO REUTILIZABLES :(

def rangonumeros(_min, args=None):
    _max, _step = None, None
    if args:
        if not isinstance(args, int):
            _max, _step = map(int, args.split(','))
        else:
            _max = args
    args = filter(None, (_min, _max + 1, _step))
    return range(*args)


def splitcadena(string, sep):
    return string.split(sep)


def tranformarstring(valor):
    return str(valor)


def mod4(valor):
    return divmod(valor, 4)[1]


@register.filter
def convert_str_date(value):
    return str(value)[:10]


def num_notificaciones_modulo(idm, perfil):
    if not Modulo.objects.values("id").filter(pk=idm).exists():
        return 0
    eModulo = Modulo.objects.get(pk=idm)
    if not eModulo.tiene_notificaciones(perfil.persona.id, perfil.id):
        return 0
    return eModulo.num_notificaciones(perfil.persona.id, perfil.id)


def get_manual_usuario_modulo(idm, perfil):
    if not Modulo.objects.values("id").filter(pk=idm).exists():
        return None
    eModulo = Modulo.objects.get(pk=idm)
    return eModulo.get_manual_user(perfil)


@register.inclusion_tag('pwa.html', takes_context=True)
def progressive_web_app_meta_i(context):
    # Pass all PWA_* settings into the template
    return {
        setting_name: getattr(settings, setting_name)
        for setting_name in dir(settings)
        if setting_name.startswith('PWA_')
    }


@register.filter
def split(val, sep):
    return val.split(sep)


@register.simple_tag
def get_image_path(image_path):
    path = default_storage.path(image_path)
    return path


def obtener_tribunal(obj):
    return obj.tribunaltematitulacionposgradomatricula_set.filter(status=True).first()


@register.filter
def obtener_numero_de_revision_tribunal(obj):
    from posgrado.models import Revision
    mensaje = ""
    tribunal = obtener_tribunal(obj)
    revisiones = Revision.objects.filter(status=True, tribunal=tribunal)
    if revisiones.exists():
        cantidad_revision = revisiones.count()
    else:
        cantidad_revision = 0

    if cantidad_revision == 0:
        mensaje = "Informe de revisión no generado"

    if cantidad_revision == 1:
        mensaje = "Primera revisión del trabajo de titulación"

    if cantidad_revision == 2:
        mensaje = "Segunda revisión del trabajo de titulación"

    if cantidad_revision == 3:
        mensaje = "Tercera revisión del trabajo de titulación"

    return mensaje


def obtener_tribunal_pareja(obj):
    return obj.tribunaltematitulacionposgradomatricula_set.filter(status=True).first()


@register.filter
def obtener_numero_de_revision_tribunal_pareja(obj):
    from posgrado.models import Revision
    mensaje = ""
    tribunal = obtener_tribunal_pareja(obj)
    revisiones = Revision.objects.filter(status=True, tribunal=tribunal)
    if revisiones.exists():
        cantidad_revision = revisiones.count()
    else:
        cantidad_revision = 0

    if cantidad_revision == 0:
        mensaje = "Informe de revisión no generado"

    if cantidad_revision == 1:
        mensaje = "Primera revisión del trabajo de titulación"

    if cantidad_revision == 2:
        mensaje = "Segunda revisión del trabajo de titulación"

    if cantidad_revision == 3:
        mensaje = "Tercera revisión del trabajo de titulación"

    return mensaje


@register.filter
def convertir_tipo_oracion(texto):
    try:
        oraciones = texto.split('.')
        full = [oracion.strip() for oracion in oraciones if oracion.strip() != '']
        final = ''
        for oracion in full:
            final += "".join(oracion[0].upper() + oracion[1:].lower())
        return final
    except:
        return ''


@register.filter
def concat_str_int(value, args):
    try:
        return int(str(int(value)) + str(int(args)))
    except:
        return ''


@register.simple_tag
def contador_lista(page, forloop_counter):
    return ((page.number - 1) * page.paginator.per_page) + forloop_counter


def realizo_busqueda(url_vars='', numero=1):
    return len(url_vars.split('&')) - numero > 1


@register.simple_tag
def materias_imparte_periodo_seguimiento_silabo(obj, periodo, carreras, carrerasselected, asignaturaid, nivelid, paraleloid, super_directivos):
    from sga.models import Materia
    filtro = Q(status=True)
    if int(asignaturaid) > 0:
        filtro = filtro & Q(asignaturamalla__asignatura__id=asignaturaid)
    if int(nivelid) > 0:
        filtro = filtro & Q(asignaturamalla__nivelmalla__id=nivelid)
    if paraleloid != '0':
        filtro = filtro & Q(paralelo=paraleloid)
    if super_directivos == False:
        return Materia.objects.filter(filtro, profesormateria__activo=True, profesormateria__status=True,
                                      asignaturamalla__malla__carrera__id__in=carreras,
                                      nivel__periodo=periodo, profesormateria__tipoprofesor__in=[1, 14],
                                      profesormateria__profesor=obj, profesormateria__principal = True, profesormateria__hora__gt=0).distinct().order_by('asignaturamalla__malla__carrera__nombre',
            'asignaturamalla__nivelmalla__nombre')
    else:
        if int(carrerasselected) > 0:
            filtro = filtro & Q(asignaturamalla__malla__carrera__id=carrerasselected)
        else:
            filtro = filtro & Q(asignaturamalla__malla__carrera__id__in=carreras)
        return Materia.objects.filter(filtro, profesormateria__activo=True, profesormateria__status=True,
                                      nivel__periodo=periodo, profesormateria__tipoprofesor__in=[1, 14],
                                      profesormateria__profesor=obj, profesormateria__principal = True, profesormateria__hora__gt=0).distinct().order_by('asignaturamalla__malla__carrera__nombre',
            'asignaturamalla__nivelmalla__nombre')


@register.simple_tag
def carreras_imparte2(obj, materias):
    carreras = []
    try:
        # materias = obj.materias_imparte_periodo_seguimiento_silabo()
        for materia in materias:
            carreras.append(materia.asignaturamalla.malla.carrera)
        return set(carreras)
    except Exception as ex:
        return None


@register.simple_tag
def informe_actividades_mensual_docente_v4_extra(obj, periodo, fechaini, fechafin, tipo, tablepromedio=None):
    from sga.models import ProfesorDistributivoHoras, ProfesorMateria
    fini = convertir_fecha_invertida(fechaini)
    ffin = convertir_fecha_invertida(fechafin)
    distributivo = ProfesorDistributivoHoras.objects.filter(periodo=periodo, profesor=obj, status=True)
    if tipo == 'TODO' or tipo == 'FACULTAD':
        if not distributivo.exists():
            mensaje = "No registra actividades de docencia, verifique el periodo."
            raise NameError('Error')
    if distributivo:
        distributivo = distributivo[0]
    return {'distributivo': distributivo, 'fini': fini, 'ffin': ffin}


@register.simple_tag
def horarios_contenido_profesor_extra(obj, profesor, materia, fechaini, fechafin):
    try:
        from sga.models import DetalleDistributivo, GuiaEstudianteSilaboSemanal, TareaPracticaSilaboSemanal, \
            TipoProfesor, ProfesorMateria, ClaseActividad, Silabo, CompendioSilaboSemanal, VideoMagistralSilaboSemanal, \
            ForoSilaboSemanal, TareaSilaboSemanal, TestSilaboSemanalAdmision, TestSilaboSemanal, \
            DiapositivaSilaboSemanal, MaterialAdicionalSilaboSemanal, SilaboSemanal
        periodorelacionado = False
        listado = []
        periodo = obj.periodo
        fechaactual = datetime.now().date()
        periodos = [obj.periodo.pk]
        detalledistributivo = DetalleDistributivo.objects.get(criteriodocenciaperiodo=obj,
                                                              distributivo__profesor=profesor, status=True)
        fechasactividades = detalledistributivo.actividaddetalledistributivo_set.filter(status=True)[0]
        fechaini = periodo.inicio if fechaini < periodo.inicio else fechaini
        if obj.periodosrelacionados.exists():
            periodorelacionado = True
            periodos = []
            for per in obj.periodosrelacionados.values_list('id', flat=True):
                periodos.append(per)
        if periodos:
            periodorelacionado = ProfesorMateria.objects.values('id').filter(profesor=profesor, materia=materia,
                                                                             materia__nivel__periodo_id__in=periodos).distinct().exists()

        profesormateria = ProfesorMateria.objects.filter(profesor=profesor, materia__nivel__periodo_id__in=periodos,
                                                         materia=materia,
                                                         activo=True, materia__fin__gte=fechasactividades.desde,
                                                         materia__inicio__lte=fechasactividades.hasta).exclude(
            tipoprofesor_id=15).only('materia').distinct()
        for m in profesormateria:
            if not m.materia.tiene_cronograma():
                return 0
        claseactividad = ClaseActividad.objects.filter(detalledistributivo__criteriodocenciaperiodo=obj,
                                                       detalledistributivo__distributivo__profesor=profesor,
                                                       status=True).order_by('inicio', 'dia', 'turno__comienza')

        # para saber total de horas en el mes
        diasclas = claseactividad.values_list('dia', 'turno_id')
        dt = fechaini
        end = fechafin
        step = timedelta(days=1)
        listaretorno = []
        result = []
        while dt <= end:
            dias_nolaborables = obj.periodo.dias_nolaborables(dt)
            if not dias_nolaborables:
                for dclase in diasclas:
                    if dt.isocalendar()[2] == dclase[0]:
                        result.append(dt.strftime('%Y-%m-%d'))
            dt += step
        # if periodo.clasificacion == 1:
        listadotipoprofesor = TipoProfesor.objects.filter(
            pk__in=ProfesorMateria.objects.values_list('tipoprofesor_id').filter(profesor=profesor, materia=materia,
                                                                                 materia__nivel__periodo_id__in=periodos,
                                                                                 tipoprofesor_id__in=[1, 2, 5, 6, 10,
                                                                                                      11, 12, 14, 16],
                                                                                 activo=True,
                                                                                 materia__fin__gte=fechasactividades.desde,
                                                                                 materia__inicio__lte=fechasactividades.hasta).exclude(
                materia__modeloevaluativo_id__in=[26]).distinct())
        resultadominimoplanificar = 0
        resultadoplanificados = 0
        resultadoparciales = '-'
        resultadoporcentajes = 0
        resultadoporcentajessyl = 0
        sumatoriaindice = 0
        sumatoriaindicesyl = 0
        resultadototal = 0
        subtipo_docentes = 0
        listasilabofaltasilabo = []
        for ltipoprofesor in listadotipoprofesor:
            subtipo_docentes = 1
            nivelacion = False
            listadosilabos = Silabo.objects.filter(status=True, materia_id__in=ProfesorMateria.objects.values_list(
                'materia_id').filter(profesor=profesor, materia__nivel__periodo_id__in=periodos, materia=materia,
                                     tipoprofesor=ltipoprofesor, activo=True, materia__fin__gte=fechasactividades.desde,
                                     materia__inicio__lte=fechasactividades.hasta).distinct())
            if listadosilabos:
                if listadosilabos.filter(materia__asignaturamalla__malla__carrera__coordinacion__id=9).exists():
                    subtipo_docentes += 1
                    nivelacion = True
                    listadosilabos = Silabo.objects.filter(status=True,
                                                           materia_id__in=ProfesorMateria.objects.values_list(
                                                               'materia_id').filter(profesor=profesor, materia=materia,
                                                                                    materia__nivel__periodo_id__in=periodos,
                                                                                    tipoprofesor=ltipoprofesor,
                                                                                    activo=True,
                                                                                    materia__fin__gte=fechasactividades.desde,
                                                                                    materia__inicio__lte=fechasactividades.hasta).exclude(
                                                               materia__asignaturamalla__malla__carrera__coordinacion__id=9).distinct())
                while subtipo_docentes > 0:
                    if not listadosilabos and nivelacion:
                        subtipo_docentes -= 1
                    if subtipo_docentes == 1 and nivelacion:
                        listadosilabos = Silabo.objects.filter(status=True,
                                                               materia_id__in=ProfesorMateria.objects.values_list(
                                                                   'materia_id').filter(profesor=profesor,
                                                                                        materia=materia,
                                                                                        materia__nivel__periodo_id__in=periodos,
                                                                                        tipoprofesor=ltipoprofesor,
                                                                                        activo=True,
                                                                                        materia__fin__gte=fechasactividades.desde,
                                                                                        materia__inicio__lte=fechasactividades.hasta,
                                                                                        materia__asignaturamalla__malla__carrera__coordinacion__id=9).distinct())
                    listadosilabos = listadosilabos.exclude(materia__modeloevaluativo_id__in=[26, 27])
                    totalsilabos = listadosilabos.count()
                    totalsilabosplanificados = listadosilabos.filter(codigoqr=True).count()
                    porcentaje = 0
                    if periodorelacionado:
                        if totalsilabosplanificados >= 1:
                            porcentaje = 100
                    else:
                        try:
                            porcentaje = round(((100 * totalsilabosplanificados) / totalsilabos), 2)
                        except ZeroDivisionError:
                            porcentaje = 0
                    totalcompendioplanificada = 0
                    totalvideoplanificada = 0
                    totalguiaestplanificada = 0
                    totalmaterialplanificada = 0
                    totalcompendiosmoodle = 0
                    totalvideomoodle = 0
                    totalguiaestmoodle = 0
                    totaldiapositivasmoodle = 0
                    totalunidades = 0
                    totalacdplanificado = 0
                    totalacdplanificadosinmigrar = 0
                    totalaaplanificado = 0
                    totalaaplan = 0
                    totalaaplanificadosinmigrar = 0
                    totalapeplanificado = 0
                    totalapeplanificadosinmigrar = 0
                    minimoacd = 0
                    minimoaa = 0
                    minimoape = 0
                    tieneape = 0
                    totaldiapositivaplanificada = 0
                    totalmaterialplanificada = 0
                    totalmaterialmoodle = 0
                    totalunidades = 0
                    nombretipo = '{} - NIVELACIÓN'.format(
                        ltipoprofesor.nombre) if subtipo_docentes == 1 and nivelacion else ltipoprofesor.nombre
                    listadolineamiento = ltipoprofesor.lineamientorecursoperiodo_set.filter(periodo_id__in=periodos,
                                                                                            status=True,
                                                                                            nivelacion=True) if subtipo_docentes == 1 and nivelacion else ltipoprofesor.lineamientorecursoperiodo_set.filter(
                        periodo_id__in=periodos, status=True, nivelacion=False)
                    listado.append([claseactividad, nombretipo, 0, 0, 0, 0, 3])
                    bandera = 0
                    if nombretipo == 'PRÁCTICA':
                        bandera = 1
                    listamateriasfaltaguias = []
                    listamateriasfaltavideo = []
                    listamateriasfaltacompendio = []
                    listamateriasfaltadiapositiva = []
                    listamateriasfaltamaterial = []
                    listamateriasfaltaaa = []
                    listamateriasfaltaacd = []
                    listamateriasfaltaape = []
                    totalminimoacd = 0
                    totalminimoaa = 0
                    totalminimoape = 0
                    totalaamoodle = 0
                    totalacdmoodle = 0
                    totalapemoodle = 0
                    listamateriasfaltadiapositiva = []
                    listamateriasfaltamaterial = []
                    iddiapositiva = 2
                    idmateriales = 11
                    cantidadplanificadatest = 0
                    fechafinsemana = 0
                    i = 0
                    for lsilabo in listadosilabos:
                        # ini -- para saber cuantas unidades han cerrado
                        materiaplanificacion = lsilabo.materia.planificacionclasesilabo_materia_set.filter(
                            status=True).first()
                        listadoparciales = materiaplanificacion.tipoplanificacion.planificacionclasesilabo_set.values_list(
                            'parcial', 'fechafin').filter(status=True).distinct('parcial').order_by('parcial',
                                                                                                    '-fechafin').exclude(
                            parcial=None)
                        if nivelacion:
                            fechamaximalimite = fechasactividades.hasta
                        else:
                            fechamaximalimite = fechafin
                        parciales = listadoparciales.values_list('parcial', 'fechafin', 'fechainicio'). \
                            filter(Q(status=True),
                                   Q(fechafin__lte=fechamaximalimite) | Q(fechainicio__lte=fechamaximalimite)). \
                            distinct('parcial').order_by('parcial', '-fechafin')
                        listaparcialterminadas = []
                        estadoparcial = 'ABIERTO'
                        idparcial = 1
                        fechaparcial = ''
                        for sise in parciales:
                            if sise[1] <= fechafin or sise[2] <= fechafin:
                                listaparcialterminadas.append(sise[0])
                        if not lsilabo.codigoqr:
                            listasilabofaltasilabo.append([2, lsilabo.id, lsilabo.materia, 0, 1])
                        listaunidadterminadas = []
                        silabosemanaluni = lsilabo.silabosemanal_set.values_list(
                            'detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden',
                            'fechafinciosemana').filter(status=True).distinct(
                            'detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden').order_by(
                            'detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden',
                            '-fechafinciosemana')
                        for sise in silabosemanaluni:
                            # if sise[1] >= fechaini and sise[1] <= fechafin:
                            if sise[0]:
                                if sise[1] <= fechafin:
                                    if not sise[0] in listaunidadterminadas:
                                        listaunidadterminadas.append(sise[0])
                        if not listaunidadterminadas:
                            listaunidadterminadas.append(1)
                        # fin --

                        ############################################################################################

                        # silabosemanal = lsilabo.silabosemanal_set.filter(fechafinciosemana__range=(fechaini, fechafin),detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden__in=listaunidadterminadas,status=True)
                        silabosemanal = lsilabo.silabosemanal_set.filter(
                            detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden__in=listaunidadterminadas,
                            detallesilabosemanaltema__status=True, status=True).distinct()
                        totaltemas = 0
                        totalunidades = len(listaunidadterminadas)
                        runidad = []
                        unidades = silabosemanal.filter(status=True).values_list(
                            'detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico_id',
                            flat=True).distinct()
                        for silabosemana in silabosemanal:
                            for u in unidades:
                                if not u in runidad:
                                    runidad.append(u)
                                    totaltemas += len(silabosemana.temas_silabounidad_fecha(u, fechafin))
                                    #########################################

                        # para sacar diapositivas
                        iddiapositiva = 2
                        if iddiapositiva in listadolineamiento.values_list('tiporecurso', flat=True):
                            if lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.exists():
                                totaldiapositivas = DiapositivaSilaboSemanal.objects.filter(
                                    silabosemanal_id__in=silabosemanal.values_list('id'),
                                    iddiapositivamoodle__gt=0,
                                    status=True).count()
                                multiplicador = len(listaparcialterminadas)
                                busc = lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                    tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                        'tipoprofesor').filter(status=True, profesor=profesor,
                                                               tipoprofesor=ltipoprofesor),
                                    tiporecurso=2, status=True)
                                if subtipo_docentes == 1 and nivelacion:
                                    totalminimoacd = 0
                                    busc = busc.filter(nivelacion=True)
                                    for lineaminetoacd in busc.filter(tiporecurso=iddiapositiva):
                                        if lineaminetoacd.aplicapara == 1:
                                            multiplicador = totalunidades
                                        elif lineaminetoacd.aplicapara == 2:
                                            multiplicador = totaltemas
                                totaldiapositivaplan = busc[0].cantidad * multiplicador
                                totaldiapositivaplanificada += totaldiapositivaplan

                                if totaldiapositivas > totaldiapositivaplan:
                                    totaldiapositivasmoodle += totaldiapositivaplan
                                else:
                                    totaldiapositivasmoodle += totaldiapositivas

                                listamateriasfaltadiapositiva.append(
                                    [1, lsilabo.id, lsilabo.materia, totaldiapositivas,
                                     totaldiapositivaplan])

                        # para sacar materialcomplementario
                        idmateriales = 11
                        if idmateriales in listadolineamiento.values_list('tiporecurso', flat=True):
                            if lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.exists():
                                totalmateriales = MaterialAdicionalSilaboSemanal.objects.filter(
                                    silabosemanal_id__in=silabosemanal.values_list('id'),
                                    idmaterialesmoodle__gt=0,
                                    status=True).count()
                                multiplicador = len(listaparcialterminadas)
                                lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                    tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                        'tipoprofesor').filter(status=True, profesor=profesor,
                                                               tipoprofesor=ltipoprofesor), tiporecurso=11,
                                    status=True)

                                busc = lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                    tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                        'tipoprofesor').filter(status=True, profesor=profesor,
                                                               tipoprofesor=ltipoprofesor),
                                    tiporecurso=11, status=True)
                                if subtipo_docentes == 1 and nivelacion:
                                    totalminimoacd = 0
                                    busc = busc.filter(nivelacion=True)
                                    for lineaminetoacd in busc.filter(tiporecurso=iddiapositiva):
                                        if lineaminetoacd.aplicapara == 1:
                                            multiplicador = totalunidades
                                        elif lineaminetoacd.aplicapara == 2:
                                            multiplicador = totaltemas
                                else:
                                    busc = busc.exclude(nivelacion=True)
                                totalmaterialplan = busc[0].cantidad * multiplicador
                                totalmaterialplanificada += totalmaterialplan
                                if totalmateriales > totalmaterialplan:
                                    totalmaterialmoodle += totalmaterialplan
                                else:
                                    totalmaterialmoodle += totalmateriales

                                listamateriasfaltamaterial.append(
                                    [2, lsilabo.id, lsilabo.materia, totalmateriales, totalmaterialplan])

                        ########################################
                        # para sacar compendios
                        idcompendio = 1
                        if idcompendio in listadolineamiento.values_list('tiporecurso', flat=True):
                            totalcompendios = CompendioSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanal.values_list('id'), idmcompendiomoodle__gt=0,
                                status=True).count()
                            totalcompendioplan = lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                    'tipoprofesor').filter(status=True, materia=materia), tiporecurso=1, status=True)[
                                                     0].cantidad * len(
                                listaunidadterminadas)
                            totalcompendioplanificada += totalcompendioplan
                            if totalcompendios > totalcompendioplan:
                                totalcompendiosmoodle += totalcompendioplan
                            else:
                                totalcompendiosmoodle += totalcompendios
                            if totalcompendios < totalcompendioplan:
                                listamateriasfaltacompendio.append(
                                    [lsilabo.id, lsilabo.materia, totalcompendios, totalcompendioplan])

                        # para sacar videomagistral
                        idvideomagistral = 12
                        if idvideomagistral in listadolineamiento.values_list('tiporecurso', flat=True):
                            totalvideos = VideoMagistralSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanal.values_list('id'), idvidmagistralmoodle__gt=0,
                                status=True).count()
                            totalvideoplan = lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                    'tipoprofesor').filter(status=True, materia=materia), tiporecurso=12, status=True)[
                                                 0].cantidad * len(
                                listaunidadterminadas)
                            totalvideoplanificada += totalvideoplan
                            if totalvideos > totalvideoplan:
                                totalvideomoodle += totalvideoplan
                            else:
                                totalvideomoodle += totalvideos
                            if totalvideos < totalvideoplan:
                                listamateriasfaltavideo.append(
                                    [lsilabo.id, lsilabo.materia, totalvideos, totalvideoplan])

                        # para sacar guiaestudiante
                        idguiaestudiante = 4
                        if idguiaestudiante in listadolineamiento.values_list('tiporecurso', flat=True):
                            totalguiaestudiante = GuiaEstudianteSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanal.values_list('id'), idguiaestudiantemoodle__gt=0,
                                status=True).count()
                            totalguiaestudianteplan = \
                                lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                    tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                        'tipoprofesor').filter(status=True, materia=materia), tiporecurso=4,
                                    status=True)[0].cantidad * len(
                                    listaunidadterminadas)
                            totalguiaestplanificada += totalguiaestudianteplan
                            if totalguiaestudiante > totalguiaestudianteplan:
                                totalguiaestmoodle += totalguiaestudianteplan
                            else:
                                totalguiaestmoodle += totalguiaestudiante
                            if totalguiaestudiante < totalguiaestudianteplan:
                                listamateriasfaltaguias.append(
                                    [lsilabo.id, lsilabo.materia, totalguiaestudiante, totalguiaestudianteplan])

                        # para sacar los compenentes acd ,aa ,ape
                        materiaplanificacion = lsilabo.materia.planificacionclasesilabo_materia_set.filter(status=True)[
                            0]
                        listadoparciales = materiaplanificacion.tipoplanificacion.planificacionclasesilabo_set.values_list(
                            'parcial', 'fechafin').filter(status=True).distinct('parcial').order_by('parcial',
                                                                                                    '-fechafin').exclude(
                            parcial=None)
                        if obj.periodosrelacionados.exists():
                            if nivelacion:
                                fecha_limite = fechasactividades.hasta + timedelta(days=30)
                            else:
                                fecha_limite = fechafin + timedelta(days=30)
                            parciales = listadoparciales.values_list('parcial', 'fechafin').filter(status=True,
                                                                                                   fechafin__lte=fecha_limite).distinct(
                                'parcial').order_by('parcial', '-fechafin')
                        else:
                            parciales = listadoparciales.values_list('parcial', 'fechafin', 'fechainicio').filter(
                                Q(status=True), Q(fechafin__lte=fechafin) | Q(fechainicio__lte=fechafin)).distinct(
                                'parcial').order_by('parcial', '-fechafin')
                        listaparcialterminadas = []
                        estadoparcial = 'ABIERTO'
                        idparcial = 1 if not obj.periodo.tipo.id in [3, 4] else 0
                        fechaparcial = ''
                        for sise in parciales:
                            if obj.periodosrelacionados.exists():
                                idparcial = sise[0]
                                listaparcialterminadas.append(sise[0])
                            else:
                                if sise[1] <= fechafin or sise[2] <= fechafin:
                                    idparcial = sise[0]
                                    listaparcialterminadas.append(sise[0])
                        for lpar in listadoparciales:
                            if listadoparciales.order_by('-parcial')[0][0] == lpar[0]:
                                if fechafin >= lpar[1]:
                                    estadoparcial = 'CERRADO'
                            if lpar[0] == idparcial:
                                fechaparcial = lpar[1]

                        if periodo.tipo.id not in [3, 4]:
                            listadocomponentes = lsilabo.materia.nivel.periodo.evaluacioncomponenteperiodo_set.select_related(
                                'componente').filter(nivelacion=True, parcial__in=listaparcialterminadas,
                                                     status=True) if subtipo_docentes == 1 and nivelacion else lsilabo.materia.nivel.periodo.evaluacioncomponenteperiodo_set.select_related(
                                'componente').filter(parcial__in=listaparcialterminadas, status=True)
                        else:
                            listadocomponentes = lsilabo.materia.nivel.periodo.evaluacioncomponenteperiodo_set.select_related(
                                'componente').filter(status=True)

                        # para sacar todos los silabos semanales segun fecha fin del parcial
                        silabosemanalparcial = lsilabo.silabosemanal_set.filter(fechafinciosemana__lte=fechaparcial,
                                                                                status=True)
                        # for silabosemana in silabosemanalparcial:
                        #     if lsilabo.silabosemanal_set.all()[i].listatest_semanales().count() > 0:
                        #         fechafinsemana = lsilabo.silabosemanal_set.values_list('fechafinciosemana',
                        #                                                                flat=True).filter(
                        #             status=True)[i]
                        #         if TestSilaboSemanal.objects.filter(silabosemanal=silabosemana,
                        #                                             silabosemanal_id__in=silabosemanalparcial.values_list(
                        #                                                 'id'), idtestmoodle__gt=0,
                        #                                             status=True).exists():
                        #             print('HA CUMPLIDO')
                        #         else:
                        #             if fechaactual <= fechafinsemana:
                        #                 print('PENDIENTE')
                        #             else:
                        #                 print('NO HA CUMPLIDO')
                        #     i += 1
                        if lsilabo.materia.modeloevaluativo.id != 25:
                            if listadocomponentes.filter(componente_id=1):
                                multiplicador = len(listaparcialterminadas)
                                if subtipo_docentes == 1 and nivelacion:
                                    totalminimoacd = 0
                                    for lineaminetoacd in listadolineamiento.filter(tiporecurso=7):
                                        if lineaminetoacd.aplicapara == 1:
                                            multiplicador = totalunidades
                                        elif lineaminetoacd.aplicapara == 2:
                                            multiplicador = totaltemas
                                        totalminimoacd += lineaminetoacd.cantidad * multiplicador
                                else:
                                    totalminimoacd = listadocomponentes.filter(componente_id=1,
                                                                               nivelacion=False).first().cantidad * multiplicador
                                minimoacd += totalminimoacd
                        totalacdplanificadotar = 0
                        totalacdplanificadosinmigrartar = 0
                        if (subtipo_docentes == 1 and not nivelacion) or (subtipo_docentes == 2 and nivelacion):
                            totalacdplanificadotar = TareaSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'), idtareamoodle__gt=0,
                                actividad_id__in=[2, 3], status=True).count()
                            totalacdplanificadosinmigrartar = TareaSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                                actividad_id__in=[2, 3], status=True).count()

                        if subtipo_docentes == 1 and nivelacion:
                            totalacdplanificadotest = TestSilaboSemanalAdmision.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'), idtestmoodle__gt=0,
                                status=True).count()
                            totalacdplanificadosinmigrartest = TestSilaboSemanalAdmision.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                                status=True).count()

                        else:
                            totalacdplanificadotest = TestSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'), idtestmoodle__gt=0,
                                tiporecurso_id__in=[11],
                                status=True).count()
                            totalacdplanificadosinmigrartest = TestSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'),tiporecurso_id__in=[11],
                                status=True).count()
                        totalacdplanificado += totalacdplanificadotar + totalacdplanificadotest
                        totalplanificadoacd = totalacdplanificadotar + totalacdplanificadotest

                        totalacdplanificadosinmigrar += totalacdplanificadosinmigrartar + totalacdplanificadosinmigrartest

                        if totalplanificadoacd > totalminimoacd:
                            totalacdmoodle += totalminimoacd
                        else:
                            totalacdmoodle += totalplanificadoacd
                        if estadoparcial == 'CERRADO':
                            if totalplanificadoacd < totalminimoacd:
                                listamateriasfaltaacd.append(
                                    [lsilabo.id, lsilabo.materia, totalplanificadoacd, totalminimoacd])

                        totalaaplanificadosinmigrartar = 0
                        if lsilabo.materia.modeloevaluativo.id != 25:
                            if listadocomponentes.filter(componente_id=3):
                                totalminimoaa = listadocomponentes.filter(componente_id=3)[0].cantidad * len(
                                    listaparcialterminadas)
                                minimoaa += totalminimoaa
                        totalplanificadoaatar = TareaSilaboSemanal.objects.filter(
                            silabosemanal_id__in=silabosemanalparcial.values_list('id'), idtareamoodle__gt=0,
                            actividad_id__in=[5, 7, 8], status=True).count()
                        totalplanificadoaasinmigrartar = TareaSilaboSemanal.objects.filter(
                            silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                            actividad_id__in=[5, 7, 8], status=True).count()
                        totalplanificadoaafor = ForoSilaboSemanal.objects.filter(
                            silabosemanal_id__in=silabosemanalparcial.values_list('id'), idforomoodle__gt=0,
                            status=True).count()
                        totalplanificadoaasinmigrarfor = ForoSilaboSemanal.objects.filter(
                            silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                            status=True).count()
                        totalaaplanificado += totalplanificadoaatar + totalplanificadoaafor
                        totalplanificadoaa = totalplanificadoaatar + totalplanificadoaafor
                        totalaaplanificadosinmigrar += totalplanificadoaasinmigrartar + totalplanificadoaasinmigrarfor

                        if totalplanificadoaa > totalminimoaa:
                            totalaamoodle += totalminimoaa
                        else:
                            totalaamoodle += totalplanificadoaa
                        if estadoparcial == 'CERRADO':
                            if totalplanificadoaa < totalminimoaa:
                                listamateriasfaltaaa.append(
                                    [lsilabo.id, lsilabo.materia, totalplanificadoaa, totalminimoaa])
                        totalapeplanificadosinmigrartar = 0
                        if lsilabo.materia.asignaturamalla.horasapeasistotal > 0:
                            if lsilabo.materia.modeloevaluativo.id != 25:
                                if listadocomponentes.filter(componente_id=2):
                                    totalminimoape = listadocomponentes.filter(componente_id=2)[0].cantidad * len(
                                        listaparcialterminadas)
                                    minimoape += totalminimoape
                                totalapeplanificadotar = TareaPracticaSilaboSemanal.objects.filter(
                                    silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                                    idtareapracticamoodle__gt=0, status=True)
                                totalapeplanificadosinmigrartar = TareaPracticaSilaboSemanal.objects.filter(
                                    silabosemanal_id__in=silabosemanalparcial.values_list('id'), status=True).count()

                                totalapeplanificado += totalapeplanificadotar.count()
                                totalapeplanificadosinmigrar += totalapeplanificadosinmigrartar
                                # totalapeplanificadoape = totalapeplanificadotar.count()
                                totalapeplanificadoape = totalapeplanificadotar.values_list(
                                    'silabosemanal__parcial').distinct().count()
                                tieneape = 1
                                if totalapeplanificadoape > totalminimoape:
                                    totalapemoodle += totalminimoape
                                else:
                                    totalapemoodle += totalapeplanificadoape
                                if estadoparcial == 'CERRADO':
                                    if totalapeplanificadoape < totalminimoape:
                                        listamateriasfaltaape.append(
                                            [lsilabo.id, lsilabo.materia, totalapeplanificadoape, totalminimoape])
                    ##################################################

                    if iddiapositiva in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajediapositivas = 0
                            if totaldiapositivasmoodle >= 1:
                                porcentajediapositivas = 100
                        else:
                            try:
                                porcentajediapositivas = round(
                                    ((100 * totaldiapositivasmoodle) / totaldiapositivaplanificada), 2)
                            except ZeroDivisionError:
                                porcentajediapositivas = 0
                    if idmateriales in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajematerial = 0
                            if totalmaterialmoodle >= 1:
                                porcentajematerial = 100
                        else:
                            try:
                                porcentajematerial = round(((100 * totalmaterialmoodle) / totalmaterialplanificada), 2)
                            except ZeroDivisionError:
                                porcentajematerial = 0
                    listado.append([claseactividad, 'Sílabo', totalsilabos, totalsilabosplanificados, porcentaje, '',
                                    'ACTIVIDADES',
                                    listasilabofaltasilabo])
                    resultadominimoplanificar += totalsilabos
                    resultadoplanificados += totalsilabosplanificados
                    resultadoporcentajessyl += porcentaje
                    sumatoriaindicesyl += 1
                    ##################################################
                    if idcompendio in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajecompendios = 0
                            if totalcompendiosmoodle >= 1:
                                porcentajecompendios = 100
                        else:
                            try:
                                porcentajecompendios = round(
                                    ((100 * totalcompendiosmoodle) / totalcompendioplanificada), 2)
                            except ZeroDivisionError:
                                porcentajecompendios = 0
                    if idvideomagistral in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajevideo = 0
                            if totalvideomoodle >= 1:
                                porcentajevideo = 100
                        else:
                            try:
                                porcentajevideo = round(((100 * totalvideomoodle) / totalvideoplanificada), 2)
                            except ZeroDivisionError:
                                porcentajevideo = 0

                    if idguiaestudiante in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajeguiaestudiante = 0
                            if totalguiaestmoodle >= 1:
                                porcentajeguiaestudiante = 100
                            else:
                                if totalguiaestplanificada == 0:
                                    porcentajeguiaestudiante = 100
                        else:
                            if totalguiaestplanificada == 0:
                                porcentajeguiaestudiante = 100
                            else:
                                try:
                                    porcentajeguiaestudiante = round(
                                        ((100 * totalguiaestmoodle) / totalguiaestplanificada), 2)
                                except ZeroDivisionError:
                                    porcentajeguiaestudiante = 0
                    try:
                        porcentajeacd = 0
                        if periodorelacionado:
                            if totalacdmoodle >= 1:
                                porcentajeacd = 100
                        else:
                            if totalacdmoodle > minimoacd:
                                porcentajeacd = 100
                            else:
                                porcentajeacd = round(((100 * totalacdmoodle) / minimoacd), 2)
                    except ZeroDivisionError:
                        porcentajeacd = 0
                    if porcentajeacd > 100:
                        porcentajeacd = 100
                    if estadoparcial == 'ABIERTO' and not nivelacion:
                        porcentajeacd = 100
                    try:
                        porcentajeaa = 0
                        if periodorelacionado:
                            if totalaamoodle >= 1:
                                porcentajeaa = 100
                        else:
                            if totalaamoodle > minimoaa:
                                porcentajeaa = 100
                            else:
                                porcentajeaa = round(((100 * totalaamoodle) / minimoaa), 2)
                    except ZeroDivisionError:
                        porcentajeaa = 0
                    if porcentajeaa > 100:
                        porcentajeaa = 100
                    if estadoparcial == 'ABIERTO':
                        porcentajeaa = 100

                    if tieneape == 1:
                        try:
                            porcentajeape = 0
                            if periodorelacionado:
                                if totalapemoodle >= 1:
                                    porcentajeape = 100
                            else:
                                if totalapemoodle > minimoape:
                                    porcentajeape = 100
                                else:
                                    porcentajeape = round(((100 * totalapemoodle) / minimoape), 2)
                        except ZeroDivisionError:
                            porcentajeape = 0
                        if porcentajeape > 100:
                            porcentajeape = 100
                        if estadoparcial == 'ABIERTO':
                            porcentajeape = 100

                    ###########################################

                    if iddiapositiva in listadolineamiento.values_list('tiporecurso', flat=True):
                        listado.append([claseactividad, 'Presentación (Diapositivas)', totaldiapositivaplanificada,
                                        totaldiapositivasmoodle, porcentajediapositivas, '', 'ACTIVIDADES',
                                        listamateriasfaltadiapositiva])
                        resultadominimoplanificar += totaldiapositivaplanificada
                        resultadoplanificados += totaldiapositivasmoodle
                        resultadoporcentajessyl += porcentajediapositivas
                        sumatoriaindicesyl += 1
                    if idmateriales in listadolineamiento.values_list('tiporecurso', flat=True):
                        listado.append(
                            [claseactividad, 'Material Complementario', totalmaterialplanificada, totalmaterialmoodle,
                             porcentajematerial, '', 'ACTIVIDADES', listamateriasfaltamaterial])
                        resultadominimoplanificar += totalmaterialplanificada
                        resultadoplanificados += totalmaterialmoodle
                        resultadoporcentajessyl += porcentajematerial
                        sumatoriaindicesyl += 1

                    ############################################
                    if idcompendio in listadolineamiento.values_list('tiporecurso', flat=True):
                        listado.append([claseactividad, 'COMPENDIO', totalcompendioplanificada, totalcompendiosmoodle,
                                        porcentajecompendios, 0, 'ACTIVIDADES', listamateriasfaltacompendio, porcentajecompendios,
                                        idcompendio, False])
                        resultadominimoplanificar += totalcompendioplanificada
                        resultadoplanificados += totalcompendiosmoodle
                        resultadoporcentajes += porcentajecompendios
                        sumatoriaindice += 1
                    if idvideomagistral in listadolineamiento.values_list('tiporecurso', flat=True):
                        listado.append([claseactividad, 'VIDEOS MAGISTRALES', totalvideoplanificada, totalvideomoodle,
                                        porcentajevideo, 0, 'ACTIVIDADES', listamateriasfaltavideo, porcentajevideo,
                                        idvideomagistral, False])
                        resultadominimoplanificar += totalvideoplanificada
                        resultadoplanificados += totalvideomoodle
                        resultadoporcentajes += porcentajevideo
                        sumatoriaindice += 1
                    if idguiaestudiante in listadolineamiento.values_list('tiporecurso', flat=True):
                        listado.append(
                            [claseactividad, 'GUÍA DEL ESTUDIANTE', totalguiaestplanificada, totalguiaestmoodle,
                             porcentajeguiaestudiante, 0, 'ACTIVIDADES', listamateriasfaltaguias, porcentajeguiaestudiante,
                             idguiaestudiante, False])
                        resultadominimoplanificar += totalguiaestplanificada
                        resultadoplanificados += totalguiaestmoodle
                        resultadoporcentajes += porcentajeguiaestudiante
                        sumatoriaindice += 1
                    if bandera != 1:
                        listado.append([claseactividad, 'ACD', minimoacd, totalacdplanificado,
                                        '-' if subtipo_docentes == 1 and nivelacion else estadoparcial, porcentajeacd,
                                        2,
                                        listamateriasfaltaacd, porcentajeacd, 8, subtipo_docentes == 1 and nivelacion,
                                        totalacdplanificadosinmigrar])
                    sumatoriaindice += 1
                    if (subtipo_docentes == 1 and not nivelacion) or (subtipo_docentes == 2 and nivelacion):
                        if bandera != 1:
                            listado.append(
                                [claseactividad, 'AA', minimoaa, totalaaplanificado, estadoparcial, porcentajeaa, 2,
                                 listamateriasfaltaaa, porcentajeaa, 9, False, totalaaplanificadosinmigrar])
                        sumatoriaindice += 1
                    if tieneape == 1:
                        if bandera == 1:
                            listado.append(
                                [claseactividad, 'APE', minimoape, totalapeplanificado, estadoparcial, porcentajeape, 2,
                                 listamateriasfaltaape, porcentajeape, 10, False, totalapeplanificadosinmigrar])
                        sumatoriaindice += 1
                    resultadominimoplanificar += minimoacd
                    resultadominimoplanificar += minimoaa
                    if tieneape == 1:
                        resultadominimoplanificar += minimoape
                    resultadoplanificados += totalacdplanificado
                    resultadoplanificados += totalaaplanificado
                    if tieneape == 1:
                        resultadoplanificados += totalapeplanificado
                    resultadoporcentajes += porcentajeacd
                    if (subtipo_docentes == 1 and not nivelacion) or (subtipo_docentes == 2 and nivelacion):
                        resultadoporcentajes += porcentajeaa
                    if tieneape == 1:
                        resultadoporcentajes += porcentajeape
                    subtipo_docentes -= 1
        try:
            resultadoporcentajes = round(((resultadoporcentajes) / sumatoriaindice), 2)
            resultadoporcentajessyl = round(((resultadoporcentajessyl) / sumatoriaindicesyl), 2)
            resultadototal = round(((resultadoporcentajes + resultadoporcentajessyl) / 2), 2)
            resultadosobre40 = round(((resultadototal * 40) / 100), 2)
        except ZeroDivisionError:
            resultadoporcentajes = 0
            resultadoporcentajessyl = 0
            resultadototal = 0
        listado.append(
            [claseactividad, resultadominimoplanificar, resultadoplanificados, resultadoporcentajes, len(result), 0, 4,
             [], resultadosobre40, resultadototal])
        return listado
    except Exception as e:
        import sys
        print(e)
        print('Error on line {} - {}'.format(sys.exc_info()[-1].tb_lineno, e))


@register.simple_tag
def listado_bitacora_docente(obj, criterio, fechafin, esautomatico=False):
    from django.db.models import Sum, F, ExpressionWrapper, TimeField
    from sga.models import ClaseActividad
    from investigacion.models import BitacoraActividadDocente

    try:
        periodo = criterio.distributivo.periodo
        profesor = criterio.distributivo.profesor

        _get_horas_minutos = lambda th: (th.total_seconds() / 3600).__str__().split('.')

        data, listabitacoras, porcentajetotal = {}, [], 0
        claseactividad = ClaseActividad.objects.filter(detalledistributivo=criterio, detalledistributivo__distributivo__profesor=profesor, status=True).order_by('inicio', 'dia', 'turno__comienza')

        inicio, fin = periodo.inicio, periodo.fin
        if actividad := criterio.actividaddetalledistributivo_set.filter(vigente=True, status=True).first():
            inicio, fin = actividad.desde, actividad.hasta

        dt, end, step = date(fechafin.year, fechafin.month, 1), fechafin, timedelta(days=1)
        _result, total_ejecutada = [], 0
        while dt <= end:
            if inicio <= dt <= fin:
                exclude = 0 # if not (criterio.criteriogestionperiodo and criterio.criteriogestionperiodo.criterio.id == 220) else 2
                if not criterio.distributivo.periodo.diasnolaborable_set.values('id').filter(status=True, fecha=dt, activo=True).exclude(motivo=exclude):
                    _result += [dt.strftime('%Y-%m-%d') for dclase in claseactividad.values_list('dia', 'turno_id') if dt.isocalendar()[2] == dclase[0]]

            dt += step

        for bitacora in BitacoraActividadDocente.objects.filter(profesor=profesor, criterio=criterio, status=True).filter(fechaini__gte=inicio, fechafin__lte=fechafin).order_by('fechafin'):
            fi, ff = date(bitacora.fechafin.year, bitacora.fechafin.month, 1), bitacora.fechafin
            detallebitacora = bitacora.detallebitacoradocente_set.filter(bitacoradocente=bitacora, fecha__lte=ff, fecha__gte=fi, status=True).annotate(diferencia=ExpressionWrapper(F('horafin') - F('horainicio'), output_field=TimeField())).order_by('fecha', 'horainicio', 'horafin')
            porcentaje_cumplimiento, total_registradas, total_aprobadas = 0, 0, 0

            if th := detallebitacora.aggregate(total=Sum('diferencia'))['total']:
                horas, minutos = _get_horas_minutos(th)
                total_registradas = float("%s.%s" % (horas, round(float('0.' + minutos) * 60)))

            if th := detallebitacora.filter(estadoaprobacion=2).aggregate(total=Sum('diferencia'))['total']:
                horas, minutos = _get_horas_minutos(th)
                total_aprobadas = float("%s.%s" % (horas, round(float('0.' + minutos) * 60)))

            if total_planificadas := bitacora.horas_planificadas():
                if bitacora.estadorevision == 3:
                    porcentaje_cumplimiento = 100 if (total_aprobadas > total_planificadas) else round((total_aprobadas / total_planificadas) * 100, 2)
                else:
                    porcentaje_cumplimiento = 100 if (total_registradas > total_planificadas) else round((total_registradas / total_planificadas) * 100, 2)
            else:
                if total_registradas:
                    porcentaje_cumplimiento = 100

            listabitacoras.append([bitacora, total_planificadas, total_registradas, total_aprobadas if bitacora.estadorevision == 3 else '-', porcentaje_cumplimiento])

        if listabitacoras:
            porcentajetotal = sum([l[4] for l in listabitacoras]) / len(listabitacoras)
            total_ejecutada = listabitacoras[-1][3]

        if esautomatico:
            totalmensual = _result.__len__()
            promedio = porcentajetotal if porcentajetotal <= 100 else 100
            listado = [totalmensual, promedio]
            return listado
        else:
            return {'listabitacoras': listabitacoras, 'claseactividad': claseactividad, 'porcentajetotal': porcentajetotal if porcentajetotal <= 100 else 100, 'planificadas_mes': _result.__len__(), 'total_ejecutada':total_ejecutada}
    except Exception as ex:
        ...

@register.simple_tag
def listado_colectivos_academicos(obj, criterio, fechainicio, fechafin, esautomatico=False):
    try:
        from sga.models import ClaseActividad, CapCabeceraSolicitudDocente, CapEventoPeriodoDocente
        from dateutil.relativedelta import relativedelta
        periodo, profesor = criterio.distributivo.periodo, criterio.distributivo.profesor
        now = datetime.now().date()

        claseactividad = ClaseActividad.objects.filter(detalledistributivo=criterio, detalledistributivo__distributivo__profesor=profesor, status=True).order_by('inicio', 'dia', 'turno__comienza')
        inicio, fin = fechainicio, fechafin
        if actividad := criterio.actividaddetalledistributivo_set.filter(vigente=True, status=True).first():
            if actividad.hasta < fechafin:
                fin = actividad.hasta

        dt, end, step = date(fechafin.year, fechafin.month, 1), fechafin, timedelta(days=1)
        _result, total_ejecutada = [], 0
        while dt <= end:
            if inicio <= dt <= fin:
                exclude = 0
                if not periodo.diasnolaborable_set.values('id').filter(status=True, fecha=dt, activo=True).exclude(motivo=exclude):
                    _result += [dt.strftime('%Y-%m-%d') for dclase in claseactividad.values_list('dia', 'turno_id') if dt.isocalendar()[2] == dclase[0]]

            dt += step

        __totalplanificadas, __porcentajegeneral, __miseventos = _result.__len__(), 0, []

        filtroa = Q(capeventoperiodo__status=True, capeventoperiodo__capevento__status=True, status=True, participante=profesor.persona)
        filtrob = Q(capeventoperiodo__fechafin__gte=fechainicio - relativedelta(months=1)) | Q(capeventoperiodo__fechafin__gte=fechainicio - relativedelta(months=1), capeventoperiodo__fechafin__lte=fechafin)

        existe_capacitacion = CapEventoPeriodoDocente.objects.filter(status=True, visualizar=True, fechainicio__gte=fechainicio - relativedelta(months=1), fechafin__lte=fechafin).values('id').exists()
        eventos = CapCabeceraSolicitudDocente.objects.select_related('capeventoperiodo').filter(filtroa & filtrob).order_by('-capeventoperiodo__fechafin').exclude(estadosolicitud=4)
        for e in eventos:
            __miseventos.append({'evento': e, 'porcentaje': 100, 'estado': 'EJECUTADO' if e.capeventoperiodo.fechafin <= fechafin else 'EN CURSO'})

        if count := __miseventos.__len__():
            __porcentajegeneral = sum([x['porcentaje'] for x in __miseventos]) / count

        __porcentajegeneral = __porcentajegeneral if __porcentajegeneral <= 100 else 100

        if esautomatico:
            totalmensual = __totalplanificadas
            promedio = __porcentajegeneral
            listado = [totalmensual, promedio] if existe_capacitacion else []
            return listado
        else:
            return {'planificadas': __totalplanificadas, 'data': __miseventos, 'porcentajegeneral': __porcentajegeneral, "claseactividad": claseactividad, 'existe_capacitacion': existe_capacitacion}
    except Exception as ex:
        pass

@register.simple_tag
def temasimpartidos(obj, idmateria, periodo):
    from sga.models import Silabo, TemaAsistencia, SubTemaAsistencia, SubTemaAdicionalAsistencia, DiasNoLaborable, DetalleSilaboSemanalSubtema
    from django.db import connections
    listado = []
    cont = 0
    porcentajecumplimiento = 0
    porcentajetotal = 0
    fechaactual = datetime.now().date()
    if silabos := Silabo.objects.filter(status=True, materia_id=idmateria):
        numeros_semana = [fecha.isocalendar()[1] for fecha in periodo.diasnolaborable_set.filter(status=True).values_list('fecha', flat=True)]
        num_sem_dia_no_laborable = list(dict.fromkeys(numeros_semana))
        silabosemanal = silabos.first().silabosemanal_set.filter(status=True)
        if silabosemanal:
            cursor = connections['sga_select'].cursor()
            for silsem in silabosemanal:
                # unidadsilsem = silsem.temas_seleccionados_planclase()
                sql_tema = f"""SELECT "sga_detallesilabosemanaltema"."id", "sga_temaunidadresultadoprogramaanalitico"."descripcion", "sga_detallesilabosemanaltema"."temaunidadresultadoprogramaanalitico_id" FROM "sga_detallesilabosemanaltema" INNER JOIN "sga_temaunidadresultadoprogramaanalitico" ON ("sga_detallesilabosemanaltema"."temaunidadresultadoprogramaanalitico_id" = "sga_temaunidadresultadoprogramaanalitico"."id") WHERE ("sga_detallesilabosemanaltema"."silabosemanal_id" = {silsem.pk} AND "sga_temaunidadresultadoprogramaanalitico"."status") ORDER BY "sga_temaunidadresultadoprogramaanalitico"."orden" ASC"""
                cursor.execute(sql_tema)
                unidadsilsem = cursor.fetchall()
                # unidadsilsem = list(silsem.detallesilabosemanaltema_set.select_related('temaunidadresultadoprogramaanalitico').values_list('id','temaunidadresultadoprogramaanalitico__descripcion','temaunidadresultadoprogramaanalitico').filter(temaunidadresultadoprogramaanalitico__status=True).order_by('temaunidadresultadoprogramaanalitico__orden'))
                listado.append([silsem.numsemana, silsem.fechainiciosemana, silsem.fechafinciosemana, '', 'fechas'])
                fechainicio = silsem.fechainiciosemana
                fechafin = silsem.fechafinciosemana
                num_semana_fechainiciosilabo = fechainicio.isocalendar()[1]
                if unidadsilsem:
                    for tema in unidadsilsem:
                        if fechafin <= fechaactual:
                            cont += 1
                            if TemaAsistencia.objects.values('id').filter(fecha__lte=fechafin, tema=tema[0]).exists() or (num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
                                porcentajecumplimiento += 1
                                listado.append(
                                    ['', '', '', tema[1], 'temas', 1])
                            else:
                                listado.append(
                                    ['', '', '', tema[1], 'temas', 0])
                        else:
                            listado.append(
                                ['', '', '', tema[1], 'temas', '-'])
                        subtemas = DetalleSilaboSemanalSubtema.objects.select_related('subtemaunidadresultadoprogramaanalitico').values_list('id','subtemaunidadresultadoprogramaanalitico__descripcion').filter(status=True,subtemaunidadresultadoprogramaanalitico__temaunidadresultadoprogramaanalitico=tema[2], subtemaunidadresultadoprogramaanalitico__status=True, subtemaunidadresultadoprogramaanalitico__temaunidadresultadoprogramaanalitico__isnull=False,subtemaunidadresultadoprogramaanalitico__temaunidadresultadoprogramaanalitico__status=True,silabosemanal=silsem).order_by('subtemaunidadresultadoprogramaanalitico__orden')
                        sql_subtemas = f"""SELECT "sga_detallesilabosemanalsubtema"."id", "sga_subtemaunidadresultadoprogramaanalitico"."descripcion" FROM "sga_detallesilabosemanalsubtema" INNER JOIN "sga_subtemaunidadresultadoprogramaanalitico" ON ("sga_detallesilabosemanalsubtema"."subtemaunidadresultadoprogramaanalitico_id" = "sga_subtemaunidadresultadoprogramaanalitico"."id") INNER JOIN "sga_temaunidadresultadoprogramaanalitico" ON ("sga_subtemaunidadresultadoprogramaanalitico"."temaunidadresultadoprogramaanalitico_id" = "sga_temaunidadresultadoprogramaanalitico"."id") WHERE ("sga_detallesilabosemanalsubtema"."silabosemanal_id" = {silsem.pk} AND "sga_detallesilabosemanalsubtema"."status" AND "sga_subtemaunidadresultadoprogramaanalitico"."status" AND "sga_subtemaunidadresultadoprogramaanalitico"."temaunidadresultadoprogramaanalitico_id" = {tema[2]} AND "sga_subtemaunidadresultadoprogramaanalitico"."temaunidadresultadoprogramaanalitico_id" IS NOT NULL AND "sga_temaunidadresultadoprogramaanalitico"."status") ORDER BY "sga_subtemaunidadresultadoprogramaanalitico"."orden" ASC"""
                        cursor.execute(sql_subtemas)
                        subtemas = cursor.fetchall()
                        # subtemas = silsem.subtemas_silabosemanal(tema.temaunidadresultadoprogramaanalitico)
                        for subtema in subtemas:
                            if fechafin <= fechaactual:
                                cont += 1
                                if SubTemaAsistencia.objects.values('id').filter(subtema__silabosemanal=silsem, fecha__lte=fechafin, subtema=subtema[0]).exists() or (num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
                                    porcentajecumplimiento += 1
                                    listado.append(['', '', '', subtema[1], 'subtemas', 1])
                                else:
                                    listado.append(['', '', '', subtema[1], 'subtemas', 0])
                            else:
                                listado.append(['', '', '', subtema[1], 'subtemas', '-'])

                        # subtemaadicional = silsem.subtemas_adicionales(tema.id)
                        subtemaadicional = silsem.subtemaadicionalessilabo_set.values_list('id','subtema').filter(status=True, tema_id=tema[0]).order_by('id')
                        for subtemasad in subtemaadicional:
                            if fechafin <= fechaactual:
                                cont += 1
                                if SubTemaAdicionalAsistencia.objects.values('id').filter(fecha__lte=fechafin, subtema=subtemasad[0]).exists() or (num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
                                    porcentajecumplimiento += 1
                                    listado.append(['', '', '', subtemasad[1], 'subtemas', 1])
                                else:
                                    listado.append(['', '', '', subtemasad[1], 'subtemas', 0])
                            else:
                                listado.append(['', '', '', subtemasad[1], 'subtemas', '-'])

    try:
        percent = round((porcentajecumplimiento / cont), 2)
        percent = round((percent * 100), 2)
        calculosobre30 = round(((percent * 30) / 100), 2)
        # resultadoporcentajes = percent if 0 < percent <= 100 else 100
    except ZeroDivisionError:
        percent = 0
        calculosobre30 = 0
    listado.append([percent, calculosobre30, 'ponderacion'])
    return listado

@register.simple_tag
def contenido_profesor_total(obj, profesor, materia, fechaini, fechafin):
    try:
        from sga.models import DetalleDistributivo, GuiaEstudianteSilaboSemanal, TareaPracticaSilaboSemanal, \
            TipoProfesor, ProfesorMateria, ClaseActividad, Silabo, CompendioSilaboSemanal, VideoMagistralSilaboSemanal, \
            ForoSilaboSemanal, TareaSilaboSemanal, TestSilaboSemanalAdmision, TestSilaboSemanal, \
            DiapositivaSilaboSemanal, MaterialAdicionalSilaboSemanal, TemaAsistencia, SubTemaAsistencia, SubTemaAdicionalAsistencia, DiasNoLaborable, DetalleSilaboSemanalSubtema
        from inno.models import RespuestaPreguntaEncuestaSilaboGrupoEstudiantes
        from django.db import connections
        periodorelacionado = False
        listado = []
        periodo = obj.periodo
        fechaactual = datetime.now().date()
        periodos = [obj.periodo.pk]
        detalledistributivo = DetalleDistributivo.objects.get(criteriodocenciaperiodo=obj,
                                                              distributivo__profesor=profesor, status=True)
        fechasactividades = detalledistributivo.actividaddetalledistributivo_set.filter(status=True)[0]
        fechaini = periodo.inicio if fechaini < periodo.inicio else fechaini
        if obj.periodosrelacionados.exists():
            periodorelacionado = True
            periodos = []
            for per in obj.periodosrelacionados.values_list('id', flat=True):
                periodos.append(per)
        if periodos:
            periodorelacionado = ProfesorMateria.objects.values('id').filter(profesor=profesor, materia=materia,
                                                                             materia__nivel__periodo_id__in=periodos).distinct().exists()

        profesormateria = ProfesorMateria.objects.filter(profesor=profesor, materia__nivel__periodo_id__in=periodos,
                                                         materia=materia,
                                                         activo=True, materia__fin__gte=fechasactividades.desde,
                                                         materia__inicio__lte=fechasactividades.hasta).exclude(
            tipoprofesor_id=15).only('materia').distinct()
        for m in profesormateria:
            if not m.materia.tiene_cronograma():
                return 0
        claseactividad = ClaseActividad.objects.filter(detalledistributivo__criteriodocenciaperiodo=obj,
                                                       detalledistributivo__distributivo__profesor=profesor,
                                                       status=True).order_by('inicio', 'dia', 'turno__comienza')

        # para saber total de horas en el mes
        diasclas = claseactividad.values_list('dia', 'turno_id')
        dt = fechaini
        end = fechafin
        step = timedelta(days=1)
        listaretorno = []
        result = []
        while dt <= end:
            dias_nolaborables = obj.periodo.dias_nolaborables(dt)
            if not dias_nolaborables:
                for dclase in diasclas:
                    if dt.isocalendar()[2] == dclase[0]:
                        result.append(dt.strftime('%Y-%m-%d'))
            dt += step
        # if periodo.clasificacion == 1:
        listadotipoprofesor = TipoProfesor.objects.filter(
            pk__in=ProfesorMateria.objects.values_list('tipoprofesor_id').filter(profesor=profesor, materia=materia,
                                                                                 materia__nivel__periodo_id__in=periodos,
                                                                                 tipoprofesor_id__in=[1, 2, 5, 6, 10,
                                                                                                      11, 12, 14, 16],
                                                                                 activo=True,
                                                                                 materia__fin__gte=fechasactividades.desde,
                                                                                 materia__inicio__lte=fechasactividades.hasta).exclude(
                materia__modeloevaluativo_id__in=[26]).distinct())
        resultadominimoplanificar = 0
        resultadoplanificados = 0
        resultadoparciales = '-'
        resultadoporcentajes = 0
        resultadoporcentajessyl = 0
        sumatoriaindice = 0
        sumatoriaindicesyl = 0
        resultadototal = 0
        subtipo_docentes = 0
        listasilabofaltasilabo = []

        porcentajetotalsilabo = 0
        resultadosobre40 = 0
        calculosobre30 = 0

        #---------------------CONFIRMACION DE TEMAS-----------------------#
        # cont = 0
        # porcentajecumplimiento = 0
        # porcentajetotal = 0
        # silabos = Silabo.objects.filter(status=True, materia_id=materia.pk)
        # if silabos:
        #     dias_no_laborales = DiasNoLaborable.objects.values_list('fecha', flat=True).filter(status=True,
        #                                                                                        periodo=periodo)
        #     numeros_semana = []
        #     for fecha in dias_no_laborales:
        #         numero_semana = fecha.isocalendar()[1]
        #         numeros_semana.append(numero_semana)
        #     num_sem_dia_no_laborable = list(dict.fromkeys(numeros_semana))
        #     silabosemanal = silabos.first().silabosemanal_set.filter(status=True)
        #     if silabosemanal:
        #         for silsem in silabosemanal:
        #             unidadsilsem = silsem.temas_seleccionados_planclase()
        #             fechainiciosilabo = silsem.fechainiciosemana
        #             fechafinsilabo = silsem.fechafinciosemana
        #             num_semana_fechainiciosilabo = fechainiciosilabo.isocalendar()[1]
        #             if unidadsilsem:
        #                 for tema in unidadsilsem:
        #                     if fechafinsilabo <= fechaactual:
        #                         cont += 1
        #                         if TemaAsistencia.objects.filter(fecha__lte=fechafinsilabo, tema=tema).exists()  or (num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
        #                             porcentajecumplimiento += 1
        #                     subtemas = silsem.subtemas_silabosemanal(tema.temaunidadresultadoprogramaanalitico)
        #                     if subtemas:
        #                         for subtema in subtemas:
        #                             if fechafinsilabo <= fechaactual:
        #                                 cont += 1
        #                                 if SubTemaAsistencia.objects.filter(fecha__lte=fechafinsilabo, subtema=subtema).exists()  or (num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
        #                                     porcentajecumplimiento += 1
        #                     subtemaadicional = silsem.subtemas_adicionales(tema.id)
        #                     if subtemaadicional:
        #                         for subtemasad in subtemaadicional:
        #                             if fechafinsilabo <= fechaactual:
        #                                 cont += 1
        #                                 if SubTemaAdicionalAsistencia.objects.filter(fecha__lte=fechafinsilabo, subtema=subtemasad).exists()  or (num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
        #                                     porcentajecumplimiento += 1

        cont = 0
        porcentajecumplimiento = 0
        porcentajetotal = 0
        if silabos := Silabo.objects.filter(status=True, materia_id=materia.pk):
            numeros_semana = [fecha.isocalendar()[1] for fecha in periodo.diasnolaborable_set.filter(status=True).values_list('fecha', flat=True)]
            num_sem_dia_no_laborable = list(dict.fromkeys(numeros_semana))
            silabosemanal = silabos.first().silabosemanal_set.filter(status=True)
            if silabosemanal:
                cursor = connections['sga_select'].cursor()
                for silsem in silabosemanal:
                    # unidadsilsem = silsem.temas_seleccionados_planclase()
                    sql_tema = f"""SELECT "sga_detallesilabosemanaltema"."id", "sga_temaunidadresultadoprogramaanalitico"."descripcion", "sga_detallesilabosemanaltema"."temaunidadresultadoprogramaanalitico_id" FROM "sga_detallesilabosemanaltema" INNER JOIN "sga_temaunidadresultadoprogramaanalitico" ON ("sga_detallesilabosemanaltema"."temaunidadresultadoprogramaanalitico_id" = "sga_temaunidadresultadoprogramaanalitico"."id") WHERE ("sga_detallesilabosemanaltema"."silabosemanal_id" = {silsem.pk} AND "sga_temaunidadresultadoprogramaanalitico"."status") ORDER BY "sga_temaunidadresultadoprogramaanalitico"."orden" ASC"""
                    cursor.execute(sql_tema)
                    unidadsilsem = cursor.fetchall()
                    # unidadsilsem = list(silsem.detallesilabosemanaltema_set.select_related('temaunidadresultadoprogramaanalitico').values_list('id','temaunidadresultadoprogramaanalitico__descripcion','temaunidadresultadoprogramaanalitico').filter(temaunidadresultadoprogramaanalitico__status=True).order_by('temaunidadresultadoprogramaanalitico__orden'))
                    fechainiciosilabo = silsem.fechainiciosemana
                    fechafinsilabo = silsem.fechafinciosemana
                    num_semana_fechainiciosilabo = fechainiciosilabo.isocalendar()[1]
                    if unidadsilsem:
                        for tema in unidadsilsem:
                            if fechafinsilabo <= fechaactual:
                                cont += 1
                                if TemaAsistencia.objects.values('id').filter(fecha__lte=fechafinsilabo,tema=tema[0]).exists() or (num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
                                    porcentajecumplimiento += 1
                            subtemas = DetalleSilaboSemanalSubtema.objects.select_related('subtemaunidadresultadoprogramaanalitico').values_list('id', 'subtemaunidadresultadoprogramaanalitico__descripcion').filter(status=True, subtemaunidadresultadoprogramaanalitico__temaunidadresultadoprogramaanalitico=tema[2],subtemaunidadresultadoprogramaanalitico__status=True,subtemaunidadresultadoprogramaanalitico__temaunidadresultadoprogramaanalitico__isnull=False,subtemaunidadresultadoprogramaanalitico__temaunidadresultadoprogramaanalitico__status=True,silabosemanal=silsem).order_by('subtemaunidadresultadoprogramaanalitico__orden')
                            sql_subtemas = f"""SELECT "sga_detallesilabosemanalsubtema"."id", "sga_subtemaunidadresultadoprogramaanalitico"."descripcion" FROM "sga_detallesilabosemanalsubtema" INNER JOIN "sga_subtemaunidadresultadoprogramaanalitico" ON ("sga_detallesilabosemanalsubtema"."subtemaunidadresultadoprogramaanalitico_id" = "sga_subtemaunidadresultadoprogramaanalitico"."id") INNER JOIN "sga_temaunidadresultadoprogramaanalitico" ON ("sga_subtemaunidadresultadoprogramaanalitico"."temaunidadresultadoprogramaanalitico_id" = "sga_temaunidadresultadoprogramaanalitico"."id") WHERE ("sga_detallesilabosemanalsubtema"."silabosemanal_id" = {silsem.pk} AND "sga_detallesilabosemanalsubtema"."status" AND "sga_subtemaunidadresultadoprogramaanalitico"."status" AND "sga_subtemaunidadresultadoprogramaanalitico"."temaunidadresultadoprogramaanalitico_id" = {tema[2]} AND "sga_subtemaunidadresultadoprogramaanalitico"."temaunidadresultadoprogramaanalitico_id" IS NOT NULL AND "sga_temaunidadresultadoprogramaanalitico"."status") ORDER BY "sga_subtemaunidadresultadoprogramaanalitico"."orden" ASC"""
                            cursor.execute(sql_subtemas)
                            subtemas = cursor.fetchall()
                            # subtemas = silsem.subtemas_silabosemanal(tema.temaunidadresultadoprogramaanalitico)
                            for subtema in subtemas:
                                if fechafinsilabo <= fechaactual:
                                    cont += 1
                                    if SubTemaAsistencia.objects.values('id').filter(subtema__silabosemanal=silsem,fecha__lte=fechafinsilabo,subtema=subtema[0]).exists() or ( num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
                                        porcentajecumplimiento += 1
                            # subtemaadicional = silsem.subtemas_adicionales(tema.id)
                            subtemaadicional = silsem.subtemaadicionalessilabo_set.values_list('id', 'subtema').filter(status=True, tema_id=tema[0]).order_by('id')
                            for subtemasad in subtemaadicional:
                                if fechafinsilabo <= fechaactual:
                                    cont += 1
                                    if SubTemaAdicionalAsistencia.objects.values('id').filter(fecha__lte=fechafinsilabo, subtema=subtemasad[0]).exists() or (num_semana_fechainiciosilabo in num_sem_dia_no_laborable):
                                        porcentajecumplimiento += 1

        ####################################################################################################
        # -------------------------------PORCENTAJE DE ENCUESTAS------------------------------------#
        preguntas_con_respuestas = RespuestaPreguntaEncuestaSilaboGrupoEstudiantes.objects.values(
            'pregunta__id', 'pregunta__descripcion'
        ).annotate(
            cantidad_si = Coalesce(Count(Case(When(respuesta='SI', then=1))), Value(0)),
            cantidad_no = Coalesce(Count(Case(When(respuesta='NO', then=1))), Value(0)),
            cantidad_total = F('cantidad_si') + F('cantidad_no'),
            porcentaje = F('cantidad_si') * 100 / F('cantidad_total')
        ).filter(
            ~Q(respuesta__isnull=True), status=True, inscripcionencuestasilabo__materia__id=materia.id)
        suma_total_encuesta = 0
        porcentaje_total_encuesta = 0
        porcentaje_encuesta_sobre30 = 0
        cont_encuesta = 0
        if preguntas_con_respuestas.exists():
            for pregunta in preguntas_con_respuestas:
                suma_total_encuesta += pregunta['porcentaje']
                cont_encuesta += 1
        if cont_encuesta > 0:
            porcentaje_total_encuesta = round((suma_total_encuesta / cont_encuesta), 2)
            porcentaje_encuesta_sobre30 = round(((porcentaje_total_encuesta * 30) / 100), 2)
        else:
            porcentaje_total_encuesta = 0
            porcentaje_encuesta_sobre30 = 0
        ####################################################################################################
        for ltipoprofesor in listadotipoprofesor:
            subtipo_docentes = 1
            nivelacion = False
            listadosilabos = Silabo.objects.filter(status=True, materia_id__in=ProfesorMateria.objects.values_list(
                'materia_id').filter(profesor=profesor, materia__nivel__periodo_id__in=periodos, materia=materia,
                                     tipoprofesor=ltipoprofesor, activo=True, materia__fin__gte=fechasactividades.desde,
                                     materia__inicio__lte=fechasactividades.hasta).distinct())
            if listadosilabos:
                if listadosilabos.filter(materia__asignaturamalla__malla__carrera__coordinacion__id=9).exists():
                    subtipo_docentes += 1
                    nivelacion = True
                    listadosilabos = Silabo.objects.filter(status=True,
                                                           materia_id__in=ProfesorMateria.objects.values_list(
                                                               'materia_id').filter(profesor=profesor, materia=materia,
                                                                                    materia__nivel__periodo_id__in=periodos,
                                                                                    tipoprofesor=ltipoprofesor,
                                                                                    activo=True,
                                                                                    materia__fin__gte=fechasactividades.desde,
                                                                                    materia__inicio__lte=fechasactividades.hasta).exclude(
                                                               materia__asignaturamalla__malla__carrera__coordinacion__id=9).distinct())
                while subtipo_docentes > 0:
                    if not listadosilabos and nivelacion:
                        subtipo_docentes -= 1
                    if subtipo_docentes == 1 and nivelacion:
                        listadosilabos = Silabo.objects.filter(status=True,
                                                               materia_id__in=ProfesorMateria.objects.values_list(
                                                                   'materia_id').filter(profesor=profesor,
                                                                                        materia=materia,
                                                                                        materia__nivel__periodo_id__in=periodos,
                                                                                        tipoprofesor=ltipoprofesor,
                                                                                        activo=True,
                                                                                        materia__fin__gte=fechasactividades.desde,
                                                                                        materia__inicio__lte=fechasactividades.hasta,
                                                                                        materia__asignaturamalla__malla__carrera__coordinacion__id=9).distinct())
                    listadosilabos = listadosilabos.exclude(materia__modeloevaluativo_id__in=[26, 27])
                    totalsilabos = listadosilabos.count()
                    totalsilabosplanificados = listadosilabos.filter(codigoqr=True).count()
                    porcentaje = 0
                    if periodorelacionado:
                        if totalsilabosplanificados >= 1:
                            porcentaje = 100
                    else:
                        try:
                            porcentaje = round(((100 * totalsilabosplanificados) / totalsilabos), 2)
                        except ZeroDivisionError:
                            porcentaje = 0
                    totalcompendioplanificada = 0
                    totalvideoplanificada = 0
                    totalguiaestplanificada = 0
                    totalmaterialplanificada = 0
                    totalcompendiosmoodle = 0
                    totalvideomoodle = 0
                    totalguiaestmoodle = 0
                    totaldiapositivasmoodle = 0
                    totalunidades = 0
                    totalacdplanificado = 0
                    totalacdplanificadosinmigrar = 0
                    totalaaplanificado = 0
                    totalaaplan = 0
                    totalapeplanificado = 0
                    minimoacd = 0
                    minimoaa = 0
                    minimoape = 0
                    tieneape = 0
                    totaldiapositivaplanificada = 0
                    totalmaterialplanificada = 0
                    totalmaterialmoodle = 0
                    totalunidades = 0
                    nombretipo = '{} - NIVELACIÓN'.format(
                        ltipoprofesor.nombre) if subtipo_docentes == 1 and nivelacion else ltipoprofesor.nombre
                    listadolineamiento = ltipoprofesor.lineamientorecursoperiodo_set.filter(periodo_id__in=periodos,
                                                                                            status=True,
                                                                                            nivelacion=True) if subtipo_docentes == 1 and nivelacion else ltipoprofesor.lineamientorecursoperiodo_set.filter(
                        periodo_id__in=periodos, status=True, nivelacion=False)
                    bandera = 0
                    if nombretipo == 'PRÁCTICA':
                        bandera = 1
                    listamateriasfaltaguias = []
                    listamateriasfaltavideo = []
                    listamateriasfaltacompendio = []
                    listamateriasfaltadiapositiva = []
                    listamateriasfaltamaterial = []
                    listamateriasfaltaaa = []
                    listamateriasfaltaacd = []
                    listamateriasfaltaape = []
                    totalminimoacd = 0
                    totalminimoaa = 0
                    totalminimoape = 0
                    totalaamoodle = 0
                    totalacdmoodle = 0
                    totalapemoodle = 0
                    listamateriasfaltadiapositiva = []
                    listamateriasfaltamaterial = []
                    iddiapositiva = 2
                    idmateriales = 11
                    for lsilabo in listadosilabos:
                        # ini -- para saber cuantas unidades han cerrado
                        materiaplanificacion = lsilabo.materia.planificacionclasesilabo_materia_set.filter(
                            status=True).first()
                        listadoparciales = materiaplanificacion.tipoplanificacion.planificacionclasesilabo_set.values_list(
                            'parcial', 'fechafin').filter(status=True).distinct('parcial').order_by('parcial',
                                                                                                    '-fechafin').exclude(
                            parcial=None)
                        if nivelacion:
                            fechamaximalimite = fechasactividades.hasta
                        else:
                            fechamaximalimite = fechafin
                        parciales = listadoparciales.values_list('parcial', 'fechafin', 'fechainicio'). \
                            filter(Q(status=True),
                                   Q(fechafin__lte=fechamaximalimite) | Q(fechainicio__lte=fechamaximalimite)). \
                            distinct('parcial').order_by('parcial', '-fechafin')
                        listaparcialterminadas = []
                        estadoparcial = 'ABIERTO'
                        idparcial = 1
                        fechaparcial = ''
                        for sise in parciales:
                            if sise[1] <= fechafin or sise[2] <= fechafin:
                                listaparcialterminadas.append(sise[0])
                        if not lsilabo.codigoqr:
                            listasilabofaltasilabo.append([2, lsilabo.id, lsilabo.materia, 0, 1])
                        listaunidadterminadas = []
                        silabosemanaluni = lsilabo.silabosemanal_set.values_list(
                            'detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden',
                            'fechafinciosemana').filter(status=True).distinct(
                            'detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden').order_by(
                            'detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden',
                            '-fechafinciosemana')
                        for sise in silabosemanaluni:
                            # if sise[1] >= fechaini and sise[1] <= fechafin:
                            if sise[0]:
                                if sise[1] <= fechafin:
                                    if not sise[0] in listaunidadterminadas:
                                        listaunidadterminadas.append(sise[0])
                        if not listaunidadterminadas:
                            listaunidadterminadas.append(1)
                        # fin --

                        ############################################################################################

                        # silabosemanal = lsilabo.silabosemanal_set.filter(fechafinciosemana__range=(fechaini, fechafin),detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden__in=listaunidadterminadas,status=True)
                        silabosemanal = lsilabo.silabosemanal_set.filter(
                            detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico__orden__in=listaunidadterminadas,
                            detallesilabosemanaltema__status=True, status=True).distinct()
                        totaltemas = 0
                        totalunidades = len(listaunidadterminadas)
                        runidad = []
                        unidades = silabosemanal.filter(status=True).values_list(
                            'detallesilabosemanaltema__temaunidadresultadoprogramaanalitico__unidadresultadoprogramaanalitico_id',
                            flat=True).distinct()
                        for silabosemana in silabosemanal:
                            for u in unidades:
                                if not u in runidad:
                                    runidad.append(u)
                                    totaltemas += len(silabosemana.temas_silabounidad_fecha(u, fechafin))
                                    #########################################

                        # para sacar diapositivas
                        iddiapositiva = 2
                        if iddiapositiva in listadolineamiento.values_list('tiporecurso', flat=True):
                            if lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.exists():
                                totaldiapositivas = DiapositivaSilaboSemanal.objects.filter(
                                    silabosemanal_id__in=silabosemanal.values_list('id'),
                                    iddiapositivamoodle__gt=0,
                                    status=True).count()
                                multiplicador = len(listaparcialterminadas)
                                busc = lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                    tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                        'tipoprofesor').filter(status=True, profesor=profesor,
                                                               tipoprofesor=ltipoprofesor),
                                    tiporecurso=2, status=True)
                                if subtipo_docentes == 1 and nivelacion:
                                    totalminimoacd = 0
                                    busc = busc.filter(nivelacion=True)
                                    for lineaminetoacd in busc.filter(tiporecurso=iddiapositiva):
                                        if lineaminetoacd.aplicapara == 1:
                                            multiplicador = totalunidades
                                        elif lineaminetoacd.aplicapara == 2:
                                            multiplicador = totaltemas
                                totaldiapositivaplan = busc[0].cantidad * multiplicador
                                totaldiapositivaplanificada += totaldiapositivaplan

                                if totaldiapositivas > totaldiapositivaplan:
                                    totaldiapositivasmoodle += totaldiapositivaplan
                                else:
                                    totaldiapositivasmoodle += totaldiapositivas

                                listamateriasfaltadiapositiva.append(
                                    [1, lsilabo.id, lsilabo.materia, totaldiapositivas,
                                     totaldiapositivaplan])

                        # para sacar materialcomplementario
                        idmateriales = 11
                        if idmateriales in listadolineamiento.values_list('tiporecurso', flat=True):
                            if lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.exists():
                                totalmateriales = MaterialAdicionalSilaboSemanal.objects.filter(
                                    silabosemanal_id__in=silabosemanal.values_list('id'),
                                    idmaterialesmoodle__gt=0,
                                    status=True).count()
                                multiplicador = len(listaparcialterminadas)
                                lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                    tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                        'tipoprofesor').filter(status=True, profesor=profesor,
                                                               tipoprofesor=ltipoprofesor), tiporecurso=11,
                                    status=True)

                                busc = lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                    tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                        'tipoprofesor').filter(status=True, profesor=profesor,
                                                               tipoprofesor=ltipoprofesor),
                                    tiporecurso=11, status=True)
                                if subtipo_docentes == 1 and nivelacion:
                                    totalminimoacd = 0
                                    busc = busc.filter(nivelacion=True)
                                    for lineaminetoacd in busc.filter(tiporecurso=iddiapositiva):
                                        if lineaminetoacd.aplicapara == 1:
                                            multiplicador = totalunidades
                                        elif lineaminetoacd.aplicapara == 2:
                                            multiplicador = totaltemas
                                else:
                                    busc = busc.exclude(nivelacion=True)
                                totalmaterialplan = busc[0].cantidad * multiplicador
                                totalmaterialplanificada += totalmaterialplan
                                if totalmateriales > totalmaterialplan:
                                    totalmaterialmoodle += totalmaterialplan
                                else:
                                    totalmaterialmoodle += totalmateriales

                                listamateriasfaltamaterial.append(
                                    [2, lsilabo.id, lsilabo.materia, totalmateriales, totalmaterialplan])

                        ########################################
                        # para sacar compendios
                        idcompendio = 1
                        if idcompendio in listadolineamiento.values_list('tiporecurso', flat=True):
                            totalcompendios = CompendioSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanal.values_list('id'), idmcompendiomoodle__gt=0,
                                status=True).count()
                            totalcompendioplan = lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                    'tipoprofesor').filter(status=True, materia=materia), tiporecurso=1, status=True)[
                                                     0].cantidad * len(
                                listaunidadterminadas)
                            totalcompendioplanificada += totalcompendioplan
                            if totalcompendios > totalcompendioplan:
                                totalcompendiosmoodle += totalcompendioplan
                            else:
                                totalcompendiosmoodle += totalcompendios
                            if totalcompendios < totalcompendioplan:
                                listamateriasfaltacompendio.append(
                                    [lsilabo.id, lsilabo.materia, totalcompendios, totalcompendioplan])

                        # para sacar videomagistral
                        idvideomagistral = 12
                        if idvideomagistral in listadolineamiento.values_list('tiporecurso', flat=True):
                            totalvideos = VideoMagistralSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanal.values_list('id'), idvidmagistralmoodle__gt=0,
                                status=True).count()
                            totalvideoplan = lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                    'tipoprofesor').filter(status=True, materia=materia), tiporecurso=12, status=True)[
                                                 0].cantidad * len(
                                listaunidadterminadas)
                            totalvideoplanificada += totalvideoplan
                            if totalvideos > totalvideoplan:
                                totalvideomoodle += totalvideoplan
                            else:
                                totalvideomoodle += totalvideos
                            if totalvideos < totalvideoplan:
                                listamateriasfaltavideo.append(
                                    [lsilabo.id, lsilabo.materia, totalvideos, totalvideoplan])

                        # para sacar guiaestudiante
                        idguiaestudiante = 4
                        if idguiaestudiante in listadolineamiento.values_list('tiporecurso', flat=True):
                            totalguiaestudiante = GuiaEstudianteSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanal.values_list('id'), idguiaestudiantemoodle__gt=0,
                                status=True).count()
                            totalguiaestudianteplan = \
                                lsilabo.materia.nivel.periodo.lineamientorecursoperiodo_set.filter(
                                    tipoprofesor_id__in=lsilabo.materia.profesormateria_set.values_list(
                                        'tipoprofesor').filter(status=True, materia=materia), tiporecurso=4,
                                    status=True)[0].cantidad * len(
                                    listaunidadterminadas)
                            totalguiaestplanificada += totalguiaestudianteplan
                            if totalguiaestudiante > totalguiaestudianteplan:
                                totalguiaestmoodle += totalguiaestudianteplan
                            else:
                                totalguiaestmoodle += totalguiaestudiante
                            if totalguiaestudiante < totalguiaestudianteplan:
                                listamateriasfaltaguias.append(
                                    [lsilabo.id, lsilabo.materia, totalguiaestudiante, totalguiaestudianteplan])

                        # para sacar los compenentes acd ,aa ,ape
                        materiaplanificacion = lsilabo.materia.planificacionclasesilabo_materia_set.filter(status=True)[
                            0]
                        listadoparciales = materiaplanificacion.tipoplanificacion.planificacionclasesilabo_set.values_list(
                            'parcial', 'fechafin').filter(status=True).distinct('parcial').order_by('parcial',
                                                                                                    '-fechafin').exclude(
                            parcial=None)
                        if obj.periodosrelacionados.exists():
                            if nivelacion:
                                fecha_limite = fechasactividades.hasta + timedelta(days=30)
                            else:
                                fecha_limite = fechafin + timedelta(days=30)
                            parciales = listadoparciales.values_list('parcial', 'fechafin').filter(status=True,
                                                                                                   fechafin__lte=fecha_limite).distinct(
                                'parcial').order_by('parcial', '-fechafin')
                        else:
                            parciales = listadoparciales.values_list('parcial', 'fechafin', 'fechainicio').filter(
                                Q(status=True), Q(fechafin__lte=fechafin) | Q(fechainicio__lte=fechafin)).distinct(
                                'parcial').order_by('parcial', '-fechafin')
                        listaparcialterminadas = []
                        estadoparcial = 'ABIERTO'
                        idparcial = 1 if not obj.periodo.tipo.id in [3, 4] else 0
                        fechaparcial = ''
                        for sise in parciales:
                            if obj.periodosrelacionados.exists():
                                idparcial = sise[0]
                                listaparcialterminadas.append(sise[0])
                            else:
                                if sise[1] <= fechafin or sise[2] <= fechafin:
                                    idparcial = sise[0]
                                    listaparcialterminadas.append(sise[0])
                        for lpar in listadoparciales:
                            if listadoparciales.order_by('-parcial')[0][0] == lpar[0]:
                                if fechafin >= lpar[1]:
                                    estadoparcial = 'CERRADO'
                            if lpar[0] == idparcial:
                                fechaparcial = lpar[1]

                        if periodo.tipo.id not in [3, 4]:
                            listadocomponentes = lsilabo.materia.nivel.periodo.evaluacioncomponenteperiodo_set.select_related(
                                'componente').filter(nivelacion=True, parcial__in=listaparcialterminadas,
                                                     status=True) if subtipo_docentes == 1 and nivelacion else lsilabo.materia.nivel.periodo.evaluacioncomponenteperiodo_set.select_related(
                                'componente').filter(parcial__in=listaparcialterminadas, status=True)
                        else:
                            listadocomponentes = lsilabo.materia.nivel.periodo.evaluacioncomponenteperiodo_set.select_related(
                                'componente').filter(status=True)

                        # para sacar todos los silabos semanales segun fecha fin del parcial
                        silabosemanalparcial = lsilabo.silabosemanal_set.filter(fechafinciosemana__lte=fechaparcial,
                                                                                status=True)
                        if lsilabo.materia.modeloevaluativo.id != 25:
                            if listadocomponentes.filter(componente_id=1):
                                multiplicador = len(listaparcialterminadas)
                                if subtipo_docentes == 1 and nivelacion:
                                    totalminimoacd = 0
                                    for lineaminetoacd in listadolineamiento.filter(tiporecurso=7):
                                        if lineaminetoacd.aplicapara == 1:
                                            multiplicador = totalunidades
                                        elif lineaminetoacd.aplicapara == 2:
                                            multiplicador = totaltemas
                                        totalminimoacd += lineaminetoacd.cantidad * multiplicador
                                else:
                                    totalminimoacd = listadocomponentes.filter(componente_id=1,
                                                                               nivelacion=False).first().cantidad * multiplicador
                                minimoacd += totalminimoacd
                        totalacdplanificadotar = 0
                        totalacdplanificadosinmigrartar = 0
                        if (subtipo_docentes == 1 and not nivelacion) or (subtipo_docentes == 2 and nivelacion):
                            totalacdplanificadotar = TareaSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'), idtareamoodle__gt=0,
                                actividad_id__in=[2, 3], status=True).count()
                            totalacdplanificadosinmigrartar = TareaSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                                actividad_id__in=[2, 3], status=True).count()

                        if subtipo_docentes == 1 and nivelacion:
                            totalacdplanificadotest = TestSilaboSemanalAdmision.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'), idtestmoodle__gt=0,
                                status=True).count()
                            totalacdplanificadosinmigrartest = TestSilaboSemanalAdmision.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                                status=True).count()

                        else:
                            totalacdplanificadotest = TestSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'), idtestmoodle__gt=0,
                                status=True).count()
                            totalacdplanificadosinmigrartest = TestSilaboSemanal.objects.filter(
                                silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                                status=True).count()
                        totalacdplanificado += totalacdplanificadotar + totalacdplanificadotest
                        totalplanificadoacd = totalacdplanificadotar + totalacdplanificadotest

                        totalacdplanificadosinmigrar += totalacdplanificadosinmigrartar + totalacdplanificadosinmigrartest

                        if totalplanificadoacd > totalminimoacd:
                            totalacdmoodle += totalminimoacd
                        else:
                            totalacdmoodle += totalplanificadoacd
                        if estadoparcial == 'CERRADO':
                            if totalplanificadoacd < totalminimoacd:
                                listamateriasfaltaacd.append(
                                    [lsilabo.id, lsilabo.materia, totalplanificadoacd, totalminimoacd])

                        totalaaplanificadosinmigrartar = 0
                        if lsilabo.materia.modeloevaluativo.id != 25:
                            if listadocomponentes.filter(componente_id=3):
                                totalminimoaa = listadocomponentes.filter(componente_id=3)[0].cantidad * len(
                                    listaparcialterminadas)
                                minimoaa += totalminimoaa
                        totalplanificadoaatar = TareaSilaboSemanal.objects.filter(
                            silabosemanal_id__in=silabosemanalparcial.values_list('id'), idtareamoodle__gt=0,
                            actividad_id__in=[5, 7, 8], status=True).count()
                        totalplanificadoaasinmigrartar = TareaSilaboSemanal.objects.filter(
                            silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                            actividad_id__in=[5, 7, 8], status=True).count()
                        totalplanificadoaafor = ForoSilaboSemanal.objects.filter(
                            silabosemanal_id__in=silabosemanalparcial.values_list('id'), idforomoodle__gt=0,
                            status=True).count()
                        totalplanificadoaasinmigrarfor = ForoSilaboSemanal.objects.filter(
                            silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                            status=True).count()
                        totalaaplanificado += totalplanificadoaatar + totalplanificadoaafor
                        totalplanificadoaa = totalplanificadoaatar + totalplanificadoaafor
                        totalaaplanificadosinmigrartar += totalplanificadoaasinmigrartar + totalplanificadoaasinmigrarfor

                        if totalplanificadoaa > totalminimoaa:
                            totalaamoodle += totalminimoaa
                        else:
                            totalaamoodle += totalplanificadoaa
                        if estadoparcial == 'CERRADO':
                            if totalplanificadoaa < totalminimoaa:
                                listamateriasfaltaaa.append(
                                    [lsilabo.id, lsilabo.materia, totalplanificadoaa, totalminimoaa])
                        totalapeplanificadosinmigrartar = 0
                        if lsilabo.materia.asignaturamalla.horasapeasistotal > 0:
                            if lsilabo.materia.modeloevaluativo.id != 25:
                                if listadocomponentes.filter(componente_id=2):
                                    totalminimoape = listadocomponentes.filter(componente_id=2)[0].cantidad * len(
                                        listaparcialterminadas)
                                    minimoape += totalminimoape
                                totalapeplanificadotar = TareaPracticaSilaboSemanal.objects.filter(
                                    silabosemanal_id__in=silabosemanalparcial.values_list('id'),
                                    idtareapracticamoodle__gt=0, status=True)
                                totalapeplanificadosinmigrartar = TareaPracticaSilaboSemanal.objects.filter(
                                    silabosemanal_id__in=silabosemanalparcial.values_list('id'), status=True).count()

                                totalapeplanificado += totalapeplanificadotar.count()
                                totalaaplanificadosinmigrartar += totalapeplanificadosinmigrartar
                                # totalapeplanificadoape = totalapeplanificadotar.count()
                                totalapeplanificadoape = totalapeplanificadotar.values_list(
                                    'silabosemanal__parcial').distinct().count()
                                tieneape = 1
                                if totalapeplanificadoape > totalminimoape:
                                    totalapemoodle += totalminimoape
                                else:
                                    totalapemoodle += totalapeplanificadoape
                                if estadoparcial == 'CERRADO':
                                    if totalapeplanificadoape < totalminimoape:
                                        listamateriasfaltaape.append(
                                            [lsilabo.id, lsilabo.materia, totalapeplanificadoape, totalminimoape])
                    ##################################################

                    if iddiapositiva in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajediapositivas = 0
                            if totaldiapositivasmoodle >= 1:
                                porcentajediapositivas = 100
                        else:
                            try:
                                porcentajediapositivas = round(
                                    ((100 * totaldiapositivasmoodle) / totaldiapositivaplanificada), 2)
                            except ZeroDivisionError:
                                porcentajediapositivas = 0
                    if idmateriales in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajematerial = 0
                            if totalmaterialmoodle >= 1:
                                porcentajematerial = 100
                        else:
                            try:
                                porcentajematerial = round(((100 * totalmaterialmoodle) / totalmaterialplanificada), 2)
                            except ZeroDivisionError:
                                porcentajematerial = 0
                    resultadominimoplanificar += totalsilabos
                    resultadoplanificados += totalsilabosplanificados
                    resultadoporcentajessyl += porcentaje
                    sumatoriaindicesyl += 1
                    ##################################################
                    if idcompendio in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajecompendios = 0
                            if totalcompendiosmoodle >= 1:
                                porcentajecompendios = 100
                        else:
                            try:
                                porcentajecompendios = round(
                                    ((100 * totalcompendiosmoodle) / totalcompendioplanificada), 2)
                            except ZeroDivisionError:
                                porcentajecompendios = 0
                    if idvideomagistral in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajevideo = 0
                            if totalvideomoodle >= 1:
                                porcentajevideo = 100
                        else:
                            try:
                                porcentajevideo = round(((100 * totalvideomoodle) / totalvideoplanificada), 2)
                            except ZeroDivisionError:
                                porcentajevideo = 0

                    if idguiaestudiante in listadolineamiento.values_list('tiporecurso', flat=True):
                        if periodorelacionado:
                            porcentajeguiaestudiante = 0
                            if totalguiaestmoodle >= 1:
                                porcentajeguiaestudiante = 100
                            else:
                                if totalguiaestplanificada == 0:
                                    porcentajeguiaestudiante = 100
                        else:
                            if totalguiaestplanificada == 0:
                                porcentajeguiaestudiante = 100
                            else:
                                try:
                                    porcentajeguiaestudiante = round(
                                        ((100 * totalguiaestmoodle) / totalguiaestplanificada), 2)
                                except ZeroDivisionError:
                                    porcentajeguiaestudiante = 0
                    try:
                        porcentajeacd = 0
                        if periodorelacionado:
                            if totalacdmoodle >= 1:
                                porcentajeacd = 100
                        else:
                            if totalacdmoodle > minimoacd:
                                porcentajeacd = 100
                            else:
                                porcentajeacd = round(((100 * totalacdmoodle) / minimoacd), 2)
                    except ZeroDivisionError:
                        porcentajeacd = 0
                    if porcentajeacd > 100:
                        porcentajeacd = 100
                    if estadoparcial == 'ABIERTO' and not nivelacion:
                        porcentajeacd = 100
                    try:
                        porcentajeaa = 0
                        if periodorelacionado:
                            if totalaamoodle >= 1:
                                porcentajeaa = 100
                        else:
                            if totalaamoodle > minimoaa:
                                porcentajeaa = 100
                            else:
                                porcentajeaa = round(((100 * totalaamoodle) / minimoaa), 2)
                    except ZeroDivisionError:
                        porcentajeaa = 0
                    if porcentajeaa > 100:
                        porcentajeaa = 100
                    if estadoparcial == 'ABIERTO':
                        porcentajeaa = 100

                    if tieneape == 1:
                        try:
                            porcentajeape = 0
                            if periodorelacionado:
                                if totalapemoodle >= 1:
                                    porcentajeape = 100
                            else:
                                if totalapemoodle > minimoape:
                                    porcentajeape = 100
                                else:
                                    porcentajeape = round(((100 * totalapemoodle) / minimoape), 2)
                        except ZeroDivisionError:
                            porcentajeape = 0
                        if porcentajeape > 100:
                            porcentajeape = 100
                        if estadoparcial == 'ABIERTO':
                            porcentajeape = 100

                    ###########################################

                    if iddiapositiva in listadolineamiento.values_list('tiporecurso', flat=True):
                        resultadominimoplanificar += totaldiapositivaplanificada
                        resultadoplanificados += totaldiapositivasmoodle
                        resultadoporcentajessyl += porcentajediapositivas
                        sumatoriaindicesyl += 1
                    if idmateriales in listadolineamiento.values_list('tiporecurso', flat=True):
                        resultadominimoplanificar += totalmaterialplanificada
                        resultadoplanificados += totalmaterialmoodle
                        resultadoporcentajessyl += porcentajematerial
                        sumatoriaindicesyl += 1

                    ############################################
                    if idcompendio in listadolineamiento.values_list('tiporecurso', flat=True):
                        resultadominimoplanificar += totalcompendioplanificada
                        resultadoplanificados += totalcompendiosmoodle
                        resultadoporcentajes += porcentajecompendios
                        sumatoriaindice += 1
                    if idvideomagistral in listadolineamiento.values_list('tiporecurso', flat=True):
                        resultadominimoplanificar += totalvideoplanificada
                        resultadoplanificados += totalvideomoodle
                        resultadoporcentajes += porcentajevideo
                        sumatoriaindice += 1
                    if idguiaestudiante in listadolineamiento.values_list('tiporecurso', flat=True):
                        resultadominimoplanificar += totalguiaestplanificada
                        resultadoplanificados += totalguiaestmoodle
                        resultadoporcentajes += porcentajeguiaestudiante
                        sumatoriaindice += 1
                    sumatoriaindice += 1
                    if (subtipo_docentes == 1 and not nivelacion) or (subtipo_docentes == 2 and nivelacion):
                        sumatoriaindice += 1
                    if tieneape == 1:
                        sumatoriaindice += 1
                    resultadominimoplanificar += minimoacd
                    resultadominimoplanificar += minimoaa
                    if tieneape == 1:
                        resultadominimoplanificar += minimoape
                    resultadoplanificados += totalacdplanificado
                    resultadoplanificados += totalaaplanificado
                    if tieneape == 1:
                        resultadoplanificados += totalapeplanificado
                    resultadoporcentajes += porcentajeacd
                    if (subtipo_docentes == 1 and not nivelacion) or (subtipo_docentes == 2 and nivelacion):
                        resultadoporcentajes += porcentajeaa
                    if tieneape == 1:
                        resultadoporcentajes += porcentajeape
                    subtipo_docentes -= 1
        try:
            resultadoporcentajes = round(((resultadoporcentajes) / sumatoriaindice), 2)
        except ZeroDivisionError:
            resultadoporcentajes = 0

        try:
            resultadoporcentajessyl = round(((resultadoporcentajessyl) / sumatoriaindicesyl), 2)
        except ZeroDivisionError:
            resultadoporcentajessyl = 0
        try:
            resultadototal = round(((resultadoporcentajes + resultadoporcentajessyl) / 2), 2)
        except ZeroDivisionError:
            resultadototal = 0

        try:
            resultadosobre40 = round(((resultadototal * 40) / 100), 2)
        except ZeroDivisionError:
            resultadosobre40 = 0

        try:
            ######CONFIRMACION TEMAS
            percent = round((porcentajecumplimiento / cont), 2)
            percent = round((percent * 100), 2)
            calculosobre30 = round(((percent * 30) / 100), 2)
        except ZeroDivisionError:
            percent = 0
            calculosobre30 = 0
        ######SUMATORIA PUNTAJE SILABO
        porcentajetotalsilabo = round((resultadosobre40 + calculosobre30 + porcentaje_encuesta_sobre30), 2)
        #####TOTAL SIN CONTAR ENCUESTA
        # porcentajetotalsilabo = round(((porcentajetotalsilabo *100) / 70), 2)

        listado.append(
            [claseactividad, resultadominimoplanificar, resultadoplanificados, resultadoporcentajes, len(result), 0, 4,
             [], resultadosobre40, resultadototal, calculosobre30, porcentaje_encuesta_sobre30, porcentajetotalsilabo])
        return listado
    except Exception as e:
        import sys
        print(e)
        print('Error on line {} - {}'.format(sys.exc_info()[-1].tb_lineno, e))


def tipo_archivo(namefile=''):
    ext = namefile[namefile.rfind("."):].lower()
    if ext in ['.pdf']:
        return 'pdf'
    elif ext in ['.png', '.jpg', '.jpeg', '.svg']:
        return 'img'
    elif ext in ['.xls', '.xlsx', '.xlsx', '.xlsb']:
        return 'excel'
    elif ext in ['.docx', '.doc']:
        return 'word'
    else:
        return 'otro'


def clean_text(html_content=''):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    solo_texto = soup.get_text().replace('\n', '<br>')
    return solo_texto

def clean_text_parsereportlab(html_content=''):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    solo_texto = soup.get_text().replace('\n', '<br/>')
    return solo_texto

def clean_text_coma(html_content=''):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    solo_texto = soup.get_text().strip()
    # Elimina solo el primer carácter de nueva línea
    if solo_texto.startswith('\n'):
        solo_texto = solo_texto[1:]
    solo_texto = solo_texto.replace('\n', ', ').replace(', , ', ', ')
    return solo_texto.capitalize()

def tiene_solicitud_de_ingreso_titulacion_posgrado(pk):
    from sga.models import TemaTitulacionPosgradoMatricula
    from posgrado.models import SolicitudIngresoTitulacionPosgrado
    eTemaTitulacionPosgradoMatricula = TemaTitulacionPosgradoMatricula.objects.get(pk=pk)
    eSolicitudIngresoTitulacionPosgrado = SolicitudIngresoTitulacionPosgrado.objects.filter(status=True,matricula = eTemaTitulacionPosgradoMatricula.matricula,firmado=True)
    return eSolicitudIngresoTitulacionPosgrado if eSolicitudIngresoTitulacionPosgrado.exists() else None

def calculaporcentaje(var, value):
    return round((value / var) * 100, 2)

register.filter('mod4', mod4)
register.filter('diaenletra', diaenletra)
register.filter('filedsmodel', fields_model)
register.filter('fielddefaultvaluemodel', field_default_value_model)
register.filter('ceros', ceros)
register.filter('fechamayor', fechamayor)
register.filter('fechaletra_corta', fechaletra_corta)
register.filter('times', times)
register.filter('multipilca', multipilca)
register.filter("call", callmethod)
register.filter("args", args)
register.filter("transformar_n_l", transformar_n_l)
register.filter("transformar_mes", transformar_mes)
register.filter("traernombre", traernombre)
register.filter("traernombrecarrera", traernombrecarrera)
register.filter("suma", suma)
register.filter("sumar_fm", sumar_fm)
register.filter("sumar_fh", sumar_fh)
register.filter("sumar_cm", sumar_cm)
register.filter("sumar_ch", sumar_ch)
register.filter("sumar_th", sumar_th)
register.filter("sumar_pagineo", sumar_pagineo)
register.filter("colores", colores)
register.filter("sumar_tm", sumar_tm)
register.filter("resta", resta)
register.filter("restanumeros", restanumeros)
register.filter("cincoacien", cincoacien)
register.filter("multiplicanumeros", multiplicanumeros)
register.filter("entrefechas", entrefechas)
register.filter("porciento", porciento)
register.filter("nombremescorto", nombremescorto)
register.filter("numerotemas", numerotemas)
register.filter("numerotemasdiv", numerotemasdiv)
register.filter("llevaraporcentaje", llevaraporcentaje)
register.filter("substraer", substraer)
register.filter("nombremes", nombremes)
register.filter("numeromes", numeromes)
register.filter("fechapermiso", fechapermiso)
register.filter("nombrepersona", nombrepersona)
register.filter("datename", datename)
register.filter("sumarfecha", sumarfecha)
register.filter("sumarvalores", sumarvalores)
register.filter("divide", divide)
register.filter("calendarbox", calendarbox)
register.filter("calendarboxdetails", calendarboxdetails)
register.filter("calendarboxdetails2", calendarboxdetails2)
register.filter("calendarboxdetailspracticas", calendarboxdetailspracticas)
register.filter("listar_campos_tabla", listar_campos_tabla)
register.filter("tieneestudiantepracticas", tieneestudiantepracticas)
register.filter("calevaluaciondocente", calevaluaciondocente)
register.filter("calmodeloevaluaciondocente", calmodeloevaluaciondocente)
register.filter("calmodeloevaluaciondocente2015", calmodeloevaluaciondocente2015)
register.filter("gedc_calculos", gedc_calculos)
register.filter("gedc_calculos_grafica", gedc_calculos_grafica)
register.filter("existe_validacion", existe_validacion)
register.filter("calendarboxdetailsmostrar", calendarboxdetailsmostrar)
register.filter("barraporciento", barraporciento)
register.filter("solo_caracteres", solo_caracteres)
register.filter("rangonumeros", rangonumeros)
register.filter("splitcadena", splitcadena)
register.filter("encrypt", encrypt)
register.filter("encrypt_alu", encrypt_alu)
register.filter("substraerconpunto", substraerconpunto)
register.filter("substraersinpuntohasta", substraersinpuntohasta)
register.filter("substraersinpuntodesde", substraersinpuntodesde)
register.filter("contarcaracter", contarcaracter)
register.filter("cambiarlinea", cambiarlinea)
register.filter("extraer", extraer)
register.filter("tranformarstring", tranformarstring)
register.filter("fechamayor_aux", fechamayor_aux)
register.filter("sumauno", sumauno)
register.filter("datetimename", datetimename)
register.filter("num_notificaciones_modulo", num_notificaciones_modulo)
register.filter("get_manual_usuario_modulo", get_manual_usuario_modulo)
register.filter("diaenletra_fecha", diaenletra_fecha)
register.filter("diaisoweekday", diaisoweekday)
register.filter("numero_a_letras", numero_a_letras)
register.filter("title2", title2)
register.filter("predecesoratitulacion", predecesoratitulacion)
register.filter("pertenecepredecesoratitulacion", pertenecepredecesoratitulacion)
register.filter("notafinalmateriatitulacion", notafinalmateriatitulacion)
register.filter("actasgradopendiente", actasgradopendiente)
register.filter("actasconsolidadaspendientes", actasconsolidadaspendientes)
register.filter("firmaactagradosistema", firmaactagradosistema)
register.filter("realizo_busqueda", realizo_busqueda)
register.filter("tipo_archivo", tipo_archivo)
register.filter("clean_text", clean_text)
register.filter("clean_text_coma", clean_text_coma)
register.filter("tiene_solicitud_de_ingreso_titulacion_posgrado", tiene_solicitud_de_ingreso_titulacion_posgrado)
register.filter("calculaedad", calculaedad)
register.filter("calculaporcentaje", calculaporcentaje)
