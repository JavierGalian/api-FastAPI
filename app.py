from fastapi import FastAPI
from config.db import engine
from controllers import auth, users, tasks, authenticate_email
from models.tasks_models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(tasks.tasks)
app.include_router(auth.user_auth)
app.include_router(users.users)
app.include_router(authenticate_email.email)


@app.get('/')
def hello():
    return 'hello world'
