#!/bin/bash

# Check if the input file exists
input_file="L3inputs.txt"
if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found."
    exit 1
fi

# Read file paths from the input file into an array
mapfile -t files < "$input_file"

# Loop through each file in the array
for file in "${files[@]}"
do
    # Run fslstats command on the current file
    echo "$file"
    fslstats "$file" -R

    # If you want to pause between commands, you can optionally add:
    # sleep 1  # Adjust sleep time as needed
done
