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
    title = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.Text)
    image = sqlalchemy.Column(sqlalchemy.String)
    posted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    def __repr__(self):
        # Метод для "красивого" вывода объекта в консоль, полезно для отладки.
        status = "✅" if self.posted else "❌" #type:ignore
        return f'''
========================================
        <Title: {self.title}>
        <Content: {self.content}>
        <Image: {self.image}>
        <Posted: {status}>
========================================='''
    
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

