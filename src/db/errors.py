class DBError(Exception):
    """Базовый класс ошибок для доступа к базе данных"""

    def __init__(self, message="DBError", error_details=None):
        """
        Инициализация класса DBError

        :param message: Сообщение об ошибке
        :param error_details: Дополнительные детали об ошибке (необязательный)
        """
        self.message = message
        self.error_details = error_details
        super().__init__(message)

    def __str__(self):
        """Возвращает строковое представление ошибки"""
        return self.message

    def __repr__(self):
        """Возвращает представление ошибки для отладки"""
        return f"DBError(message='{self.message}', error_details={self.error_details})"


class DBConnectionError(DBError):
    """Ошибка подключения к базе данных"""

    def __init__(self, message="DBConnectionError", host=None, port=None, database=None,
                 username=None, error_code=None, error_details=None):
        """
        Инициализация класса ConnectionError

        :param message: Сообщение об ошибке
        :param host: Хост базы данных (необязательный)
        :param port: Порт базы данных (необязательный)
        :param database: Имя базы данных (необязательный)
        :param username: Имя пользователя базы данных (необязательный)
        :param error_details: Дополнительные детали об ошибке (необязательный)
        """
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        super().__init__(message, error_details)

    def __str__(self):
        """Возвращает строковое представление ошибки"""
        if self.host and self.port and self.database and self.username:
            return f"{self.message} (Хост: {self.host}, Порт: {self.port}, База данных: {self.database}, Пользователь: {self.username})"
        else:
            return self.message

    def __repr__(self):
        """Возвращает представление ошибки для отладки"""
        return (f"ConnectionError(message='{self.message}', host='{self.host}', port='{self.port}', "
                f"database='{self.database}', username='{self.username}', error_details={self.error_details})")


class IntegrityException(DBError):
    pass
