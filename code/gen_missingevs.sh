#!/bin/bash

# Define the base directory
BASE_DIR="/ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/EVfiles"

# Define the list of files to be created
FILES=(
    "run-1_computer_non-face.txt" "run-1_event_friend_punish.txt" "run-1_friend_face.txt"
    "run-2_event_computer_reward.txt" "run-2_event_stranger_punish.txt" "run-1_event_computer_neutral.txt"
    "run-1_event_friend_reward.txt" "run-1_stranger_face.txt" "run-2_computer_non-face.txt"
    "run-2_event_friend_punish.txt" "run-2_event_stranger_reward.txt" "run-1_event_computer_punish.txt"
    "run-1_event_stranger_neutral.txt" "run-1_event_computer_reward.txt" "run-1_event_stranger_punish.txt"
    "run-2_event_computer_neutral.txt" "run-2_event_friend_reward.txt" "run-2_friend_face.txt"
    "run-2_event_computer_punish.txt" "run-2_event_stranger_neutral.txt" "run-2_stranger_face.txt"
)

# Iterate through each subject directory with numeric IDs
for SUB_DIR in "$BASE_DIR"/sub-[0-9]*/sharedreward/; do
    # Check if the directory exists
    if [ -d "$SUB_DIR" ]; then
        # Iterate through each file
        for FILE in "${FILES[@]}"; do
            # Define the full path to the file
            FILE_PATH="$SUB_DIR/$FILE"
            # Check if the file already exists
            if [ ! -f "$FILE_PATH" ]; then
                # Create the file with the contents "0 0 0"
                echo "0 0 0" > "$FILE_PATH"
                echo "Created $FILE_PATH"
            else
                echo "$FILE_PATH already exists, skipping."
            fi
        done
    else
        echo "Directory $SUB_DIR does not exist, skipping."
    fi
done
