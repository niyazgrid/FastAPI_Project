from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends
from typing import Optional, List, Dict, Annotated
from sqlalchemy.orm import Session

from models import Base, User, Post
from database import engine, session_local
from schemas import UserCreate, User as DbUser, PostCreate, PostResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=DbUser)
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> DbUser:
    db_user = User(name=user.name, age=user.age)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post("/posts/", response_model=PostResponse)
async def create_user(post: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    db_user = db.query(User).filter(User.id == post.author_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    db_post = Post(title=post.title, body=post.body, author_id=post.author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post

@app.get("/posts/", response_model=List[PostResponse])
async def posts(db: Session = Depends(get_db)):
    return db.query(Post).all()




"""
users = [
    {'id': 1, 'name': "Mike", 'age': 33},
    {'id': 2, 'name': "Kevin", 'age': 22},
    {'id': 3, 'name': "Tom", 'age': 28},
]


posts = [
    {'id': 1, 'title': 'News 1', 'body': 'Text 1', 'author': users[2]},
    {'id': 2, 'title': 'News 2', 'body': 'Text 2', 'author': users[1]},
    {'id': 3, 'title': 'News 3', 'body': 'Text 3', 'author': users[0]},
]
#Длинная версия кода
#@app.get("/items")
#async def items() -> List[Post]:
#    post_objects = []
#    for post in posts:
#        post_objects.append(Post(id=post['id'], title=post['title'], body=post['body']))
#    return post_objects

#То же самое что и это вверху, только короткая версия кода
@app.get("/items")
async def items() -> List[Post]:
    return [Post(**post) for post in posts]


@app.post("/user/add")
async def user_add(user: Annotated[
    UserCreate,
    Body(..., example={
        "name": "Username", 
        "age": 1
        })
    ]) -> User:
    new_user_id = len(users) + 1

    new_user = {'id': new_user_id, 'name': user.name, 'age': user.age}
    users.append(new_user)

    return User(**new_user)



@app.get("/items/{id}")
async def items(id: Annotated[int, Path(..., title='Здесь указывается id поста', ge=1, lt=100)]) -> Post:
    for post in posts:
        if post['id'] == id:
            return Post(**post)
        
    raise HTTPException(status_code=404, detail="Post not found")

@app.get("/search")
async def search(post_id: Annotated[ 
    Optional[int], 
    Query(title="ID of post to search for", ge=1, le=50)
    ]) -> Dict[str, Optional[Post]]:
    if post_id:
        for post in posts:
            if post['id'] == post_id:
                return {"data": Post(**post)}
        raise HTTPException(status_code=404, detail="Post not found")
    else:
        return {"data": None}
"""