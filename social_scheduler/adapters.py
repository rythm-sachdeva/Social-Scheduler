from abc import ABC , abstractmethod


class AccountAdapter(ABC):

    @abstractmethod
    def get_headers(self):
        pass
    
    @abstractmethod
    def get_body(self):
        pass

    @abstractmethod
    def refresh_token(self):
        pass