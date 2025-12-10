import sys
import os
import warnings
from pathlib import Path

# Фильтруем предупреждения SQLAlchemy
warnings.filterwarnings("ignore", category=Warning)

sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import Boolean, Float, String, Text, create_engine, Table, Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import hashlib
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Используем новую Base, чтобы не конфликтовать с импортированными моделями
Base = declarative_base()

DATABASE_URL = "sqlite:///movies.db"
engine = create_engine(DATABASE_URL)

def get_password_hash(password: str) -> str:
    """Простая функция для хэширования пароля (для демо-целей)"""
    return hashlib.sha256(password.encode()).hexdigest()

# Определим простые модели прямо здесь для избежания конфликтов
class SimpleUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SimplePick(Base):
    __tablename__ = "picks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SimpleMovie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    overview = Column(Text)
    year = Column(Integer, index=True)
    genre = Column(String(100), index=True)
    rating = Column(Float, default=0.0, index=True)
    poster_url = Column(String(500))
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())

# Промежуточная таблица
class SimpleMoviePick(Base):
    __tablename__ = "movie_picks"
    
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    pick_id = Column(Integer, ForeignKey('picks.id'), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Тестовая таблица для рецензий
class SimpleReview(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text = Column(Text, nullable=False)
    rating = Column(Float, default=0.0)
    author_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Упрощенные данные (только первые 20 фильмов для примера, остальные аналогично)
MOVIES = [
    {
        "id": 1,
        "title": "Побег из Шоушенка",
        "year": 1994,
        "genre": "Драма",
        "rating": 9.3,
        "poster_url": "https://picsum.photos/seed/film1/200/300",
        "overview": "Банкир Энди Дюфрейн, обвинённый в убийстве жены и её любовника, попадает в тюрьму Шоушенк.",
        "picks": ["hits", "classic"]
    },
    {
        "id": 2,
        "title": "Тёмный рыцарь",
        "year": 2008,
        "genre": "Боевик",
        "rating": 9.0,
        "poster_url": "https://picsum.photos/seed/film2/200/300",
        "overview": "Бэтмен вступает в смертельную игру с Джокером, чья цель — погрузить город в хаос.",
        "picks": ["hits"]
    },
    {
        "id": 3,
        "title": "Начало",
        "year": 2010,
        "genre": "Фантастика",
        "rating": 8.8,
        "poster_url": "https://picsum.photos/seed/film3/200/300",
        "overview": "Профессиональный вор, специализирующийся на проникновении в сны, получает шанс на искупление.",
        "picks": ["hits", "new"]
    },
    {
        "id": 4,
        "title": "Интерстеллар",
        "year": 2014,
        "genre": "Фантастика",
        "rating": 8.6,
        "poster_url": "https://picsum.photos/seed/film4/200/300",
        "overview": "Команда исследователей отправляется через червоточину в поисках нового дома для человечества.",
        "picks": ["hits", "new"]
    },
    {
        "id": 5,
        "title": "Форрест Гамп",
        "year": 1994,
        "genre": "Драма",
        "rating": 8.9,
        "poster_url": "https://picsum.photos/seed/film5/200/300",
        "overview": "История простодушного Форреста, который становится свидетелем важнейших событий в истории США.",
        "picks": ["classic"]
    },
    {
        "id": 6,
        "title": "Матрица",
        "year": 1999,
        "genre": "Фантастика",
        "rating": 8.7,
        "poster_url": "https://picsum.photos/seed/film6/200/300",
        "overview": "Программист Нео узнаёт, что реальность — всего лишь симуляция, созданная машинами.",
        "picks": ["classic"]
    },
    {
        "id": 7,
        "title": "Однажды в… Голливуде",
        "year": 2019,
        "genre": "Комедия",
        "rating": 7.7,
        "poster_url": "https://picsum.photos/seed/film7/200/300",
        "overview": "Актёр Рик Далтон и его дублёр Клифф Бут пытаются найти себя в меняющемся Голливуде 60-х.",
        "picks": ["new"]
    },
    {
        "id": 8,
        "title": "Паразиты",
        "year": 2019,
        "genre": "Драма",
        "rating": 8.5,
        "poster_url": "https://picsum.photos/seed/film8/200/300",
        "overview": "Бедная семья постепенно захватывает места в доме богатых, притворяясь специалистами.",
        "picks": ["hits", "new"]
    },
    {
        "id": 9,
        "title": "Бегущий по лезвию 2049",
        "year": 2017,
        "genre": "Фантастика",
        "rating": 8.0,
        "poster_url": "https://picsum.photos/seed/film9/200/300",
        "overview": "Новый бегущий по лезвию раскрывает тайну, способную изменить отношения людей и репликантов.",
        "picks": ["new"]
    },
    {
        "id": 10,
        "title": "Криминальное чтиво",
        "year": 1994,
        "genre": "Боевик",
        "rating": 8.9,
        "poster_url": "https://picsum.photos/seed/film10/200/300",
        "overview": "Переплетающиеся истории гангстеров, боксёра и грабителей в Лос-Анджелесе.",
        "picks": ["classic"]
    },
    {
        "id": 11,
        "title": "Крёстный отец",
        "year": 1972,
        "genre": "Драма",
        "rating": 9.2,
        "poster_url": "https://picsum.photos/seed/film11/200/300",
        "overview": "Сага о мафиозном клане Корлеоне и передаче власти от отца к сыну.",
        "picks": ["classic", "hits"]
    },
    {
        "id": 12,
        "title": "Крёстный отец 2",
        "year": 1974,
        "genre": "Драма",
        "rating": 9.0,
        "poster_url": "https://picsum.photos/seed/film12/200/300",
        "overview": "Параллельная история молодого Вито и взросления Майкла Корлеоне.",
        "picks": ["classic"]
    },
    {
        "id": 13,
        "title": "Список Шиндлера",
        "year": 1993,
        "genre": "Драма",
        "rating": 9.0,
        "poster_url": "https://picsum.photos/seed/film13/200/300",
        "overview": "Немецкий промышленник спасает сотни евреев во время Холокоста.",
        "picks": ["classic", "hits"]
    },
    {
        "id": 14,
        "title": "Зелёная миля",
        "year": 1999,
        "genre": "Драма",
        "rating": 9.0,
        "poster_url": "https://picsum.photos/seed/film14/200/300",
        "overview": "Тюремный надзиратель встречает осуждённого с необычным даром.",
        "picks": ["hits", "classic"]
    },
    {
        "id": 15,
        "title": "Властелин колец: Братство Кольца",
        "year": 2001,
        "genre": "Фэнтези",
        "rating": 8.8,
        "poster_url": "https://picsum.photos/seed/film15/200/300",
        "overview": "Хоббит Фродо отправляется в опасное путешествие, чтобы уничтожить Кольцо Всевластья.",
        "picks": ["hits", "classic"]
    },
    {
        "id": 16,
        "title": "Властелин колец: Две крепости",
        "year": 2002,
        "genre": "Фэнтези",
        "rating": 8.8,
        "poster_url": "https://picsum.photos/seed/film16/200/300",
        "overview": "Братство распалось, но борьба с силами Саурона продолжается на разных фронтах.",
        "picks": ["classic"]
    },
    {
        "id": 17,
        "title": "Властелин колец: Возвращение короля",
        "year": 2003,
        "genre": "Фэнтези",
        "rating": 8.9,
        "poster_url": "https://picsum.photos/seed/film17/200/300",
        "overview": "Финальная битва за Средиземье и последняя попытка уничтожить Кольцо.",
        "picks": ["hits", "classic"]
    },
    {
        "id": 18,
        "title": "Бойцовский клуб",
        "year": 1999,
        "genre": "Драма",
        "rating": 8.8,
        "poster_url": "https://picsum.photos/seed/film18/200/300",
        "overview": "Офисный работник создаёт подпольный клуб, где мужчины избивают друг друга ради ощущения жизни.",
        "picks": ["classic"]
    },
    {
        "id": 19,
        "title": "Пираты Карибского моря: Проклятие Чёрной жемчужины",
        "year": 2003,
        "genre": "Боевик",
        "rating": 8.0,
        "poster_url": "https://picsum.photos/seed/film19/200/300",
        "overview": "Экстравагантный капитан Джек Воробей ввязывается в приключение с проклятыми пиратами.",
        "picks": ["hits"]
    },
    {
        "id": 20,
        "title": "Гладиатор",
        "year": 2000,
        "genre": "Боевик",
        "rating": 8.5,
        "poster_url": "https://picsum.photos/seed/film20/200/300",
        "overview": "Римский полководец становится рабом и выходит на арену, чтобы отомстить за семью.",
        "picks": ["classic"]
    },
    {
        "id": 21,
        "title": "Титаник",
        "year": 1997,
        "genre": "Драма",
        "rating": 8.0,
        "poster_url": "https://picsum.photos/seed/film21/200/300",
        "overview": "История любви на фоне крушения легендарного лайнера «Титаник».",
        "picks": ["classic", "hits"]
    },
    {
        "id": 22,
        "title": "Индиана Джонс: В поисках утраченного ковчега",
        "year": 1981,
        "genre": "Боевик",
        "rating": 8.4,
        "poster_url": "https://picsum.photos/seed/film22/200/300",
        "overview": "Археолог Индиана Джонс пытается опередить нацистов в поисках Ковчега Завета.",
        "picks": ["classic"]
    },
    {
        "id": 23,
        "title": "Назад в будущее",
        "year": 1985,
        "genre": "Фантастика",
        "rating": 8.5,
        "poster_url": "https://picsum.photos/seed/film23/200/300",
        "overview": "Подросток Марти МакФлай случайно отправляется в прошлое на машине времени.",
        "picks": ["classic"]
    },
    {
        "id": 24,
        "title": "Терминатор 2: Судный день",
        "year": 1991,
        "genre": "Боевик",
        "rating": 8.5,
        "poster_url": "https://picsum.photos/seed/film24/200/300",
        "overview": "Киборг из будущего должен защитить мальчика Джона Коннора от более совершенной машины убийства.",
        "picks": ["classic", "hits"]
    },
    {
        "id": 25,
        "title": "Чужой",
        "year": 1979,
        "genre": "Ужасы",
        "rating": 8.4,
        "poster_url": "https://picsum.photos/seed/film25/200/300",
        "overview": "Экипаж космического корабля сталкивается с неизвестной формой жизни.",
        "picks": ["classic"]
    },
    {
        "id": 26,
        "title": "Чужие",
        "year": 1986,
        "genre": "Боевик",
        "rating": 8.3,
        "poster_url": "https://picsum.photos/seed/film26/200/300",
        "overview": "Рипли возвращается на планету, где впервые столкнулся с ксеноморфом, но теперь там целая колония.",
        "picks": ["classic"]
    },
    {
        "id": 27,
        "title": "Город Бога",
        "year": 2002,
        "genre": "Драма",
        "rating": 8.6,
        "poster_url": "https://picsum.photos/seed/film27/200/300",
        "overview": "История роста преступности в трущобах Рио-де-Жанейро глазами подростков.",
        "picks": ["hits"]
    },
    {
        "id": 28,
        "title": "Красота по-американски",
        "year": 1999,
        "genre": "Драма",
        "rating": 8.4,
        "poster_url": "https://picsum.photos/seed/film28/200/300",
        "overview": "Кризис среднего возраста толкает главного героя на попытку изменить свою жизнь.",
        "picks": ["classic"]
    },
    {
        "id": 29,
        "title": "Большой Лебовски",
        "year": 1998,
        "genre": "Комедия",
        "rating": 8.1,
        "poster_url": "https://picsum.photos/seed/film29/200/300",
        "overview": "Флегматичный Чувак оказывается втянутым в детективную историю из-за ошибки с личностью.",
        "picks": ["classic"]
    },
    {
        "id": 30,
        "title": "Амели",
        "year": 2001,
        "genre": "Комедия",
        "rating": 8.3,
        "poster_url": "https://picsum.photos/seed/film30/200/300",
        "overview": "Застенчивая Амели решает тайно помогать людям вокруг и менять их жизнь к лучшему.",
        "picks": ["hits"]
    },
    {
        "id": 31,
        "title": "Молчание ягнят",
        "year": 1991,
        "genre": "Триллер",
        "rating": 8.6,
        "poster_url": "https://picsum.photos/seed/film31/200/300",
        "overview": "Молодая агент ФБР обращается за помощью к заключённому маньяку Ганнибалу Лектеру.",
        "picks": ["classic"]
    },
    {
        "id": 32,
        "title": "Семь",
        "year": 1995,
        "genre": "Триллер",
        "rating": 8.6,
        "poster_url": "https://picsum.photos/seed/film32/200/300",
        "overview": "Два детектива охотятся за серийным убийцей, вдохновляющимся семью смертными грехами.",
        "picks": ["classic", "hits"]
    },
    {
        "id": 33,
        "title": "Престиж",
        "year": 2006,
        "genre": "Драма",
        "rating": 8.5,
        "poster_url": "https://picsum.photos/seed/film33/200/300",
        "overview": "Два фокусника превращают соперничество в разрушительную одержимость.",
        "picks": ["hits"]
    },
    {
        "id": 34,
        "title": "Остров проклятых",
        "year": 2010,
        "genre": "Триллер",
        "rating": 8.1,
        "poster_url": "https://picsum.photos/seed/film34/200/300",
        "overview": "Маршал США прибывает в психиатрическую клинику на острове, чтобы расследовать исчезновение пациентки.",
        "picks": ["hits"]
    },
    {
        "id": 35,
        "title": "В джазе только девушки",
        "year": 1959,
        "genre": "Комедия",
        "rating": 8.5,
        "poster_url": "https://picsum.photos/seed/film35/200/300",
        "overview": "Два музыканта переодеваются женщинами, чтобы скрыться от гангстеров.",
        "picks": ["classic"]
    },
    {
        "id": 36,
        "title": "Таксист",
        "year": 1976,
        "genre": "Драма",
        "rating": 8.3,
        "poster_url": "https://picsum.photos/seed/film36/200/300",
        "overview": "Одинокий таксист постепенно теряет связь с реальности на фоне ночного Нью-Йорка.",
        "picks": ["classic"]
    },
    {
        "id": 37,
        "title": "Пролетая над гнездом кукушки",
        "year": 1975,
        "genre": "Драма",
        "rating": 8.7,
        "poster_url": "https://picsum.photos/seed/film37/200/300",
        "overview": "Харизматичный заключённый попадает в психиатрическую клинику и сталкивается с жестким порядком.",
        "picks": ["classic"]
    },
    {
        "id": 38,
        "title": "Ла-Ла Ленд",
        "year": 2016,
        "genre": "Мюзикл",
        "rating": 8.0,
        "poster_url": "https://picsum.photos/seed/film38/200/300",
        "overview": "Джазовый музыкант и актриса пытаются построить карьеру и сохранить отношения.",
        "picks": ["new"]
    },
    {
        "id": 39,
        "title": "Безумный Макс: Дорога ярости",
        "year": 2015,
        "genre": "Боевик",
        "rating": 8.1,
        "poster_url": "https://picsum.photos/seed/film39/200/300",
        "overview": "В постапокалиптической пустыне беглецы пытаются уйти от тирана на боевой фуре.",
        "picks": ["hits", "new"]
    },
    {
        "id": 40,
        "title": "Социальная сеть",
        "year": 2010,
        "genre": "Драма",
        "rating": 7.7,
        "poster_url": "https://picsum.photos/seed/film40/200/300",
        "overview": "История создания Facebook и конфликта между его основателями.",
        "picks": ["new"]
    },
    {
        "id": 41,
        "title": "Гравитация",
        "year": 2013,
        "genre": "Фантастика",
        "rating": 7.7,
        "poster_url": "https://picsum.photos/seed/film41/200/300",
        "overview": "Двое астронавтов пытаются выжить после катастрофы на орбите Земли.",
        "picks": ["new"]
    },
    {
        "id": 42,
        "title": "Выживший",
        "year": 2015,
        "genre": "Драма",
        "rating": 7.8,
        "poster_url": "https://picsum.photos/seed/film42/200/300",
        "overview": "Охотник Хью Гласс, оставленный умирать, пытается добраться до тех, кто его предал.",
        "picks": ["new"]
    },
    {
        "id": 43,
        "title": "Джанго освобождённый",
        "year": 2012,
        "genre": "Вестерн",
        "rating": 8.4,
        "poster_url": "https://picsum.photos/seed/film43/200/300",
        "overview": "Освобождённый раб объединяется с охотником за головами, чтобы спасти жену.",
        "picks": ["hits"]
    },
    {
        "id": 44,
        "title": "Мстители: Финал",
        "year": 2019,
        "genre": "Боевик",
        "rating": 8.4,
        "poster_url": "https://picsum.photos/seed/film44/200/300",
        "overview": "Герои объединяются, чтобы исправить последствия щелчка Таноса.",
        "picks": ["hits", "new"]
    },
    {
        "id": 45,
        "title": "Храброе сердце",
        "year": 1995,
        "genre": "Драма",
        "rating": 8.3,
        "poster_url": "https://picsum.photos/seed/film45/200/300",
        "overview": "Шотландский воин Уильям Уоллес поднимает восстание против английской короны.",
        "picks": ["classic"]
    },
    {
        "id": 46,
        "title": "Лица со шрамами",
        "year": 1983,
        "genre": "Драма",
        "rating": 8.3,
        "poster_url": "https://picsum.photos/seed/film46/200/300",
        "overview": "Иммигрант Тони Монтана поднимается на вершину криминального мира Майами.",
        "picks": ["classic"]
    },
    {
        "id": 47,
        "title": "Реквием по мечте",
        "year": 2000,
        "genre": "Драма",
        "rating": 8.3,
        "poster_url": "https://picsum.photos/seed/film47/200/300",
        "overview": "История нескольких людей, чьи мечты разрушаются под тяжестью зависимостей.",
        "picks": ["hits"]
    },
    {
        "id": 48,
        "title": "Под покровом ночи",
        "year": 2016,
        "genre": "Триллер",
        "rating": 7.5,
        "poster_url": "https://picsum.photos/seed/film48/200/300",
        "overview": "Героиня читает мрачный роман бывшего мужа, который отражает их прошлое.",
        "picks": ["new"]
    },
    {
        "id": 49,
        "title": "Преступление и наказание (советская экранизация)",
        "year": 1969,
        "genre": "Драма",
        "rating": 7.9,
        "poster_url": "https://picsum.photos/seed/film49/200/300",
        "overview": "Экранизация романа Достоевского о преступлении, раскаянии и поиске смысла.",
        "picks": ["classic"]
    },
    {
        "id": 50,
        "title": "Нефть",
        "year": 2007,
        "genre": "Драма",
        "rating": 8.1,
        "poster_url": "https://picsum.photos/seed/film50/200/300",
        "overview": "Амбициозный нефтяник строит империю и теряет остатки человечности.",
        "picks": ["hits"]
    },
    # ... остальные фильмы аналогично ...
]

# Тестовые рецензии
TEST_REVIEWS = [
    {
        "text": "Фильм о силе надежды и достоинства, который мягко подводит к мощному катарсису и долго не отпускает после финала.",
        "rating": 9.5,
        "author_name": "Киноман"
    },
    {
        "text": "Один из тех редких случаев, когда душевность и драматизм идеально уравновешены.",
        "rating": 9.0,
        "author_name": "Критик"
    },
    {
        "text": "Нолан превращает супергеройский фильм в мрачную криминальную драму с одним из лучших злодеев в истории кино.",
        "rating": 9.2,
        "author_name": "Рецензент"
    },
    {
        "text": "Интеллектуальный блокбастер, который предлагает зрителю собрать головоломку из снов и воспоминаний.",
        "rating": 8.8,
        "author_name": "Кинообозреватель"
    },
    {
        "text": "Космическая драма о родительской любви и цене прогресса, совмещающая научные идеи и искренние эмоции.",
        "rating": 8.7,
        "author_name": "Научный журналист"
    },
]

def create_test_users():
    """Создает тестовых пользователей если их нет"""
    with Session(engine) as session:
        try:
            users_created = []
            
            # Создаем администратора
            admin = session.query(SimpleUser).filter(SimpleUser.username == "admin").first()
            if not admin:
                admin = SimpleUser(
                    username="admin",
                    email="admin@kinovzor.ru",
                    password_hash=get_password_hash("1234"),
                    is_active=True,
                    is_superuser=True
                )
                session.add(admin)
                users_created.append("admin")
            
            # Создаем обычного пользователя
            user = session.query(SimpleUser).filter(SimpleUser.username == "user").first()
            if not user:
                user = SimpleUser(
                    username="user",
                    email="user@kinovzor.ru",
                    password_hash=get_password_hash("1234"),
                    is_active=True,
                    is_superuser=False
                )
                session.add(user)
                users_created.append("user")
            
            # Создаем модератора
            moderator = session.query(SimpleUser).filter(SimpleUser.username == "moderator").first()
            if not moderator:
                moderator = SimpleUser(
                    username="moderator",
                    email="moderator@kinovzor.ru",
                    password_hash=get_password_hash("1234"),
                    is_active=True,
                    is_superuser=False
                )
                session.add(moderator)
                users_created.append("moderator")
            
            session.commit()
            
            if users_created:
                logger.info(f"✅ Созданы пользователи: {', '.join(users_created)}")
            else:
                logger.info("ℹ️ Все пользователи уже существуют")
            
            # Возвращаем ID пользователей
            admin_user = session.query(SimpleUser).filter(SimpleUser.username == "admin").first()
            return admin_user.id if admin_user else 1
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Ошибка при создании пользователей: {e}")
            import traceback
            traceback.print_exc()
            return 1

def create_picks(admin_id):
    """Создает подборки"""
    with Session(engine) as session:
        try:
            picks_data = [
                {"name": "Хиты", "slug": "hits", "description": "Самые популярные фильмы"},
                {"name": "Новинки", "slug": "new", "description": "Новые поступления"},
                {"name": "Классика", "slug": "classic", "description": "Великие классические фильмы"},
            ]
            
            picks_created = []
            
            for pick_data in picks_data:
                pick = session.query(SimplePick).filter(SimplePick.slug == pick_data["slug"]).first()
                if not pick:
                    pick = SimplePick(
                        name=pick_data["name"],
                        slug=pick_data["slug"],
                        description=pick_data["description"],
                        created_by=admin_id
                    )
                    session.add(pick)
                    picks_created.append(pick_data["name"])
            
            session.commit()
            
            if picks_created:
                logger.info(f"✅ Созданы подборки: {', '.join(picks_created)}")
            else:
                logger.info("ℹ️ Все подборки уже существуют")
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Ошибка при создании подборок: {e}")
            import traceback
            traceback.print_exc()

def load_movies_and_picks(admin_id):
    """Загружает фильмы и связывает их с подборками"""
    with Session(engine) as session:
        try:
            # Получаем подборки из базы
            picks = {}
            for pick in session.query(SimplePick).all():
                picks[pick.slug] = pick.id
            
            movies_loaded = 0
            movie_picks_added = 0
            
            for movie_data in MOVIES:
                # Проверяем существование
                existing = session.query(SimpleMovie).filter(SimpleMovie.id == movie_data["id"]).first()
                if existing:
                    logger.info(f"⚠️ Фильм '{movie_data['title']}' уже существует, пропускаем...")
                    continue
                
                # Создаем фильм
                movie = SimpleMovie(
                    id=movie_data["id"],
                    title=movie_data["title"],
                    year=movie_data["year"],
                    genre=movie_data["genre"],
                    rating=movie_data["rating"],
                    overview=movie_data["overview"],
                    poster_url=movie_data.get("poster_url") or movie_data.get("poster"),
                    created_by=admin_id
                )
                session.add(movie)
                session.flush()  # Получаем ID фильма
                
                # Добавляем связи с подборками если указаны
                if "picks" in movie_data:
                    for pick_slug in movie_data["picks"]:
                        pick_id = picks.get(pick_slug)
                        if pick_id:
                            # Проверяем, не добавлен ли уже фильм в эту подборку
                            existing = session.query(SimpleMoviePick).filter(
                                SimpleMoviePick.movie_id == movie.id,
                                SimpleMoviePick.pick_id == pick_id
                            ).first()
                            if not existing:
                                movie_pick = SimpleMoviePick(movie_id=movie.id, pick_id=pick_id)
                                session.add(movie_pick)
                                movie_picks_added += 1
                
                movies_loaded += 1
                if movies_loaded % 10 == 0:
                    logger.info(f"✅ Загружено {movies_loaded} фильмов...")
            
            session.commit()
            
            if movies_loaded > 0:
                logger.info(f"✅ Загружено {movies_loaded} фильмов!")
            else:
                logger.info("ℹ️ Все фильмы уже загружены")
            
            if movie_picks_added > 0:
                logger.info(f"✅ Добавлено {movie_picks_added} связей фильмов с подборками")
            
            return movies_loaded
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Ошибка при загрузке фильмов: {e}")
            import traceback
            traceback.print_exc()
            return 0

def add_test_reviews():
    """Добавляет тестовые рецензии"""
    with Session(engine) as session:
        try:
            # Проверяем, есть ли уже рецензии
            review_count = session.query(SimpleReview).count()
            
            if review_count > 0:
                logger.info(f"✅ В базе данных уже есть {review_count} рецензий")
                return 0
            
            logger.info("📝 Добавление тестовых рецензий...")
            
            # Получаем пользователей
            users = session.query(SimpleUser).limit(3).all()
            if not users:
                logger.warning("⚠️ Нет пользователей для добавления рецензий")
                return 0
            
            # Получаем несколько фильмов
            movies = session.query(SimpleMovie).limit(5).all()
            
            reviews_added = 0
            for i, movie in enumerate(movies):
                if i < len(TEST_REVIEWS):
                    review_data = TEST_REVIEWS[i]
                    user = users[i % len(users)]
                    
                    review = SimpleReview(
                        movie_id=movie.id,
                        user_id=user.id,
                        text=review_data["text"],
                        rating=review_data["rating"],
                        author_name=review_data["author_name"]
                    )
                    session.add(review)
                    reviews_added += 1
            
            session.commit()
            
            if reviews_added > 0:
                logger.info(f"✅ Добавлено {reviews_added} тестовых рецензий")
            else:
                logger.info("ℹ️ Рецензии уже добавлены")
            
            return reviews_added
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Ошибка добавления рецензий: {e}")
            import traceback
            traceback.print_exc()
            return 0

def load_simple_movies():
    """Загружает простые фильмы без сложных связей"""
    try:
        logger.info("=" * 50)
        logger.info("НАЧАЛО ЗАГРУЗКИ ДАННЫХ")
        logger.info("=" * 50)
        
        # Создаем таблицы
        logger.info("🔄 Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы созданы")
        
        # Создаем тестовых пользователей
        logger.info("👤 Создание тестовых пользователей...")
        admin_id = create_test_users()
        
        if not admin_id:
            logger.error("❌ Не удалось создать пользователей, загрузка прервана")
            return
        
        # Создаем подборки
        logger.info("📂 Создание подборок...")
        create_picks(admin_id)
        
        # Загружаем фильмы и связываем с подборками
        logger.info("🎬 Загрузка фильмов...")
        movies_loaded = load_movies_and_picks(admin_id)
        
        # Добавляем тестовые рецензии
        logger.info("📝 Добавление тестовых рецензий...")
        reviews_added = add_test_reviews()
        
        # Выводим статистику
        with Session(engine) as session:
            total_movies = session.query(SimpleMovie).count()
            total_picks = session.query(SimplePick).count()
            total_users = session.query(SimpleUser).count()
            total_reviews = session.query(SimpleReview).count()
        
        logger.info("=" * 50)
        logger.info("СТАТИСТИКА:")
        logger.info(f"🎬 Фильмы: {total_movies}")
        logger.info(f"📂 Подборки: {total_picks}")
        logger.info(f"👤 Пользователи: {total_users}")
        logger.info(f"📝 Рецензии: {total_reviews}")
        logger.info("=" * 50)
        
        if movies_loaded > 0 or reviews_added > 0:
            logger.info("✅ ЗАГРУЗКА ДАННЫХ ЗАВЕРШЕНА УСПЕШНО!")
        else:
            logger.info("ℹ️ Все данные уже загружены, ничего нового не добавлено")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Настройка логгирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data_loader.log', encoding='utf-8')
        ]
    )
    
    # Удалите старую базу данных если нужно
    if os.path.exists("movies.db"):
        logger.info("🗑️ Удаляю старую базу данных...")
        os.remove("movies.db")
    
    # Запуск загрузки
    load_simple_movies()
    
