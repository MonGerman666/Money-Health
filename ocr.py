# ocr.py
import re
import cv2
import pytesseract
import numpy as np
from PIL import Image

# Ajusta el camí a l'executable de Tesseract si cal.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def deskew_image(gray_img):
    """
    Opcional: corregeix la inclinació (deskew) si la imatge surt torta.
    """
    coords = np.column_stack(np.where(gray_img > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    (h, w) = gray_img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(gray_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def preprocess_image(image_path):
    """
    1) Llegeix la imatge en escala de grisos
    2) (Opcional) Corregeix la inclinació
    3) Aplica binarització adaptativa
    4) Aplica una morfologia de tancament per reduir forats en el text
    """
    # Llegeix en escala de grisos
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"No s'ha pogut llegir la imatge: {image_path}")

    # (Opcional) Deskew per corregir la inclinació
    # img = deskew_image(img)  # Descomenta si cal

    # Binarització adaptativa
    bin_img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 31, 2)
    # Morfologia de tancament per omplir forats en caràcters
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    closed = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)

    processed_path = image_path.replace('.', '_processed.')
    cv2.imwrite(processed_path, closed)
    return processed_path

def processar_tiquet(image_path):
    """
    Retorna tot el text extret (mode 'string') d'una imatge després de pre-processar-la.
    """
    processed_path = preprocess_image(image_path)
    # Obre la imatge amb Pillow
    imatge = Image.open(processed_path)
    # PSM 6 assumeix un bloc de text. També pots provar psm 4, etc.
    custom_config = r'--psm 6'
    # 'cat+spa' si el text pot estar en català i castellà
    text = pytesseract.image_to_string(imatge, lang="cat+spa", config=custom_config)
    return text

def extract_items_from_image(image_path):
    """
    Extrau ítems (producte i preu) combinant:
     - Pre-processament avançat (binarització, morfologia)
     - 'image_to_data' per obtenir bounding boxes de cada paraula
     - Filtrat de paraules clau (TOTAL, EFECTIVO, etc.)
     - Heurístiques (descartar valors massa grans, etc.)
    """
    processed_path = preprocess_image(image_path)
    img = cv2.imread(processed_path, cv2.IMREAD_GRAYSCALE)
    custom_config = r'--psm 6'
    data = pytesseract.image_to_data(img, lang="cat+spa", config=custom_config, output_type=pytesseract.Output.DICT)

    n_boxes = len(data['text'])
    lines = {}
    for i in range(n_boxes):
        # Convertim confidence a float
        try:
            conf = float(data['conf'][i])
        except:
            conf = 0
        # Filtra paraules amb baixa confiança o buides
        if conf > 30 and data['text'][i].strip() != '':
            key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
            lines.setdefault(key, []).append(data['text'][i])
    
    extracted_items = []
    ignore_keywords = ["TOTAL", "EFECTIVO", "CAMBIO", "COMPRA", "COBRADO",
                       "UNITARIO", "IVA", "TARJETA", "CRÉDITO", "CREDITO",
                       "BASE", "CUOTA", "SUBTOTAL"]
    for key, words in lines.items():
        line_text = " ".join(words)
        # Ignora línies amb paraules clau
        if any(k in line_text.upper() for k in ignore_keywords):
            continue
        # Busca format "xxx ... 1,23" a final de línia
        match = re.search(r'(.+?)\s+(\d+(?:[.,]\d+))$', line_text)
        if match:
            prod_name = match.group(1).strip()
            price_str = match.group(2).replace(',', '.')
            try:
                price = float(price_str)
                # Heurística: descarta >100€
                if 0 < price < 100:
                    extracted_items.append({
                        'nom_producte': prod_name,
                        'preu': round(price, 2)
                    })
            except:
                continue
    return extracted_items
