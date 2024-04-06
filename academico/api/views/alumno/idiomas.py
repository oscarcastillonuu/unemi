# coding=utf-8
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from api.helpers.decorators import api_security
from api.helpers.response_herlper import Helper_Response
from api.serializers.alumno.idiomas import PeriodoSerializer, GrupoSerializer, GrupoInscripcionSerializer, \
    IdiomaSerializer, GrupoInscripcionAsignaturaSerializer
from idioma.models import Grupo, Periodo, GrupoInscripcion, GrupoInscripcionAsignatura
from sga.models import PerfilUsuario, Malla, RecordAcademico, Idioma
from sga.templatetags.sga_extras import encrypt

class IdiomaAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    api_key_module = 'ALUMNO_IDIOMA_KEY'

    @api_security
    def post(self, request):
        hoy = datetime.now().date()
        payload = request.auth.payload
        ePerfilUsuario = PerfilUsuario.objects.get(pk=encrypt(payload['perfilprincipal']['id']))
        if not ePerfilUsuario.es_estudiante():
            raise NameError(u'Solo los perfiles de estudiantes pueden ingresar al modulo.')
        eInscripcion = ePerfilUsuario.inscripcion

        if 'multipart/form-data' in request.content_type:
            eRequest = request._request.POST
            eFiles = request._request.FILES
        else:
            eRequest = request.data
        try:
            if not 'action' in eRequest:
                raise NameError(u'Parametro de acciòn no encontrado')

            action = eRequest['action']

            if action == 'guardar_inscripcion':
                try:
                    ESTADO_SOLICITADO = 0
                    id = int(encrypt(eRequest['id']))
                    eGrupo = Grupo.objects.get(pk=id)
                    if not GrupoInscripcion.objects.values('id').filter(status=True, grupo = eGrupo,inscripcion=eInscripcion).exists():
                        if eGrupo.existe_cupo_disponible():
                            eGrupoInscripcion = GrupoInscripcion(grupo=eGrupo,
                                                                 inscripcion = eInscripcion,
                                                                 estado = ESTADO_SOLICITADO)
                            eGrupoInscripcion.save(request)
                        else:
                            raise NameError(u'Lo sentimos, no existe cupos disponibles en este grupo, actualice e intente de nuevo.')
                    else:
                            raise NameError( u'Ya se encuentra registrada su inscripción')
                    aData = {}
                    return Helper_Response(isSuccess=True, data=aData, status=status.HTTP_200_OK)
                except Exception as ex:
                    return Helper_Response(isSuccess=False, data={}, message=f'Ocurrio un error: {ex.__str__()}',
                                           status=status.HTTP_200_OK)




            return Helper_Response(isSuccess=False, data={}, message=f'Acciòn no encontrada', status=status.HTTP_200_OK)
        except Exception as ex:
            return Helper_Response(isSuccess=False, data={}, message=f'Ocurrio un error: {ex.__str__()}', status=status.HTTP_200_OK)

    @api_security
    def get(self, request):
        try:
            if 'action' in request.query_params:
                action = request.query_params['action']
                if action == 'loadGrupos':
                    try:
                        id = int(encrypt(request.query_params['id']))
                        ePeriodo = Periodo.objects.get(pk=id)
                        eGrupo= ePeriodo.primer_grupo_disponible()
                        grupoSerializer = GrupoSerializer(eGrupo)
                        aData = {
                            'eGrupo': grupoSerializer.data if eGrupo else [],

                        }
                        return Helper_Response(isSuccess=True, data=aData, status=status.HTTP_200_OK)
                    except Exception as ex:
                        return Helper_Response(isSuccess=False, data={}, message=f'Ocurrio un error: {ex.__str__()}',
                                               status=status.HTTP_200_OK)

                if action == 'loadModulosHomologados':
                    try:
                        id = int(encrypt(request.query_params['id']))
                        eGrupoInscripcion = GrupoInscripcion.objects.get(pk = id)
                        eGrupoInscripcion_serializer = GrupoInscripcionSerializer(eGrupoInscripcion)

                        aData = {
                            'eGrupoInscripcion': eGrupoInscripcion_serializer.data if eGrupoInscripcion else [],

                        }
                        return Helper_Response(isSuccess=True, data=aData, status=status.HTTP_200_OK)
                    except Exception as ex:
                        return Helper_Response(isSuccess=False, data={}, message=f'Ocurrio un error: {ex.__str__()}',
                                               status=status.HTTP_200_OK)

                if action == 'loadTablaHomologar':
                    try:
                        id = int(encrypt(request.query_params['id']))
                        eGrupoInscripcion = GrupoInscripcion.objects.get(pk=id)
                        eGrupoInscripcion_serializer = GrupoInscripcionSerializer(eGrupoInscripcion)

                        aData = {
                            'eGrupoInscripcion': eGrupoInscripcion_serializer.data if eGrupoInscripcion else [],

                        }
                        return Helper_Response(isSuccess=True, data=aData, status=status.HTTP_200_OK)
                    except Exception as ex:
                        return Helper_Response(isSuccess=False, data={}, message=f'Ocurrio un error: {ex.__str__()}',
                                               status=status.HTTP_200_OK)

            else:
                try:
                    hoy = datetime.now().date()
                    payload = request.auth.payload
                    ePerfilUsuario = PerfilUsuario.objects.get(pk=encrypt(payload['perfilprincipal']['id']))
                    if not ePerfilUsuario.es_estudiante():
                        raise NameError(u'Solo los perfiles de estudiantes pueden ingresar al modulo.')
                    inscripcion = ePerfilUsuario.inscripcion
                    if inscripcion.carrera.id == 7 or inscripcion.carrera.id == 138 or inscripcion.carrera.id == 129 or inscripcion.carrera.id == 90 or inscripcion.carrera.id == 157 or inscripcion.carrera.id == 134:
                        raise NameError(u'Lo sentimos, no puedes inscribirte porque ya constan las materias de ingles en tu carrera.')

                    eIdioma = Idioma.objects.filter(status=True)
                    idiomas_serializer = IdiomaSerializer(eIdioma, many=True)

                    ePeriodo = Periodo.objects.filter(status=True, estado=True)
                    periodoSerializer = PeriodoSerializer(ePeriodo, many=True)

                    malla_ingles = Malla.objects.get(pk=353)
                    id_asignaturas_ingles=  malla_ingles.lista_materias_malla().values_list('asignatura__id',flat = True)
                    cursa_modulo_de_ingles = RecordAcademico.objects.filter(status=True,inscripcion = inscripcion, asignatura_id__in= id_asignaturas_ingles).exists()

                    eGrupoInscripcion = GrupoInscripcion.objects.filter(status=True, inscripcion=inscripcion)
                    gruposInscripcionSerializer = GrupoInscripcionSerializer(eGrupoInscripcion, many=True)
                    data = {
                        'ePeriodo': periodoSerializer.data if ePeriodo else [],
                        'mis_gruposInscripcion': gruposInscripcionSerializer.data if eGrupoInscripcion else [],
                        'idiomas': idiomas_serializer.data if eIdioma else [],
                        'cursa_modulo_de_ingles': cursa_modulo_de_ingles,

                    }
                    return Helper_Response(isSuccess=True, data=data, status=status.HTTP_200_OK)
                except Exception as ex:
                    return Helper_Response(isSuccess=False, data={}, message=f'Ocurrio un error: {ex.__str__()}', status=status.HTTP_200_OK)
        except Exception as ex:
            return Helper_Response(isSuccess=False, data={}, message=f'Ocurrio un error: {ex.__str__()}',
                                   status=status.HTTP_200_OK)