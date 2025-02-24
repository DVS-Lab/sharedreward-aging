import json
import glob
import re
import csv

def extract_flip_angles(base_path, output_csv):
    data = []
    
    # Define the path pattern to match all subject directories
    subject_dirs = glob.glob(f"{base_path}/sub-*")
    
    for sub_dir in subject_dirs:
        # Extract subject number
        match = re.search(r'sub-(\d+)', sub_dir)
        if match:
            sub = match.group(1)
            sub_int = int(sub)
            
            # Determine correct file path based on sub length
            if len(sub) == 3:
                json_file = f"{sub_dir}/func/sub-{sub}_task-sharedreward_run-01_bold.json"
            elif len(sub) == 5:
                json_file = f"{sub_dir}/func/sub-{sub}_task-sharedreward_run-1_echo-2_part-mag_bold.json"
            else:
                continue
            
            try:
                # Open and read JSON file
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                    flip_angle = json_data.get("FlipAngle")  # Get FlipAngle, None if not found
                    
                    if flip_angle is not None:
                        coded = 0 if flip_angle in [20, 76] else 1
                        data.append([sub, flip_angle, coded])
                    else:
                        print(f"Missing FlipAngle in: {json_file}")
            except FileNotFoundError:
                print(f"File not found: {json_file}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {json_file}")
    
    # Write to CSV if data is available
    if data:
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["sub", "flip", "coded"])  # Header
            writer.writerows(data)
        
        print(f"CSV file created: {output_csv}")
    else:
        print("No data found. CSV file not created.")

# Run the script
base_path = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging/bids"
output_csv = "flip-angles.csv"
extract_flip_angles(base_path, output_csv)

