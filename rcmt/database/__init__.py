from datetime import datetime

import alembic.command
from alembic.config import Config as AlembicConfig
from sqlalchemy import Column, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker

from ..config import Database as DatabaseConfig

Base = declarative_base()


class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True)
    executed_at = Column(DateTime, nullable=False)


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    checksum = Column(String(length=32), nullable=False)
    name = Column(String(length=255), nullable=False)


class Database:
    def __init__(self, engine):
        self.session: sessionmaker = sessionmaker(engine, expire_on_commit=False)

    def get_last_execution(self) -> Execution:
        stmt = select(Execution).order_by(Execution.executed_at.desc())
        with self.session() as session:
            execution = session.scalars(stmt).first()
            if execution:
                return execution
            else:
                ex = Execution()
                ex.executed_at = datetime.fromtimestamp(0.0)
                return ex

    def get_or_create_run(self, name: str, checksum: str = "") -> Run:
        stmt = select(Run).where(Run.name == name)
        with self.session() as session, session.begin():
            run = session.scalars(stmt).first()
            if run:
                return run

            run = Run()
            run.checksum = checksum
            run.name = name
            session.add(run)
            return run

    def update_run(self, name: str, checksum: str) -> None:
        stmt = select(Run).where(Run.name == name)
        with self.session() as session, session.begin():
            run = session.scalars(stmt).first()
            run.checksum = checksum
            session.add(run)
            return

    def save_execution(self, execution: Execution):
        with self.session() as session, session.begin():
            session.add(execution)
            session.commit()


def new_database(cfg: DatabaseConfig) -> Database:
    engine = create_engine(cfg.connection)
    if cfg.migrate is True:
        with engine.begin() as connection:
            alembic_config = AlembicConfig()
            alembic_config.set_main_option(
                "script_location", "rcmt:database:migrations"
            )
            alembic_config.attributes["connection"] = connection
            alembic.command.upgrade(config=alembic_config, revision="head")

    return Database(engine)
