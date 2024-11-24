import os
import sys
from transformers import pipeline
from transformers import BartTokenizer

# Load the summarization model and tokenizer from HuggingFace
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Define paths
input_folder = "data/inaugural_speeches/original/"
output_file = "data/inaugural_speeches/inaugural_speeches-queries.txt"

def chunk_document(document, max_length=1000):
    # Start with an empty list of chunks
    chunks = []
    start_index = 0  # Start at the beginning of the document
    
    while start_index < len(document):
        end_index = start_index + max_length
        
        if end_index > len(document):
            end_index = len(document)
        elif end_index < len(document):
            space_index = document.rfind(' ', start_index, end_index)
            if space_index != -1:  # Found a space
                end_index = space_index

        chunks.append(document[start_index:end_index].replace(".","").strip())
        start_index = end_index
    return chunks


# Open the output file for writing the queries
with open(output_file, 'w') as query_file:
    # Loop through all text files in the 'converted' folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            # Full path to the document
            file_path = os.path.join(input_folder, filename)
            
            # Read the content of the file
            with open(file_path, 'r') as f:
                document = f.read()
            #remove the president's name and year
            document = document.split("\t",3)[2]
            # Split the document into smaller chunks if it's too long
            chunks = chunk_document(document)

            # Generate summaries for each chunk and combine them
            summaries = []
            i = 0
            min_length = 25
            max_length = 50
            for chunk in chunks:
                print(f"Summarizing chunk {i} of document {filename}")
                # print(f"Len of chunk:{len(chunk)}")
                if (len(chunk) > max_length*2):
                    summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                else:
                    #for end of file chunks that are too small to summarize with min_length and max_length, 
                    #generate proportional values for the summary's min and max size
                    summary = summarizer(chunk, max_length=int(len(chunk)/2), min_length=int(len(chunk)/4), do_sample=False)
                summaries.append(str(summary[0]['summary_text']).reaplce(".","").strip())
                i+=1
            # Combine all chunk summaries into a single query (can also be improved with more complex logic)
            combined_query = " ".join(summaries)

            # Write the query to the output file, one query per line
            query_file.write(combined_query + "\n")

print(f"Queries have been generated and saved to {output_file}")
