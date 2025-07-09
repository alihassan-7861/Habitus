#pdf with border
# import os
# import tempfile
# import string
# import numpy as np
# import cv2
# from PIL import Image, ImageOps
# from shapely.geometry import Polygon
# from shapely.strtree import STRtree
# from skimage import measure
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm
# from reportlab.lib.colors import HexColor


# def process_image_to_pbn_pdf(django_file, dpi=300):
#     PAGE_WIDTH, PAGE_HEIGHT = A4
#     BORDER = 1 * cm

#     SIDE_PALETTE_WIDTH = 0.2 * cm
#     TOP_BOTTOM_PALETTE_HEIGHT = 0.2 * cm
#     SWATCH_GAP = 0.1 * cm

#     INNER_X = BORDER + SIDE_PALETTE_WIDTH + SWATCH_GAP
#     INNER_Y = BORDER + TOP_BOTTOM_PALETTE_HEIGHT + SWATCH_GAP
#     INNER_WIDTH = PAGE_WIDTH - 2 * (BORDER + SIDE_PALETTE_WIDTH + SWATCH_GAP)
#     INNER_HEIGHT = PAGE_HEIGHT - 2 * (BORDER + TOP_BOTTOM_PALETTE_HEIGHT + SWATCH_GAP)

#     PALETTE = [
#         "#FFFFFF", "#1A1A1A", "#DADADA", "#999999", "#B7D79A", "#4C8C4A",
#         "#2E472B", "#FDE74C", "#F5C243", "#F28C28", "#C85A27", "#F88379",
#         "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2", "#1B3B6F", "#3CCFCF",
#         "#FBE3D4", "#D5A97B", "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8"
#     ]
#     letters = string.ascii_uppercase
#     LABEL_MAP = dict(zip([c.lower() for c in PALETTE], [f"{letters[i // 10]}{i % 10}" for i in range(len(PALETTE))]))

#     with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
#         for chunk in django_file.chunks():
#             tmp.write(chunk)
#         tmp.flush()
#         pil_image = Image.open(tmp.name)
#         pil_image = ImageOps.exif_transpose(pil_image)
#         src = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

#     h_px, w_px = src.shape[:2]
#     img_ratio = w_px / h_px
#     box_ratio = INNER_WIDTH / INNER_HEIGHT

#     if img_ratio > box_ratio:
#         draw_width = INNER_WIDTH
#         draw_height = draw_width / img_ratio
#     else:
#         draw_height = INNER_HEIGHT
#         draw_width = draw_height * img_ratio

#     sx = draw_width / w_px
#     sy = draw_height / h_px
#     offset_x = INNER_X + (INNER_WIDTH - draw_width) / 2
#     offset_y = INNER_Y + (INNER_HEIGHT - draw_height) / 2

#     pdf_path = tempfile.mktemp(suffix=".pdf")
#     canv = canvas.Canvas(pdf_path, pagesize=A4)
#     canv.setStrokeColorRGB(0, 0, 0)
#     canv.setLineWidth(1)
#     canv.rect(INNER_X, INNER_Y, INNER_WIDTH, INNER_HEIGHT)

#     label_boxes = []
#     str_tree = STRtree([])

#     sketch = np.ones((h_px, w_px, 3), dtype=np.uint8) * 255  # white background

#     for hex_col in PALETTE:
#         bgr = np.array([int(hex_col[i:i + 2], 16) for i in (5, 3, 1)], dtype=np.uint8)
#         mask = cv2.inRange(src, bgr, bgr)
#         mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
#         contours = measure.find_contours(mask, level=0.5)

#         if not contours:
#             continue

#         label = LABEL_MAP[hex_col.lower()]
#         for cnt in contours:
#             if cnt.shape[0] < 4:
#                 continue
#             cnt = cnt[:, [1, 0]]
#             epsilon = 0.0015 * cv2.arcLength(cnt.astype(np.float32), True)
#             approx = cv2.approxPolyDP(cnt.astype(np.float32), epsilon, True)[:, 0, :]
#             area = cv2.contourArea(approx.astype(np.int32))
#             if area < 30: continue
#             x, y, w, h = cv2.boundingRect(approx.astype(np.int32))
#             if max(w / h, h / w) > 10: continue
#             perimeter = cv2.arcLength(approx.astype(np.float32), True)
#             if 4 * np.pi * area / (perimeter ** 2 + 1e-6) < 0.05: continue

#             # PDF path
#             path = canv.beginPath()
#             x0, y0 = approx[0]
#             path.moveTo(offset_x + x0 * sx, offset_y + (h_px - y0) * sy)
#             for x1, y1 in approx[1:]:
#                 path.lineTo(offset_x + x1 * sx, offset_y + (h_px - y1) * sy)
#             path.close()
#             canv.setLineWidth(0.4)
#             canv.drawPath(path)

#             # JPEG drawing
#             cv2.polylines(sketch, [approx.astype(np.int32)], isClosed=True, color=(0, 0, 0), thickness=1)

#             m = cv2.moments(approx.astype(np.float32))
#             if m["m00"] == 0: continue
#             cx = int(m["m10"] / m["m00"])
#             cy = int(m["m01"] / m["m00"])
#             font_size = min(6, max(1, int(area // 100)))

#             label_box = Polygon([
#                 (cx - font_size, cy - font_size / 2),
#                 (cx + font_size, cy - font_size / 2),
#                 (cx + font_size, cy + font_size / 2),
#                 (cx - font_size, cy + font_size / 2)
#             ])
#             if not Polygon(approx).contains(label_box): continue
#             if len(str_tree.query(label_box)) > 0: continue

#             label_boxes.append(label_box)
#             str_tree = STRtree(label_boxes)

#             canv.setFont("Helvetica", font_size)
#             canv.drawCentredString(offset_x + cx * sx, offset_y + (h_px - cy) * sy - font_size / 2, label)

#             # JPEG label
#             font_scale = max(0.3, min(0.5, area / 1500.0))
#             font_thickness = 1
#             text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
#             text_x = cx - text_size[0] // 2
#             text_y = cy + text_size[1] // 2
#             cv2.putText(sketch, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness,cv2.LINE_AA)

#     # Palette for PDF
#     canv.setFont("Helvetica", 6)
#     v_swatch_h = (PAGE_HEIGHT - 2 * BORDER - (23 * SWATCH_GAP)) / 24
#     v_swatch_w = SIDE_PALETTE_WIDTH - 0.1 * cm

#     for i in range(24):
#         hex_color = PALETTE[i]
#         label = LABEL_MAP[hex_color.lower()]
#         y = BORDER + i * (v_swatch_h + SWATCH_GAP)
#         x_left = BORDER + 0.1 * cm
#         canv.setFillColor(HexColor(hex_color))
#         canv.rect(x_left, y, v_swatch_w, v_swatch_h, fill=1, stroke=0)
#         canv.setFillColorRGB(0, 0, 0)
#         canv.drawRightString(x_left - 1, y + v_swatch_h / 4, label)
#         x_right = PAGE_WIDTH - BORDER - SIDE_PALETTE_WIDTH + 0.1 * cm
#         canv.setFillColor(HexColor(hex_color))
#         canv.rect(x_right, y, v_swatch_w, v_swatch_h, fill=1, stroke=0)
#         canv.setFillColorRGB(0, 0, 0)
#         canv.drawString(x_right + v_swatch_w + 2, y + v_swatch_h / 4, label)

#     h_swatch_w = (PAGE_WIDTH - 2 * BORDER - (11 * SWATCH_GAP)) / 12
#     h_swatch_h = TOP_BOTTOM_PALETTE_HEIGHT - 0.1 * cm

#     for j in range(12):
#         hex_top = PALETTE[j]
#         hex_bot = PALETTE[j + 12]
#         label_top = LABEL_MAP[hex_top.lower()]
#         label_bot = LABEL_MAP[hex_bot.lower()]
#         x = BORDER + j * (h_swatch_w + SWATCH_GAP)
#         y_top = PAGE_HEIGHT - BORDER - TOP_BOTTOM_PALETTE_HEIGHT + 0.1 * cm
#         y_bot = BORDER + 0.1 * cm
#         canv.setFillColor(HexColor(hex_top))
#         canv.rect(x, y_top, h_swatch_w, h_swatch_h, fill=1, stroke=0)
#         canv.setFillColorRGB(0, 0, 0)
#         canv.drawCentredString(x + h_swatch_w / 2, y_top + h_swatch_h + 1, label_top)
#         canv.setFillColor(HexColor(hex_bot))
#         canv.rect(x, y_bot, h_swatch_w, h_swatch_h, fill=1, stroke=0)
#         canv.setFillColorRGB(0, 0, 0)
#         canv.drawCentredString(x + h_swatch_w / 2, y_bot - 6, label_bot)

#     canv.setFont("Helvetica-Bold", 9)
#     canv.drawCentredString(PAGE_WIDTH / 2, 0.5 * cm, "Habitus")
#     canv.save()
#     os.remove(tmp.name)

#     # Save JPEG sketch
#     jpeg_path = tempfile.mktemp(suffix=".jpeg")
#     cv2.imwrite(jpeg_path, sketch)

#     return pdf_path, jpeg_path



import os
import tempfile
import string
import numpy as np
import cv2
from PIL import Image, ImageOps
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from skimage import measure
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


def process_image_to_pbn_pdf(django_file, dpi=300):
    PAGE_WIDTH, PAGE_HEIGHT = A4
    BORDER = 1 * cm

    SWATCH_GAP = 0.1 * cm
    INNER_X = BORDER
    INNER_Y = BORDER
    INNER_WIDTH = PAGE_WIDTH - 2 * BORDER
    INNER_HEIGHT = PAGE_HEIGHT - 2 * BORDER

    PALETTE = [
        "#FFFFFF", "#1A1A1A", "#DADADA", "#999999", "#B7D79A", "#4C8C4A",
        "#2E472B", "#FDE74C", "#F5C243", "#F28C28", "#C85A27", "#F88379",
        "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2", "#1B3B6F", "#3CCFCF",
        "#FBE3D4", "#D5A97B", "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8"
    ]
    letters = string.ascii_uppercase
    LABEL_MAP = dict(zip([c.lower() for c in PALETTE], [f"{letters[i // 10]}{i % 10}" for i in range(len(PALETTE))]))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        for chunk in django_file.chunks():
            tmp.write(chunk)
        tmp.flush()
        pil_image = Image.open(tmp.name)
        pil_image = ImageOps.exif_transpose(pil_image)
        src = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    h_px, w_px = src.shape[:2]
    img_ratio = w_px / h_px
    box_ratio = INNER_WIDTH / INNER_HEIGHT

    if img_ratio > box_ratio:
        draw_width = INNER_WIDTH
        draw_height = draw_width / img_ratio
    else:
        draw_height = INNER_HEIGHT
        draw_width = draw_height * img_ratio

    sx = draw_width / w_px
    sy = draw_height / h_px
    offset_x = INNER_X + (INNER_WIDTH - draw_width) / 2
    offset_y = INNER_Y + (INNER_HEIGHT - draw_height) / 2

    pdf_path = tempfile.mktemp(suffix=".pdf")
    canv = canvas.Canvas(pdf_path, pagesize=A4)
    canv.setStrokeColorRGB(0, 0, 0)
    canv.setLineWidth(1)
    canv.rect(INNER_X, INNER_Y, INNER_WIDTH, INNER_HEIGHT)

    label_boxes = []
    str_tree = STRtree([])

    sketch = np.ones((h_px, w_px, 3), dtype=np.uint8) * 255  # white background

    for hex_col in PALETTE:
        bgr = np.array([int(hex_col[i:i + 2], 16) for i in (5, 3, 1)], dtype=np.uint8)
        mask = cv2.inRange(src, bgr, bgr)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        contours = measure.find_contours(mask, level=0.5)

        if not contours:
            continue

        label = LABEL_MAP[hex_col.lower()]
        for cnt in contours:
            if cnt.shape[0] < 4:
                continue
            cnt = cnt[:, [1, 0]]
            epsilon = 0.0015 * cv2.arcLength(cnt.astype(np.float32), True)
            approx = cv2.approxPolyDP(cnt.astype(np.float32), epsilon, True)[:, 0, :]
            area = cv2.contourArea(approx.astype(np.int32))
            if area < 30:
                continue
            x, y, w, h = cv2.boundingRect(approx.astype(np.int32))
            if max(w / h, h / w) > 10:
                continue
            perimeter = cv2.arcLength(approx.astype(np.float32), True)
            if 4 * np.pi * area / (perimeter ** 2 + 1e-6) < 0.05:
                continue

            # PDF path
            path = canv.beginPath()
            x0, y0 = approx[0]
            path.moveTo(offset_x + x0 * sx, offset_y + (h_px - y0) * sy)
            for x1, y1 in approx[1:]:
                path.lineTo(offset_x + x1 * sx, offset_y + (h_px - y1) * sy)
            path.close()
            canv.setLineWidth(0.4)
            canv.drawPath(path)

            # JPEG drawing
            cv2.polylines(sketch, [approx.astype(np.int32)], isClosed=True, color=(0, 0, 0), thickness=1)

            m = cv2.moments(approx.astype(np.float32))
            if m["m00"] == 0:
                continue
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            font_size = min(6, max(1, int(area // 100)))

            label_box = Polygon([
                (cx - font_size, cy - font_size / 2),
                (cx + font_size, cy - font_size / 2),
                (cx + font_size, cy + font_size / 2),
                (cx - font_size, cy + font_size / 2)
            ])
            if not Polygon(approx).contains(label_box):
                continue
            if len(str_tree.query(label_box)) > 0:
                continue

            label_boxes.append(label_box)
            str_tree = STRtree(label_boxes)

            canv.setFont("Helvetica", font_size)
            canv.drawCentredString(offset_x + cx * sx, offset_y + (h_px - cy) * sy - font_size / 2, label)

            # JPEG label
            font_scale = max(0.3, min(0.5, area / 1500.0))
            font_thickness = 1
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
            text_x = cx - text_size[0] // 2
            text_y = cy + text_size[1] // 2
            cv2.putText(sketch, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)

    # Title at bottom
    canv.setFont("Helvetica-Bold", 9)
    canv.drawCentredString(PAGE_WIDTH / 2, 0.5 * cm, "Habitus")
    canv.save()
    os.remove(tmp.name)

    # Save JPEG sketch
    jpeg_path = tempfile.mktemp(suffix=".jpeg")
    cv2.imwrite(jpeg_path, sketch)

    return pdf_path, jpeg_path
