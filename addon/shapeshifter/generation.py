import subprocess
import sys
from shapeshifter import library

# Check if spaCy is installed
python_exe = sys.executable
try:
    import spacy
except ImportError:
    # Install spaCy
    python_exe = sys.executable
    print("spaCy is not installed. Installing...")
    subprocess.call([python_exe, '-m', 'ensurepip'])
    subprocess.call([python_exe, '-m', 'pip', 'install', 'spacy'])
    import spacy  # Import spaCy after installation

from spacy.lang.en.stop_words import STOP_WORDS
from collections import defaultdict

# Download spaCy models if needed
model_name = 'en_core_web_md'
if model_name not in spacy.util.get_installed_models():
    print(f"Downloading spaCy model: {model_name}")
    subprocess.call([python_exe, '-m', 'spacy', 'download', model_name])

# Load spaCy model
nlp = spacy.load(model_name)

def preprocess_input(text):
    doc = nlp(text.lower().strip())
    preprocess = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'VERB', 'PROPN', 'ADJ']]
    return preprocess

def word_similarity(word1, word2):
    return library.map_value(nlp(word1).similarity(nlp(word2)), -1, 1, 0, 1)

def assets_evaluation(preprocess, assets):
    assets_evaluated = []
    for asset in assets:
        asset_types = library.format_tags_asset(library.get_tags_asset(asset, 'type'))[0]
        asset_infos = library.format_tags_asset(library.get_tags_asset(asset, 'info'))[0]
        asset_similarity = 0
        for input_data in preprocess:
            if input_data['type'] in asset_types or input_data['type'] == "ALL":
                similarity_type = 1
            else:
                similarity_type = 0
            # Calculate Similarity Info
            similarity_info = 0
            for input_info in input_data['prompt']:
                similarity_input_info = 0
                for asset_info in asset_infos:
                    similarity_input_info += word_similarity(input_info, asset_info)
                similarity_input_info /= len(asset_infos)
                similarity_info += similarity_input_info
            similarity_info /= len(input_data['prompt'])
            # Calculate Similarity
            asset_similarity += similarity_type * similarity_info * input_data['threshold']
        assets_evaluated.append([asset, asset_similarity])
    # -------- CREDIBILITY TO DO
    # --------------------------
    return assets_evaluated


def library_evaluation(library, evaluation, credibility):
    max_total_distance = -float("inf")
    min_total_distance = float("inf")

    assets = []
    for asset in library:
        tags = library.get_tags_asset(asset, "info")
        total_distance = 0.0
        for individual in evaluation:
            max_distance = 0.0
            for word_struct in individual[1]:
                if word_struct[0] in tags and word_struct[1]>max_distance:
                    max_distance=word_struct[1]
            total_distance+=max_distance
        if total_distance > max_total_distance:
            max_total_distance = total_distance
        if total_distance < min_total_distance:
            min_total_distance = total_distance
        assets.append([asset, total_distance])
    
    assets = sorted(assets, key=lambda x: x[1], reverse=True)
    
    mapped_assets = []
    for asset in assets:
        mapped_distance = library.map_value(asset[1], min_total_distance, max_total_distance, 0, 1)
        if mapped_distance >= credibility:
            mapped_assets.append(asset[0])

    return mapped_assets