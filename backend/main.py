from fastapi import FastAPI
from database import Base, engine
from routers import user_route, project_rout, task_rout


app = FastAPI()
app.include_router(user_route.router)
app.include_router(project_rout.router)
app.include_router(task_rout.router)

Base.metadata.create_all(bind=engine)
