from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String, nullable=True)

    last_commit = relationship('Commit',
                               order_by='asc(Commit.commit_date)',
                               primaryjoin='and_(Project.id==Commit.project_id)',
                               uselist=False,
                               backref='project')


class Commit(Base):
    __tablename__ = 'commit_'

    id = Column(String, primary_key=True)
    branch = Column(String, nullable=False)
    pipeline_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    author = Column(String, nullable=False)
    url_test = Column(String, nullable=True)
    status = Column(String, nullable=True)
    commit_date = Column(DateTime)
    coverage = Column(Float, nullable=True)

    project_id = Column(String, ForeignKey('project.id'))


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False)
    start = Column(DateTime, nullable=True)
    stop = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    log = Column(String, nullable=True)
    request_headers = Column(String)
    request_content = Column(String)

    commit_id = Column(String, ForeignKey('commit_.id'))
