async function processCorrection() {
    const text = document.getElementById('input-text').value;
    const resultBox = document.getElementById('result-box');
    
    if (!text) return alert("Veuillez saisir du texte");

    const response = await fetch('/api/correct', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: text})
    });

    const data = await response.json();
    resultBox.classList.remove('hidden');
    resultBox.innerHTML = `<strong>Suggestion :</strong> ${data.corrected}`;
}

// Exemple pour le sentiment (à lier dans sentiment.html)
async function analyzeSentiment() {
    const text = document.getElementById('input-text').value;
    const response = await fetch('/api/sentiment', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: text})
    });
    const data = await response.json();
    alert(`Sentiment : ${data.status} (Score: ${data.score})`);
}