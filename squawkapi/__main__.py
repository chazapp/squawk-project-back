from squawkapi.app import create_app

app = create_app()

if __name__ == '__main__':
    app.app_context().push()
    app.run(host='0.0.0.0')


def __main__():
    app.app_context().push()
    app.run(host='0.0.0.0')

