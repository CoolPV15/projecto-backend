from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views
from accounts import views as user_views
from projects import views as project_views
'''
Author: Pranav Singh
'''

'''
A router for generating the URL patterns for the Registration viewsets
'''
router = routers.DefaultRouter()
router.register(r'accounts',user_views.RegistrationView,'accounts')
router.register(r'projectleads',project_views.ProjectLeadView,'projectleads')
router.register(r'projects',project_views.ProjectsDisplayView,"projects")
router.register(r'projectrequests',project_views.ProjectRequestView,"projectrequest")
router.register(r'projectrequestsdisplay',project_views.ProjectRequestDisplayView,"projectrequestdisplay")
router.register(r'projectmembers',project_views.ProjectMembersView,"projectmembersview")
router.register(r'projectreject',project_views.ProjectRejectedView,"projectrejectedview")
router.register(r'joinedprojects',project_views.JoinedProjectDisplayView,"joinedprojects")
router.register(r'projectmembersdisplay',project_views.ProjectMembersDisplayView,"projectmembersdisplay")
router.register(r'pendingprojects',project_views.PendingProjectsView,"pendingprojects")
router.register(r'projectcount',project_views.ProjectCountView,"projectcount")
'''
urlpatterns that include endpoints for the jwt token authentication, and paths from other apps
'''
urlpatterns = [
    path('api/token/',jwt_views.TokenObtainPairView.as_view()),
    path('api/token/refresh/',jwt_views.TokenRefreshView.as_view()),
    path('api/token/verify/',jwt_views.TokenVerifyView.as_view()),
    path('api/accounts/',include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('api/',include(router.urls)),
]
