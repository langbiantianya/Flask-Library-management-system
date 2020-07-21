class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Develop(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:123456@localhost/flask_db"