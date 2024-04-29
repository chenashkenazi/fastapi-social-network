import psycopg
import time
from psycopg.cursor import Cursor
from typing import Optional

from fastapi import FastAPI, Response, status, HTTPException, Depends
from random import randrange
from . import models
from app.schemas import PostCreate
from sqlalchemy.orm import Session
from .database import engine, get_db


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


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # query = "SELECT * FROM posts;"
    # posts = db_connect_and_execute(query=query, fetch_option=2)
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: PostCreate, db: Session = Depends(get_db)):
    # query = """INSERT INTO posts (title, content, published) VALUES ('{post_title}', '{post_content}', '{post_published}') RETURNING *;""".format(
    #     post_title=post.title, post_content=post.content, post_published=post.published)
    # new_post = db_connect_and_execute(query=query, fetch_option=1)
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # retrieve the new post and save it to variable new_post
    return {"data": new_post}


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    # query = """SELECT * FROM posts WHERE id = {post_id};""".format(post_id=post_id)
    # post = db_connect_and_execute(query=query, fetch_option=1)
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    # query = """DELETE FROM posts WHERE id = {post_id} RETURNING * """.format(post_id=post_id)
    # deleted_post = db_connect_and_execute(query=query, fetch_option=1)
    post = db.query(models.Post).filter(models.Post.id == post_id)

    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} was not found")
    else:
        post.delete(synchronize_session=False)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}")
def update_post(post_id: int, updated_post: PostCreate, db: Session = Depends(get_db)):
    # query = """UPDATE posts SET title = '{post_title}', content = '{post_content}', published = '{post_published}' WHERE id = {post_id} RETURNING * """.format(
    #     post_title=post.title, post_content=post.content, post_published=post.published, post_id=str(post_id))
    # updated_post = db_connect_and_execute(query=query, fetch_option=1)
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} was not found")
    else:
        post_query.update(updated_post.dict(), synchronize_session=False)
        db.commit()
    return {"data": post_query.first()}

