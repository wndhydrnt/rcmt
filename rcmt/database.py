from datetime import date

from sqlalchemy import Column, Date, Integer, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import Database as DatabaseConfig

Base = declarative_base()


class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True)
    counter = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)


class Database:
    def __init__(self, engine):
        self.session: sessionmaker = sessionmaker(engine)

    def get_execution_today(self) -> Execution:
        today = date.today()
        stmt = select(Execution).where(Execution.date == today)
        with self.session() as session:
            execution = session.scalars(stmt).first()
            if execution:
                return execution
            else:
                return Execution(counter=0, date=date.today())

    def save_execution(self, execution: Execution):
        with self.session() as session:
            session.add(execution)
            session.commit()


def new_database(cfg: DatabaseConfig) -> Database:
    engine = create_engine(cfg.connection)
    return Database(engine)
