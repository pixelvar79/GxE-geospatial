
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import seaborn as sns  # Import seaborn for color palette


# Define the input and output paths
input_path = "../data/tabular_outputs"
output_path = "../data/figures_temporal_genotypes_LA"

output_path = os.path.join(output_path)
os.makedirs(output_path, exist_ok=True)
# Create an empty list to store DataFrames for all states
all_states_dfs = []
# Iterate through AL, LA, MS, IL subfolders
#for state_folder in ["AL", "LA", "MS", "IL"]:
    
for state_folder in ["LA","MS"]:
    state_path = os.path.join(input_path, state_folder)

    # Create output subfolder for the state in figures directory
    #state_output_path = os.path.join(output_path, state_folder)
    #os.makedirs(state_output_path, exist_ok=True)

    # Collect DataFrames for the current state
    state_dfs = []

    # Iterate through subfolders inside each state folder
    for subfolder in os.listdir(state_path):
        subfolder_path = os.path.join(state_path, subfolder)

        # Collect DataFrames for the current subfolder
        subfolder_dfs = []

        # Use the first string of subfolder name for matching
        ref_join_name = subfolder.split('_')[0]

        # Load CSV file from ref_join subfolder based on matching name
        ref_join_folder = "../data/ref_join"
        ref_join_path = os.path.join(ref_join_folder, state_folder, f"{ref_join_name}.csv")
        print(ref_join_path)
        encoding = 'latin1'

# Assuming ref_join_path is the path to your CSV file
        ref_join_df = pd.read_csv(ref_join_path, encoding=encoding)
        #ref_join_df = pd.read_csv(ref_join_path)
        #print(ref_join_df)

        # Iterate through CSV files in the current subfolder
        for csv_file in os.listdir(subfolder_path):
            csv_path = os.path.join(subfolder_path, csv_file)
            #print(csv_path)
            # Use the first string of CSV file name for matching
            csv_name = csv_file.split('_')[0]

            # Read CSV file into a DataFrame
            df = pd.read_csv(csv_path)

            # Filter data based on the 'order' column (selecting orders 1-4)
            #df_filtered = df[df['order'].between(1, 4)]
            # Replace -66666 with NaN
            df.replace(-66666, np.nan, inplace=True)
            
            # Join with the corresponding ref_join DataFrame based on 'order' column
            #df = pd.merge(df, ref_join_df, on='order', how='inner')
            df = pd.merge(df, ref_join_df, on='order', how='inner', suffixes=('', '_ref_join'))

            print(df.head())
            
            subfolder_dfs.append(df)

        # Concatenate DataFrames within the current subfolder along rows
        concatenated_subfolder_df = pd.concat(subfolder_dfs, ignore_index=True)

        # Append the concatenated DataFrame to the list for the current state
        state_dfs.append(concatenated_subfolder_df)

    # Concatenate DataFrames from all subfolders within the current state along rows
    concatenated_state_df = pd.concat(state_dfs, ignore_index=True)
    
    # Append the concatenated state DataFrame to the list for all states
    all_states_dfs.append(concatenated_state_df)

# Concatenate DataFrames for all states along rows
all_data_df = pd.concat(all_states_dfs, ignore_index=True)

# Drop duplicated columns based on column names
all_data_df = all_data_df.loc[:, ~all_data_df.columns.duplicated()]

pd.set_option('display.max_columns', None)
#print(all_data_df.head(100))
#print(all_data_df.shape)

# Specify the path where you want to save the CSV file
output_csv_path = "../data/figures_temporal_genotypes_LA/output_file_locations.csv"

# Save the DataFrame to a CSV file
all_data_df.to_csv(output_csv_path, index=False)

# print(all_data_df)

# Group by 'Accession' only
grouped_all_data_df = all_data_df.groupby(['Accession'])

# Iterate through groups
for accession, group_df in grouped_all_data_df:
    # Skip accessions that are present in only one location
    if len(group_df['Location'].unique()) <= 1:
        continue

    # Order by 'Date_julian' column
    ordered_group_df = group_df.sort_values(by='Date_julian')

    # Extract the first string of the first column (assuming the first column name is 'First_Column')
    first_string = ordered_group_df.iloc[0, 0].split('_')[0]

    # Set up seaborn color palette for locations
    colors = sns.color_palette("husl", len(ordered_group_df['Location'].unique()))

    # Iterate over each column starting from the 6th column (index 5)
    for col_idx in range(5, 38):
        column_name = ordered_group_df.columns[col_idx]

        # Convert the column to numeric values, handling non-numeric values by converting them to NaN
        ordered_group_df[column_name] = pd.to_numeric(ordered_group_df[column_name], errors='coerce')

        # Plot figure for the current column
        plt.figure(figsize=(10, 6))

        # Iterate through unique 'Location' values and plot corresponding mean and sd
        for loc_idx, location_val in enumerate(ordered_group_df['Location'].unique()):
            location_rows = ordered_group_df[ordered_group_df['Location'] == location_val]

            # Calculate mean and standard deviation for each location
            mean_values = location_rows.groupby('Date_julian')[column_name].mean()
            std_values = location_rows.groupby('Date_julian')[column_name].std()

            # Plot mean line
            plt.plot(mean_values.index, mean_values, label=f"{location_val}", linestyle='--', color=colors[loc_idx])

            # Add shaded envelope around the mean line using standard deviation
            plt.fill_between(mean_values.index, mean_values - std_values, mean_values + std_values, alpha=0.2, color=colors[loc_idx])

        plt.xlabel("Date_julian")
        plt.ylabel(column_name)
        plt.legend()
        plt.title(f"{first_string} - Accession {accession} - {column_name}")

        # Save the figure in the folder for the current accession
        output_path = os.path.join('../data/figures_temporal_genotypes_LA/2locations_LA', f"accession_{accession}")
        os.makedirs(output_path, exist_ok=True)
        figure_name = f"accession_{accession}_{column_name}.png"
        figure_path = os.path.join(output_path, figure_name)
        plt.savefig(figure_path)
        plt.close()

