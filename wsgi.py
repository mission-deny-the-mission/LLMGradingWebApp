# this file is necessary for the web server to actually see the app and work
# development server can also be used by executing this file directly
from create_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
