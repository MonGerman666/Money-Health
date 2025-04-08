# ocr.py
import pytesseract
from PIL import Image
import re

def processar_tiquet(path_imagen):
    """
    Rep el camí a una imatge i retorna el text extret utilitzant pytesseract.
    """
    imatge = Image.open(path_imagen)
    text = pytesseract.image_to_string(imatge, lang="cat")  # Usa 'cat' per català o actualitza al llenguatge que necessitis
    return text

def parsear_text_tiquet(text):
    """
    Processa el text extret i cerca línies que coincideixin amb un patró bàsic (nom + preu).
    Aquest exemple utilitza una expressió regular simple.
    """
    lines = text.split('\n')
    expenses = []
    for line in lines:
        line = line.strip()
        if line:
            # Exemple bàsic: cerca un patró on el nom del producte acabi amb espais i un número
            match = re.search(r'([A-Za-zÀ-ÿ0-9\s]+)\s+(\d+(?:[.,]\d+)?)', line)
            if match:
                nom_producte = match.group(1).strip()
                preu = float(match.group(2).replace(',', '.'))
                expenses.append({'nom_producte': nom_producte, 'preu': preu})
    return expenses
