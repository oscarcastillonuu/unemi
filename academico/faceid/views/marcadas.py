# -*- coding: latin-1 -*-
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from decorators import inhouse_check, get_client_ip
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
# from faceid.backEnd import FaceRecognition
from sagest.models import LogDia, LogMarcada, MarcadasDia, RegistroMarcada
from settings import DEBUG
from sga.funciones import variable_valor, loglogin, isInsideUnemi
from bd.models import APP_SGA, APP_SAGEST, APP_POSGRADO, APP_MARCADAS, FLAG_FAILED, FLAG_SUCCESSFUL, FLAG_UNKNOWN
from sga.models import Persona
from faceid.functions import calculando_marcadasotro


@transaction.atomic()
def index(request):
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'updateTime':
            try:
                hour = datetime.now().time().hour
                minute = datetime.now().time().minute
                second = datetime.now().time().second
                if hour < 10:
                    hour = '0' + str(hour)
                if minute < 10:
                    minute = '0' + str(minute)
                if second < 10:
                    second = '0' + str(second)
                tiempo = {"hour": str(hour),
                          "minute": str(minute),
                          "second": str(second)}
                return JsonResponse({"result": "ok", "tiempo": tiempo})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'checkAuth':
            try:
                if not inhouse_check(request):
                    raise NameError(u'No puede ingresar marcadas fuera de la institucion.')
                valorregistro = request.POST['marcada']
                capippriva = request.POST['capippriva'] if 'capippriva' in request.POST else ''
                browser = request.POST['navegador']
                ops = request.POST['os']
                cookies = request.POST['cookies']
                screensize = request.POST['screensize']
                if not DEBUG:
                    if variable_valor('VALIDAR_CON_CAPTCHA_MARCADAS'):
                        recaptcha_response = request.POST.get('g-recaptcha-response')
                        url = 'https://www.google.com/recaptcha/api/siteverify'
                        values = {'secret': variable_valor('GOOGLE_RECAPTCHA_SECRET_KEY'),
                                  'response': recaptcha_response}
                        data = urlencode(values)
                        data = data.encode('utf-8')
                        req = Request(url, data)
                        response = urlopen(req)
                        result = json.loads(response.read().decode())
                        if not result['success']:
                            raise NameError(u'ReCaptcha no v�lido. Vuelve a intentarlo..')
                user = authenticate(username=request.POST['usuario'].lower().strip(), password=request.POST['password'])
                if user is None:
                    raise NameError(u"Credenciales incorrectas")
                client_address = get_client_ip(request)
                if not user.is_active:
                    loglogin(action_flag=FLAG_FAILED, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, user=user, change_message=u"Usuario no activo")
                    raise NameError(u"Usuario no activo")
                if not Persona.objects.values("id").filter(usuario=user).exists():
                    loglogin(action_flag=FLAG_UNKNOWN, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, change_message=u"USUARIO: %s - CLAVE: %s" % (request.POST['usuario'].lower().strip(), request.POST['password']))
                    raise NameError(f"Usuario no existe")
                persona = Persona.objects.filter(usuario=user)[0]
                if not persona.perfilusuario_set.values("id").filter(Q(administrativo__isnull=False) | Q(profesor__isnull=False), status=True):
                    loglogin(action_flag=FLAG_FAILED, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, user=user, change_message=u"Usuario no activo")
                    raise NameError(f"Usuario no activo")
                fecha = datetime.now().date()
                time = datetime.now()
                horaactual = datetime.now().time().hour
                minutoactual = datetime.now().time().minute
                segundoactual = datetime.now().time().second
                if persona.logdia_set.values("id").filter(fecha=fecha).exists():
                    logdia = persona.logdia_set.filter(fecha=fecha)[0]
                    if logdia.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=logdia.fecha, fechafin__gte=logdia.fecha).exists():
                        logdia.jornada = logdia.persona.historialjornadatrabajador_set.filter(fechainicio__lte=logdia.fecha, fechafin__gte=logdia.fecha).order_by('fechainicio')[0].jornada
                    elif logdia.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=logdia.fecha, fechafin=None).exists():
                        logdia.jornada = logdia.persona.historialjornadatrabajador_set.filter(fechainicio__lte=logdia.fecha, fechafin=None)[0].jornada
                    logdia.cantidadmarcadas += 1
                    logdia.procesado = False
                else:
                    logdia = LogDia(persona=persona,
                                    fecha=fecha,
                                    cantidadmarcadas=1)
                logdia.save(request)
                if not logdia.logmarcada_set.values("id").filter(time=time).exists():
                    registro = LogMarcada(logdia=logdia,
                                          time=time,
                                          direccion=request.path,
                                          secuencia=logdia.cantidadmarcadas)
                    registro.save(request)
                for l in LogDia.objects.filter(persona=persona, status=True, procesado=False).order_by("fecha"):
                    if not l.jornada:
                        if l.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=l.fecha, fechafin__gte=l.fecha).exists():
                            l.jornada = l.persona.historialjornadatrabajador_set.filter(fechainicio__lte=l.fecha, fechafin__gte=l.fecha).order_by('fechainicio')[0].jornada
                        elif l.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=l.fecha, fechafin=None).exists():
                            l.jornada = l.persona.historialjornadatrabajador_set.filter(fechainicio__lte=l.fecha, fechafin=None)[0].jornada

                    cm = l.logmarcada_set.values("id").filter(status=True).count()
                    MarcadasDia.objects.filter(persona=l.persona, fecha=l.fecha).delete()
                    l.cantidadmarcadas = cm
                    if (cm % 2) == 0:
                        marini = 1
                        for dl in l.logmarcada_set.filter(status=True).order_by("time"):
                            if marini == 2:
                                salida = dl.time
                                marini = 1
                                if l.persona.marcadasdia_set.values("id").filter(fecha=l.fecha).exists():
                                    marcadadia = l.persona.marcadasdia_set.filter(fecha=l.fecha)[0]
                                else:
                                    marcadadia = MarcadasDia(persona=l.persona,
                                                             fecha=l.fecha,
                                                             logdia=l,
                                                             segundos=0)
                                    marcadadia.save(request)
                                if not marcadadia.registromarcada_set.values("id").filter(entrada=entrada).exists():
                                    registro = RegistroMarcada(marcada=marcadadia,
                                                               entrada=entrada,
                                                               salida=salida,
                                                               segundos=(salida - entrada).seconds)
                                    registro.save(request)
                                marcadadia.actualizar_marcadas()
                            else:
                                entrada = dl.time
                                marini += 1
                        l.procesado = True
                    else:
                        l.cantidadmarcadas = 0
                    l.save(request)
                    # if l.procesado:
                    #     calculando_marcadas(request, l.fecha, l.fecha, l.persona)
                calculando_marcadasotro(fecha, fecha, persona)
                loglogin(action_flag=FLAG_SUCCESSFUL, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, user=user)
                return JsonResponse({"result": "ok", "persona": persona.__str__(), "fecha": fecha, "horaactual": horaactual, "minutoactual": minutoactual, "segundoactual": segundoactual})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos. %s" % ex.__str__()})

        elif action == 'checkAuthGeolocation':
            try:
                latitude = request.POST['latitude'].strip()
                longitude = request.POST['longitude'].strip()

                if not isInsideUnemi(latitude, longitude):
                    raise NameError(u'No puede ingresar marcadas fuera de la institucion.')

                valorregistro = request.POST['marcada']
                capippriva = request.POST['capippriva'] if 'capippriva' in request.POST else ''
                browser = request.POST['navegador']
                ops = request.POST['os']
                cookies = request.POST['cookies']
                screensize = request.POST['screensize']
                if not DEBUG:
                    if variable_valor('VALIDAR_CON_CAPTCHA_MARCADAS'):
                        recaptcha_response = request.POST.get('g-recaptcha-response')
                        url = 'https://www.google.com/recaptcha/api/siteverify'
                        values = {'secret': variable_valor('GOOGLE_RECAPTCHA_SECRET_KEY'),
                                  'response': recaptcha_response}
                        data = urlencode(values)
                        data = data.encode('utf-8')
                        req = Request(url, data)
                        response = urlopen(req)
                        result = json.loads(response.read().decode())
                        if not result['success']:
                            raise NameError(u'ReCaptcha no v�lido. Vuelve a intentarlo..')
                user = authenticate(username=request.POST['usuario'].lower().strip(), password=request.POST['password'])
                if user is None:
                    raise NameError(u"Credenciales incorrectas")
                client_address = get_client_ip(request)
                if not user.is_active:
                    loglogin(action_flag=FLAG_FAILED, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, user=user, change_message=u"Usuario no activo")
                    raise NameError(u"Usuario no activo")
                if not Persona.objects.values("id").filter(usuario=user).exists():
                    loglogin(action_flag=FLAG_UNKNOWN, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, change_message=u"USUARIO: %s - CLAVE: %s" % (request.POST['usuario'].lower().strip(), request.POST['password']))
                    raise NameError(f"Usuario no existe")
                persona = Persona.objects.filter(usuario=user)[0]
                if not persona.perfilusuario_set.values("id").filter(Q(administrativo__isnull=False) | Q(profesor__isnull=False), status=True):
                    loglogin(action_flag=FLAG_FAILED, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, user=user, change_message=u"Usuario no activo")
                    raise NameError(f"Usuario no activo")
                fecha = datetime.now().date()
                time = datetime.now()
                horaactual = datetime.now().time().hour
                minutoactual = datetime.now().time().minute
                segundoactual = datetime.now().time().second
                if persona.logdia_set.values("id").filter(fecha=fecha).exists():
                    logdia = persona.logdia_set.filter(fecha=fecha)[0]
                    if logdia.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=logdia.fecha, fechafin__gte=logdia.fecha).exists():
                        logdia.jornada = logdia.persona.historialjornadatrabajador_set.filter(fechainicio__lte=logdia.fecha, fechafin__gte=logdia.fecha).order_by('fechainicio')[0].jornada
                    elif logdia.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=logdia.fecha, fechafin=None).exists():
                        logdia.jornada = logdia.persona.historialjornadatrabajador_set.filter(fechainicio__lte=logdia.fecha, fechafin=None)[0].jornada
                    logdia.cantidadmarcadas += 1
                    logdia.procesado = False
                else:
                    logdia = LogDia(persona=persona,
                                    fecha=fecha,
                                    cantidadmarcadas=1)
                logdia.save(request)
                if not logdia.logmarcada_set.values("id").filter(time=time).exists():
                    registro = LogMarcada(logdia=logdia,
                                          time=time,
                                          direccion=request.path,
                                          secuencia=logdia.cantidadmarcadas)
                    registro.save(request)
                for l in LogDia.objects.filter(persona=persona, status=True, procesado=False).order_by("fecha"):
                    if not l.jornada:
                        if l.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=l.fecha, fechafin__gte=l.fecha).exists():
                            l.jornada = l.persona.historialjornadatrabajador_set.filter(fechainicio__lte=l.fecha, fechafin__gte=l.fecha).order_by('fechainicio')[0].jornada
                        elif l.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=l.fecha, fechafin=None).exists():
                            l.jornada = l.persona.historialjornadatrabajador_set.filter(fechainicio__lte=l.fecha, fechafin=None)[0].jornada

                    cm = l.logmarcada_set.values("id").filter(status=True).count()
                    MarcadasDia.objects.filter(persona=l.persona, fecha=l.fecha).delete()
                    l.cantidadmarcadas = cm
                    if (cm % 2) == 0:
                        marini = 1
                        for dl in l.logmarcada_set.filter(status=True).order_by("time"):
                            if marini == 2:
                                salida = dl.time
                                marini = 1
                                if l.persona.marcadasdia_set.values("id").filter(fecha=l.fecha).exists():
                                    marcadadia = l.persona.marcadasdia_set.filter(fecha=l.fecha)[0]
                                else:
                                    marcadadia = MarcadasDia(persona=l.persona,
                                                             fecha=l.fecha,
                                                             logdia=l,
                                                             segundos=0)
                                    marcadadia.save(request)
                                if not marcadadia.registromarcada_set.values("id").filter(entrada=entrada).exists():
                                    registro = RegistroMarcada(marcada=marcadadia,
                                                               entrada=entrada,
                                                               salida=salida,
                                                               segundos=(salida - entrada).seconds)
                                    registro.save(request)
                                marcadadia.actualizar_marcadas()
                            else:
                                entrada = dl.time
                                marini += 1
                        l.procesado = True
                    else:
                        l.cantidadmarcadas = 0
                    l.save(request)
                    # if l.procesado:
                    #     calculando_marcadas(request, l.fecha, l.fecha, l.persona)
                calculando_marcadasotro(fecha, fecha, persona)
                loglogin(action_flag=FLAG_SUCCESSFUL, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, user=user)
                return JsonResponse({"result": "ok", "persona": persona.__str__(), "fecha": fecha, "horaactual": horaactual, "minutoactual": minutoactual, "segundoactual": segundoactual})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos. %s" % ex.__str__()})

        # elif action == 'recognizeFace':
        #     try:
        #         if not inhouse_check(request):
        #             raise NameError(u'No puede ingresar marcadas fuera de la institucion.')
        #         valorregistro = request.POST['marcada']
        #         capippriva = request.POST['capippriva'] if 'capippriva' in request.POST else ''
        #         browser = request.POST['navegador']
        #         ops = request.POST['os']
        #         cookies = request.POST['cookies']
        #         screensize = request.POST['screensize']
        #         if not DEBUG:
        #             if variable_valor('VALIDAR_CON_CAPTCHA_MARCADAS'):
        #                 recaptcha_response = request.POST.get('g-recaptcha-response')
        #                 url = 'https://www.google.com/recaptcha/api/siteverify'
        #                 values = {'secret': variable_valor('GOOGLE_RECAPTCHA_SECRET_KEY'),
        #                           'response': recaptcha_response}
        #                 data = urlencode(values)
        #                 data = data.encode('utf-8')
        #                 req = Request(url, data)
        #                 response = urlopen(req)
        #                 result = json.loads(response.read().decode())
        #                 if not result['success']:
        #                     raise NameError(u'ReCaptcha no v�lido. Vuelve a intentarlo..')
        #         # eFaceRecognition = FaceRecognition()
        #         # ePersona, msg = eFaceRecognition.recognizeFace(request)
        #         ePersona, msg = True, ''
        #         if ePersona is None:
        #             raise NameError(msg)
        #         user = ePersona.usuario
        #         if user is None:
        #             raise NameError(u"Credenciales incorrectas")
        #         user.backend = 'django.contrib.auth.backends.ModelBackend'
        #         client_address = get_client_ip(request)
        #         if not user.is_active:
        #             loglogin(action_flag=FLAG_FAILED, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, user=user, change_message=u"Usuario no activo")
        #             raise NameError(u"Usuario no activo")
        #         # if not Persona.objects.values("id").filter(usuario=user).exists():
        #         #     loglogin(action_flag=FLAG_UNKNOWN, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, change_message=u"USUARIO: %s - CLAVE: %s" % (request.POST['usuario'].lower().strip(), request.POST['password']))
        #         #     raise NameError(f"Usuario no existe")
        #         if not ePersona.perfilusuario_set.values("id").filter(Q(administrativo__isnull=False) | Q(profesor__isnull=False), status=True):
        #             loglogin(action_flag=FLAG_FAILED, action_app=APP_MARCADAS, ip_private=capippriva, ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize, user=user, change_message=u"Usuario no activo")
        #             raise NameError(f"Usuario no activo")
        #         fecha = datetime.now().date()
        #         time = datetime.now()
        #         horaactual = datetime.now().time().hour
        #         minutoactual = datetime.now().time().minute
        #         segundoactual = datetime.now().time().second
        #         if ePersona.logdia_set.values("id").filter(fecha=fecha).exists():
        #             logdia = ePersona.logdia_set.filter(fecha=fecha)[0]
        #             if logdia.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=logdia.fecha, fechafin__gte=logdia.fecha).exists():
        #                 logdia.jornada = logdia.persona.historialjornadatrabajador_set.filter(fechainicio__lte=logdia.fecha, fechafin__gte=logdia.fecha).order_by('fechainicio')[0].jornada
        #             elif logdia.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=logdia.fecha, fechafin=None).exists():
        #                 logdia.jornada = logdia.persona.historialjornadatrabajador_set.filter(fechainicio__lte=logdia.fecha, fechafin=None)[0].jornada
        #             logdia.cantidadmarcadas += 1
        #             logdia.procesado = False
        #         else:
        #             logdia = LogDia(persona=ePersona,
        #                             fecha=fecha,
        #                             cantidadmarcadas=1)
        #         logdia.save(request)
        #         if not logdia.logmarcada_set.values("id").filter(time=time).exists():
        #             registro = LogMarcada(logdia=logdia,
        #                                   time=time,
        #                                   secuencia=logdia.cantidadmarcadas)
        #             registro.save(request)
        #         for l in LogDia.objects.filter(persona=ePersona, status=True, procesado=False).order_by("fecha"):
        #             if not l.jornada:
        #                 if l.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=l.fecha, fechafin__gte=l.fecha).exists():
        #                     l.jornada = l.persona.historialjornadatrabajador_set.filter(fechainicio__lte=l.fecha, fechafin__gte=l.fecha).order_by('fechainicio')[0].jornada
        #                 elif l.persona.historialjornadatrabajador_set.values("id").filter(fechainicio__lte=l.fecha, fechafin=None).exists():
        #                     l.jornada = l.persona.historialjornadatrabajador_set.filter(fechainicio__lte=l.fecha, fechafin=None)[0].jornada
        #             cm = l.logmarcada_set.values("id").filter(status=True).count()
        #             MarcadasDia.objects.filter(persona=l.persona, fecha=l.fecha).delete()
        #             l.cantidadmarcadas = cm
        #             if (cm % 2) == 0:
        #                 marini = 1
        #                 for dl in l.logmarcada_set.filter(status=True).order_by("time"):
        #                     if marini == 2:
        #                         salida = dl.time
        #                         marini = 1
        #                         if l.persona.marcadasdia_set.values("id").filter(fecha=l.fecha).exists():
        #                             marcadadia = l.persona.marcadasdia_set.filter(fecha=l.fecha)[0]
        #                         else:
        #                             marcadadia = MarcadasDia(persona=l.persona,
        #                                                      fecha=l.fecha,
        #                                                      logdia=l,
        #                                                      segundos=0)
        #                             marcadadia.save(request)
        #                         if not marcadadia.registromarcada_set.values("id").filter(entrada=entrada).exists():
        #                             registro = RegistroMarcada(marcada=marcadadia,
        #                                                        entrada=entrada,
        #                                                        salida=salida,
        #                                                        segundos=(salida - entrada).seconds)
        #                             registro.save(request)
        #                         marcadadia.actualizar_marcadas()
        #                     else:
        #                         entrada = dl.time
        #                         marini += 1
        #                 l.procesado = True
        #             else:
        #                 l.cantidadmarcadas = 0
        #             l.save(request)
        #             # if l.procesado:
        #             #     calculando_marcadas(request, l.fecha, l.fecha, l.persona)
        #         calculando_marcadasotro(fecha, fecha, ePersona)
        #         loglogin(action_flag=FLAG_SUCCESSFUL, action_app=APP_MARCADAS, ip_private=capippriva,
        #                  ip_public=client_address, browser=browser, ops=ops, cookies=cookies, screen_size=screensize,
        #                  user=user)
        #         return JsonResponse({"result": "ok", "persona": ePersona.__str__(), "fecha": fecha, "horaactual": horaactual, "minutoactual": minutoactual, "segundoactual": segundoactual})
        #         # log(u'%s - Inicio reconocimiento facial: %s' % (persona, str(user)), request, "add")
        #         # login(request, user)
        #     except Exception as ex:
        #         transaction.set_rollback(True)
        #         return JsonResponse({"result": "bad", "mensaje": f"Error al guardar los datos. {ex.__str__()}"})

        elif action == 'verifyLocationU':
            try:
                if 'latitude' not in request.POST or 'longitude' not in request.POST:
                    raise NameError(u'Error al procesar la solicitud')

                latitude = request.POST['latitude'].strip()
                longitude = request.POST['longitude'].strip()

                if isInsideUnemi(latitude, longitude):
                    return JsonResponse({"result": "ok", "enunemi": "S", "mensaje": u"Usted se encuentra dentro de la Universidad"})
                else:
                    return JsonResponse({"result": "ok", "enunemi": "N", "mensaje": u"Usted se encuentra fuera de la Universidad"})

            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": f"Error al consultar los datos. {ex.__str__()}"})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'geolocation':
                try:
                    data = {}
                    data['title'] = u'Registro de marcadas Usando GeoLocalizaci�n'
                    my_ip = get_client_ip(request)
                    data['my_ip'] = my_ip
                    data['valida_captcha'] = variable_valor('VALIDAR_CON_CAPTCHA_MARCADAS') if not DEBUG else False
                    data['public_key'] = variable_valor('GOOGLE_RECAPTCHA_PUBLIC_KEY')
                    hour = datetime.now().time().hour
                    minute = datetime.now().time().minute
                    second = datetime.now().time().second
                    if hour < 10:
                        hour = '0' + str(hour)
                    if minute < 10:
                        minute = '0' + str(minute)
                    if second < 10:
                        second = '0' + str(second)
                    data['tiempo'] = {"hour": str(hour),
                                      "minute": str(minute),
                                      "second": str(second)}
                    return render(request, "faceid/viewgeolocation.html", data)
                except Exception as ex:
                    return HttpResponseRedirect(f"/?info{ex.__str__()}")

        #     if action == 'biometrics':
        #         data = {}
        #         data['title'] = u'Registro de marcadas por biometr�a'
        #         my_ip = get_client_ip(request)
        #         data['my_ip'] = my_ip
        #         inhouse = True
        #         if not inhouse_check(request):
        #             inhouse = False
        #         data['inhouse'] = inhouse
        #         data['valida_captcha'] = variable_valor('VALIDAR_CON_CAPTCHA_MARCADAS') if not DEBUG else False
        #         data['public_key'] = variable_valor('GOOGLE_RECAPTCHA_PUBLIC_KEY')
        #         hour = datetime.now().time().hour
        #         minute = datetime.now().time().minute
        #         second = datetime.now().time().second
        #         if hour < 10:
        #             hour = '0' + str(hour)
        #         if minute < 10:
        #             minute = '0' + str(minute)
        #         if second < 10:
        #             second = '0' + str(second)
        #         data['tiempo'] = {"hour": str(hour),
        #                           "minute": str(minute),
        #                           "second": str(second)}
        #         return render(request, "faceid/biometrics.html", data)
        #     return HttpResponseRedirect(request.path)
        else:
            try:
                data = {}
                data['title'] = u'Registro de marcadas'
                my_ip = get_client_ip(request)
                data['my_ip'] = my_ip
                inhouse = True
                if not inhouse_check(request):
                    inhouse = False
                data['inhouse'] = inhouse
                data['valida_captcha'] = variable_valor('VALIDAR_CON_CAPTCHA_MARCADAS') if not DEBUG else False
                data['public_key'] = variable_valor('GOOGLE_RECAPTCHA_PUBLIC_KEY')
                hour = datetime.now().time().hour
                minute = datetime.now().time().minute
                second = datetime.now().time().second
                if hour < 10:
                    hour = '0' + str(hour)
                if minute < 10:
                    minute = '0' + str(minute)
                if second < 10:
                    second = '0' + str(second)
                data['tiempo'] = {"hour": str(hour),
                                  "minute": str(minute),
                                  "second": str(second)}
                return render(request, "faceid/view.html", data)
            except Exception as ex:
                return HttpResponseRedirect(f"/?info{ex.__str__()}")