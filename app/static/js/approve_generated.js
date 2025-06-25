async function generatePreviewCaption() {
    const imagePath = document.querySelector("input[name='image_path']").value;
    const response = await fetch("/generate_blip_caption", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_path: imagePath })
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById("captionField").value = data.caption;
    } else {
        alert("Fehler bei der Caption-Generierung");
    }
}

async function generatePreviewHashtags() {
    const imagePath = document.querySelector("input[name='image_path']").value;
    const response = await fetch("/generate_blip_hashtags", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_path: imagePath })
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById("hashtagsField").value = data.hashtags;
    } else {
        alert("Fehler bei der Hashtag-Generierung");
    }
}