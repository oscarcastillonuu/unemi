from django.contrib import admin
from certi.models import ConfiguracionCarnet, FuncionAdjuntarArchivoCertificado

from sga.admin import MANAGERS


class ModeloBaseAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        actions = super(ModeloBaseAdmin, self).get_actions(request)
        if request.user.username not in [x[0] for x in MANAGERS]:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return request.user.username in [x[0] for x in MANAGERS]

    def has_module_permission(self, request):
        return request.user.username in [x[0] for x in MANAGERS]

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.username in [x[0] for x in MANAGERS]

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("usuario_creacion", "fecha_creacion", "usuario_modificacion", "fecha_modificacion")
        form = super(ModeloBaseAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        if request.user.username not in [x[0] for x in MANAGERS]:
            raise Exception('Sin permiso a modificacion')
        else:
            obj.save(request)


class ConfiguracionCarnetAdmin(ModeloBaseAdmin):
    search_fields = ['nombre', ]
    list_display = ['nombre', 'version', 'get_tipo_perfil_display', 'get_tipo_validacion_display', 'activo']
    raw_id_fields = ('reporte',)
    
class FuncionAdjuntarArchivoCertificadoAdmin(ModeloBaseAdmin):
    search_fields = ['nombrevisual', ]
    list_display = ['nombrevisual', 'nombrefuncion']
    # raw_id_fields = ('reporte',)


admin.site.register(ConfiguracionCarnet, ConfiguracionCarnetAdmin)
admin.site.register(FuncionAdjuntarArchivoCertificado, FuncionAdjuntarArchivoCertificadoAdmin)
