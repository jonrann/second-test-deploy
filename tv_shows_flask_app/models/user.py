from tv_shows_flask_app.config.mysqlconnection import connectToMySQL
from tv_shows_flask_app.models import tv_show as tv_show_module
from flask import request, flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    def __init__(self, data) -> None:
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.posts = []
        self.likes = []

    def add_to_likes(self, show):
        self.likes.append(show)

    def remove_from_likes(self, show):
        if show in self.likes:
            self.likes.remove(show)
            tv_show_module.TV_show.remove_from_liked_by(self)

# CRUD Functions (Create and Read only needed for users)

    # Create
    @classmethod
    def create_user(cls, data):
    # Use a query to insert data from the form
        query = """
            INSERT INTO users (
                first_name,
                last_name,
                email,
                password,
                created_at,
                updated_at
            )
            VALUES (
                %(first_name)s,
                %(last_name)s,
                %(email)s,
                %(password)s,
                NOW(),
                NOW()
            );
        """
        return connectToMySQL('tv_show_schema').query_db(query, data)

    # Read

    # Get All
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"

        results = connectToMySQL('tv_show_schema').query_db(query)

        users = []

        for row in results:
            users.append(cls(row))
        return users

    # Get one by id
    @classmethod
    def get_by_id(cls, user_id):
    # Write the query to get one single user by its id
        query = "SELECT * FROM users WHERE id = %(id)s;"
        data = {
            'id' : user_id
        }
        # Run the query in MySQL to get back a result
        result = connectToMySQL('tv_show_schema').query_db(query, data)
        # Intialize the first result I get (which should only be one result) into an object using __init__ function.
        if result:
            return cls(result[0])
        else:
            return None
        
    # Get one by email
    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        data = {
            'email' : email
        }
        # Run the query in MySQL to get back a result
        result = connectToMySQL('tv_show_schema').query_db(query, data)
        # Intialize the first result I get (which should only be one result) into an object using __init__ function.
        if result:
            return cls(result[0])
        else:
            return None
    
    @classmethod
    def get_user_with_liked_shows(cls, user_id):
        query = """
            SELECT tv_shows.*
            FROM tv_shows
            JOIN likes ON tv_shows.id = likes.tv_show_id
            WHERE likes.user_id = %(user_id)s;
        """

        data = {
            'user_id' : user_id
        }

        results = connectToMySQL('tv_show_schema').query_db(query, data)

        user = cls.get_by_id(user_id)  

        for row in results:
            show = tv_show_module.TV_show(row)
            user.likes.append(show)
        return user.likes


    
    # Validator
    @staticmethod
    def validate_user(data):
        is_valid = True
        # Validate first name
        if len(data['first_name']) < 3:
            flash('First name needs to be at least 3 characters', 'register_error')
            is_valid = False

        # Validate last name
        if len(data['last_name']) < 3:
            flash('Last name needs to be at least 3 characters', 'register_error')
            is_valid = False

        # Validate email
        if not EMAIL_REGEX.match(data['email']):
            flash('Invalid email', 'register_error')
            is_valid = False

        # Validate password
        if len(data['password']) < 5:
            flash('Password needs to be at least 3 characters', 'register_error')
            is_valid = False
        if not re.search("[A-Z]", data['password']):
            flash('Password needs at least 1 capital letter', 'register_error')
            is_valid = False
        if not re.search("[0-9]", data['password']):
            flash('Password needs at least 1 number', 'register_error')
            is_valid = False

        # Validate confirme password
        if data['password'] != data['confirm_password']:
            flash('Passwords do not match', 'register_error')
            is_valid = False
        return is_valid



