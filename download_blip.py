from huggingface_hub import snapshot_download

# BLIP captioning base
snapshot_download(
    repo_id="Salesforce/blip-image-captioning-base",
    local_dir="./data/blip-image-captioning-base",
    local_dir_use_symlinks=False
)
