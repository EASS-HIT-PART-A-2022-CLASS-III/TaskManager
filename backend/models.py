from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from enum import Enum as PythonEnum

project_users = Table('project_users', Base.metadata,
                         Column('user_id', Integer, ForeignKey('users.id',ondelete='CASCADE' )),
                         Column('project_id', Integer, ForeignKey('projects.id',ondelete='CASCADE')))

project_managers = Table('project_managers', Base.metadata,
                         Column('user_id', Integer, ForeignKey('users.id',ondelete='CASCADE' )),
                         Column('project_id', Integer, ForeignKey('projects.id',ondelete='CASCADE')))

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

    my_projects = relationship("Project",secondary=project_users ,back_populates="users")
    managed_projects = relationship("Project",secondary=project_managers ,back_populates="managers")
    created_tasks = relationship("Task", foreign_keys="Task.created_by_id" ,back_populates="created_by")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id" ,back_populates="assignee")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship('User', backref='created_projects')
    users = relationship("User", secondary= project_users ,back_populates="my_projects")
    managers = relationship('User', secondary=project_managers, back_populates='managed_projects')
    tasks = relationship("Task" ,back_populates="project")

class TaskStatus(str,PythonEnum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    status = Column(Enum(TaskStatus),default= TaskStatus.IN_PROGRESS)
    date_of_creation = Column(DateTime(timezone=True), server_default= func.now())
    deadline = Column(DateTime(timezone=True))
    project_id = Column(Integer, ForeignKey('projects.id',ondelete='CASCADE'))
    created_by_id = Column(Integer, ForeignKey('users.id'))
    assignee_id = Column(Integer, ForeignKey('users.id'))

    project = relationship("Project",foreign_keys=[project_id] ,back_populates="tasks")
    created_by = relationship("User", foreign_keys=[created_by_id] ,back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[assignee_id] ,back_populates="assigned_tasks")

