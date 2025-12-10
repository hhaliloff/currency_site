class subscription():
    def __init__(self, login, valute):
        self.username = login
        self.email = valute

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self):
        return self.login

    @property
    def valute(self):
        return self._valute

    @valute.setter
    def valute(self):
        return self.valute

