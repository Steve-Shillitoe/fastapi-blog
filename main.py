from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Steve Shillitoe",
        "title": "FastAPI vs Flask",
        "content": "FastAPI is better than Flask "
        "because it provides built-in data validation, automatic interactive API documentation, and high performance via async support "
        "and type hints—while requiring far less boilerplate for production-ready APIs.",
        "date_posted": "February 12, 2026",
    },
    {
        "id": 2,
        "author": "Steve Shillitoe",
        "title": "But is FastAPI always better than Flask?",
        "content": "Flask remains better than FastAPI for many projects because it is simpler, "
        "more flexible, and more mature, with a vast ecosystem and fewer abstractions—making it "
        "easier to understand, customize, and maintain for small to medium applications "
        "where FastAPI`s complexity and async model add unnecessary overhead.",
        "date_posted": "February 12, 2026",
    },
]

@app.get("/",  include_in_schema=False, name="home")
@app.get("/posts",  include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(request, 
                                      "home.html", 
                                      {"posts":posts, "title":"Home"})

@app.get("/posts/{post_id}")
def post_page(request: Request, post_id:int):
    for post in posts:
        if post.get("id") == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(request, 
                                      "post.html", 
                                      {"post":post, "title":title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/api/posts")
def get_posts():
    return posts


@app.get("/api/posts/{post_id}")
def get_post(post_id:int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")