async function generateBLIPCaption() {
    const fileInput = document.getElementById('imageCaptionFile');
    if (fileInput.files.length === 0) {
        alert('Bitte wähle ein Bild aus.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = await fetch('/generate_blip_caption', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    if (response.ok) {
        document.getElementById('captionField').value = data.caption || '';
    } else {
        alert(data.error || 'Fehler bei der Caption-Generierung');
    }
}

async function generateBLIPHashtags() {
    const fileInput = document.getElementById('imageCaptionFile');
    if (fileInput.files.length === 0) {
        alert('Bitte wähle ein Bild aus.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = await fetch('/generate_blip_hashtags', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    if (response.ok) {
        document.getElementById('hashtagsField').value = data.hashtags || '';
    } else {
        alert(data.error || 'Fehler bei der Hashtag-Generierung');
    }
}
