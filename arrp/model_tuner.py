from typing import Callable, Tuple, Dict
from keras.layers import Layer
from gaussian_process import GaussianProcess, Space
from .model_score import average_model_score
from .model import model

class ModelTuner:
    def __init__(self, structure:Callable, space:Space, holdouts:Callable, training:Dict, monitor:str):
        self._structure = structure
        self._space = space
        self._holdouts = holdouts
        self._training = training
        self._monitor = monitor

    def _score(self, **structure:Dict):
        return average_model_score(self._holdouts, model(*self._structure(**structure)), self._training, self._monitor)

    def tune(self, **kwargs)->Dict:
        gp = GaussianProcess(self._score, self._space)
        gp.minimize(**kwargs)
        return gp.best_parameters