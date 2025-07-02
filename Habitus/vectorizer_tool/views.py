import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VectorizerSerializer
import requests
from django.http import HttpResponse
import json 
import re


def register(request):
    context={}
    return render(request,'vectorizer_tool/register.html',context)


def instruction(request):
    context={}
    return render(request,'vectorizer_tool/instruction.html',context)


def myAccount(request):
    context={}
    return render(request,'vectorizer_tool/myAccount.html',context)


def vectorizer_form_view(request):
    return render(request, 'vectorizer_tool/vectorizer.html')


class VectorizeImageView(APIView):
    def post(self, request):
        serializer = VectorizerSerializer(data=request.data)
        if serializer.is_valid():
            validated = serializer.validated_data

            api_id = os.environ.get("VECTORIZER_API_ID")
            api_key = os.environ.get("VECTORIZER_API_KEY")

            if not api_id or not api_key:
                return Response({"error": "Missing Vectorizer API credentials"}, status=500)

            image = validated['image']
            files = {"image": image}

            HABITUS_PALETTE = [
                "#FFFFFF", "#1A1A1A", "#DADADA", "#999999",
                "#B7D79A", "#4C8C4A", "#2E472B", "#FDE74C",
                "#F5C243", "#F28C28", "#C85A27", "#F88379",
                "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2",
                "#1B3B6F", "#3CCFCF", "#FBE3D4", "#D5A97B",
                "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8"
            ]
            palette_string = ";".join(HABITUS_PALETTE)  

            API_FIELD_MAPPING = {
                "minimum_area": "processing.shapes.min_area_px",
                "output_format": "output.file_format",
                "smoothing": "output.bitmap.anti_aliasing_mode",
                "level_of_details": "output.curves.line_fit_tolerance",
                # "width": "output.size.width",
                # "height": "output.size.height",
                "mode": "mode"
            }

            payload = {
               
                

            }


            def set_nested_key(obj, dotted_key, value):
                keys = dotted_key.split('.')
                for key in keys[:-1]:
                    obj = obj.setdefault(key, {})
                obj[keys[-1]] = value

            for local_field, api_field in API_FIELD_MAPPING.items():
                if local_field in validated:
                    set_nested_key(payload, api_field, validated[local_field])


                form_data = {
                    "json": json.dumps(payload),
                    "processing.palette": palette_string  # ✅ passed separately
                }
            # ✅ Enable bitmap output for PNG
            if validated.get("output_format") == "png":
                set_nested_key(payload, "output.bitmap.enabled", True)
                set_nested_key(payload, "output.bitmap.resolution_dpi", 300)

            # ✅ Debug final payload
            print("📦 Final payload:", json.dumps(payload, indent=2))

            try:
                response = requests.post(
                    "https://api.vectorizer.ai/api/v1/vectorize",
                    data=form_data, 
                    files={"image": image},             
                    auth=(api_id, api_key),
                   
                )

                print("🧪 Response status code:", response.status_code)

                if response.status_code == 200:
                    output_format = validated.get("output_format", "svg").lower()
                    content_type = "image/svg+xml" if output_format == "svg" else "image/png"
                    file_extension = output_format

                    # Debug image analysis (optional)
                    if output_format == "svg":
                        svg_text = response.content.decode('utf-8', errors='ignore')
                        used_colors = set(re.findall(r'fill="(#(?:[0-9a-fA-F]{3}){1,2})"', svg_text))
                        used_colors = {c.lower() for c in used_colors}
                        habitus_palette = {c.lower() for c in HABITUS_PALETTE}
                        if used_colors.issubset(habitus_palette):
                            print("✅ Verified: Only Habitus® palette colors used.")
                        else:
                            print("❌ Extra colors found:", used_colors - habitus_palette)

                    return HttpResponse(
                        response.content,
                        content_type=content_type,
                        headers={
                            "Content-Disposition": f'attachment; filename="vectorized_output.{file_extension}"'
                        }
                    )

                else:
                    return Response({
                        "error": "Vectorizer API returned an error",
                        "status_code": response.status_code,
                        "details": response.text
                    }, status=response.status_code)

            except requests.exceptions.RequestException as e:
                return Response({
                    "error": "Request to Vectorizer API failed",
                    "details": str(e)
                }, status=500)

        else:
            return Response(serializer.errors, status=400)





# import os
# import requests
# from django.conf import settings
# from django.http import FileResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
# from django.core.files.storage import default_storage


# @csrf_exempt
# @require_POST
# def vectorize_image(request):
#     # Get file and format
#     image_file = request.FILES.get("image")
#     output_format = request.POST.get("format", "svg")

#     if not image_file:
#         return JsonResponse({"error": "Image file is required."}, status=400)

#     # Save image temporarily
#     image_path = default_storage.save(image_file.name, image_file)
#     full_path = os.path.join(settings.MEDIA_ROOT, image_path)

#     # Custom color palette (24 colors)
#     custom_palette = [
#         "#FFFFFF", "#1A1A1A", "#DADADA", "#999999",
#         "#B7D79A", "#4C8C4A", "#2E472B", "#FDE74C",
#         "#F5C243", "#F28C28", "#C85A27", "#F88379",
#         "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2",
#         "#1B3B6F", "#3CCFCF", "#FBE3D4", "#D5A97B",
#         "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8"
#     ]

#     # Form data as list of tuples
#     form_data = [
#         ("mode", "production"),
#         ("processing.shapes.min_area_px", "45"),
#         ("output.file_format", output_format),
#         ("output.bitmap.anti_aliasing_mode", "aliased"),
#         ("output.curves.line_fit_tolerance", "0.1"),
#         ("output.size.width", "45"),
#         ("output.size.height", "30"),
#         ("processing.palette", ";".join(custom_palette)),  # ✅ Correct single field
#     ]

#     # Send request to Vectorizer API
#     with open(full_path, "rb") as f:
#         files = {"image": f}
#         response = requests.post(
#             "https://vectorizer.ai/api/v1/vectorize",
#             data=form_data,
#             files=files,
#             auth=("vkqi8vk8s2ks85b", "74vgc7l4527jrha395en131ifuvmbp31iem60vh81pvf76i4b6sn")  # 🔐 Replace with your credentials
#         )

#     # Clean up uploaded image
#     default_storage.delete(image_path)

#     if response.status_code == 200:
#         # Save the result image (svg or png)
#         output_filename = f"vectorized.{output_format}"
#         output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

#         with open(output_path, "wb") as f:
#             f.write(response.content)

#         return FileResponse(open(output_path, "rb"), as_attachment=True, filename=output_filename)

#     # Return error response
#     return JsonResponse({"error": response.text}, status=response.status_code)
