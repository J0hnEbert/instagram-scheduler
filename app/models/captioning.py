from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import re

MODEL_DIR = "./data/blip-image-captioning-base"

processor = BlipProcessor.from_pretrained(MODEL_DIR)
model = BlipForConditionalGeneration.from_pretrained(MODEL_DIR).to("cpu")

def generate_caption(image_path):
    raw_image = Image.open(image_path).convert('RGB')
    inputs = processor(raw_image, return_tensors="pt")
    out = model.generate(**inputs, max_length=50)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

def generate_hashtags(image_path):
    caption = generate_caption(image_path)
    words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]{3,}\b', caption.lower())
    unique_words = sorted(set(words))
    hashtags = ' '.join(['#' + w for w in unique_words])
    return hashtags
