from contextlib import contextmanager

from pydantic import BaseSettings, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class MysqlSetting(BaseSettings):
    host: str = "localhost"
    user: str = "root"
    password: str = "password"
    db_name: str = "qq"

    @property
    def url(self):
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:3306/{self.db_name}"

    class Config:
        env_prefix = "MYSQL_"


settings = MysqlSetting()
engine = create_engine(url=settings.url)
session_maker = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def create_session():
    session = session_maker()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
