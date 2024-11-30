class User:
    def __init__(self, id=None, username='', email='', password=None,
                 password_hash=None, active=True, confirmed_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password  # Хранит простой пароль до сохранения
        self.password_hash = password_hash
        self.active = active
        self.confirmed_at = confirmed_at
        self.roles = []
        self.results = []

    def set_password(self, password):
        """ Хеширование пароля """
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
        if not self.password_hash:
            raise ValueError("Пароль не был успешно зашифрован")

    def check_password(self, password):
        """ Проверка пароля """
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        """ Проверка активности пользователя """
        return self.active

    @property
    def is_authenticated(self):
        """ Проверка аутентификации пользователя """
        return True

    @property
    def is_anonymous(self):
        """ Проверка анонимности пользователя """
        return False

    def get_id(self):
        """ Получение ID пользователя """
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'
