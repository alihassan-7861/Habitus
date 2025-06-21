from django.urls import path
from . import views
from .views import vectorizer_form_view, VectorizerAPIView



urlpatterns = [
        path('vectorizer-ui/', vectorizer_form_view, name='vectorizer_ui'),

    # path('', views.vectorizer, name='vectorizer_tool'),
    path('vectorize/', VectorizerAPIView.as_view(), name='vectorize'),

    path('register/', views.register, name='register'),
    path('instruction/', views.instruction, name='instruction'),
    path('myAccount/', views.myAccount, name='myAccount'),
]