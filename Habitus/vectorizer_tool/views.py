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
from rest_framework.parsers import MultiPartParser
from .utils import process_image_to_pbn_pdf
from django.http import FileResponse

def register(request):
    context={}
    return render(request,'vectorizer_tool/register.html',context)


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



def test_pbn_frontend(request):
    return render(request, "vectorizer_tool/register.html")




class PaintByNumberView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        image_file = request.FILES.get("image")
        selected_format = request.POST.get("format", "pdf").lower()

        if not image_file:
            return Response({"error": "No image uploaded."}, status=400)

        try:
            pdf_path, jpeg_path = process_image_to_pbn_pdf(image_file)

            if selected_format == "jpeg":
                return FileResponse(
                    open(jpeg_path, 'rb'),
                    as_attachment=True,
                    filename='habitus.jpeg',
                    content_type='image/jpeg'
                )
            else:  # default to PDF
                return FileResponse(
                    open(pdf_path, 'rb'),
                    as_attachment=True,
                    filename='habitus.pdf',
                    content_type='application/pdf'
                )

        except Exception as e:
            return Response({"error": str(e)}, status=500)


