from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import re

def load_model(model_dir):
    print(f"Lade Modell aus: {model_dir}")
    processor = BlipProcessor.from_pretrained(model_dir)
    model = BlipForConditionalGeneration.from_pretrained(model_dir)
    return processor, model

def generate_caption(processor, model, image_path):
    print(f"Öffne Bild: {image_path}")
    raw_image = Image.open(image_path).convert('RGB')
    
    inputs = processor(raw_image, return_tensors="pt")
    device = torch.device("cpu")
    model.to(device)
    
    print("Generiere Caption...")
    out = model.generate(**inputs, max_length=50)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

def generate_hashtags(caption):
    # Einfache Regel: Nimm bedeutungstragende Wörter
    # Entferne kurze Wörter, Zahlen, Sonderzeichen
    words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]{3,}\b', caption.lower())
    # Einfache Duplikat-Entfernung
    unique_words = sorted(set(words))
    hashtags = ['#' + w for w in unique_words]
    return ' '.join(hashtags)

if __name__ == "__main__":
    MODEL_DIR = "./data/blip-image-captioning-base"  # Pfad anpassen
    IMAGE_PATH = "app/static/generated/20250621172545_512.png"   # Pfad anpassen
    
    processor, model = load_model(MODEL_DIR)
    caption = generate_caption(processor, model, IMAGE_PATH)
    hashtags = generate_hashtags(caption)

    print(f"\n🔹 Generierte Caption:\n{caption}")
    print(f"\n🔹 Generierte Hashtags:\n{hashtags}")
