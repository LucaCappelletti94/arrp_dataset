from typing import List, Dict, Tuple
import pandas as pd
from .build_task import build_task
from ..utils import get_cell_lines, tqdm, mkdir

def load_cellular_variables(target:str, cell_line:str):
    return pd.read_csv(
        "{target}/data/{cell_line}.csv".format(
            target=target,
            cell_line=cell_line
        ), 
        index_col=0
    )

def load_nucleotides_sequences(target:str, cell_line:str):
    return pd.read_csv(
        "{target}/one_hot_encoded_expanded_regions/{cell_line}.csv".format(
            target=target,
            cell_line=cell_line,
            k=1,
        ), 
        index_col=0
    ).values.reshape(-1, 200, 5)

def load_classes(target:str, cell_line:str):
    return pd.read_csv(
        "{target}/one_hot_encoded_classes/{cell_line}.csv".format(
            target=target,
            cell_line=cell_line,
        ), 
        index_col=0
    )

def drop_unknown(cellular_variables:pd.DataFrame, nucleotides_sequences:pd.DataFrame, classes:pd.DataFrame)->Tuple:
    """Remove datapoints labeles as UK."""
    unknown = classes["UK"] == 1
    cellular_variables = cellular_variables.drop(index=cellular_variables.index[unknown])
    nucleotides_sequences = nucleotides_sequences[~unknown]
    classes = classes.drop(index=classes.index[unknown])
    classes = classes.drop(columns=["UK"])
    return cellular_variables, nucleotides_sequences, classes

@mkdir
def get_cell_line_path(path:str, cell_line:str):
    return "{path}/{cell_line}".format(path=path, cell_line=cell_line)

@mkdir
def get_task_path(path:str, task:str):
    return "{path}/{task}".format(path=path, task=task.replace(" ", "_"))

def build_tasks(target:str, tasks:List, holdouts:int, validation_split:float, test_split:float, balance_settings:Dict):
    for cell_line in tqdm(get_cell_lines(target), desc="Cell lines"):
        cellular_variables = load_cellular_variables(target, cell_line)
        nucleotides_sequences = load_nucleotides_sequences(target, cell_line)
        classes = load_classes(target, cell_line)
        cellular_variables, nucleotides_sequences, classes = drop_unknown(cellular_variables, nucleotides_sequences, classes)
        cell_line_path = get_cell_line_path(target, cell_line)
        for task in tqdm([task for task in tasks if any(task["balancing"].values())], desc="Building tasks"):
            build_task(
                get_cell_line_path(cell_line_path, task["name"]),
                task,
                balance_settings,
                holdouts,
                validation_split,
                test_split,
                cellular_variables,
                nucleotides_sequences,
                classes
            )