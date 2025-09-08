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


def ambiguity_drop_score(synsets_x, synsets_y, synsets_x_y):
    """
    synsets_x: list of synset ids for the term X in L1
    synsets_y: list of synset ids for the term Y in L2
    """





    if synsets_x == 0 or synsets_y == 0:
        return 0

    ambiguity_drop = 2 * (((synsets_x + synsets_y - 2 * synsets_x_y) * math.sqrt(synsets_x * synsets_y))
                     / math.pow(synsets_x + synsets_y, 2))

    return ambiguity_drop

"""results = pd.read_csv("./results/results.csv")

ambiguity_drops = []
for index, row in results.iterrows():
    synsets_x = row["|synsets_L1|"]
    synsets_y = row["|synsets_L2|"]
    synsets_x_y = row["|synsets_L1_L2|"]

    ambiguity_drop = ambiguity_drop_score(synsets_x, synsets_y, synsets_x_y)
    ambiguity_drops.append(ambiguity_drop)

# Inserisce la colonna "ambiguity_drop" alla posizione 2 (terza colonna)
results.insert(2, "ambiguity_drop", ambiguity_drops)

results.to_csv("./results/results_updated.csv", index=False)"""



path = "./results"
merge_results(path)







