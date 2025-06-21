from diffusers import StableDiffusionPipeline
from PIL import Image
import os

UPLOAD_DIR = "./app/static/uploads"
GENERATED_DIR = "./app/static/generated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

def generate_image_and_upscale(prompt, filename_base):
    pipe = StableDiffusionPipeline.from_pretrained("./data/dreamshaper-6")
    pipe = pipe.to("cpu")

    result = pipe(prompt, num_inference_steps=20, height=512, width=512)
    image = result.images[0]

    path_512 = os.path.join(GENERATED_DIR, f"{filename_base}_512.png")
    path_1080 = os.path.join(GENERATED_DIR, f"{filename_base}_1080.png")
    upload_1080 = os.path.join(UPLOAD_DIR, f"{filename_base}_1080.png")

    image.save(path_512)
    image_1080 = image.resize((1080, 1080), resample=Image.LANCZOS)
    image_1080.save(path_1080)
    image_1080.save(upload_1080)

    return path_512, path_1080, upload_1080
