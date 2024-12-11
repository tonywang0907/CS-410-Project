.PHONY: all run generateIndexInput generateQueries clean

all: generateIndexInput generateQueries generate_qrels run

run: generateIndexInput generate_qrels
	python3 main.py

generateIndexInput:
	bash "./data/convert.bash"
	python3 -m pyserini.index.lucene \
		--collection JsonCollection \
		--input "./data/inaugural_speeches/converted/" \
		--index "indexes/inaugural_speeches" \
		--generator DefaultLuceneDocumentGenerator \
		--threads 1 \
		--storePositions --storeDocvectors --storeRaw

generateQueries:
	python3 generate_queries.py

generate_qrels:
	python3 generate_qrels.py

clean:
	rm -f ./data/inaugural_speeches/converted/*.json || true
	rm -f -rf ./indexes/* || true
	rm ./data/indexes/inaugural_speeches/segments* || true
	rm -f ./data/inaugural_speeches/inaugural_speeches-queries.txt || true
