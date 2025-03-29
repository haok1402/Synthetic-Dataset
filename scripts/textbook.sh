#!/bin/bash
# Transform the corpus into academic, textbook style.

main() {
    job1_id=$(sbatch scripts/modules/textbook_job1.sh | awk '{print $4}')
    job2_id=$(sbatch --dependency=afterok:$job1_id scripts/modules/textbook_job2.sh | awk '{print $4}')
    echo "Submitted jobs: $job1_id, $job2_id"
}

main
