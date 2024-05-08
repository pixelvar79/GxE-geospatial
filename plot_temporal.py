
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the input and output paths
input_path = "../data/tabular_outputs"
output_path = "../data/figures_temporal1"

# Iterate through AL, LA, MS, IL subfolders
for state_folder in ["AL", "LA", "MS", "IL"]:
    state_path = os.path.join(input_path, state_folder)

    # Create output subfolder for the state in figures directory
    state_output_path = os.path.join(output_path, state_folder)
    os.makedirs(state_output_path, exist_ok=True)

    # Collect DataFrames for the current state
    state_dfs = []

    # Iterate through subfolders inside each state folder
    for subfolder in os.listdir(state_path):
        subfolder_path = os.path.join(state_path, subfolder)

        # Collect DataFrames for the current subfolder
        subfolder_dfs = []
        for csv_file in os.listdir(subfolder_path):
            csv_path = os.path.join(subfolder_path, csv_file)
            df = pd.read_csv(csv_path)

            # Replace -66666 with NaN
            df.replace(-66666, np.nan, inplace=True)
            subfolder_dfs.append(df)

        # Concatenate DataFrames within the current subfolder along rows
        concatenated_subfolder_df = pd.concat(subfolder_dfs, ignore_index=True)

        # Append the concatenated DataFrame to the list for the current state
        state_dfs.append(concatenated_subfolder_df)

    # Concatenate DataFrames from all subfolders within the current state along rows
    concatenated_state_df = pd.concat(state_dfs, ignore_index=True)

    # Group by the first string in the 'TIF_Name' column
    grouped_state_df = concatenated_state_df.groupby(concatenated_state_df['TIF_Name'].str.split('_').str[0])

    #Iterate through groups
    # for group_name, group_df in grouped_state_df:
    #     # Order by 'Date_julian' column
    #     ordered_group_df = group_df.sort_values(by='Date_julian')

    #     # Iterate over each column starting from the 6th column (index 5)
    #     for col_idx in range(5, len(ordered_group_df.columns)):
    #         column_name = ordered_group_df.columns[col_idx]
            
    #         # Convert the column to numeric values, handling non-numeric values by converting them to NaN
    #         ordered_group_df[column_name] = pd.to_numeric(ordered_group_df[column_name], errors='coerce')

    #         # Calculate mean and standard deviation for the current column within the group
    #         mean_values = ordered_group_df.groupby('Date_julian')[column_name].mean()
    #         std_values = ordered_group_df.groupby('Date_julian')[column_name].std()
    #         print(f'mean values are: {mean_values}')
    #         print(f'sd values are: {std_values}')

    #         # Plot figure for the current column
    #         plt.figure(figsize=(10, 6))

    #         # Plot mean line
    #         plt.plot(mean_values.index, mean_values, label=f"Mean", linestyle='--', color='black')

    #         # Add shaded envelope around the mean line using standard deviation
    #         plt.fill_between(mean_values.index, mean_values - std_values, mean_values + std_values, alpha=0.2)

    #         plt.xlabel("Date_julian")
    #         plt.ylabel(column_name)
    #         plt.legend()
    #         # Hide the legend
    #         plt.legend().set_visible(False)
    #         plt.title(f"Plot for {state_folder}/{group_name} - Mean and SD of {column_name}, Ordered by Date_julian")

    #         # Save the figure in a subfolder named after the current column
    #         #column_output_path = os.path.join(state_output_path, subfolder, column_name)
    #         column_output_path = os.path.join(state_output_path, subfolder, column_name)
    #         os.makedirs(column_output_path, exist_ok=True)
    #         figure_name = f"{state_folder}_{group_name}_{column_name}_ordered_plot.png"
    #         figure_path = os.path.join(column_output_path, figure_name)
    #         plt.savefig(figure_path)
    #         plt.close()
            
    for group_name, group_df in grouped_state_df:
    # Order by 'Date_julian' column
        ordered_group_df = group_df.sort_values(by='Date_julian')

        # Iterate over each column starting from the 6th column (index 5)
        for col_idx in range(5, len(ordered_group_df.columns)):
            column_name = ordered_group_df.columns[col_idx]
            
            # Convert the column to numeric values, handling non-numeric values by converting them to NaN
            ordered_group_df[column_name] = pd.to_numeric(ordered_group_df[column_name], errors='coerce')

            # Plot figure for the current column
            plt.figure(figsize=(10, 6))

            #Plot all original row values
            #for index, row in ordered_group_df.iterrows():
            for idx, row in ordered_group_df.iterrows():
                # Plot the row values as a line without markers
                plt.plot(row['Date_julian'], row[column_name],marker='o', linestyle='-')

            plt.xlabel("Date_julian")
            plt.ylabel(column_name)
            plt.legend()
            # Hide the legend
            plt.legend().set_visible(False)
            plt.title(f"Plot for {state_folder}/{group_name} - {column_name} values, Ordered by Date_julian")

            # Save the figure in a subfolder named after the current column
            column_output_path = os.path.join(state_output_path, subfolder, column_name)
            os.makedirs(column_output_path, exist_ok=True)
            figure_name = f"{state_folder}_{group_name}_{column_name}_ordered_plot.png"
            figure_path = os.path.join(column_output_path, figure_name)
            plt.savefig(figure_path)
            plt.close()
            
            

