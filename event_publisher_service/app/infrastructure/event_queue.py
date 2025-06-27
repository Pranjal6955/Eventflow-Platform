from abc import ABC, abstractmethod

class EventQueue(ABC):
    @abstractmethod
    def enqueue(self, event: dict):
        pass 