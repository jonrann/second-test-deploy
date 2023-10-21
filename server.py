from tv_shows_flask_app import app
# Import Controllers here
from tv_shows_flask_app.controllers import users
from tv_shows_flask_app.controllers import tv_shows

if __name__ == "__main__":
    app.run(debug=True)