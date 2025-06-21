import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import VectorizerSerializer
import requests

# Create your views here.
def vectorizer(request):
    context={}
    return render(request,'vectorizer_tool/vectorizer.html',context)

def register(request):
    context={}
    return render(request,'vectorizer_tool/register.html',context)


def instruction(request):
    context={}
    return render(request,'vectorizer_tool/instruction.html',context)


def myAccount(request):
    context={}
    return render(request,'vectorizer_tool/myAccount.html',context)



from django.shortcuts import render

def vectorizer_form_view(request):
    return render(request, 'vectorizer_tool/vectorizer.html')




import os
import uuid
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import VectorizerSerializer

import os
import uuid
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import VectorizerSerializer

class VectorizerAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = VectorizerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        image = data.pop('image')
        output_format = data.get('output_format', 'svg')

        extension = 'png' if output_format == 'png' else 'svg'
        filename = f'vector_output_{uuid.uuid4().hex}.{extension}'
        relative_path = f'vectorized/{filename}'
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        api_id = os.environ.get("VECTORIZER_API_ID")
        api_key = os.environ.get("VECTORIZER_API_KEY")

        try:
            response = requests.post(
                "https://api.vectorizer.ai/api/v1/vectorize",
                data=data,
                files={"image": image},
                auth=(api_id, api_key),
                headers={"accept": "application/json"}
            )

            if response.status_code != 200:
                return Response({
                    "error": f"Vectorizer API failed",
                    "status_code": response.status_code,
                    "api_message": response.text[:300]
                }, status=response.status_code)

            content_type = response.headers.get("Content-Type", "")

            # ✅ Ensure the returned content is a valid image
            if output_format == "png" and "image/png" in content_type:
                with open(full_path, 'wb') as f:
                    f.write(response.content)

            elif output_format == "svg" and "image/svg+xml" in content_type:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)

            else:
                # ❌ Invalid or unsupported format returned from API
                return Response({
                    "error": "Invalid image returned from API",
                    "status_code": response.status_code,
                    "content_type": content_type,
                    "api_message_preview": response.text[:300]
                }, status=400)

            return Response({
                "message": f"{extension.upper()} saved successfully",
                "file_path": relative_path,
                "media_url": request.build_absolute_uri(f"/images/{relative_path}")
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
