import os
import json
from tqdm import tqdm
from pyserini.search.lucene import LuceneSearcher
from pyserini.index.lucene import IndexReader
import numpy as np
import subprocess
import time
import matplotlib.pyplot as plt

#helper functions - sustainability metrics
from sustainability import (
    calculateJobSustainabilityCost,
    amortizedSustainabilityCost, 
    sustainability_cost_rate_per_second,
    carbon_mix
)

def preprocess_corpus(input_file, output_dir):
    """preprocess corpus into jsonl format"""
    os.makedirs(output_dir, exist_ok=True)
    with open(input_file, 'r') as f:
        for i, line in enumerate(tqdm(f, desc="Preprocessing corpus")):
            doc = {
                "id": f"{i}",  # Changed to match qrels format
                "contents": line.strip()
            }
            with open(os.path.join(output_dir, f"doc{i}.json"), 'w') as out:
                json.dump(doc, out)


def build_index(input_dir, index_dir):
    """build index from processed corpus"""
    if os.path.exists(index_dir) and os.listdir(index_dir):
        print(f"Index already exists at {index_dir}. Skipping index building.")
        return

    cmd = [
        "python", "-m", "pyserini.index.lucene",
        "--collection", "JsonCollection",
        "--input", input_dir,
        "--index", index_dir,
        "--generator", "DefaultLuceneDocumentGenerator",
        "--threads", "1",
        "--storePositions", "--storeDocvectors", "--storeRaw"
    ]
    subprocess.run(cmd, check=True)


def load_queries(query_file):
    """load queries into a list"""
    with open(query_file, 'r') as f:
        return [line.strip() for line in f]


def load_qrels(qrels_file):
    """load qrels into a dictionary"""
    qrels = {}
    with open(qrels_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                qid, docid, rel = parts
            else:
                raise Exception(f"incorrect line: {line.strip()}")

            if qid not in qrels:
                qrels[qid] = {}
            qrels[qid][docid] = int(rel)
    return qrels


def search(searcher, queries, top_k=10, query_id_start=0):
    """search for queries and return results"""
    results = {}
    for i, query in enumerate(tqdm(queries, desc="Searching")):
        hits = searcher.search(query, k=top_k)
        results[str(i + query_id_start)] = [(hit.docid, hit.score) for hit in hits]
    return results


def compute_ndcg(results, qrels, k=10):
    """compute nDCG@k"""
    def dcg(relevances):
        """compute DCG@k"""
        # return sum((2 ** rel - 1) / np.log2(i + 2) for i, rel in enumerate(relevances[:k]))
        dcg_simple = sum(rel / np.log2(i + 2) for i, rel in enumerate(relevances[:k]))
        return dcg_simple

    ndcg_scores = []
    for qid, query_results in results.items():
        if qid not in qrels:
            # print(f"Query {qid} not found in qrels")
            continue
        relevances_current = [qrels[qid].get(docid, 0) for docid, _ in query_results]
        idcg = dcg(sorted(qrels[qid].values(), reverse=True))
        if idcg == 0:
            print(f"IDCG is 0 for query {qid}")
            continue
        ndcg_scores.append(dcg(relevances_current) / idcg)

    if not ndcg_scores:
        print("No valid NDCG scores computed")
        return 0.0
    return np.mean(ndcg_scores)

def compute_precision(results, qrels, k=10):
    """compute precision@k"""
    precision_scores = []
    for qid, query_results in results.items():
        if qid not in qrels:
            continue
        relevances_current = [qrels[qid].get(docid, 0) for docid, _ in query_results]
        relevant_docs = [rel for rel in relevances_current if rel > 0]
        precision_scores.append(len(relevant_docs) / k)
    return np.mean(precision_scores)


def run_search(k, b, metric_type, save_results=False, debug=False, model="bm25", dataset="inaugural_speeches"):
    """main function for searching and evaluating using nDCG@10 or precision@10 
    metric_type and using the BM25, RM3 Pseudo-Relevance, or Query Likelihood with Dirichelet Smoothing models"""

    base_dir = f"data/{dataset}"
    query_id_start = {
        "apnews": 0,
        "cranfield": 1,
        "new_faculty": 1,
        "inaugural_speeches" : 0
    }[dataset]

    # Paths to the raw corpus, queries, and relevance label files
    corpus_file = os.path.join(base_dir, f"{dataset}.dat")
    query_file = os.path.join(base_dir, f"{dataset}-queries.txt")
    qrels_file = os.path.join(base_dir, f"{dataset}-qrels.txt")
    # processed_corpus_dir = os.path.join(base_dir, "corpus")

    # Directories where the processed corpus and index will be stored for toolkit
    processed_corpus_dir = f"processed_corpus/{dataset}"
    os.makedirs(processed_corpus_dir, exist_ok=True)
    index_dir = f"indexes/{dataset}"

    # # Preprocess corpus
    # if not os.path.exists(processed_corpus_dir) or not os.listdir(processed_corpus_dir):
    #     preprocess_corpus(corpus_file, processed_corpus_dir)
    # else:
    #     print(f"Preprocessed corpus already exists at {processed_corpus_dir}. Skipping preprocessing.")

    # Build index
    build_index(processed_corpus_dir, index_dir)

    # Load queries and qrels
    queries = load_queries(query_file)
    qrels = load_qrels(qrels_file)

    # Debug info
    if debug:
        print(f"Number of queries: {len(queries)}")
        print(f"Number of qrels: {len(qrels)}")
        print(f"Sample qrel: {list(qrels.items())[0] if qrels else 'No qrels'}")

    # Search
    searcher = LuceneSearcher(index_dir)

    match model:
        case "bm25":
            searcher.set_bm25(k1=k, b=b)
        case "rm3-pseudo-relevance":
            searcher.set_rm3() # use default hyperparameters
            # fb_terms=10, fb_docs=10, original_query_weight=float(0.5)
        case "query-likelihood":
            searcher.set_qld() # use default hyperparameters for query likelihood with Dirichlet smoothing 
            # mu = 1000

    results = search(searcher, queries, query_id_start=query_id_start)

    # Debug info
    if debug:
        print(f"Number of results: {len(results)}")
        print(f"Sample result: {list(results.items())[0] if results else 'No results'}")

    # Evaluate
    topk = 10
    if metric_type == "ndcg":
        metric = compute_ndcg(results, qrels, k=topk)
        print(f"NDCG@{topk}: {metric:.4f}")
    elif metric_type == "precision":
        metric = compute_precision(results, qrels, k=topk)
        print(f"Precision@{topk}: {metric:.4f}")

    # Save results
    if save_results:
        with open(f"results_{dataset}.json", "w") as f:
            json.dump({"results": results, metric_type: metric}, f, indent=2)

    return metric

def calculate_sustainability_metrics(kilojoules_used=20, job_time_in_seconds=5):
    """Calculate and print various sustainability metrics."""
    jsc_value_min, jsc_value_max = calculateJobSustainabilityCost(carbon_mix, kilojoules_used)
    print(f"JSC Values")
    print(f"Min: {jsc_value_min:.2f} gCO2e")
    print(f"Max: {jsc_value_max:.2f} gCO2e")

    asc_value_min = amortizedSustainabilityCost(jsc_value_min, 5, 3, 10000)
    asc_value_max = amortizedSustainabilityCost(jsc_value_max, 5, 3, 10000)
    print(f"\nASC Values")
    print(f"Min: {asc_value_min:.2f} gCO2e")
    print(f"Max: {asc_value_max:.2f} gCO2e")

    scr_value_min = sustainability_cost_rate_per_second(jsc_value_min, job_time_in_seconds)
    scr_value_max = sustainability_cost_rate_per_second(jsc_value_max, job_time_in_seconds)

    print(f"\nSCR Values")
    print(f"Min: {scr_value_min:.2f} gCO2e/s")
    print(f"Max: {scr_value_max:.2f} gCO2e/s")

if __name__ == "__main__":
    # Run search for inaugural speeches dataset
    k = 1.2  # Default k1 value for BM25
    b = 0.75  # Default b value for BM25
    machineWatage = 800 #watts
    
    # Run search with BM25 model and compute NDCG@10
    start_time = time.time()
    ndcg_score = run_search(
        k=k,
        b=b,
        metric_type="ndcg",
        save_results=True,
        debug=True,
        model="tf-idf",
        dataset="inaugural_speeches"
    ) 

    end_time = time.time()
    total_time = end_time - start_time
    print(f"TF-IDF total time taken: {total_time:.2f} seconds")
    joulesUsed = int(total_time * machineWatage) #force to integer
    calculate_sustainability_metrics(kilojoules_used=joulesUsed, job_time_in_seconds=total_time)


    start_time = time.time()
    
    # Run search with BM25 model and compute NDCG@10
    ndcg_score = run_search(
        k=k,
        b=b,
        metric_type="ndcg",
        save_results=True,
        debug=True,
        model="bm25",
        dataset="inaugural_speeches"
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"BM25 total time taken: {total_time:.2f} seconds")

    # Calculate sustainability metrics
    joulesUsed = int(total_time * machineWatage) #force to integer
    calculate_sustainability_metrics(kilojoules_used=joulesUsed, job_time_in_seconds=total_time)


