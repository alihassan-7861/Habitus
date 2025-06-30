import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VectorizerSerializer
import requests
from django.http import HttpResponse
import json  # ✅ Add this at the top of the file

# Create your views here.
# def vectorizer(request):
#     context={}
#     return render(request,'vectorizer_tool/vectorizer.html',context)

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



import re



class VectorizeImageView(APIView):
    def post(self, request):
        serializer = VectorizerSerializer(data=request.data)
        if serializer.is_valid():
            validated = serializer.validated_data
            print("🧪 Output format received from validated data:", validated.get("output_format"))

            api_id = os.environ.get("VECTORIZER_API_ID")
            api_key = os.environ.get("VECTORIZER_API_KEY")

            if not api_id or not api_key:
                return Response({"error": "Missing Vectorizer API credentials"}, status=500)

            image = validated['image']
            files = {"image": image}

            # ✅ Locked custom palette
            HABITUS_PALETTE = [
                "#FFFFFF", "#1A1A1A", "#DADADA", "#999999",
                "#B7D79A", "#4C8C4A", "#2E472B", "#FDE74C",
                "#F5C243", "#F28C28", "#C85A27", "#F88379",
                "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2",
                "#1B3B6F", "#3CCFCF", "#FBE3D4", "#D5A97B",
                "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8"
            ]

            # Field mapping from validated serializer input
            API_FIELD_MAPPING = {
                "minimum_area": "processing.shapes.min_area_px",
                "output_format": "output.file_format",
                "smoothing": "output.bitmap.anti_aliasing_mode",
                "level_of_details": "output.curves.line_fit_tolerance",
                "width": "output.size.width",
                "height": "output.size.height",
            }

           # ✅ Build payload
            payload = {
                "mode": validated.get("mode", "production"),
                "processing": {
                    "palette": { "type": "custom", "colors": [  "#FFFFFF", "#1A1A1A", "#DADADA", "#999999",
                            "#B7D79A", "#4C8C4A", "#2E472B", "#FDE74C",
                            "#F5C243", "#F28C28", "#C85A27", "#F88379",
                            "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2",
                            "#1B3B6F", "#3CCFCF", "#FBE3D4", "#D5A97B",
                            "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8" ] },
                    "max_colors": 24
                },
                "output_format": "png",
                "gap_filler": {
                        "enabled": False
                        }

                }

            


            # ✅ Populate mapped fields into payload
            def set_nested_key(obj, dotted_key, value):
                keys = dotted_key.split('.')
                for key in keys[:-1]:
                    obj = obj.setdefault(key, {})
                obj[keys[-1]] = value

            for local_field, api_field in API_FIELD_MAPPING.items():
                if local_field in validated:
                    set_nested_key(payload, api_field, validated[local_field])
                
                
            print("Mode:", validated.get("mode"))
            print("Width:", validated.get("width"))
            print("Height:", validated.get("height"))
            print("Level of Detail:", validated.get("level_of_details"))
            print("Minimum Area:", validated.get("minimum_area"))
            print("Smoothing:", validated.get("smoothing"))

            # ✅ Debug the final payload
            print("Final payload:", json.dumps(payload, indent=2))
            print("Expected format:", validated.get("output_format"))

            try:
                response = requests.post(
                    "https://api.vectorizer.ai/api/v1/vectorize",
                    json=payload,
                    files=files,
                    auth=(api_id, api_key),
                    headers={"Accept": "application/json"}
                )
                print("🧪 First 200 bytes of response content:\n", response.content[:200])

                if response.status_code == 200:
                   svg_text = response.content.decode('utf-8', errors='ignore')

                   used_colors = set(re.findall(r'fill="(#(?:[0-9a-fA-F]{3}){1,2})"', svg_text))
                   used_colors = {c.lower() for c in used_colors}

                   habitus_palette = {
                        "#ffffff", "#1a1a1a", "#dadada", "#999999",
                        "#b7d79a", "#4c8c4a", "#2e472b", "#fde74c",
                        "#f5c243", "#f28c28", "#c85a27", "#f88379",
                        "#d63e3e", "#8c1c13", "#aed9e0", "#4a90e2",
                        "#1b3b6f", "#3ccfcf", "#fbe3d4", "#d5a97b",
                        "#5c3b28", "#f5e0c3", "#a24b7b", "#ffcfd8"
                    }

                   print("✅ Colors used in SVG:", used_colors)
                   if used_colors.issubset(habitus_palette):
                        print("✅ Verified: Only Habitus® palette colors used.")
                   else:
                        print("❌ Extra colors found:", used_colors - habitus_palette)
                   output_format = validated.get("output_format", "svg")
                  # Check if content is SVG based on content, not just header
                   is_svg = response.content.lstrip().startswith(b"<?xml") or b"<svg" in response.content[:200]
                   file_extension = "svg" if is_svg else "png"
                   content_type = "image/svg+xml" if is_svg else "image/png"
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
            return Response(serializer.errors, status=400)
