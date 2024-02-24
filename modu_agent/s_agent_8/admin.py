from django.contrib import admin
from .models import AuthGroup, AuthGroupPermissions, AuthPermission, AuthUser, AuthUserGroups, AuthUserUserPermissions, Careerpath, DjangoAdminLog, DjangoContentType, DjangoMigrations, DjangoSession, Initialgoalparameter, Inputparameter, Knowledgeforcareerpath, Lhs, Outputparameter, Parameterhierarchy, Parameterlist, Result, Rhs, Ruleinfo, Webservicelist

# Register your models here.
admin.site.register(AuthGroup)
admin.site.register(AuthGroupPermissions)
admin.site.register(AuthPermission)
admin.site.register(AuthUser)
admin.site.register(AuthUserGroups)
admin.site.register(AuthUserUserPermissions)
admin.site.register(Careerpath)
admin.site.register(DjangoAdminLog)
admin.site.register(DjangoContentType)
admin.site.register(DjangoMigrations)
admin.site.register(DjangoSession)
admin.site.register(Knowledgeforcareerpath)
admin.site.register(Lhs)
admin.site.register(Rhs)
admin.site.register(Ruleinfo)
admin.site.register(Webservicelist)

class InitialgoalparameterAdmin(admin.ModelAdmin):
    list_display = ('transactionid', 'iorg', 'parameterid')
    search_fields = ('transactionid', 'iorg', 'parameterid__parametername')
    list_filter = ('iorg', 'parameterid')

class InputparameterAdmin(admin.ModelAdmin):
    list_display = ('webserviceid', 'parameterid')
    search_fields = ('webserviceid', 'parameterid')
    list_filter = ('webserviceid',)

class OutputparameterAdmin(admin.ModelAdmin):
    list_display = ('webserviceid', 'parameterid')
    search_fields = ('webserviceid', 'parameterid')
    list_filter = ('webserviceid',)

class ParameterhierarchyAdmin(admin.ModelAdmin):
    list_display = ('parentparameterid', 'childparameterid', 'noofdepth', 'noofchildren')
    search_fields = ('parentparameterid', 'childparameterid')
    list_filter = ('parentparameterid', 'childparameterid')

class ParameterlistAdmin(admin.ModelAdmin):
    list_display = ('parameterid', 'parametername')
    search_fields = ('parameterid', 'parametername')

class ResultAdmin(admin.ModelAdmin):
    list_display = ('transactionid', 'stage', 'webserviceid')
    search_fields = ('transactionid', 'stage', 'webserviceid')
    list_filter = ('stage', 'webserviceid')

admin.site.register(Initialgoalparameter, InitialgoalparameterAdmin)
admin.site.register(Inputparameter, InputparameterAdmin)
admin.site.register(Outputparameter, OutputparameterAdmin)
admin.site.register(Parameterhierarchy, ParameterhierarchyAdmin)
admin.site.register(Parameterlist, ParameterlistAdmin)
admin.site.register(Result, ResultAdmin)