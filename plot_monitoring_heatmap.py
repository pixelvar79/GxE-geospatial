# import os
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

# # Define the input and output paths
# input_path = "../data/tabular_outputs"
# output_path = "../data/figure_heatmap"

# # Iterate through AL, LA, MS, IL subfolders
# for state_folder in ["AL", "LA", "MS", "IL"]:
#     state_path = os.path.join(input_path, state_folder)

#     # Create output subfolder for the state in figures directory
#     state_output_path = os.path.join(output_path, state_folder)
#     os.makedirs(state_output_path, exist_ok=True)

#     # Collect DataFrames for the current state
#     state_dfs = []

#     # Iterate through subfolders inside each state folder
#     for subfolder in os.listdir(state_path):
#         subfolder_path = os.path.join(state_path, subfolder)

#         # Collect DataFrames for the current subfolder
#         subfolder_dfs = []
#         for csv_file in os.listdir(subfolder_path):
#             csv_path = os.path.join(subfolder_path, csv_file)
#             df = pd.read_csv(csv_path)

#             # Replace -66666 with NaN
#             df.replace(-66666, np.nan, inplace=True)
#             subfolder_dfs.append(df)

#         # Concatenate DataFrames within the current subfolder along rows
#         concatenated_subfolder_df = pd.concat(subfolder_dfs, ignore_index=True)

#         # Append the concatenated DataFrame to the list for the current state
#         state_dfs.append(concatenated_subfolder_df)

#     # Concatenate DataFrames from all subfolders within the current state along rows
#     concatenated_state_df = pd.concat(state_dfs, ignore_index=True)

#     # Group by the first string in the 'TIF_Name' column
#     grouped_state_df = concatenated_state_df.groupby(concatenated_state_df['TIF_Name'].str.split('_').str[0])
    
#     # Create a dictionary to store unique Julian_date values for each group
#     unique_julian_dates_by_group = {}

#     # Iterate through groups
#     for group_name, group_df in grouped_state_df:
#         # Obtain unique Julian_date values for the current group
#         print(group_name)
#         unique_julian_dates = group_df['Date_julian'].unique()

#         # Store the unique Julian_date values in the dictionary
#         unique_julian_dates_by_group[group_name] = unique_julian_dates

#     # Print or further process the unique Julian_date values for each group
#     for group_name, unique_julian_dates in unique_julian_dates_by_group.items():
#         print(f"Group: {group_name}, Unique Julian Dates: {unique_julian_dates}")


#     # Create a dictionary to store counts for each group
#     counts_by_group = {}

#     # Iterate through groups
# for group_name, group_df in grouped_state_df:
#     # Order by 'Date_julian' column
#     ordered_group_df = group_df.sort_values(by='Date_julian')

#     # Convert 'Date_julian' column to numeric
#     ordered_group_df['Date_julian'] = pd.to_numeric(ordered_group_df['Date_julian'], errors='coerce')

#     # Count Julian date events per month
#     counts_per_month = ordered_group_df.groupby(ordered_group_df['Date_julian'].dt.month)['Date_julian'].count()

#     # Store the counts in the dictionary
#     counts_by_group[group_name] = counts_per_month

#     # Create a heatmap for the ordered group
#     plt.figure(figsize=(12, 8))
#     sns.heatmap(counts_per_month.reset_index().pivot(index='Date_julian', columns='month_name', values='Date_julian'),
#                 annot=True, cmap="YlGnBu", fmt='g', cbar_kws={'label': 'Count of Julian Date Events'})
#     plt.title(f'Heatmap for {state_folder} - Group {group_name}')
#     plt.xlabel('Month')
#     plt.ylabel('UAV dataset count per month')
#     plt.savefig(os.path.join(state_output_path, f'heatmap_{group_name}.png'))
#     plt.close()

# Iterate through groups
# Iterate through groups
# Iterate through groups
# for group_name, group_df in grouped_state_df:
#     # Order by 'Date' column
#     ordered_group_df = group_df.sort_values(by='Date')

#     # Convert 'Date' column to datetime format
#     ordered_group_df['Date'] = pd.to_datetime(ordered_group_df['Date'], errors='coerce')

#     # Check if the conversion was successful
#     if pd.api.types.is_datetime64_any_dtype(ordered_group_df['Date']):
#         # Extract month name from the 'Date' column
#         ordered_group_df['month_name'] = ordered_group_df['Date'].dt.strftime('%B')

#         # Count unique date events for each group and month
#         counts_per_group_month = ordered_group_df.groupby(['TIF_Name', 'month_name']).size().reset_index(name='count')

#         # Store the counts in the dictionary
#         counts_by_group[group_name] = counts_per_group_month

#         # Create a heatmap for the ordered group
#         plt.figure(figsize=(12, 8))
#         sns.heatmap(counts_per_group_month.pivot(index='TIF_Name', columns='month_name', values='count'),
#                     annot=True, cmap="YlGnBu", fmt='g', cbar_kws={'label': 'Count of Unique Date Events'})
#         plt.title(f'Heatmap for {state_folder} - Group {group_name}')
#         plt.xlabel('Month')
#         plt.ylabel('Count of Unique Date Events')
#         plt.savefig(os.path.join(state_output_path, f'heatmap_{group_name}.png'))
#         plt.close()
#     else:
#         print(f"Conversion to datetime failed for Group {group_name}")

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Define the input and output paths
input_path = "../data/tabular_outputs"
output_path = "../data/figures_heatmaps"

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

    # Convert 'Date' column to datetime
    concatenated_state_df['Date'] = pd.to_datetime(concatenated_state_df['Date'], errors='coerce')

    # Extract 'month_name' from the 'Date' column
    concatenated_state_df['month_name'] = concatenated_state_df['Date'].dt.strftime('%B')

    # Use the common first string in 'TIF_Name' for grouping
    concatenated_state_df['common_first_string'] = concatenated_state_df['TIF_Name'].str.split('_').str[0]
    grouped_state_df = concatenated_state_df.groupby(['common_first_string', 'month_name'])

    # Count unique date events for each group and month
    counts_per_group_month = grouped_state_df['Date'].nunique().reset_index(name='count')

    # Order the months in a natural sequence
    months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    counts_per_group_month['month_name'] = pd.Categorical(counts_per_group_month['month_name'], categories=months_order, ordered=True)

    # Sort the DataFrame by the ordered month categories
    counts_per_group_month = counts_per_group_month.sort_values(by='month_name')

    # Create a heatmap for the ordered group
    plt.figure(figsize=(12, 8))
    sns.heatmap(counts_per_group_month.pivot(index='common_first_string', columns='month_name', values='count'),
                annot=True, cmap="YlGnBu", fmt='g', cbar_kws={'label': 'Count of Unique Date Events'})
    plt.title(f'Heatmap for {state_folder}')
    plt.xlabel('Month')
    plt.ylabel('Count of Unique Date Events')
    plt.savefig(os.path.join(state_output_path, f'heatmap.png'))
    plt.close()
