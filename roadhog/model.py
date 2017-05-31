from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base =  declarative_base()


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String, nullable=False)


class Commit(Base):
    __tablename__ = 'commit'

    id = Column(Integer, primary_key=True)
    branch = Column(String, nullable=False)

    project_id = Column(String, ForeignKey('project.id'))
    project = relationship('Project', backref='project')

    jobs = relationship('Job', backref='job')


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False)
    start = Column(Date)
    end = Column(Date)
    status = Column(String, nullable=False)
    log = Column(String)
    request_headers = Column(String)
    request_content = Column(String)

    commit_id = Column(String, ForeignKey('commit.id'))
    commit = relationship('Commit', backref='commit')
