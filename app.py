from flask import Flask, render_template, request, jsonify
import os
import json
from nlp.chatbot import chatbot_response
from gtts import gTTS
import re


app = Flask(__name__)

# --- ROUTES HTML (Celles de votre sidebar) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/traducteur')
def traducteur():
    return render_template('traducteur.html')

@app.route('/analyse-sentiment')
def sentiment():
    return render_template('sentiment.html')

@app.route('/synthese-vocale')
def tts():
    return render_template('tts.html')

def split_syllables(word):
    """Découpe le mot en syllabes pour une lecture plus fluide"""
    syllables = re.findall(r'[^aeiouy]*[aeiouy]+', word.lower())
    return " ".join(syllables) if syllables else word

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get("text", "").strip()
    
    if not text:
        return jsonify({"error": "Texte vide"}), 400

    try:
        # 1. Traitement du texte (Syllabisation)
        words = text.split()
        processed_text = "  ".join([split_syllables(w) for w in words])

        # 2. Génération gTTS (Intonation Indonésienne)
        tts = gTTS(text=processed_text, lang="id")
        
        # 3. Sauvegarde dans le dossier static
        file_path = os.path.join('static', 'output.mp3')
        tts.save(file_path)

        return jsonify({"audio_url": "/static/output.mp3?v=" + str(os.urandom(4).hex())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entites')
def entities():
    return render_template('entities.html')


@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    response = chatbot_response(message)
    return jsonify({"response": response})

# La route pour afficher la page (Endpoint: chatbot)
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# --- PARTIE API (Pour la traduction mot-à-mot) ---

def load_dictionary():
    # Détermine le chemin absolu du dossier 'data'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dict_path = os.path.join(base_dir, 'data', 'dictionary.json')
    
    print(f"Tentative de lecture du dictionnaire ici : {dict_path}") # Debug

    try:
        if os.path.exists(dict_path):
            with open(dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Succès ! {len(data)} mots chargés.") # Debug
                return data
        else:
            print("ERREUR : Le fichier dictionary.json n'existe pas dans le dossier data.")
    except Exception as e:
        print(f"ERREUR de lecture JSON : {e}")
    
    return {}

@app.route('/api/translate-word', methods=['POST'])
def translate_api():
    data = request.json
    word_input = data.get('word', '').lower().strip()
    dictionary = load_dictionary()
    
    result = dictionary.get(word_input)
    if result:
        return jsonify({
            "status": "success",
            "translation_fr": result.get('fr', 'N/A'),
            "translation_en": result.get('en', 'N/A'),
            "source": "Dictionnaire"
        })
    
    return jsonify({"status": "not_found"})

if __name__ == '__main__':
    app.run(debug=True, port=8080 )