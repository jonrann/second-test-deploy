from tv_shows_flask_app.config.mysqlconnection import connectToMySQL
from tv_shows_flask_app.models import user as user_module
from flask import request, flash
from datetime import datetime


class TV_show:
    def __init__(self, data) -> None:
        self.id = data['id']
        self.title = data['title']
        self.network = data['network']
        self.release_date = data['release_date']
        self.description = data['description']
        self.creator = None
        self.liked_by = []

    def add_to_liked_by(self, user):
        self.liked_by.append(user)

    def remove_from_liked_by(self, user):
        if user in self.liked_by:
            self.liked_by.remove(user)
            user_module.User.remove_from_likes(self)

    # CRUD Functions

    # Create
    @classmethod
    def create_show(cls, data):
        query = """
            INSERT INTO tv_shows (
                title,
                network,
                release_date,
                description,
                user_id
            )
            VALUES (
                %(title)s,
                %(network)s,
                %(release_date)s,
                %(description)s,
                %(user_id)s
            );
        """
        return connectToMySQL('tv_show_schema').query_db(query, data)
    
    # Read
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM tv_shows"
        results = connectToMySQL('tv_show_schema').query_db(query)
        shows = []
        for row in results:
            shows.append(cls(row))
        return shows
    
    @classmethod
    def get_by_id(cls, show_id):
        query = "SELECT * FROM tv_shows WHERE id = %(id)s;"
        data = {
            'id' : show_id
        }

        result = connectToMySQL('tv_show_schema').query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return None
        
    @classmethod
    def get_one_show_with_creator(cls, show_id, user_id):
        query = """
            SELECT users.id AS user_id, users.first_name AS user_first_name , users.last_name as user_last_name, users.email AS user_email, users.password AS user_password, users.created_at, users.updated_at, tv_shows.*
            FROM tv_shows
            JOIN users ON tv_shows.user_id = users.id
            WHERE tv_shows.id = %(show_id)s AND users.id = %(user_id)s;
        """
        data = {'show_id': show_id,
                'user_id' : user_id
            }

        result = connectToMySQL('tv_show_schema').query_db(query, data)

        row = result[0]

        user_data = {
            'id': row['user_id'],
            'first_name': row['user_first_name'],
            'last_name': row['user_last_name'],
            'email': row['user_email'],
            'password': row['user_password'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        user = user_module.User(user_data)

        show_data = {
            'id': row['id'],
            'title': row['title'],
            'network': row['network'],
            'release_date': row['release_date'],
            'description': row['description']
        }
        show = cls(show_data)


        show.creator = user
        return show

    @classmethod
    def get_shows_with_creator(cls):
        query = """
            SELECT users.id AS user_id, users.first_name AS user_first_name , users.last_name as user_last_name, users.email AS user_email, users.password AS user_password, users.created_at, users.updated_at, tv_shows.*
            FROM tv_shows
            JOIN users ON tv_shows.user_id = users.id;
        """
        results = connectToMySQL('tv_show_schema').query_db(query)
        shows = []
        for row in results:
            show_data = {
                'id': row['id'],
                'title': row['title'],
                'network': row['network'],
                'release_date' : row['release_date'],
                'description' : row['description']
            }

            show = cls(show_data)

            user_data = {
                'id': row['user_id'],
                'first_name': row['user_first_name'],
                'last_name': row['user_last_name'],
                'email': row['user_email'],
                'password': row['user_password'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }

            user = user_module.User(user_data)

            show.creator = user
            shows.append(show)

        return shows
    

    @classmethod
    def get_show_with_liked_users(cls, show_id):
        query = """
            SELECT users.*
            FROM users
            JOIN likes ON users.id = likes.user_id
            WHERE likes.tv_show_id = %(show_id)s;
        """
        
        data = {
            'show_id': show_id
        }
        
        results = connectToMySQL('tv_show_schema').query_db(query, data)
        
        show = cls.get_by_id(show_id)
        
        for row in results:
            user = user_module.User(row)
            show.liked_by.append(user)
            
        return show.liked_by



    # Update
    @classmethod
    def update_show(cls, data):
        query = """
            UPDATE tv_shows
            SET title = %(title)s,
                network = %(network)s,
                release_date = %(release_date)s,
                description = %(description)s
            WHERE id = %(id)s;
        """
        return connectToMySQL('tv_show_schema').query_db(query, data)
    
    @classmethod
    def delete_show(cls, show_id):
        query = "DELETE FROM tv_shows WHERE id = %(id)s;"
        
        data = {
            'id' : show_id
        }

        return connectToMySQL('tv_show_schema').query_db(query, data)
    
    # Validate TV Show
    @staticmethod
    def validate_show(data):
        is_valid = True
        # Validate title
        if len(data['title']) < 1:
            flash('Title must not be blank', 'danger')
            is_valid = False

        # Validate network
        if len(data['network']) < 1:
            flash('Network must not be blank', 'danger')
            is_valid = False

        # Validate date
        try:
            datetime.strptime(data['release_date'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date.', 'danger')
            is_valid = False

        # Validate description
        if len(data['description']) < 1:
            flash('Description must not be blank', 'danger')
            is_valid = False
        return is_valid