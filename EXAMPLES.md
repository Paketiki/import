# Примеры использования API

## Базовые процедуры

### Получить все фильмы

**curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/movies"
```

**JavaScript (Fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/v1/movies');
const movies = await response.json();
console.log(movies);
```

**Python (requests):**
```python
import requests

response = requests.get('http://localhost:8000/api/v1/movies')
movies = response.json()
print(movies)
```

---

### Поиск фильмов

**curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/movies?search=Inception"
```

**JavaScript:**
```javascript
const query = 'Inception';
const response = await fetch(`http://localhost:8000/api/v1/movies?search=${query}`);
const movies = await response.json();
console.log(movies);
```

**Python:**
```python
import requests

params = {'search': 'Inception'}
response = requests.get('http://localhost:8000/api/v1/movies', params=params)
movies = response.json()
print(movies)
```

---

### Получить фильмы с признаками

**curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/movies?genre=drama&rating_min=7.0"
```

**JavaScript:**
```javascript
const params = new URLSearchParams();
params.append('genre', 'drama');
params.append('rating_min', '7.0');

const response = await fetch(`http://localhost:8000/api/v1/movies?${params}`);
const movies = await response.json();
console.log(movies);
```

**Python:**
```python
import requests

params = {
    'genre': 'drama',
    'rating_min': 7.0
}
response = requests.get('http://localhost:8000/api/v1/movies', params=params)
movies = response.json()
print(movies)
```

---

### Получить конкретный фильм

**curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/movies/1"
```

**JavaScript:**
```javascript
const movieId = 1;
const response = await fetch(`http://localhost:8000/api/v1/movies/${movieId}`);
const movie = await response.json();
console.log(movie);
```

**Python:**
```python
import requests

movie_id = 1
response = requests.get(f'http://localhost:8000/api/v1/movies/{movie_id}')
movie = response.json()
print(movie)
```

---

## Процедуры с данными

### Создать новый фильм

**curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/movies" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Film",
    "year": 2024,
    "rating": 8.5,
    "genre": "drama, thriller",
    "overview": "Film description",
    "poster_url": "https://example.com/poster.jpg"
  }'
```

**JavaScript:**
```javascript
const newMovie = {
    title: 'New Film',
    year: 2024,
    rating: 8.5,
    genre: 'drama, thriller',
    overview: 'Film description',
    poster_url: 'https://example.com/poster.jpg'
};

const response = await fetch('http://localhost:8000/api/v1/movies', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(newMovie)
});

const createdMovie = await response.json();
console.log(createdMovie);
```

**Python:**
```python
import requests

new_movie = {
    "title": "New Film",
    "year": 2024,
    "rating": 8.5,
    "genre": "drama, thriller",
    "overview": "Film description",
    "poster_url": "https://example.com/poster.jpg"
}

response = requests.post('http://localhost:8000/api/v1/movies', json=new_movie)
created_movie = response.json()
print(created_movie)
```

---

### Обновить фильм

**curl:**
```bash
curl -X PUT "http://localhost:8000/api/v1/movies/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "rating": 9.0
  }'
```

**Python:**
```python
import requests

update_data = {
    "title": "Updated Title",
    "rating": 9.0
}

response = requests.put('http://localhost:8000/api/v1/movies/1', json=update_data)
updated_movie = response.json()
print(updated_movie)
```

---

### Удалить фильм

**curl:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/movies/1"
```

**Python:**
```python
import requests

response = requests.delete('http://localhost:8000/api/v1/movies/1')
print(response.status_code)  # Он должен быть 200
```

---

## Процедуры с рецензиями

### Получить рецензии для фильма

**curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/reviews?movie_id=1"
```

**Python:**
```python
import requests

params = {'movie_id': 1}
response = requests.get('http://localhost:8000/api/v1/reviews', params=params)
reviews = response.json()
print(reviews)
```

---

### Написать рецензию

**curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_id": 1,
    "user_id": 1,
    "rating": 8,
    "text": "Great movie!"
  }'
```

**Python:**
```python
import requests

review_data = {
    "movie_id": 1,
    "user_id": 1,
    "rating": 8,
    "text": "Great movie!"
}

response = requests.post('http://localhost:8000/api/v1/reviews', json=review_data)
created_review = response.json()
print(created_review)
```

---

## Пользователи

### Проверка текущего пользователя

**curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/me"
```

**Python:**
```python
import requests

response = requests.get('http://localhost:8000/api/v1/users/me')
user = response.json()
print(user)
```

---

## Подборки

### Получить все подборки

**curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/picks"
```

**Python:**
```python
import requests

response = requests.get('http://localhost:8000/api/v1/picks')
picks = response.json()
print(picks)
```

---

## Жанры

### Получить список жанров

**curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/movies/genres/list"
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/movies/genres/list');
const data = await response.json();
console.log(data.genres);
```

**Python:**
```python
import requests

response = requests.get('http://localhost:8000/api/v1/movies/genres/list')
data = response.json()
print(data['genres'])
```

---

## Обработка ошибок

### Пример обработки ошибок

**JavaScript:**
```javascript
const fetchMovie = async (movieId) => {
    try {
        const response = await fetch(`http://localhost:8000/api/v1/movies/${movieId}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                console.error('Film not found');
            } else {
                console.error('API error:', response.status);
            }
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('Network error:', error);
        return null;
    }
};

// Usage
const movie = await fetchMovie(999);
if (movie) {
    console.log(movie);
}
```

**Python:**
```python
import requests
from requests.exceptions import RequestException

def fetch_movie(movie_id):
    try:
        response = requests.get(f'http://localhost:8000/api/v1/movies/{movie_id}')
        response.raise_for_status()  # Raise error for bad status codes
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print('Film not found')
        else:
            print(f'API error: {e.response.status_code}')
    except RequestException as e:
        print(f'Network error: {e}')
    
    return None

# Usage
movie = fetch_movie(999)
if movie:
    print(movie)
```

---

## Ноты

- Все данные вводятся в формате JSON
- Не забывайте установить заголовок `Content-Type: application/json` для POST/PUT реквестов
- Понимаются коды ответов:
  - `200` - ОК
  - `201` - Создано
  - `400` - Неправильные данные
  - `401` - Не авторизован
  - `404` - Не найдено
  - `500` - Ошибка сервера
