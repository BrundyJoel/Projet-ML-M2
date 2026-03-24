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


SYNONYMS = load_json("synonyms.json", {})
TRANSLATIONS = load_json("translations.json", {})
DICTIONARY = load_json("word_list.json", [])

if not DICTIONARY:
    DICTIONARY = sorted(set(list(SYNONYMS.keys()) + list(TRANSLATIONS.keys())))

LAST_SUGGESTION = None
LAST_WORD = None


def normalize_text(text):
    return text.lower().strip()


def detect_intent(msg):
    if any(x in msg for x in ["salama", "manao ahoana"]):
        return "greeting"

    if any(x in msg for x in ["fanampiana", "ampio aho", "inona no azonao atao"]):
        return "help"

    if any(x in msg for x in ["teny mitovy", "mitovy hevitra"]):
        return "synonym"

    if any(x in msg for x in ["dikan", "dikany", "fandikana", "adika"]):
        return "translation"

    if any(x in msg for x in ["fitsipika", "lalàna", "lalana"]):
        return "rule"

    if any(x in msg for x in ["ahitsio", "fanitsiana", "jereo ity teny ity"]):
        return "correction"

    if any(x in msg for x in ["endrika", "fandrafetana", "conjugaison"]):
        return "conjugation"

    return "unknown"


def extract_word(msg):
    patterns = [
        # Teny mitovy hevitra
        r"teny mitovy amin'?ny ([\w-]+)",
        r"mitovy hevitra amin'?ny ([\w-]+)",
        r"teny mitovy ([\w-]+)",

        # Dikan-teny
        r"dikan'?ny ([\w-]+)",
        r"fandikana ([\w-]+)",
        r"adika ([\w-]+)",
        r"inona ny dikan'?ny ([\w-]+)",

        # Fanitsiana
        r"ahitsio ([\w-]+)",
        r"fanitsiana ([\w-]+)",
        r"jereo ity teny ity ([\w-]+)",

        # Endrika
        r"endrika ([\w-]+)",
        r"fandrafetana ([\w-]+)",

        # Fitsipika
        r"fitsipika ([\w-]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, msg)
        if match:
            return match.group(1)

    words = msg.split()
    if len(words) > 1:
        return words[-1]

    return None


def suggest_word(word):
    candidates = get_close_matches(word, DICTIONARY, n=5, cutoff=0.4)

    for candidate in candidates:
        score = 0

        if len(candidate) > 0 and len(word) > 0 and candidate[0] == word[0]:
            score += 1

        if len(candidate) > 1 and len(word) > 1 and candidate[:2] == word[:2]:
            score += 2

        if abs(len(candidate) - len(word)) <= 2:
            score += 1

        if score >= 3:
            return candidate

    return None


def detect_rule_issue(word):
    banned_patterns = ["nb", "mk", "dt", "bp", "sz"]
    for pattern in banned_patterns:
        if pattern in word:
            return pattern
    return None


def generate_word_forms(word):
    base = word.strip()
    if not base:
        return []

    forms = [
        f"mi{base}",
        f"man{base}",
        f"ma{base}",
        f"{base}ana"
    ]
    return forms


def chatbot_response(message):
    global LAST_SUGGESTION, LAST_WORD

    msg = normalize_text(message)
    intent = detect_intent(msg)

    if msg in ["eny", "ye", "ok", "okay", "marina"]:
        if LAST_SUGGESTION:
            return f"Tsara 👍 ampiasao ny teny '{LAST_SUGGESTION}' ho fanitsiana an'ilay '{LAST_WORD}'."
        return "Misy teny tianao hohamarinina ve ?"

    if msg in ["tsia", "non", "no"]:
        if LAST_WORD:
            return f"Eny ary. Raha tianao dia afaka mijery soso-kevitra hafa momba ny teny '{LAST_WORD}' aho."
        return "Eny ary, andao hanohy."

    if intent == "greeting":
        responses = [
            "Salama 👋 Inona no azoko anampiana anao ?",
            "Salama 😊 Afaka manampy anao amin'ny teny mitovy hevitra, fandikana, fanitsiana ary fitsipika aho.",
            "Manao ahoana 👋 Soraty izay tianao hojerena."
        ]
        return random.choice(responses)

    if intent == "help":
        responses = [
            "Afaka manao ireto aho :\n- teny mitovy amin'ny tsara\n- dikan'ny trano\n- ahitsio tranoo\n- endrika tosika\n- omeo fitsipika",
            "Ireto misy ohatra azonao andramana :\n- teny mitovy amin'ny tsara\n- dikan'ny trano\n- ahitsio tranoo\n- endrika tosika\n- omeo fitsipika",
            "Azonao atao ny manoratra toy izao :\n- teny mitovy amin'ny tsara\n- dikan'ny trano\n- ahitsio tranoo\n- endrika tosika\n- omeo fitsipika"
        ]
        return random.choice(responses)

    if intent == "synonym":
        word = extract_word(msg)
        if word and word in SYNONYMS:
            responses = [
                f"Ireto ny teny mitovy hevitra amin'ny '{word}' : {', '.join(SYNONYMS[word])}.",
                f"Afaka mampiasa ireto ho solon'ny '{word}' ianao : {', '.join(SYNONYMS[word])}.",
                f"Mitovy hevitra amin'ny '{word}' ireto : {', '.join(SYNONYMS[word])}."
            ]
            return random.choice(responses)

        return random.choice([
            "Tsy nahita teny mitovy hevitra ho an'io teny io aho.",
            "Miala tsiny fa tsy mbola manana teny mitovy hevitra ho an'io aho.",
            "Tsy hitako ny teny mitovy hevitra amin'io teny io."
        ])

    if intent == "translation":
        word = extract_word(msg)
        if word and word in TRANSLATIONS:
            responses = [
                f"Ny dikan'ny '{word}' dia : {TRANSLATIONS[word]}.",
                f"Adika hoe : {TRANSLATIONS[word]}.",
                f"Ny fandikana ny '{word}' dia : {TRANSLATIONS[word]}."
            ]
            return random.choice(responses)

        return random.choice([
            "Tsy hitako ny fandikana an'io teny io.",
            "Miala tsiny fa tsy mbola fantatro ny dikan'io teny io.",
            "Tsy mbola ao anaty rakibolana ny fandikana an'io teny io."
        ])

    if intent == "rule":
        word = extract_word(msg)
        if word:
            issue = detect_rule_issue(word)
            if issue:
                return f"Ny teny '{word}' dia misy fitambarana litera '{issue}' izay mety tsy mahazatra amin'ny teny malagasy."
            return f"Tsy nahita olana mazava tamin'ny teny '{word}' aho araka ny fitsipika tsotra ampiasaina."

        return random.choice([
            "Ohatra amin'ny fitsipika : tsy dia mahazatra amin'ny teny malagasy ny fitambarana litera toy ny 'nb' na 'mk'.",
            "Fitsipika tsotra : misy fitambarana litera sasany tsy fahita amin'ny teny malagasy, toy ny 'nb' sy 'mk'.",
            "Azo marihina ho tsy mahazatra amin'ny teny malagasy ny fitambarana toy ny 'nb' na 'mk'."
        ])

    if intent == "correction":
        word = extract_word(msg)
        if word:
            issue = detect_rule_issue(word)
            suggestion = suggest_word(word)

            LAST_WORD = word
            LAST_SUGGESTION = suggestion

            if issue and suggestion is not None:
                return f"Ny teny '{word}' dia toa misy olana amin'ny fitsipika ('{issue}'). Angamba '{suggestion}' no marina ?"

            if suggestion is not None and suggestion != word:
                responses = [
                    f"Toa diso ny teny '{word}'. Angamba '{suggestion}' no marina ?",
                    f"Raha jerena amin'ny rakibolana, '{word}' dia toa diso. Soso-kevitra : '{suggestion}'.",
                    f"Mety diso ny teny '{word}'. Heveriko fa '{suggestion}' no tianao hosoratana."
                ]
                return random.choice(responses)

            if word in DICTIONARY:
                LAST_SUGGESTION = word
                return f"Ny teny '{word}' dia hita ao anaty rakibolana ka toa marina."

            return f"Tsy nahita fanitsiana mazava ho an'ny teny '{word}' aho."

        return random.choice([
            "Omeo teny iray aho hojerena.",
            "Soraty ilay teny tianao hohamarinina.",
            "Ampidiro aloha ilay teny tianao hahitsy."
        ])

    if intent == "conjugation":
        word = extract_word(msg)
        if word:
            forms = generate_word_forms(word)
            if forms:
                return f"Ireto misy endrika azo atolotra ho an'ny '{word}' : {', '.join(forms)}."
        return "Soraty ilay teny tianao hamoahana endrika, ohatra : endrika tosika."

    return random.choice([
        "Azafady, tsy azoko tsara ilay fangatahanao. Andramo ireto :\n- teny mitovy amin'ny tsara\n- dikan'ny trano\n- ahitsio tranoo\n- endrika tosika\n- omeo fitsipika",
        "Mbola tsy azoko ilay izy 😅 Andramo iray amin'ireto :\n- teny mitovy amin'ny tsara\n- dikan'ny trano\n- ahitsio tranoo\n- endrika tosika\n- omeo fitsipika",
        "Azafady fa tsy mazava ilay fangatahanao. Afaka manoratra toy izao ianao :\n- teny mitovy amin'ny tsara\n- dikan'ny trano\n- ahitsio tranoo\n- endrika tosika\n- omeo fitsipika"
    ])