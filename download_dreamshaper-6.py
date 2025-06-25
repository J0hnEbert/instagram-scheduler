from huggingface_hub import snapshot_download

print("Starte Download des distillierten Modells...")

snapshot_download(
    repo_id="Lykon/dreamshaper-6",
    local_dir="./data/dreamshaper-6",
    local_dir_use_symlinks=False,
    resume_download=True,
    max_workers=2
)


print("Download abgeschlossen!")

