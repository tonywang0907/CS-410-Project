.PHONY: all run generateIndexInput generateQueries clean

all: generateIndexInput generateQueries run

run:
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

clean:
	rm -f ./data/inaugural_speeches/converted/*.json || true
	rm -f ./indexes/inaugural_speeches/* || true
	rm -f ./data/inaugural_speeches/inaugural_speeches-queries.txt || true