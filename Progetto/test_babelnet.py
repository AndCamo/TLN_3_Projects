import requests
import json
import deepl
import pandas as pd
import dotenv

BABELNET_API_KEY = dotenv.get_key(".env", "BABELNET_API_KEY1")
DEEPL_API_KEY = dotenv.get_key(".env", "DEEPL_API_KEY")

translator = deepl.Translator(DEEPL_API_KEY)

def get_synset_ids(lemma, search_lang, target_lang = None):
    url = "https://babelnet.io/v9/getSynsetIds"

    souce_mapping = {
        "IT": ["OMWN_IT", "WIKI"],
        "EN": ["WN", "WIKI"],
        "FR": ["OMWN_FR", "WIKI"],
        "ES": ["MCR_ES", "WIKI"],
    }

    params = {
        "lemma": lemma,
        "searchLang": search_lang,
        "target_lang": target_lang,
        "key": BABELNET_API_KEY,
        "source": souce_mapping[search_lang]
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Errore nella richiesta: {response.status_code}, {response.text}")

    data = response.json()

    result = []

    for synset in data:
        result.append(synset["id"])

    return result

def get_synset_glosses(synset_id, lang):
    url = "https://babelnet.io/v9/getSynset"

    params = {
        "id": synset_id,
        "targetLang": lang,
        "key": BABELNET_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Errore nella richiesta: {response.status_code}, {response.text}")

    data = response.json()
    glosses = data["glosses"]

    return glosses

def ambiguity_reduction_score(synsets_x, synsets_y):
    """
    synsets_x: list of synset ids for the term X in L1
    synsets_y: list of synset ids for the term Y in L2
    """

    synsets_x_set = set(synsets_x)
    synsets_y_set = set(synsets_y)

    if (len(synsets_x) + len(synsets_y)) == 0:
        return 0

    synsets_x_y_set = synsets_x_set.intersection(synsets_y_set)

    ambiguity_reduction = ((len(synsets_x) + len(synsets_y) - 2 * len(synsets_x_y_set))
                           / (len(synsets_x) + len(synsets_y)))

    return ambiguity_reduction


def get_all_pseudoword(lemma):
    search_lang = "EN"
    languages = ["IT", "FR", "ES"]

    # initialize the synsets dictionary with the initial lemma
    synsets = {tuple([lemma, search_lang]): get_synset_ids(lemma, search_lang=search_lang)}

    for lang in languages:
        translated_lemma = translator.translate_text(lemma, target_lang=lang, source_lang="EN")
        synsets[tuple([translated_lemma.text, lang])] = get_synset_ids(translated_lemma.text, search_lang=lang)

    pseudowords = {}

    for lemma1, synset_ids1 in synsets.items():
        for lemma2, synset_ids2 in synsets.items():
            if lemma1 != lemma2:

                pseudoword = f"{lemma1[0]}-{lemma2[0]}"
                check_pseudoword = f"{lemma2[0]}-{lemma1[0]}"

                if check_pseudoword not in pseudowords:
                    synsets_intersection = list(set(synset_ids1).intersection(synset_ids2))
                    if len(synsets_intersection) == 0:
                        ambiguity_reduction = -1
                    else:
                        ambiguity_reduction = ambiguity_reduction_score(synset_ids1, synset_ids2)

                    pseudowords[pseudoword] = {
                        "ambiguity_reduction": ambiguity_reduction,
                        "L1": lemma1[1],
                        "L2": lemma2[1],
                        "|synsets_L1|": len(synset_ids1),
                        "|synsets_L2|": len(synset_ids2),
                        "|synsets_L1_L2|": len(synsets_intersection),
                        "synsets_intersection": synsets_intersection
                    }

    return pseudowords

def get_best_pseudoword(lemma):
    all_pseudowords = get_all_pseudoword(lemma)
    best_pseudoword = max(all_pseudowords, key=lambda x: all_pseudowords[x]["ambiguity_reduction"])

    result = {
        "pseudoword": best_pseudoword
    }
    result.update(all_pseudowords[best_pseudoword])

    return result

def save_pseudowords(pseudowords):


    data_list = []
    pseudoword_list = []

    for pseudoword, data in pseudowords.items():
        data_list.append(data)
        pseudoword_list.append(pseudoword)

    dataframe = pd.DataFrame(data_list, index=pseudoword_list)
    dataframe.to_csv("pseudowords.csv")



lemmas = ["active", "bad", "big", "bound", "drag", "drift", "exchange", "extend", "fair", "feel", "fix", "home", "job", "leave", "out", "puff", "range", "register", "regular", "scratch", "shock", "slack", "spike", "squeeze", "string", "take in", "train", "trim", "upset", "walk", "wild", "yield"]

size = len(lemmas)
results = []

for lemma in lemmas:
    print(f"{lemmas.index(lemma) + 1}/{size}")
    pseudoword = get_best_pseudoword(lemma)
    results.append(pseudoword)

dataframe = pd.DataFrame(results, index=lemmas)
dataframe.to_csv("17_meanings_pseudowords.csv", index=False)



