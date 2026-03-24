import json
import os

def index_dictionary():
    input_file = 'kaikki.org-dictionary-Malagasy.jsonl'
    output_file = 'data/dictionary.json'
    
    # Dictionnaire final
    indexed_data = {}

    if not os.path.exists(input_file):
        print(f"Erreur : Posez le fichier {input_file} à la racine du projet.")
        return

    print("Indexation du dictionnaire en cours... Patientez...")

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line)
                word = entry.get('word', '').lower()
                
                # On récupère les définitions (glosses)
                senses = entry.get('senses', [])
                translations = []
                for sense in senses:
                    glosses = sense.get('glosses', [])
                    translations.extend(glosses)
                
                if word and translations:
                    # On nettoie la traduction (on prend la première définition)
                    main_translation = translations[0]
                    
                    # On stocke dans notre format
                    indexed_data[word] = {
                        "fr": "À traduire (ou via API)", # Le fichier est surtout MG->EN
                        "en": main_translation
                    }
            except:
                continue

    # Sauvegarde dans le dossier data
    os.makedirs('data', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(indexed_data, out, indent=4, ensure_ascii=False)
    
    print(f"Succès ! {len(indexed_data)} mots indexés dans {output_file}")

if __name__ == "__main__":
    index_dictionary()