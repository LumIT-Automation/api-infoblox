from django.urls import include, path

urlpatterns = [
    path('', include('infoblox.urls')),
]
