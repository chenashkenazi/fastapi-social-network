import psycopg
from fastapi import FastAPI, Depends
from app import models
from sqlalchemy.orm import Session
from .database import engine, get_db
from app.routers import post, user


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def db_connect_and_execute(query: str, fetch_option: int):
    try:
        with psycopg.connect("dbname=fastapi user=postgres password=Tomorrow324") as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                match fetch_option:
                    case 1:
                        query_result = cursor.fetchone()
                    case 2:
                        query_result = cursor.fetchall()
                    case _:
                        raise Exception("Please specify fetch option")
                return query_result
    except Exception as ex:
        print(f"Database operation failed: {str(ex)}")


app.include_router(post.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts
