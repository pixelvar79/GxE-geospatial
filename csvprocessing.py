import pandas as pd

# Read the CSV file
# Read the CSV file
df = pd.read_csv('../data/ref_join/IL/1row.csv')
print(df.head())
# Create an empty DataFrame to store the replicated data
df_replicated = pd.DataFrame()

# Initialize id counter
id_counter = 0

# Iterate over unique plot_row values
for j, row in enumerate(df['Plot_row'].unique(), start=1):
    # Iterate over the range 1-8 and create new rows
    for i, index in enumerate(range(1, 9)):
        # Filter original DataFrame based on the plot_row value
        filtered_df = df[df['Plot_row'] == row].copy().reset_index(drop=True)
        # Assign new columns and id
        #filtered_df.insert(0, 'Plot_row2', j)
        id_counter += 1
        filtered_df.insert(0, 'id', id_counter)
        filtered_df.insert(1,'Plot_row2', index)
        # Concatenate the result to df_replicated
        df_replicated = pd.concat([df_replicated, filtered_df], ignore_index=True)

# Sort the DataFrame by the 'id' column
df_replicated = df_replicated.sort_values(by='id')

# Save the modified DataFrame to a new CSV file
df_replicated.to_csv('../data/ref_join/IL/1row1.csv', index=False, sep=',')