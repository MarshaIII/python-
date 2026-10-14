class User:
    count = 0

    def __init__(self, name: str, login: str, password: str, grade: int):
        if type(self) is User:
            User.count += 1

        self._name = name
        self._login = login
        self._password = password

        if not isinstance(grade, int) or grade <= 0:
            raise ValueError("grade должен быть положительным целым числом")
        self._grade = grade

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        print("Невозможно изменить логин!")

    @property
    def password(self):
        return "********"

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def grade(self):
        return "Неизвестное свойство grade"

    @grade.setter
    def grade(self, value):
        print("Неизвестное свойство grade")

    def showInfo(self):
        print(f"Name: {self._name}, Login: {self._login}")

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return self._grade == other._grade

    def __lt__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return self._grade < other._grade

    def __gt__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return self._grade > other._grade


class SuperUser(User):
    count = 0

    def __init__(self, name: str, login: str, password: str, role: str, grade: int):
        SuperUser.count += 1

        self._name = name
        self._login = login
        self._password = password

        if not isinstance(grade, int) or grade <= 0:
            raise ValueError("grade должен быть положительным целым числом")
        self._grade = grade

        self._role = role

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        self._role = value

    def show_info(self):
        print(f"Name: {self._name}, Login: {self._login}, Role: {self._role}")

user1 = User('Paul McCartney', 'paul', '1234', 3)
user2 = User('George Harrison', 'george', '5678', 2)
user3 = User('Richard Starkey', 'ringo', '8523', 3)
admin = SuperUser('John Lennon', 'john', '0000', 'admin', 5)

print("=== Информация о пользователях ===")
user1.showInfo()
admin.show_info()
print()

print("=== Счётчики ===")
users = User.count
admins = SuperUser.count
print(f'Всего обычных пользователей: {users}')
print(f'Всего супер-пользователей: {admins}')
print()

print("=== Сравнения ===")
print(user1 < user2)
print(admin > user3)
print(user1 == user3)
print()

print("=== Операции с атрибутами ===")
user3.name = 'Ringo Starr'
print("user3.name =", user3.name)

user1.password = 'Pa$$w0rd'
print("user1.password =", user1.password)

print("user2.password =", user2.password)
print("user2.login =", user2.login)

print("Попытка изменить login для user2:")
user2.login = 'geo'

print("user1.grade =", user1.grade)

print("Попытка изменить grade для admin:")
admin.grade = 10
print()

print("=== Финальные счётчики ===")
print(f'Обычных пользователей: {User.count}')
print(f'Супер-пользователей: {SuperUser.count}')