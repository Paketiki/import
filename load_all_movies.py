import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.database.base import Base
from app.models.movies import Movie
from app.models.picks import Pick
from app.models.movie_picks import MoviePick
from app.models.users import User
from app.models.roles import Role
import hashlib

DATABASE_URL = "sqlite:///movies.db"
engine = create_engine(DATABASE_URL)

# Полный список фильмов (первые 5 для примера)
ALL_MOVIES = [
    {
        "id": 1,
        "title": "Побег из Шоушенка",
        "year": 1994,
        "genre": "Драма",
        "rating": 9.3,
        "picks": ["hits", "classic"],
        "poster": "https://picsum.photos/seed/film1/200/300",
        "overview": "Банкир Энди Дюфрейн, обвинённый в убийстве жены и её любовника, попадает в тюрьму Шоушенк.",
    },
    {
        "id": 2,
        "title": "Тёмный рыцарь",
        "year": 2008,
        "genre": "Боевик",
        "rating": 9.0,
        "picks": ["hits"],
        "poster": "https://picsum.photos/seed/film2/200/300",
        "overview": "Бэтмен вступает в смертельную игру с Джокером, чья цель — погрузить город в хаос.",
    },
    {
        "id": 3,
        "title": "Начало",
        "year": 2010,
        "genre": "Фантастика",
        "rating": 8.8,
        "picks": ["hits", "new"],
        "poster": "https://picsum.photos/seed/film3/200/300",
        "overview": "Профессиональный вор, специализирующийся на проникновении в сны, получает шанс на искупление.",
    },
    {
        "id": 4,
        "title": "Интерстеллар",
        "year": 2014,
        "genre": "Фантастика",
        "rating": 8.6,
        "picks": ["hits", "new"],
        "poster": "https://picsum.photos/seed/film4/200/300",
        "overview": "Команда исследователей отправляется через червоточину в поисках нового дома для человечества.",
    },
    {
        "id": 5,
        "title": "Форрест Гамп",
        "year": 1994,
        "genre": "Драма",
        "rating": 8.9,
        "picks": ["classic"],
        "poster": "https://picsum.photos/seed/film5/200/300",
        "overview": "История простодушного Форреста, который становится свидетелем важнейших событий в истории США.",
    },
{
                    "id": 6,
                    "title": "Матрица",
                    "year": 1999,
                    "genre": "Фантастика",
                    "rating": 8.7,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film6/200/300",
                    "overview": "Программист Нео узнаёт, что реальность — всего лишь симуляция, созданная машинами.",
                },
                {
                    "id": 7,
                    "title": "Однажды в… Голливуде",
                    "year": 2019,
                    "genre": "Комедия",
                    "rating": 7.7,
                    "picks": ["new"],
                    "poster_url": "https://picsum.photos/seed/film7/200/300",
                    "overview": "Актёр Рик Далтон и его дублёр Клифф Бут пытаются найти себя в меняющемся Голливуде 60-х.",
                },
                {
                    "id": 8,
                    "title": "Паразиты",
                    "year": 2019,
                    "genre": "Драма",
                    "rating": 8.5,
                    "picks": ["hits", "new"],
                    "poster_url": "https://picsum.photos/seed/film8/200/300",
                    "overview": "Бедная семья постепенно захватывает места в доме богатых, притворяясь специалистами.",
                },
                {
                    "id": 9,
                    "title": "Бегущий по лезвию 2049",
                    "year": 2017,
                    "genre": "Фантастика",
                    "rating": 8.0,
                    "picks": ["new"],
                    "poster_url": "https://picsum.photos/seed/film9/200/300",
                    "overview": "Новый бегущий по лезвию раскрывает тайну, способную изменить отношения людей и репликантов.",
                },
                {
                    "id": 10,
                    "title": "Криминальное чтиво",
                    "year": 1994,
                    "genre": "Боевик",
                    "rating": 8.9,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film10/200/300",
                    "overview": "Переплетающиеся истории гангстеров, боксёра и грабителей в Лос-Анджелесе.",
                },
                {
                    "id": 11,
                    "title": "Крёстный отец",
                    "year": 1972,
                    "genre": "Драма",
                    "rating": 9.2,
                    "picks": ["classic", "hits"],
                    "poster_url": "https://picsum.photos/seed/film11/200/300",
                    "overview": "Сага о мафиозном клане Корлеоне и передаче власти от отца к сыну.",
                },
                {
                    "id": 12,
                    "title": "Крёстный отец 2",
                    "year": 1974,
                    "genre": "Драма",
                    "rating": 9.0,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film12/200/300",
                    "overview": "Параллельная история молодого Вито и взросления Майкла Корлеоне.",
                },
                {
                    "id": 13,
                    "title": "Список Шиндлера",
                    "year": 1993,
                    "genre": "Драма",
                    "rating": 9.0,
                    "picks": ["classic", "hits"],
                    "poster_url": "https://picsum.photos/seed/film13/200/300",
                    "overview": "Немецкий промышленник спасает сотни евреев во время Холокоста.",
                },
                {
                    "id": 14,
                    "title": "Зелёная миля",
                    "year": 1999,
                    "genre": "Драма",
                    "rating": 9.0,
                    "picks": ["hits", "classic"],
                    "poster_url": "https://picsum.photos/seed/film14/200/300",
                    "overview": "Тюремный надзиратель встречает осуждённого с необычным даром.",
                },
                {
                    "id": 15,
                    "title": "Властелин колец: Братство Кольца",
                    "year": 2001,
                    "genre": "Фэнтези",
                    "rating": 8.8,
                    "picks": ["hits", "classic"],
                    "poster_url": "https://picsum.photos/seed/film15/200/300",
                    "overview": "Хоббит Фродо отправляется в опасное путешествие, чтобы уничтожить Кольцо Всевластья.",
                },
                {
                    "id": 16,
                    "title": "Властелин колец: Две крепости",
                    "year": 2002,
                    "genre": "Фэнтези",
                    "rating": 8.8,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film16/200/300",
                    "overview": "Братство распалось, но борьба с силами Саурона продолжается на разных фронтах.",
                },
                {
                    "id": 17,
                    "title": "Властелин колец: Возвращение короля",
                    "year": 2003,
                    "genre": "Фэнтези",
                    "rating": 8.9,
                    "picks": ["hits", "classic"],
                    "poster_url": "https://picsum.photos/seed/film17/200/300",
                    "overview": "Финальная битва за Средиземье и последняя попытка уничтожить Кольцо.",
                },
                {
                    "id": 18,
                    "title": "Бойцовский клуб",
                    "year": 1999,
                    "genre": "Драма",
                    "rating": 8.8,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film18/200/300",
                    "overview": "Офисный работник создаёт подпольный клуб, где мужчины избивают друг друга ради ощущения жизни.",
                },
                {
                    "id": 19,
                    "title": "Пираты Карибского моря: Проклятие Чёрной жемчужины",
                    "year": 2003,
                    "genre": "Боевик",
                    "rating": 8.0,
                    "picks": ["hits"],
                    "poster_url": "https://picsum.photos/seed/film19/200/300",
                    "overview": "Экстравагантный капитан Джек Воробей ввязывается в приключение с проклятыми пиратами.",
                },
                {
                    "id": 20,
                    "title": "Гладиатор",
                    "year": 2000,
                    "genre": "Боевик",
                    "rating": 8.5,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film20/200/300",
                    "overview": "Римский полководец становится рабом и выходит на арену, чтобы отомстить за семью.",
                },
                {
                    "id": 21,
                    "title": "Титаник",
                    "year": 1997,
                    "genre": "Драма",
                    "rating": 8.0,
                    "picks": ["classic", "hits"],
                    "poster_url": "https://picsum.photos/seed/film21/200/300",
                    "overview": "История любви на фоне крушения легендарного лайнера «Титаник».",
                },
                {
                    "id": 22,
                    "title": "Индиана Джонс: В поисках утраченного ковчега",
                    "year": 1981,
                    "genre": "Боевик",
                    "rating": 8.4,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film22/200/300",
                    "overview": "Археолог Индиана Джонс пытается опередить нацистов в поисках Ковчега Завета.",
                },
                {
                    "id": 23,
                    "title": "Назад в будущее",
                    "year": 1985,
                    "genre": "Фантастика",
                    "rating": 8.5,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film23/200/300",
                    "overview": "Подросток Марти МакФлай случайно отправляется в прошлое на машине времени.",
                },
                {
                    "id": 24,
                    "title": "Терминатор 2: Судный день",
                    "year": 1991,
                    "genre": "Боевик",
                    "rating": 8.5,
                    "picks": ["classic", "hits"],
                    "poster_url": "https://picsum.photos/seed/film24/200/300",
                    "overview": "Киборг из будущего должен защитить мальчика Джона Коннора от более совершенной машины убийства.",
                },
                {
                    "id": 25,
                    "title": "Чужой",
                    "year": 1979,
                    "genre": "Ужасы",
                    "rating": 8.4,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film25/200/300",
                    "overview": "Экипаж космического корабля сталкивается с неизвестной формой жизни.",
                },
                {
                    "id": 26,
                    "title": "Чужие",
                    "year": 1986,
                    "genre": "Боевик",
                    "rating": 8.3,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film26/200/300",
                    "overview": "Рипли возвращается на планету, где впервые столкнулся с ксеноморфом, но теперь там целая колония.",
                },
                {
                    "id": 27,
                    "title": "Город Бога",
                    "year": 2002,
                    "genre": "Драма",
                    "rating": 8.6,
                    "picks": ["hits"],
                    "poster_url": "https://picsum.photos/seed/film27/200/300",
                    "overview": "История роста преступности в трущобах Рио-де-Жанейро глазами подростков.",
                },
                {
                    "id": 28,
                    "title": "Красота по-американски",
                    "year": 1999,
                    "genre": "Драма",
                    "rating": 8.4,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film28/200/300",
                    "overview": "Кризис среднего возраста толкает главного героя на попытку изменить свою жизнь.",
                },
                {
                    "id": 29,
                    "title": "Большой Лебовски",
                    "year": 1998,
                    "genre": "Комедия",
                    "rating": 8.1,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film29/200/300",
                    "overview": "Флегматичный Чувак оказывается втянутым в детективную историю из-за ошибки с личностью.",
                },
                {
                    "id": 30,
                    "title": "Амели",
                    "year": 2001,
                    "genre": "Комедия",
                    "rating": 8.3,
                    "picks": ["hits"],
                    "poster_url": "https://picsum.photos/seed/film30/200/300",
                    "overview": "Застенчивая Амели решает тайно помогать людям вокруг и менять их жизнь к лучшему.",
                },
                {
                    "id": 31,
                    "title": "Молчание ягнят",
                    "year": 1991,
                    "genre": "Триллер",
                    "rating": 8.6,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film31/200/300",
                    "overview": "Молодая агент ФБР обращается за помощью к заключённому маньяку Ганнибалу Лектеру.",
                },
                {
                    "id": 32,
                    "title": "Семь",
                    "year": 1995,
                    "genre": "Триллер",
                    "rating": 8.6,
                    "picks": ["classic", "hits"],
                    "poster_url": "https://picsum.photos/seed/film32/200/300",
                    "overview": "Два детектива охотятся за серийным убийцей, вдохновляющимся семью смертными грехами.",
                },
                {
                    "id": 33,
                    "title": "Престиж",
                    "year": 2006,
                    "genre": "Драма",
                    "rating": 8.5,
                    "picks": ["hits"],
                    "poster_url": "https://picsum.photos/seed/film33/200/300",
                    "overview": "Два фокусника превращают соперничество в разрушительную одержимость.",
                },
                {
                    "id": 34,
                    "title": "Остров проклятых",
                    "year": 2010,
                    "genre": "Триллер",
                    "rating": 8.1,
                    "picks": ["hits"],
                    "poster_url": "https://picsum.photos/seed/film34/200/300",
                    "overview": "Маршал США прибывает в психиатрическую клинику на острове, чтобы расследовать исчезновение пациентки.",
                },
                {
                    "id": 35,
                    "title": "В джазе только девушки",
                    "year": 1959,
                    "genre": "Комедия",
                    "rating": 8.5,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film35/200/300",
                    "overview": "Два музыканта переодеваются женщинами, чтобы скрыться от гангстеров.",
                },
                {
                    "id": 36,
                    "title": "Таксист",
                    "year": 1976,
                    "genre": "Драма",
                    "rating": 8.3,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film36/200/300",
                    "overview": "Одинокий таксист постепенно теряет связь с реальностью на фоне ночного Нью-Йорка.",
                },
                {
                    "id": 37,
                    "title": "Пролетая над гнездом кукушки",
                    "year": 1975,
                    "genre": "Драма",
                    "rating": 8.7,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film37/200/300",
                    "overview": "Харизматичный заключённый попадает в психиатрическую клинику и сталкивается с жестким порядком.",
                },
                {
                    "id": 38,
                    "title": "Ла-Ла Ленд",
                    "year": 2016,
                    "genre": "Мюзикл",
                    "rating": 8.0,
                    "picks": ["new"],
                    "poster_url": "https://picsum.photos/seed/film38/200/300",
                    "overview": "Джазовый музыкант и актриса пытаются построить карьеру и сохранить отношения.",
                },
                {
                    "id": 39,
                    "title": "Безумный Макс: Дорога ярости",
                    "year": 2015,
                    "genre": "Боевик",
                    "rating": 8.1,
                    "picks": ["hits", "new"],
                    "poster_url": "https://picsum.photos/seed/film39/200/300",
                    "overview": "В постапокалиптической пустыне беглецы пытаются уйти от тирана на боевой фуре.",
                },
                {
                    "id": 40,
                    "title": "Социальная сеть",
                    "year": 2010,
                    "genre": "Драма",
                    "rating": 7.7,
                    "picks": ["new"],
                    "poster_url": "https://picsum.photos/seed/film40/200/300",
                    "overview": "История создания Facebook и конфликта между его основателями.",
                },
                {
                    "id": 41,
                    "title": "Гравитация",
                    "year": 2013,
                    "genre": "Фантастика",
                    "rating": 7.7,
                    "picks": ["new"],
                    "poster_url": "https://picsum.photos/seed/film41/200/300",
                    "overview": "Двое астронавтов пытаются выжить после катастрофы на орбите Земли.",
                },
                {
                    "id": 42,
                    "title": "Выживший",
                    "year": 2015,
                    "genre": "Драма",
                    "rating": 7.8,
                    "picks": ["new"],
                    "poster_url": "https://picsum.photos/seed/film42/200/300",
                    "overview": "Охотник Хью Гласс, оставленный умирать, пытается добраться до тех, кто его предал.",
                },
                {
                    "id": 43,
                    "title": "Джанго освобождённый",
                    "year": 2012,
                    "genre": "Вестерн",
                    "rating": 8.4,
                    "picks": ["hits"],
                    "poster_url": "https://picsum.photos/seed/film43/200/300",
                    "overview": "Освобождённый раб объединяется с охотником за головами, чтобы спасти жену.",
                },
                {
                    "id": 44,
                    "title": "Мстители: Финал",
                    "year": 2019,
                    "genre": "Боевик",
                    "rating": 8.4,
                    "picks": ["hits", "new"],
                    "poster_url": "https://picsum.photos/seed/film44/200/300",
                    "overview": "Герои объединяются, чтобы исправить последствия щелчка Таноса.",
                },
                {
                    "id": 45,
                    "title": "Храброе сердце",
                    "year": 1995,
                    "genre": "Драма",
                    "rating": 8.3,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film45/200/300",
                    "overview": "Шотландский воин Уильям Уоллес поднимает восстание против английской короны.",
                },
                {
                    "id": 46,
                    "title": "Лица со шрамами",
                    "year": 1983,
                    "genre": "Драма",
                    "rating": 8.3,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film46/200/300",
                    "overview": "Иммигрант Тони Монтана поднимается на вершину криминального мира Майами.",
                },
                {
                    "id": 47,
                    "title": "Реквием по мечте",
                    "year": 2000,
                    "genre": "Драма",
                    "rating": 8.3,
                    "picks": ["hits"],
                    "poster_url": "https://picsum.photos/seed/film47/200/300",
                    "overview": "История нескольких людей, чьи мечты разрушаются под тяжестью зависимостей.",
                },
                {
                    "id": 48,
                    "title": "Под покровом ночи",
                    "year": 2016,
                    "genre": "Триллер",
                    "rating": 7.5,
                    "picks": ["new"],
                    "poster_url": "https://picsum.photos/seed/film48/200/300",
                    "overview": "Героиня читает мрачный роман бывшего мужа, который отражает их прошлое.",
                },
                {
                    "id": 49,
                    "title": "Преступление и наказание (советская экранизация)",
                    "year": 1969,
                    "genre": "Драма",
                    "rating": 7.9,
                    "picks": ["classic"],
                    "poster_url": "https://picsum.photos/seed/film49/200/300",
                    "overview": "Экранизация романа Достоевского о преступлении, раскаянии и поиске смысла.",
                },
                {
                    "id": 50,
                    "title": "Нефть",
                    "year": 2007,
                    "genre": "Драма",
                    "rating": 8.1,
                    "picks": ["hits"],
                    "poster_url": "https://picsum.photos/seed/film50/200/300",
                    "overview": "Амбициозный нефтяник строит империю и теряет остатки человечности.",
                },
   
    # Добавьте остальные фильмы здесь...
]

def create_tables_if_not_exist():
    """Создает таблицы если их не существует"""
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)

def load_all_movies():
    """Загружает все фильмы в БД"""
    with Session(engine) as session:
        try:
            print("Начало загрузки всех фильмов...")
            
            # 1. Создаем тестовую роль если нет
            role = session.query(Role).filter(Role.name == "Администратор").first()
            if not role:
                role = Role(name="Администратор", description="Администратор системы")
                session.add(role)
                session.commit()
                session.refresh(role)
                print(f"Создана роль: {role.name}")
            
            # 2. Создаем тестового пользователя если нет
            user = session.query(User).filter(User.username == "admin").first()
            if not user:
                user = User(
                    username="admin",
                    email="admin@example.com",
                    password_hash=hashlib.md5("admin123".encode()).hexdigest(),
                    role_id=role.id
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"Создан пользователь: {user.username} (ID: {user.id})")
            
            # 3. Создаем подборки
            picks_data = [
                {"id": 1, "name": "Хиты", "slug": "hits"},
                {"id": 2, "name": "Новинки", "slug": "new"},
                {"id": 3, "name": "Классика", "slug": "classic"},
            ]
            
            picks_map = {}
            for pick_data in picks_data:
                pick = session.query(Pick).filter(Pick.slug == pick_data["slug"]).first()
                if not pick:
                    pick = Pick(
                        id=pick_data["id"],
                        name=pick_data["name"],
                        slug=pick_data["slug"],
                        description=f"Подборка фильмов: {pick_data['name']}"
                        # creator_id можно не указывать, оно nullable
                    )
                    session.add(pick)
                    session.commit()
                    session.refresh(pick)
                picks_map[pick_data["slug"]] = pick.id
                print(f"Создана подборка: {pick.name} (ID: {pick.id})")
            
            # 4. Загружаем фильмы
            for movie_data in ALL_MOVIES:
                # Проверяем, существует ли фильм
                existing_movie = session.query(Movie).filter(Movie.id == movie_data["id"]).first()
                
                if existing_movie:
                    print(f"Фильм '{movie_data['title']}' уже существует, пропускаем...")
                    continue
                
                # Создаем фильм
                movie = Movie(
                    id=movie_data["id"],
                    title=movie_data["title"],
                    year=movie_data["year"],
                    genre=movie_data["genre"],
                    rating=movie_data["rating"],
                    overview=movie_data["overview"],
                    poster_url=movie_data["poster"],
                    created_by=user.id
                )
                session.add(movie)
                session.commit()
                session.refresh(movie)
                
                # Добавляем связи с подборками
                for pick_slug in movie_data.get("picks", []):
                    if pick_slug in picks_map:
                        # Проверяем, существует ли связь
                        existing_link = session.query(MoviePick).filter(
                            MoviePick.movie_id == movie.id,
                            MoviePick.pick_id == picks_map[pick_slug]
                        ).first()
                        
                        if not existing_link:
                            movie_pick = MoviePick(
                                movie_id=movie.id,
                                pick_id=picks_map[pick_slug]
                            )
                            session.add(movie_pick)
                
                session.commit()
                print(f"Загружен фильм: {movie_data['title']} (ID: {movie.id})")
            
            print(f"✅ Загружено {len(ALL_MOVIES)} фильмов!")
            
            # Выводим статистику
            movie_count = session.query(Movie).count()
            pick_count = session.query(Pick).count()
            print(f"Всего в базе: {movie_count} фильмов, {pick_count} подборок")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()

def check_existing_data():
    """Проверяет существующие данные в БД"""
    with Session(engine) as session:
        try:
            movie_count = session.query(Movie).count()
            pick_count = session.query(Pick).count()
            user_count = session.query(User).count()
            
            print(f"Текущая статистика БД:")
            print(f"- Фильмы: {movie_count}")
            print(f"- Подборки: {pick_count}")
            print(f"- Пользователи: {user_count}")
            
            if movie_count > 0:
                print("\nСписок фильмов:")
                movies = session.query(Movie).limit(5).all()
                for movie in movies:
                    print(f"  - {movie.title} ({movie.year})")
            
            if pick_count > 0:
                print("\nСписок подборок:")
                picks = session.query(Pick).all()
                for pick in picks:
                    print(f"  - {pick.name} ({pick.slug})")
                    
        except Exception as e:
            print(f"Ошибка при проверке данных: {e}")

if __name__ == "__main__":
    # Сначала создаем таблицы
    create_tables_if_not_exist()
    
    # Проверяем текущие данные
    check_existing_data()
    
    # Загружаем фильмы
    load_all_movies()
    