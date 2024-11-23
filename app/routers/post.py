from fastapi import status, HTTPException, Depends, APIRouter, Response
from app import models
from app.schemas import Post, PostCreate
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from app import oauth2

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[Post])
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # query = "SELECT * FROM posts;"
    # posts = db_connect_and_execute(query=query, fetch_option=2)
    posts = db.query(models.Post).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_posts(post: PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # query = """INSERT INTO posts (title, content, published) VALUES ('{post_title}', '{post_content}', '{post_published}') RETURNING *;""".format(
    #     post_title=post.title, post_content=post.content, post_published=post.published)
    # new_post = db_connect_and_execute(query=query, fetch_option=1)

    new_post = models.Post(user_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # retrieve the new post and save it to variable new_post
    return new_post


@router.get("/{post_id}", response_model=Post)
def get_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # query = """SELECT * FROM posts WHERE id = {post_id};""".format(post_id=post_id)
    # post = db_connect_and_execute(query=query, fetch_option=1)
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} was not found")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
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


@router.put("/{post_id}", response_model=Post)
def update_post(post_id: int, updated_post: PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # query = """UPDATE posts SET title = '{post_title}', content = '{post_content}', published = '{post_published}' WHERE id = {post_id} RETURNING * """.format(
    #     post_title=post.title, post_content=post.content, post_published=post.published, post_id=str(post_id))
    # updated_post = db_connect_and_execute(query=query, fetch_option=1)
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} was not found")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
