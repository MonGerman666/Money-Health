# custom_dataset.py
import os
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as transforms

class OCRDataset(Dataset):
    def __init__(self, image_folder, transform=None):
        """
        image_folder: carpeta amb imatges i fitxers .txt amb les transcripcions.
        transform: transformacions per a la imatge.
        """
        self.image_folder = image_folder
        self.image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_name = self.image_files[idx]
        image_path = os.path.join(self.image_folder, image_name)
        # Suposem que el fitxer d'etiqueta té el mateix nom amb extensió .txt
        label_path = os.path.splitext(image_path)[0] + '.txt'
        
        image = Image.open(image_path).convert('L')  # Convertim a escala de grisos
        if self.transform:
            image = self.transform(image)
        else:
            # Transformació bàsica: redimensionem a una mida fixa (ex. 100 de height) i normalitzem
            self.transform = transforms.Compose([
                transforms.Resize((100, 400)),
                transforms.ToTensor(),  # forma (1, H, W)
                transforms.Normalize((0.5,), (0.5,))
            ])
            image = self.transform(image)
        
        # Llegeix l'etiqueta: Suposem que és una cadena simple amb els caràcters.
        with open(label_path, 'r', encoding='utf-8') as f:
            label = f.read().strip()
        
        return image, label
