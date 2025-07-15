from django.urls import path
from . import views
from .views import vectorizer_form_view,VectorizeImageView,PaintByNumberView,MultiFormatVectorizerView, test_upload_ui



urlpatterns = [
    path('', vectorizer_form_view, name='vectorizer_ui'),
    path('vectorize/',  VectorizeImageView.as_view(), name='vectorize'),
    path('test-pbn/', views.test_pbn_frontend, name='test_pbn_frontend'),
    path("generate-pbn/", PaintByNumberView.as_view(), name="generate_pbn"),

        # path('vectorize23/', vectorize_image, name='vectorize_image'),
    path("vectorize1234/", MultiFormatVectorizerView.as_view(), name="vectorize"),
    path("vectorize/ui/", test_upload_ui, name="vectorize_ui"),  # UI form

]
