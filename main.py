from flask import Flask, render_template
from data import db_session
from data.exhibits import Exhibits

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/blogs.db")


def main():
    @app.route("/")
    def index():
        db_sess = db_session.create_session()
        ex = db_sess.query(Exhibits)
        return render_template("index.html", exhibits=ex)

    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
