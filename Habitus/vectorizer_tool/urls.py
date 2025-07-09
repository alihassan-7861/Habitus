from django.urls import path
from . import views
from .views import vectorizer_form_view,VectorizeImageView,PaintByNumberView



urlpatterns = [
    path('vectorizer-ui/', vectorizer_form_view, name='vectorizer_ui'),
    path('vectorize/',  VectorizeImageView.as_view(), name='vectorize'),
    path('test-pbn/', views.test_pbn_frontend, name='test_pbn_frontend'),
    path("generate-pbn/", PaintByNumberView.as_view(), name="generate_pbn"),
]