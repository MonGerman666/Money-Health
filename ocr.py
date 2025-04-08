import pytesseract

# Defineix la ruta completa on s'instal·la l'executable de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Ara pots processar les imatges sense problemes
from PIL import Image

def processar_tiquet(path_imagen):
    imatge = Image.open(path_imagen)
    text = pytesseract.image_to_string(imatge, lang="cat")  # Ajusta el llenguatge si cal
    return text

# Exemple de comprovació
if __name__ == '__main__':
    resultat = processar_tiquet('exemple_tiquet.jpg')
    print(resultat)


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
