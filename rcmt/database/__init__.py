import enum
from datetime import datetime

import alembic.command
from alembic.config import Config as AlembicConfig
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from ..config import Database as DatabaseConfig

Base = declarative_base()


class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True)
    executed_at = Column(DateTime, nullable=False)


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    hash = Column(Integer, nullable=False)
    name = Column(String(length=255), nullable=False)
    pull_requests = relationship("PullRequest")


class PullRequestStatus(enum.Enum):
    open = 1
    closed = 2
    merged = 3


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True)
    repository = Column(String(length=255), nullable=False)
    status = Column(Enum(PullRequestStatus), nullable=False)
    run_id = Column(Integer, ForeignKey("runs.id"))
    run = relationship("Run", back_populates="pull_requests")


class Database:
    def __init__(self, engine):
        self.session: sessionmaker = sessionmaker(engine)

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

    def save_execution(self, execution: Execution):
        with self.session() as session:
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
