class User:
    def __init__(self):
        self.orders = 4
    
    def update_name(self, name, id):
        self.name = name
        self.id = id

    def update_surname(self, surname):
        self.surname = surname
    
    def update_room_number(self, room):
        self.room = room

    def print(self):
        print(f'User: {self.name} {self.surname} {self.room} {self.id}')
    # def update_phone_number(self, phone):
    #     self.phone = phone