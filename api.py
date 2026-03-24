import os
import json
import difflib
from flask import Blueprint, request, jsonify
from mtranslate import translate as google_translate

# Tentative d'import de RapidFuzz, sinon on utilise difflib par défaut
try:
    from rapidfuzz import process, distance
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

# Import du lemmatiseur
try:
    from nlp.lemmatizer import MalagasyLemmatizer
    lemmatizer = MalagasyLemmatizer()
except ImportError:
    lemmatizer = None

api_bp = Blueprint('api', __name__)

def load_dictionary():
    """Charge le dictionnaire JSON extrait du DOCX"""
    # On utilise un chemin absolu pour éviter les erreurs de dossier
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_path = os.path.join(base_dir, 'data', 'dictionary.json')
    
    try:
        if os.path.exists(dict_path):
            with open(dict_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"ATTENTION : Fichier non trouvé à {dict_path}")
            return {}
    except Exception as e:
        print(f"Erreur de lecture du dictionnaire : {e}")
        return {}

@api_bp.route('/translate-word', methods=['POST'])
def translate():
    data = request.json
    word_input = data.get('word', '').lower().strip()
    
    if not word_input:
        return jsonify({"status": "error", "message": "Aucun mot fourni"})

    # On charge les données (Flask lira le JSON généré par votre script d'extraction)
    dictionary = load_dictionary()
    
    # --- ÉTAPE 1 : Recherche directe ---
    result = dictionary.get(word_input)
    final_word = word_input
    source_label = "Dictionnaire DOCX"

    # --- ÉTAPE 2 : Lemmatisation (si non trouvé) ---
    if not result and lemmatizer:
        root = lemmatizer.get_root(word_input)
        if root != word_input:
            result = dictionary.get(root)
            if result:
                final_word = root
                source_label = f"Racine : {root}"

    # --- ÉTAPE 3 : Recherche Floue (si toujours pas trouvé) ---
    if not result:
        all_words = list(dictionary.keys())
        if all_words: # On vérifie que le dictionnaire n'est pas vide
            if HAS_RAPIDFUZZ:
                closest = process.extractOne(word_input, all_words, scorer=distance.Levenshtein.distance)
                if closest and closest[1] <= 2:
                    final_word = closest[0]
                    result = dictionary.get(final_word)
                    source_label = f"Correction : {final_word}"
            else:
                matches = difflib.get_close_matches(word_input, all_words, n=1, cutoff=0.7)
                if matches:
                    final_word = matches[0]
                    result = dictionary.get(final_word)
                    source_label = f"Correction : {final_word}"

    # --- ÉTAPE 4 : Envoi des résultats ---
    if result:
        # On récupère les colonnes extraites du Word
        en_text = result.get('en', 'N/A')
        fr_text = result.get('fr', 'N/A')

        return jsonify({
            "status": "success",
            "word": final_word,
            "translation_en": en_text,
            "translation_fr": fr_text,
            "source": source_label
        })

    # --- ÉTAPE 5 : Si vraiment rien n'est trouvé ---
    return jsonify({
        "status": "not_found", 
        "word": word_input,
        "source": "Non répertorié"
    })