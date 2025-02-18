from abc import ABC, abstractmethod


class AbstractProcessor(ABC):
    @abstractmethod
    def process(self):
        raise NotImplementedError("Subclasses must implement the process method")