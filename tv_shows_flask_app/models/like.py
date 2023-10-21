from tv_shows_flask_app.config.mysqlconnection import connectToMySQL

class Like:
    @classmethod
    def like_tv_show(cls, user_id, tv_show_id):
        query = """
            INSERT INTO likes (
                user_id, 
                tv_show_id
            )
            VALUES (
                %(user_id)s,
                %(tv_show_id)s
            );
        """

        data = {
            'user_id': user_id,
            'tv_show_id': tv_show_id
        }

        return connectToMySQL('tv_show_schema').query_db(query, data)
    
    @classmethod
    def unlike_tv_show(cls, user_id, tv_show_id):
        query = "DELETE FROM likes WHERE user_id = %(user_id)s AND tv_show_id = %(tv_show_id)s"
        data = {
            'user_id': user_id,
            'tv_show_id': tv_show_id
        }

        return connectToMySQL('tv_show_schema').query_db(query, data)

    @classmethod
    def check_like(cls, user_id, tv_show_id):
        query = "SELECT * FROM likes WHERE user_id = %(user_id)s AND tv_show_id = %(tv_show_id)s"
        data = {
            'user_id': user_id,
            'tv_show_id': tv_show_id
        }
        result = connectToMySQL('tv_show_schema').query_db(query, data)
        return result