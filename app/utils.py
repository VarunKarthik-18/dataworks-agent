import re

def extract_h1_index(markdown_text: str) -> dict:
    """Extracts H1 headings and their positions from markdown text."""
    lines = markdown_text.split("\n")
    index = {}
    for i, line in enumerate(lines):
        match = re.match(r"^#\s+(.+)", line)  # Matches lines starting with '# '
        if match:
            heading = match.group(1).strip()
            index[heading] = i  # Store the line number
    return index
from sentence_transformers import SentenceTransformer, util

# Load the model globally for efficiency
model = SentenceTransformer("all-MiniLM-L6-v2")

def find_similar_comments(comments: list) -> tuple:
    """Finds the most similar pair of comments using embeddings."""
    if len(comments) < 2:
        return None  # Not enough comments to compare

    embeddings = model.encode(comments, convert_to_tensor=True)

    best_pair = None
    best_score = -1

    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            similarity = util.cos_sim(embeddings[i], embeddings[j]).item()
            if similarity > best_score:
                best_score = similarity
                best_pair = (comments[i], comments[j])

    return best_pair
