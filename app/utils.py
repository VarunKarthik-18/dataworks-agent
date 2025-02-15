# app/utils.py
import re
from sentence_transformers import SentenceTransformer, util

# Load model globally (better performance)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_h1_index(markdown_text):
    """Extracts H1 headings from markdown text."""
    return re.findall(r"^# (.+)", markdown_text, re.MULTILINE)

def find_similar_comments(comments):
    """Finds the most similar pair of comments using embeddings."""
    if len(comments) < 2:
        return None  # Not enough comments to compare

    embeddings = embedding_model.encode(comments, convert_to_tensor=True)
    best_pair = None
    best_score = -1

    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            similarity = util.cos_sim(embeddings[i], embeddings[j]).item()
            if similarity > best_score:
                best_score = similarity
                best_pair = (comments[i], comments[j])

    return best_pair
