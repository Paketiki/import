# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import sqlite3
from pathlib import Path

app = FastAPI(
    title="КиноВзор API",
    description="API для сайта КиноВзор",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Получаем абсолютный путь к директории проекта
BASE_DIR = Path(__file__).parent

# Монтирование статических файлов
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn

# Модели Pydantic
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class MovieResponse(BaseModel):
    id: int
    title: str
    year: int
    rating: float
    genre: str
    poster_url: Optional[str] = None
    overview: Optional[str] = None
    
    class Config:
        from_attributes = True

# API endpoints

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = BASE_DIR / "templates" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>КиноВзор API работает</h1>")

@app.get("/api/v1/movies", response_model=List[MovieResponse])
async def get_movies(
    genre: Optional[str] = None,
    rating_min: Optional[float] = None,
    pick: Optional[str] = None,
    search: Optional[str] = None
):
    """Получить список фильмов"""
    conn = get_db_connection()
    
    query = "SELECT * FROM movies WHERE 1=1"
    params = []
    
    if genre and genre != "all":
        query += " AND genre LIKE ?"
        params.append(f"%{genre}%")
    
    if rating_min:
        query += " AND rating >= ?"
        params.append(rating_min)
    
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
    
    cursor = conn.execute(query, params)
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return movies

@app.get("/api/v1/movies/{movie_id}")
async def get_movie(movie_id: int):
    """Получить информацию о фильме"""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()
    conn.close()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    
    # Получаем подборки
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT p.slug FROM picks p
        JOIN movie_picks mp ON p.id = mp.pick_id
        WHERE mp.movie_id = ?
    """, (movie_id,))
    picks = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    movie_dict = dict(movie)
    movie_dict["picks"] = picks
    return movie_dict

@app.get("/api/v1/movies/genres/list")
async def get_genres_list():
    """Получить список всех жанров"""
    conn = get_db_connection()
    cursor = conn.execute("SELECT DISTINCT genre FROM movies")
    genres_set = set()
    
    for row in cursor.fetchall():
        if row[0]:
            for genre in row[0].split(','):
                genres_set.add(genre.strip())
    
    conn.close()
    return {"genres": sorted(list(genres_set))}

@app.post("/api/v1/auth/login")
async def login(user_data: UserLogin):
    """Вход в систему"""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM users WHERE username = ?", 
        (user_data.username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    # В реальном приложении проверяем хэш пароля
    if user["password_hash"] != user_data.password:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    # В реальном приложении генерируем JWT токен
    return {
        "access_token": f"token_{user['id']}",
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/register")
async def register(user_data: UserCreate):
    """Регистрация нового пользователя"""
    conn = get_db_connection()
    
    # Проверяем существование пользователя
    cursor = conn.execute(
        "SELECT * FROM users WHERE username = ?", 
        (user_data.username,)
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    
    # Создаем пользователя
    conn.execute(
        "INSERT INTO users (username, email, password_hash, is_active, is_superuser, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_data.username, user_data.email, user_data.password, True, False, datetime.now())
    )
    conn.commit()
    
    # Получаем ID нового пользователя
    cursor = conn.execute("SELECT last_insert_rowid()")
    user_id = cursor.fetchone()[0]
    conn.close()
    
    return {
        "access_token": f"token_{user_id}",
        "token_type": "bearer"
    }

@app.get("/api/v1/users/me")
async def get_current_user():
    """Получить информацию о текущем пользователе (заглушка)"""
    return {
        "id": 1,
        "username": "demo",
        "email": "demo@example.com",
        "is_active": True,
        "is_superuser": False
    }

# Простые рецензии
@app.get("/api/v1/reviews")
async def get_reviews(movie_id: int):
    """Получить рецензии для фильма"""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM reviews WHERE movie_id = ? ORDER BY created_at DESC",
        (movie_id,)
    )
    reviews = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reviews

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API работает нормально"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)