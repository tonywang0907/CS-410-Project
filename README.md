# CS-410-Project


The original datasets were not in a JSON format, so a small bash script was used to convert these documents to JSON for ingestion into the pyserini indexer
   -> data/inaugural_speeches/convert.bash : extracts the contents of the files from the data/original folder, converts them to JSON, and outputs that to file in data/inaugural_speeches/converted

To index the data in its current folder configuration:
   ```python -m pyserini.index.lucene -collection JsonCollection -input ./data/inaugural_speeches/converted/  -index ./indexes/inaugural_speeches/ -generator DefaultLuceneDocumentGenerator```
This produces an index for main.py to use.

To generate the queries, you can use the generate_queries.py file by calling ```python3 generateQueries.py```. NOTE THAT THIS TAKES A LONG TIME. 
   -> There is a sample file already generated (data/inaugaral_speeches/inaugaral_speeches-queries.txt)

# First, build the index as mentioned in README
```python -m pyserini.index.lucene -collection JsonCollection -input ./data/inaugural_speeches/converted/ -index ./indexes/inaugural_speeches/ -generator DefaultLuceneDocumentGenerator```

# Second, run main.py to evaluate the search
```python main.py```