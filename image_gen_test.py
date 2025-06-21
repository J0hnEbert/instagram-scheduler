from diffusers import StableDiffusionPipeline
import torch
import os
from PIL import Image

MODEL_PATH = "./data/dreamshaper-6"  # Anpassen falls nötig
OUTPUT_DIR = "./data/generated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_image(prompt, filename_base):
    pipe = StableDiffusionPipeline.from_pretrained(MODEL_PATH)
    pipe = pipe.to("cpu")

    print(f"Generiere 512x512 Bild für Prompt: '{prompt}' ...")
    result = pipe(
        prompt,
        num_inference_steps=45,
        height=512,
        width=512
    )
    image = result.images[0]
    
    # 512x512 speichern
    path_512 = os.path.join(OUTPUT_DIR, f"{filename_base}_512.png")
    image.save(path_512)
    print(f"✅ 512x512 Bild gespeichert: {path_512}")
    
    # Skalieren auf 1080x1080
    image_1080 = image.resize((1080, 1080), resample=Image.LANCZOS)
    path_1080 = os.path.join(OUTPUT_DIR, f"{filename_base}_1080.png")
    image_1080.save(path_1080)
    print(f"✅ 1080x1080 Bild gespeichert: {path_1080}")
    
    return path_512, path_1080

if __name__ == "__main__":
    generate_image("A beautiful mountain landscape during sunset", "mountain_sunset")
