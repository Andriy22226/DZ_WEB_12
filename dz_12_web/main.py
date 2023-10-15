from fastapi import FastAPI


from src.routes import users, contacts, auth
app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contacts.router)


@app.get("/") 
def read_root(): 
    return {"message": "Application started"}
