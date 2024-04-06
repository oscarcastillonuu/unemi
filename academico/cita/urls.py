from django.urls import re_path

from cita import adm_agendamientocitas, alu_agendamientocitas, adm_gestorcitas


urlpatterns = [
    re_path(r'^adm_agendamientocitas$', adm_agendamientocitas.view, name='adm_agendamientocitas'),
    re_path(r'^alu_agendamientocitas$', alu_agendamientocitas.view, name='alu_agendamientocitas'),
    re_path(r'^adm_gestorcitas$', adm_gestorcitas.view, name='adm_gestorcitas'),
]
