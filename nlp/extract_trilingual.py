import json
import os
from docx import Document

def build_trilingual_json():
    # Nom du fichier que vous venez d'envoyer
    docx_path = 'Dictionnaire.docx'
    output_path = 'data/dictionary.json'
    
    if not os.path.exists(docx_path):
        print(f"Erreur : Posez le fichier {docx_path} à la racine du projet.")
        return

    doc = Document(docx_path)
    final_dict = {}

    print("Extraction du dictionnaire trilingue en cours...")

    for paragraph in doc.paragraphs:
        line = paragraph.text.strip()
        
        # On ignore les lignes vides ou les en-têtes de colonnes
        if not line or "English Words" in line:
            continue
            
        # Dans les fichiers Word de ce type, les colonnes sont souvent 
        # séparées par des tabulations (\t)
        parts = line.split('\t')
        
        if len(parts) >= 3:
            english = parts[0].strip().lower()
            malagasy_raw = parts[1].strip().lower()
            french = parts[2].strip()
            
            # Le malgache peut contenir plusieurs synonymes séparés par des virgules
            # On crée une entrée pour chaque mot malgache pour que le clic droit fonctionne sur tous
            malagasy_synonyms = [m.strip() for m in malagasy_raw.split(',')]
            
            for m_word in malagasy_synonyms:
                if m_word:
                    # Si le mot existe déjà, on ne l'écrase pas, on ajoute les options
                    if m_word not in final_dict:
                        final_dict[m_word] = {
                            "fr": french,
                            "en": english
                        }
                    else:
                        # Optionnel : ajouter de nouveaux synonymes si nécessaire
                        pass

    # Sauvegarde au format JSON
    os.makedirs('data', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_dict, f, indent=4, ensure_ascii=False)
    
    print(f"Succès ! {len(final_dict)} entrées malgaches créées dans {output_path}")

if __name__ == "__main__":
    build_trilingual_json()