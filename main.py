from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Any, Dict, List

app = FastAPI()

# ----- Models -----
class Posts(BaseModel):
    id: int
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

class PostUpdate(BaseModel):
    # for PATCH: all fields optional; id is not patchable
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
    rating: Optional[int] = None

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# In-memory "DB" (dict keyed by id)
postData: Dict[int, Posts] = {}

# ---------- READ ----------
@app.get("/api/posts", response_model=ResponseModel)
def get_posts():
    all_posts: List[Posts] = list(postData.values())
    return ResponseModel(
        success=True,
        message="All posts retrieved successfully",
        data=all_posts
    )

@app.get("/api/posts/{post_id}", response_model=ResponseModel)
def get_post(post_id: int):
    post = postData.get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return ResponseModel(success=True, message="Post retrieved successfully", data=post)

# ---------- CREATE ----------
@app.post("/api/posts", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
def create_post(payload: Posts):
    if payload.id in postData:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Post ID already exists")
    postData[payload.id] = payload
    return ResponseModel(success=True, message="Post created successfully", data=payload)

# ---------- UPDATE (full replace) ----------
@app.put("/api/posts/{post_id}", response_model=ResponseModel)
def update_post(post_id: int, payload: Posts):
    if payload.id != post_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Body ID must match path ID")
    if post_id not in postData:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    postData[post_id] = payload
    return ResponseModel(success=True, message="Post updated successfully", data=payload)

# ---------- PATCH (partial update) ----------
# @app.patch("/api/posts/{post_id}", response_model=ResponseModel)
# def patch_post(post_id: int, payload: PostUpdate):
#     existing = postData.get(post_id)
#     if not existing:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
#     updated = existing.copy(update=payload.dict(exclude_unset=True))
#     postData[post_id] = updated
#     return ResponseModel(success=True, message="Post partially updated successfully", data=updated)

# ---------- DELETE ----------
@app.delete("/api/posts/{post_id}", response_model=ResponseModel)
def delete_post(post_id: int):
    if post_id not in postData:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    deleted = postData.pop(post_id)
    return ResponseModel(success=True, message="Post deleted successfully", data=deleted)
