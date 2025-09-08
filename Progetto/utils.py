import os
import random

import pandas as pd
import math
import json

def merge_results(path):
    dataframes = []
    length = 0

    for file in os.listdir(path):
        if file.endswith(".csv"):
            file_path = os.path.join(path, file)
            df = pd.read_csv(file_path)

            print(f"Lunghezza del DataFrame {file}: {len(df)}")
            length += len(df)
            dataframes.append(df)


    df_unico = pd.concat(dataframes, ignore_index=True)

    print(f"Lunghezza totale dei DataFrame: {length}")

    df_unico.to_csv("./results/final_pseudoword_dictionary.csv", index=False)



results = pd.read_csv("./results/top_pseudowords_by_ambiguity_drop.csv")

cleaned_results = results[results["|synsets_L1_L2|"] != 0]

cleaned_results.describe().to_csv("./results/top_ambiguity_drop_stats.csv")

"""
# extract the top N rows
N = 100
top_n_results = results.nlargest(N, "ambiguity_drop")
top_n_results.to_csv("./results/top_pseudowords_by_ambiguity_drop.csv", index=False)
"""









