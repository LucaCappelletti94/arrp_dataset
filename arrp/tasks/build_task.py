import pandas as pd
from typing import Dict, Tuple
import numpy as np
from ..utils import tqdm, balance, mkdir
from sklearn.model_selection import train_test_split
import os
from multiprocessing import cpu_count, Pool

@mkdir
def get_model_validation_path(path:str):
    return "{path}/model_validation".format(path=path)

@mkdir
def get_model_selection_path(path:str):
    return "{path}/model_selection".format(path=path)

@mkdir
def get_holdout_path(path:str, holdout:int):
    return "{path}/{holdout}".format(path=path, holdout=holdout)

@mkdir
def get_balancing_path(path:str, balancing:str):
    return "{path}/{balancing}".format(path=path, balancing=balancing)

def get_default_file_names():
    return [
        "cellular_variables_train", "cellular_variables_test", "nucleotides_sequences_train", "nucleotides_sequences_test", "classes_train", "classes_test"
    ]

def is_nucleotide_sequence_file(name:str):
    return name.startswith("nucleotides_sequences_")

def is_cached(path:str):
    return all([
        os.path.exists("{path}/{name}.csv".format(
            path=path,
            name=name
        )) for name in get_default_file_names()
    ])

def store_balance(path:str, headers, *dataset_split):
    for name, header, array in zip(get_default_file_names(), headers, dataset_split):
        if is_nucleotide_sequence_file(name):
            array = array.reshape(-1, 5)
        pd.DataFrame(array, columns=header).to_csv(
            "{path}/{name}.csv".format(path=path, name=name)
        )

def build_balance(job:Tuple):
    path, task, balance_settings, headers, dataset_split = job
    for balancing in [balancing for balancing, boolean in task["balancing"].items() if boolean]:
        balanced_path = get_balancing_path(path, balancing)
        if not is_cached(balanced_path):
            balanced = balance(
                *dataset_split,
                balance_callback=balancing, 
                positive_class="+".join(task["positive"]),
                negative_class="+".join(task["negative"]),
                settings=balance_settings
            )
            store_balance(balanced_path, headers, *balanced)

def build_task(path:str, task:Dict, balance_settings:Dict, holdouts:int, validation_split:float, test_split:float, cellular_variables:pd.DataFrame, nucleotides_sequences:pd.DataFrame, nucleotides_sequences_header, classes:pd.DataFrame)->Dict:
    """Build given task's holdouts and validation split for given target."""
    headers = cellular_variables.columns, cellular_variables.columns, nucleotides_sequences_header, nucleotides_sequences_header, classes.columns, classes.columns
    cellular_variables, nucleotides_sequences, classes = cellular_variables.values, nucleotides_sequences, classes.values
    dataset_split = cellular_variables_train, _, nucleotides_sequences_train, _, classes_train, _ = train_test_split(
        cellular_variables, nucleotides_sequences, classes, random_state=42, test_size=test_split
    )
    build_balance(get_model_validation_path(path), task, balance_settings, headers=headers, dataset_split=dataset_split)
    model_selection_path = get_model_selection_path(path)
    jobs = (
        get_holdout_path(model_selection_path, holdout), task, balance_settings, headers, (train_test_split(cellular_variables_train, nucleotides_sequences_train, classes_train, random_state=holdout, test_size=validation_split),)
        for holdout in range(holdouts)
    )
    with Pool(cpu_count) as p:
        list(tqdm(p.imap(build_balance, jobs), total=holdouts, desc="Holdouts"))