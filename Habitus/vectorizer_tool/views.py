import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VectorizerSerializer
import requests
from django.http import HttpResponse

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




# import os
# import uuid
# import requests
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import VectorizerSerializer

# import os
# import uuid
# import requests
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import VectorizerSerializer

# class VectorizerAPIView(APIView):
#     parser_classes = [MultiPartParser, FormParser]

#     def post(self, request):
#         serializer = VectorizerSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=400)

#         data = serializer.validated_data
#         image = data.pop('image')
#         output_format = data.get('output_format', 'svg')

#         extension = 'png' if output_format == 'png' else 'svg'
#         filename = f'vector_output_{uuid.uuid4().hex}.{extension}'
#         relative_path = f'vectorized/{filename}'
#         full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
#         os.makedirs(os.path.dirname(full_path), exist_ok=True)

#         api_id = os.environ.get("VECTORIZER_API_ID")
#         api_key = os.environ.get("VECTORIZER_API_KEY")

#         # ✅ Map your flat fields to what the API expects
#         payload = {
#                 "mode": data["mode"],
#                 "output.size.width": data["width"],
#                 "output.size.height": data["height"],
#                 "processing.max_colors": data["maximum_colors"],
#                 "processing.shapes.min_area_px": data["minimum_area"],
#                 "output.file_format": output_format,
#                 "output.bitmap.anti_aliasing_mode": data["smoothing"]
#             }
#         try:
#             response = requests.post(
#                 "https://api.vectorizer.ai/api/v1/vectorize",
#                 data=payload,
#                 files={"image": image},
#                 auth=(api_id, api_key),
#                 headers={"accept": "application/json"}
#             )

#             if response.status_code != 200:
#                 return Response({
#                     "error": "Vectorizer API failed",
#                     "status_code": response.status_code,
#                     "api_message": response.text[:300]
#                 }, status=response.status_code)

#             content_type = response.headers.get("Content-Type", "")

#             # ✅ Ensure valid image returned
#             if output_format == "png" and "image/png" in content_type:
#                 with open(full_path, 'wb') as f:
#                     f.write(response.content)

#             elif output_format == "svg" and "image/svg+xml" in content_type:
#                 with open(full_path, 'w', encoding='utf-8') as f:
#                     f.write(response.text)

#             else:
#                 return Response({
#                     "error": "Invalid image returned from API",
#                     "status_code": response.status_code,
#                     "content_type": content_type,
#                     "api_message_preview": response.text[:300]
#                 }, status=400)

#             return Response({
#                 "message": f"{extension.upper()} saved successfully",
#                 "file_path": relative_path,
#                 "media_url": request.build_absolute_uri(f"/images/{relative_path}")
#             }, status=200)

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)






class VectorizeImageView(APIView):
    def post(self, request):
        serializer = VectorizerSerializer(data=request.data)
        if serializer.is_valid():
            validated = serializer.validated_data

            # Load auth credentials
            api_id = os.environ.get("VECTORIZER_API_ID")
            api_key = os.environ.get("VECTORIZER_API_KEY")

            if not api_id or not api_key:
                return Response(
                    {"error": "Missing Vectorizer API credentials"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            image = validated['image']
            files = {"image": image}

            # Map local serializer fields to API fields
            API_FIELD_MAPPING = {
                "maximum_colors": "processing.max_colors",
                "minimum_area": "processing.shapes.min_area_px",
                "output_format": "output.file_format",
                "smoothing": "output.bitmap.anti_aliasing_mode",
                "level_of_details": "output.curves.line_fit_tolerance",
                "width": "output.size.width",
                "height": "output.size.height",
            }

            # Base payload
            payload = {"mode": validated.get("mode", "test")}

            for local_field, api_field in API_FIELD_MAPPING.items():
                if local_field in validated:
                    payload[api_field] = validated[local_field]

            try:
                response = requests.post(
                    "https://api.vectorizer.ai/api/v1/vectorize",
                    data=payload,
                    files=files,
                    auth=(api_id, api_key),
                    headers={"Accept": "application/json"}
                )

                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "application/octet-stream")
                    file_extension = "svg" if content_type == "image/svg+xml" else "png"
                    return HttpResponse(
                        response.content,
                        content_type=content_type,
                        headers={
                            "Content-Disposition": f'attachment; filename="vectorized_output.{file_extension}"'
                        }
                    )
                else:
                    return Response(
                        {
                            "error": "Vectorizer API returned an error",
                            "status_code": response.status_code,
                            "details": response.text
                        },
                        status=response.status_code
                    )

            except requests.exceptions.RequestException as e:
                return Response(
                    {"error": "Request to Vectorizer API failed", "details": str(e)},
                    status=500
                )

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
