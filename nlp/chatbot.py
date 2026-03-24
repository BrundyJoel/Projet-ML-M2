import json
import os
import re
import random
from difflib import get_close_matches

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(filename, default=None):
    path = os.path.join(BASE_DIR, "data", filename)
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- CHARGEMENT DES DONNÉES ---
SYNONYMS = load_json("synonyms.json", {})
TRANSLATIONS = load_json("translations.json", {})
# On change le nom ici pour éviter le conflit
WORD_LIST = load_json("word_list.json", []) 

# Si word_list est vide, on le remplit avec les clés des autres fichiers
if not WORD_LIST:
    WORD_LIST = sorted(set(list(SYNONYMS.keys()) + list(TRANSLATIONS.keys())))

# --- LOGIQUE DU CHATBOT ---

def suggest_word(word):
    # On utilise WORD_LIST pour les suggestions de correction
    candidates = get_close_matches(word, WORD_LIST, n=5, cutoff=0.4)
    # ... (gardez votre logique de score ici)
    return candidates[0] if candidates else None

def chatbot_response(message):
    # ... (gardez votre logique de chatbot_response inchangée)
    # Assurez-vous simplement qu'elle utilise bien WORD_LIST au lieu de DICTIONARY
    pass
