class user():
    def __init__(self, login, name, password):
        self.username = login
        self.email = name

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self):
        return self.login

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self):
        return self.name

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self):
        return self.password


