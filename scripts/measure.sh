#!/bin/bash
# This script extracts token processing speeds from log files and calculates the average input and output token rates.
# This script was generated with the assistance of GPT-4.

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

# Function to calculate average
calculate_average() {
    local -a arr=("$@")
    local len=${#arr[@]}

    if (( len == 0 )); then
        echo "N/A"
        return
    fi

    awk '{sum += $1} END {print sum / NR}' <<< "$(printf "%s\n" "${arr[@]}")"
}

# Compute average values
average_input=$(calculate_average "${input_speeds[@]}")
average_output=$(calculate_average "${output_speeds[@]}")

# Display results
echo "Average input token speed: $average_input toks/s"
echo "Average output token speed: $average_output toks/s"
