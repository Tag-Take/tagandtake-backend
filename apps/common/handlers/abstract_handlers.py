from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    @abstractmethod
    def handle(self):
        raise NotImplementedError("Subclasses must implement the handle method")
