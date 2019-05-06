from django.conf.urls import include, url 
 
urlpatterns = [ 
    url(r'^hello/', include('helloworld.urls')), 
]
