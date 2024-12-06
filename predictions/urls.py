from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_image, name='upload_image'),
    path('result/<int:pk>/', views.result_detail, name='result_detail'),
    path('result/<int:pk>/edit/', views.result_edit, name='result_edit'),
    path('result/<int:pk>/delete/', views.result_delete, name='result_delete'),
    path('results/', views.result_list, name='result_list'),
    path('common_symptoms/<str:condition>/', views.common_symptoms, name='common_symptoms'),
    path('prevention_tips/<str:condition>/', views.prevention_tips, name='prevention_tips'),
    path('when_to_see_doctor/<str:condition>/', views.when_to_see_doctor, name='when_to_see_doctor'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
