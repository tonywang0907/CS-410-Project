all: generateIndexInput generateQueries run
	echo "All done"
run:
	python3 main.py

generateIndexInput:
	./data/convert.bash
	python3 -m pyserini.index.lucene \
  --collection JsonCollection \
  --input ./data/inaugural_speeches/converted/ \
  --index indexes/inaugural_speeches \
  --generator DefaultLuceneDocumentGenerator \
  --threads 1

generateQueries:
	python3 generate_queries.py

clean:
	rm ./data/inaugural_speeches/converted/*.json
	rm -rf ./indexes/*
	rm ./data/indexes/inaugural_speeches/segments_*
	rm ./data/inaugural_speeches/inaugural_speeches-queries.txt
