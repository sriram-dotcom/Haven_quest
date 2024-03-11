import sqlite3


class Database:

    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def select(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        return c.fetchall()

    def execute(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        self.conn.commit()
        return c.lastrowid

    def get_properties(self, n, offset):
        data = self.select(
            'SELECT * FROM properties ORDER BY id ASC LIMIT ? OFFSET ?', [n, offset])
        return [{
            'id': d[0],
            'name': d[1],
            'description': d[2],
            'price': d[3],
            'address': d[4],
            'city':d[5],
            'country':d[6],
            'image': d[7],
            'booked': d[8]
        } for d in data]

    def get_user_properties(self, user_id, bookedOrOwned):
        data = self.select(
            'SELECT * FROM properties RIGHT JOIN userDetails ON (properties.id == userDetails.propertyId) WHERE userId=? AND bookedOrOwned=?',
            [user_id, bookedOrOwned])
        return [{
            'id': d[0],
            'name': d[1],
            'description': d[2],
            'price': d[3],
            'address': d[4],
            'city':d[5],
            'country':d[6],
            'image': d[7],
            'booked': d[8]
        } for d in data]

    def add_booking_for_user(self, property_id, user_id):
        self.execute('INSERT INTO userDetails (userId, propertyId, bookedOrOwned) VALUES (?, ?, ?)',
                     [user_id, property_id, -1]) 
        
    def remove_booking_for_user(self, property_id, user_id):
        self.execute('DELETE FROM userDetails WHERE userId=? AND propertyId=? AND bookedOrOwned=?',
                     [user_id, property_id, -1]) 

    def add_property_for_user(self, user_id, name, description, price, address, city, country, image):
        property_id = self.execute('INSERT INTO properties (name, description, price, address, city, country, image, booked) VALUES (?, ?, ?, ?, ?, ?, ?, -1)',
                     [name, description, price, address, city, country, image])
        
        self.execute('INSERT INTO userDetails (userId, propertyId, bookedOrOwned) VALUES (?, ?, ?)',
                     [user_id, property_id, 2]) 
        
    def remove_property_for_user(self, user_id, property_id):
        self.execute('DELETE FROM userDetails WHERE userId=? AND propertyId=? AND bookedOrOwned=?',
                     [user_id, property_id, 2])
        
        self.execute('DELETE FROM properties WHERE id=?',
                     [property_id])

    def get_property_type(self, property_id, user_id):
        type = ''
        if (user_id != None):
            data = self.select('SELECT * FROM userDetails WHERE userId=? AND propertyId=?',
                               [user_id, property_id])
            # print("data: " + str(data))
            if data:
                d = data[0]
                if d[3] == -1:
                    type = 'booked'
                else:
                    type = 'owned'
        
        print("called with property_id:" + str(property_id) + " - user_id:" + str(user_id) + " response: " + type)
        return type

    def get_num_properties(self):
        data = self.select('SELECT COUNT(*) FROM properties')
        return data[0][0]

    def update_property(self, id, booked):
        self.execute('UPDATE properties  SET booked=? WHERE id=?', [booked, id])

    def create_user(self, name, username, encrypted_password):
        self.execute('INSERT INTO users (name, username, encrypted_password) VALUES (?, ?, ?)',
                     [name, username, encrypted_password])

    def get_user(self, username):
        data = self.select(
            'SELECT * FROM users WHERE username=?', [username])
        
        print("data: " + str(data))

        if data:
            d = data[0]
            return {
                'id': d[0],
                'name': d[1],
                'username': d[2],
                'encrypted_password': d[3],
            }
        else:
            return None

    def close(self):
        self.conn.close()
