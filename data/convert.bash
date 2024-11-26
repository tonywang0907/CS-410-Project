#!/bin/bash

# Ensure the 'converted' directory exists
mkdir -p ./converted

# Loop through all the text files in the current directory
for file in original/*.txt; do
  # Extract the filename without the extension
  filename=$(basename "$file" .txt)

  # Read the contents of the file
  contents=$(<"$file")

  # Remove all quotation marks and replace all whitespace characters with a single space
  stripped_contents=$(echo "$contents" | tr -d '"' | tr -s '[:space:]' ' ')

  # Create the JSON structure
  json="{\"id\": \"$filename\", \"contents\": \"$stripped_contents\"}"

  # Write the JSON to a new file in the 'converted' directory
  echo "$json" > "./converted/$filename.json"
done

echo "Conversion complete. JSON files are in the 'converted' folder."
