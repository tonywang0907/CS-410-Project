
all:
	generateIndexInput
	generateQueries
	run
run:
	python3 main.py

generateIndexInput:
	./data/convert.bash
	python3 -m pyserini.index.lucene \
  --input ./data/inaugural_speeches/converted/ \
  --index indexes/inaugural_speeches \
  --generator DefaultLuceneDocumentGenerator \
  --threads 1

generateQueries:
	python3 generateQueries.py

clean:
	rm ./data/inaugural_speeches/converted/*.json
	rm ./indexes/inaugural_speeches/_*
	rm ./data/inaugural_speeches/inaugural_speeches-queries.txt