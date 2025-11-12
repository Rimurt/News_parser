import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем базовый класс для декларативных моделей.
# Все наши ORM-модели будут наследоваться от этого класса.
Base = declarative_base()

engine = sqlalchemy.create_engine("sqlite:///news.db")

class News(Base):
        __tablename__ = "news"

        # Определяем колонки таблицы
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        title = sqlalchemy.Column(sqlalchemy.Text)
        content = sqlalchemy.Column(sqlalchemy.Text)
        image = sqlalchemy.Column(sqlalchemy.Text)
        post_content = sqlalchemy.Column(sqlalchemy.Text)
        content_is_redacted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
        posted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

