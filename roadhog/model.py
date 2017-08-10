from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String, nullable=False)


class Commit(Base):
    __tablename__ = 'commit_'

    id = Column(String, primary_key=True)
    branch = Column(String, nullable=False)
    pipeline_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)

    project_id = Column(String, ForeignKey('project.id'))
    project = relationship('Project', backref='project')


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False)
    start = Column(DateTime)
    stop = Column(DateTime)
    status = Column(String, nullable=False)
    log = Column(String)
    request_headers = Column(String)
    request_content = Column(String)

    commit_id = Column(String, ForeignKey('commit_.id'))
