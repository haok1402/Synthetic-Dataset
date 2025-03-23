#!/bin/bash
# This script extracts token processing speeds from log files and calculates the median input and output token rates.
# It was generated with the assistance of GPT-4.

# Ensure a log directory is provided
if [[ -z "$1" ]]; then
    echo "Usage: $0 <log_directory>"
    exit 1
fi

log_dir="$1"

# Arrays to store token speeds
input_speeds=()
output_speeds=()

# Extract token speeds from log files
for file in "$log_dir"/*.log; do
    [[ -e "$file" ]] || continue  # Skip if no log files present

    while IFS= read -r line; do
        if [[ $line =~ input:\ ([0-9]+\.[0-9]+)\ toks/s,\ output:\ ([0-9]+\.[0-9]+)\ toks/s ]]; then
            input_speeds+=("${BASH_REMATCH[1]}")
            output_speeds+=("${BASH_REMATCH[2]}")
        fi
    done < "$file"
done

# Function to calculate median
calculate_median() {
    local -a arr=("$@")
    local len=${#arr[@]}

    if (( len == 0 )); then
        echo "N/A"
        return
    fi

    # Sort array and calculate median
    sorted=($(printf "%s\n" "${arr[@]}" | sort -n))
    local mid=$((len / 2))

    if (( len % 2 == 1 )); then
        echo "${sorted[mid]}"
    else
        echo "$(awk "BEGIN {print (${sorted[mid-1]} + ${sorted[mid]}) / 2}")"
    fi
}

# Compute and display median values
median_input=$(calculate_median "${input_speeds[@]}")
median_output=$(calculate_median "${output_speeds[@]}")

echo "Median input token speed: $median_input toks/s"
echo "Median output token speed: $median_output toks/s"
