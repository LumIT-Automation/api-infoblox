from django.urls import path, include

from .controllers import Root


urlpatterns = [
    path('api/', Root.RootController.as_view()),
    path('api/v1/', Root.RootController.as_view()),

    path('api/v1/infoblox/', include('infoblox.InfobloxUrls')),
]
