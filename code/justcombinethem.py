import pandas as pd

# Define the paths to the files
combined_logs_path = '/ZPOOL/data/projects/sharedreward-aging/code/combined_logs-edited.csv'
participants_rf1_path = '/ZPOOL/data/projects/sharedreward-aging/ds003745/participants-rf1.tsv'
participants_srndna_path = '/ZPOOL/data/projects/sharedreward-aging/ds003745/participants-srndna.tsv'

# Read the combined logs dataframe
combined_df = pd.read_csv(combined_logs_path)

# Read the participant files into dataframes
participants_rf1_df = pd.read_csv(participants_rf1_path, sep='\t')
participants_srndna_df = pd.read_csv(participants_srndna_path, sep='\t')

# Combine the participant dataframes into one
participants_df = pd.concat([participants_rf1_df, participants_srndna_df], ignore_index=True)

# Ensure sub and participant_id are of the same type
combined_df['sub'] = combined_df['sub'].astype(str)
participants_df['participant_id'] = participants_df['participant_id'].astype(str)

# Remove the 'sub-' prefix from the participant_id column
participants_df['participant_id'] = participants_df['participant_id'].str.replace('sub-', '')

# Merge the combined dataframe with the participants dataframe on the 'sub' column
merged_df = combined_df.merge(participants_df[['participant_id', 'age']], left_on='sub', right_on='participant_id', how='left')

# Drop the redundant 'participant_id' column
merged_df.drop(columns=['participant_id'], inplace=True)

# Print the shape of the combined dataframe
print("Shape of the combined dataframe:", merged_df.shape)

# Print the entire combined dataframe
print("Combined dataframe with age information:")
print(merged_df)

# Output the combined dataframe to a new CSV file (optional)
new_file_path = '/ZPOOL/data/projects/sharedreward-aging/code/combined_logs_with_age.csv'
merged_df.to_csv(new_file_path, index=False)
print(f"Combined dataframe with age information has been saved to {new_file_path}")
