from sentence_transformers import SentenceTransformer
from typing import List

# Initialize the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings(sentences: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of sentences
    
    Args:
        sentences: List of strings to generate embeddings for
        
    Returns:
        List of embeddings as float arrays
    """
    try:
        embeddings = model.encode(sentences)
        return embeddings.tolist()
    except Exception as e:
        raise ValueError(f"Error generating embeddings: {str(e)}")