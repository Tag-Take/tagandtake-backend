from abc import ABC, abstractmethod


class AbstractProcessor(ABC):
    @abstractmethod
    def process(self):
        raise NotImplementedError("Subclasses must implement the process method")


class BaseTaskRunner(ABC):
    @abstractmethod
    def run_task(self):
        raise NotImplementedError("Subclasses must implement the run_task method.")
