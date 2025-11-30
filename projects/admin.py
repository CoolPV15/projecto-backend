from django.contrib import admin
from .models import ProjectLead, ProjectRequest, ProjectMembers, ProjectRequestRejected

#Registering all the models related to project in the admin site
admin.site.register(ProjectLead)
admin.site.register(ProjectRequest)
admin.site.register(ProjectMembers)
admin.site.register(ProjectRequestRejected)