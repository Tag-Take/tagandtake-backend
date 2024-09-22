from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    @abstractmethod
    def handle(self):
        raise NotImplementedError("Subclasses must implement the handle method")


class BaseTaskRunner(ABC):
    @abstractmethod
    def run_task(self):
        raise NotImplementedError("Subclasses must implement the run_task method.")
