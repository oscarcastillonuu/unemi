from django.urls import re_path

from ejecuform import adm_ejecuform

urlpatterns = [
    re_path(r'^adm_formejecuperiodo$',adm_ejecuform.view,name="ejecuform_adm_formejecuperiodo"),
]