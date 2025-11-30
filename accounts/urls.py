from django.urls import path,include
from accounts import views
'''
Auther: Pranav Singh
'''


'''
urlpatterns specific for the signin application, which includes the path for all the views inside the application
'''
urlpatterns = [
    path('home/',views.HomeView.as_view(),name='home'),
    path('me/',views.RetrieveUserView.as_view()),
    path('logout/',views.LogOutView.as_view(),name='logout')
]