import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from tqdm import tqdm

def load_documents(converted_dir):
    """Loading documents from JSON files"""
    documents = {}
    for filename in os.listdir(converted_dir):
        if filename.endswith('.json'):
            with open(os.path.join(converted_dir, filename), 'r') as f:
                doc = json.load(f)
                documents[doc['id']] = doc['contents']
    return documents

def load_queries(query_file):
    """Loading queries from query file"""
    with open(query_file, 'r') as f:
        return [line.strip() for line in f]

def generate_qrels(documents, queries, threshold=0.3, top_k=5):
    """Generate qrels for TF-IDF similarity"""
    all_texts = list(documents.values()) + queries
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    doc_vectors = tfidf_matrix[:len(documents)]
    query_vectors = tfidf_matrix[len(documents):]
    qrels = []
    doc_ids = list(documents.keys())

    for query_idx, query_vector in enumerate(tqdm(query_vectors, desc="Generating qrels...")): 
        similarities = cosine_similarity(query_vector, doc_vectors)[0]

        # top-k similar documents above threshold
        top_indices = np.argsort(similarities)[::-1]

        for idx in top_indices[:top_k]:
            if similarities[idx] >= threshold:
                qrels.append((query_idx, doc_ids[idx], 1))

    return qrels

def save_qrels(qrels, output_file):
    """Save qrels to file..."""
    with open(output_file, 'w') as f:
        for query_id, doc_id, relevance in qrels:
            f.write(f"{query_id} {doc_id} {relevance}\n")




def main():

    base_dir = "data/inaugural_speeches"
    converted_dir = os.path.join(base_dir, "converted")
    query_file = os.path.join(base_dir, "inaugural_speeches-queries.txt")
    qrels_file = os.path.join(base_dir, "inaugural_speeches-qrels.txt")


    
    print("Loading documents...")
    documents = load_documents(converted_dir)

    print("Loading queries...")
    queries = load_queries(query_file)

    print("Generating qrels...")
    qrels = generate_qrels(documents, queries)

    print("Saving qrels...")
    save_qrels(qrels, qrels_file)

    print(f"Generated qrels saved to {qrels_file}")
    print(f"Total qrels generated: {len(qrels)}")

if __name__ == "__main__":
    main()