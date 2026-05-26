from abc import ABC, abstractmethod
from typing import Any, Dict, List


class NetworkDevice(ABC):
    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_identity(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_version(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_interfaces(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_clock(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def ping(self, target: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def backup_config(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def check_ntp(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


CommandLog = List[Dict[str, str]]
