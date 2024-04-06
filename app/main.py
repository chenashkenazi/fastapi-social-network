from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Response, status, HTTPException
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [{"title": "title 1", "content": "content 1", "post_id": 1},
            {"title": "title 2", "content": "content 2", "post_id": 2}]


def find_post(post_id):
    for p in my_posts:
        if p["post_id"] == post_id:
            return p


def find_index_post(post_id):
    for i, p in enumerate(my_posts):
        if p["post_id"] == post_id:
            return i


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.model_dump()
    post_dict['post_id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.get("/posts/{post_id}")
def get_post(post_id: int):

    post = find_post(post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} was not found")
    return {"data": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    index = find_index_post(post_id=post_id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    index = find_index_post(post_id=post_id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} does not exist")
    post_dict = post.dict()
    post_dict["post_id"] = post_id
    my_posts[index] = post_dict
    return {"data": post_dict}
