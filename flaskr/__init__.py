import os
from flask import (
    Flask, current_app
)


def create_app(test_config=None):
    """
    create_app是默认的名称, flask run的时候会自动来运行这个函数
    :param test_config:
    :return:
    """
    # create and configure the app
    app: Flask = Flask(__name__, instance_relative_config=True)
    # print(app.instance_path)  # /Users/thomas_young/Documents/code/flask_project/instance
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        ret = app.config.from_pyfile('config.py', silent=True)
        print('load the config.py ' + ('success' if ret else 'fail'))
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        print('make instance_path', app.instance_path)
        os.makedirs(app.instance_path)
    except OSError as e:
        pass

    # a simple page that says hello
    def hello():
        print(f'current app url map is {current_app.url_map}')
        return 'Hello, World!'
    app.add_url_rule('/hello', view_func=hello)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', 'index')


    return app