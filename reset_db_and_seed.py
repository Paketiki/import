import os

from app.database.database import engine, SessionLocal
from app.database.base import Base
from app.utils.security import get_password_hash

from app.models.users import User
from app.models.roles import Role
from app.models.picks import Pick
from app.models.movies import Movie
from app.models.reviews import Review
from app.models.movie_picks import MoviePick
from app.models.favorites import Favorite

MOVIES_DATA = [
    {"id": 1, "title": "Побег из Шоушенка", "year": 1994, "genre": "Драма", "rating": 9.3, "poster_url": "https://picsum.photos/seed/film1/200/300", "overview": "Банкир Энди Дюфрейн, обвинънный в убийстве жены и её любовника, попадает в тюрьму Шоушенк.", "picks": ["hits", "classic"]},
    {"id": 2, "title": "Тёмный рыцарь", "year": 2008, "genre": "Боевик", "rating": 9.0, "poster_url": "https://picsum.photos/seed/film2/200/300", "overview": "Бэтмен вступает в смертельную игру с Джокером, чья цель — погрузить город в хаос.", "picks": ["hits"]},
    {"id": 3, "title": "Начало", "year": 2010, "genre": "Фантастика", "rating": 8.8, "poster_url": "https://picsum.photos/seed/film3/200/300", "overview": "Профессиональный вор, специализирующийся на проникновении в сны, получает шанс на искупление.", "picks": ["hits", "new"]},
    {"id": 4, "title": "Интерстеллар", "year": 2014, "genre": "Фантастика", "rating": 8.6, "poster_url": "https://picsum.photos/seed/film4/200/300", "overview": "Команда исследователей отправляется через червоточину в поисках нового дома для человечества.", "picks": ["hits", "new"]},
    {"id": 5, "title": "Форрест Гамп", "year": 1994, "genre": "Драма", "rating": 8.9, "poster_url": "https://picsum.photos/seed/film5/200/300", "overview": "История простодушного Форреста, который становится свидетелем важнейших событий в истории УСА.", "picks": ["classic"]},
    {"id": 6, "title": "Матрица", "year": 1999, "genre": "Фантастика", "rating": 8.7, "poster_url": "https://picsum.photos/seed/film6/200/300", "overview": "Программист Нео узнаёт, что реальность — всего лишь симуляция, созданная машинами.", "picks": ["classic"]},
    {"id": 7, "title": "Однажды в... Голливуде", "year": 2019, "genre": "Комедия", "rating": 7.7, "poster_url": "https://picsum.photos/seed/film7/200/300", "overview": "Актър Рик Далтон и его дублёр Клифф Бут пытаются найти себя в меняющемся Голливуде 60-х.", "picks": ["new"]},
    {"id": 8, "title": "Паразиты", "year": 2019, "genre": "Драма", "rating": 8.5, "poster_url": "https://picsum.photos/seed/film8/200/300", "overview": "Бедная семья постепенно захватывает места в доме богатых, притворяясь специалистами.", "picks": ["hits", "new"]},
    {"id": 9, "title": "Бегущий по лезвию 2049", "year": 2017, "genre": "Фантастика", "rating": 8.0, "poster_url": "https://picsum.photos/seed/film9/200/300", "overview": "Новый бегущий по лезвию раскрывает тайну, способную изменить отношения людей и репликантов.", "picks": ["new"]},
    {"id": 10, "title": "Криминальное чтиво", "year": 1994, "genre": "Боевик", "rating": 8.9, "poster_url": "https://picsum.photos/seed/film10/200/300", "overview": "Переплетающиеся истории гангстеров, боксёра и грабителей в Лос-Анджелесе.", "picks": ["classic"]},
    {"id": 11, "title": "Крёстный отец", "year": 1972, "genre": "Драма", "rating": 9.2, "poster_url": "https://picsum.photos/seed/film11/200/300", "overview": "Сага о мафиозном клане Корлеоне и передаче власти от отца к сыну.", "picks": ["classic", "hits"]},
    {"id": 12, "title": "Крёстный отец 2", "year": 1974, "genre": "Драма", "rating": 9.0, "poster_url": "https://picsum.photos/seed/film12/200/300", "overview": "Параллельная история молодого Вито и взросления Майкла Корлеоне.", "picks": ["classic"]},
    {"id": 13, "title": "Список Шиндлера", "year": 1993, "genre": "Драма", "rating": 9.0, "poster_url": "https://picsum.photos/seed/film13/200/300", "overview": "Немецкий промышленник спасает сотни евреев во время Холокоста.", "picks": ["classic", "hits"]},
    {"id": 14, "title": "Зелёная миля", "year": 1999, "genre": "Драма", "rating": 9.0, "poster_url": "https://picsum.photos/seed/film14/200/300", "overview": "Тюремный надзиратель встречает осужденного с необычным даром.", "picks": ["hits", "classic"]},
    {"id": 15, "title": "Властелин колец: Братство Кольца", "year": 2001, "genre": "Фэнтези", "rating": 8.8, "poster_url": "https://picsum.photos/seed/film15/200/300", "overview": "Хоббит Фродо отправляется в опасное путешествие, чтобы уничтожить Кольцо Всевластья.", "picks": ["hits", "classic"]},
    {"id": 16, "title": "Властелин колец: Две крепости", "year": 2002, "genre": "Фэнтези", "rating": 8.8, "poster_url": "https://picsum.photos/seed/film16/200/300", "overview": "Братство распалось, но борьба с силами Саурона продолжается на разных фронтах.", "picks": ["classic"]},
    {"id": 17, "title": "Властелин колец: Возвращение короля", "year": 2003, "genre": "Фэнтези", "rating": 8.9, "poster_url": "https://picsum.photos/seed/film17/200/300", "overview": "Финальная битва за Средиземье и последняя попытка уничтожить Кольцо.", "picks": ["hits", "classic"]},
    {"id": 18, "title": "Бойцовский клуб", "year": 1999, "genre": "Драма", "rating": 8.8, "poster_url": "https://picsum.photos/seed/film18/200/300", "overview": "Офисный работник создает подпольный клуб, где мужчины избивают друг друга ради ощущения жизни.", "picks": ["classic"]},
    {"id": 19, "title": "Пираты Карибского моря: Проклятие Чёрной жемчужины", "year": 2003, "genre": "Боевик", "rating": 8.0, "poster_url": "https://picsum.photos/seed/film19/200/300", "overview": "Экстравагантный капитан Джек Воробей ввязывается в приключение с проклятыми пиратами.", "picks": ["hits"]},
    {"id": 20, "title": "Гладиатор", "year": 2000, "genre": "Боевик", "rating": 8.5, "poster_url": "https://picsum.photos/seed/film20/200/300", "overview": "Римский полководец становится рабом и выходит на арену, чтобы отомстить за семью.", "picks": ["classic"]},
    {"id": 21, "title": "Титаник", "year": 1997, "genre": "Драма", "rating": 8.0, "poster_url": "https://picsum.photos/seed/film21/200/300", "overview": "Остория любви на фоне крушения легендарного лайнера Титаник.", "picks": ["classic", "hits"]},
    {"id": 22, "title": "Индиана Джонс: В поисках утраченного ковчега", "year": 1981, "genre": "Боевик", "rating": 8.4, "poster_url": "https://picsum.photos/seed/film22/200/300", "overview": "Археолог Индиана Джонс пытается опередить нацистов в поисках Ковчега Завета.", "picks": ["classic"]},
    {"id": 23, "title": "Назад в будущее", "year": 1985, "genre": "Фантастика", "rating": 8.5, "poster_url": "https://picsum.photos/seed/film23/200/300", "overview": "Подросток Марти МакФлай случайно отправляется в прошлое на машине времени.", "picks": ["classic"]},
    {"id": 24, "title": "Терминатор 2: Судный день", "year": 1991, "genre": "Боевик", "rating": 8.5, "poster_url": "https://picsum.photos/seed/film24/200/300", "overview": "Киборг из будущего должен защитить мальчика Джона Коннора от более совершенной машины убийцы.", "picks": ["classic", "hits"]},
    {"id": 25, "title": "Чужой", "year": 1979, "genre": "Ужасы", "rating": 8.4, "poster_url": "https://picsum.photos/seed/film25/200/300", "overview": "Экипаж космического корабля сталкивается с неизвестной формой жизни.", "picks": ["classic"]},
    {"id": 26, "title": "Чужие", "year": 1986, "genre": "Боевик", "rating": 8.3, "poster_url": "https://picsum.photos/seed/film26/200/300", "overview": "Рипли возвращается на планету, где впервые столкнулся с ксеноморфом, но теперь там целая колония.", "picks": ["classic"]},
    {"id": 27, "title": "Город Бога", "year": 2002, "genre": "Драма", "rating": 8.6, "poster_url": "https://picsum.photos/seed/film27/200/300", "overview": "История роста преступности в трущобах Рио-де-Жанейро глазами подростков.", "picks": ["hits"]},
    {"id": 28, "title": "Краса по-американски", "year": 1999, "genre": "Драма", "rating": 8.4, "poster_url": "https://picsum.photos/seed/film28/200/300", "overview": "Кризис среднего возраста толкает главного героя на попытку изменить свою жизнь.", "picks": ["classic"]},
    {"id": 29, "title": "Большой Лебовски", "year": 1998, "genre": "Комедия", "rating": 8.1, "poster_url": "https://picsum.photos/seed/film29/200/300", "overview": "Флегматичный Чувак оказывается ввлёчен в детективную историю из-за ошибки с личностью.", "picks": ["classic"]},
    {"id": 30, "title": "Амели", "year": 2001, "genre": "Комедия", "rating": 8.3, "poster_url": "https://picsum.photos/seed/film30/200/300", "overview": "Застенчивая Амели решает тайно помогать людям вокруг и менять их жизнь к лучшему.", "picks": ["hits"]},
    {"id": 31, "title": "Молчание ягнят", "year": 1991, "genre": "Триллер", "rating": 8.6, "poster_url": "https://picsum.photos/seed/film31/200/300", "overview": "Молодая агент ФБР обращается за помощью к заключенному маньяку Ганнибалу Лектеру.", "picks": ["classic"]},
    {"id": 32, "title": "Семь", "year": 1995, "genre": "Триллер", "rating": 8.6, "poster_url": "https://picsum.photos/seed/film32/200/300", "overview": "Два детектива охотятся за серийным убийцей, вдохновляющимся семью смертными грехами.", "picks": ["classic", "hits"]},
    {"id": 33, "title": "Престиж", "year": 2006, "genre": "Драма", "rating": 8.5, "poster_url": "https://picsum.photos/seed/film33/200/300", "overview": "Два фокусника превращают соперничество в разрушительную одержимость.", "picks": ["hits"]},
    {"id": 34, "title": "Остров проклятых", "year": 2010, "genre": "Триллер", "rating": 8.1, "poster_url": "https://picsum.photos/seed/film34/200/300", "overview": "Маршал УСА прибывает в психиатрическую клинику на острове, чтобы расследовать исчезновение пациентки.", "picks": ["hits"]},
    {"id": 35, "title": "В джазе только девушки", "year": 1959, "genre": "Комедия", "rating": 8.5, "poster_url": "https://picsum.photos/seed/film35/200/300", "overview": "Два музыканта переодеваются женщинами, чтобы скрыться от гангстеров.", "picks": ["classic"]},
    {"id": 36, "title": "Таксист", "year": 1976, "genre": "Драма", "rating": 8.3, "poster_url": "https://picsum.photos/seed/film36/200/300", "overview": "Одинокий таксист постепенно теряет связь с реальностью на фоне ночного Нью-Йорка.", "picks": ["classic"]},
    {"id": 37, "title": "Пролетая над гнездом кукушки", "year": 1975, "genre": "Драма", "rating": 8.7, "poster_url": "https://picsum.photos/seed/film37/200/300", "overview": "Харизматичный заключённый попадает в психиатрическую клинику и сталкивается с жестким порядком.", "picks": ["classic"]},
    {"id": 38, "title": "Ла-Ла Ленд", "year": 2016, "genre": "Мюзикл", "rating": 8.0, "poster_url": "https://picsum.photos/seed/film38/200/300", "overview": "Джазовый музыкант и актриса пытаются построить карьеру и сохранить отношения.", "picks": ["new"]},
    {"id": 39, "title": "Безумный Макс: Дорога ярости", "year": 2015, "genre": "Боевик", "rating": 8.1, "poster_url": "https://picsum.photos/seed/film39/200/300", "overview": "В постапокалиптической пустыне беглецы пытаются уйти от тирана на боевой фуре.", "picks": ["hits", "new"]},
    {"id": 40, "title": "Социальная сеть", "year": 2010, "genre": "Драма", "rating": 7.7, "poster_url": "https://picsum.photos/seed/film40/200/300", "overview": "Остория создания Facebook и конфликта между его основателями.", "picks": ["new"]},
    {"id": 41, "title": "Гравитация", "year": 2013, "genre": "Фантастика", "rating": 7.7, "poster_url": "https://picsum.photos/seed/film41/200/300", "overview": "Двое астронавтов пытаются выжить после катастрофы на орбите Земли.", "picks": ["new"]},
    {"id": 42, "title": "Выживший", "year": 2015, "genre": "Драма", "rating": 7.8, "poster_url": "https://picsum.photos/seed/film42/200/300", "overview": "Охотник Хью Гласс, оставленный умирать, пытается добраться до тех, кто его предал.", "picks": ["new"]},
    {"id": 43, "title": "Джанго освобождённый", "year": 2012, "genre": "Вестерн", "rating": 8.4, "poster_url": "https://picsum.photos/seed/film43/200/300", "overview": "Освобождённый раб объединяется с охотником за головами, чтобы спасти жену.", "picks": ["hits"]},
    {"id": 44, "title": "Мстители: Финаль", "year": 2019, "genre": "Боевик", "rating": 8.4, "poster_url": "https://picsum.photos/seed/film44/200/300", "overview": "Герои объединяются, чтобы исправить последствия щелчка Таноса.", "picks": ["hits", "new"]},
    {"id": 45, "title": "Храброе сердце", "year": 1995, "genre": "Драма", "rating": 8.3, "poster_url": "https://picsum.photos/seed/film45/200/300", "overview": "Шотландский воин Уильям Уоллас поднимает восстание против английской короны.", "picks": ["classic"]},
    {"id": 46, "title": "Лица со шрамами", "year": 1983, "genre": "Драма", "rating": 8.3, "poster_url": "https://picsum.photos/seed/film46/200/300", "overview": "Иммигрант Тони Монтана поднимается на вершину криминального мира Майами.", "picks": ["classic"]},
    {"id": 47, "title": "Реквием по мечте", "year": 2000, "genre": "Драма", "rating": 8.3, "poster_url": "https://picsum.photos/seed/film47/200/300", "overview": "Остория нескольких людей, чьи мечты разрушаются под тяжестью зависимостей.", "picks": ["hits"]},
    {"id": 48, "title": "Под покровом ночи", "year": 2016, "genre": "Триллер", "rating": 7.5, "poster_url": "https://picsum.photos/seed/film48/200/300", "overview": "Героиня читает мрачный роман бывшего мужа, который отражает их прошлое.", "picks": ["new"]},
    {"id": 49, "title": "Преступление и наказание (советская экранизация)", "year": 1969, "genre": "Драма", "rating": 7.9, "poster_url": "https://picsum.photos/seed/film49/200/300", "overview": "Экранизация романа Достоевского о преступлении, раскаянии и поиске смысла.", "picks": ["classic"]},
    {"id": 50, "title": "Нефть", "year": 2007, "genre": "Драма", "rating": 8.1, "poster_url": "https://picsum.photos/seed/film50/200/300", "overview": "Амбициозный нефтянык строит империю и теряет остатки человечности.", "picks": ["hits"]},
]

PICKS_DATA = [
    {"id": 1, "name": "Хиты", "slug": "hits", "description": "Самые популярные фильмы"},
    {"id": 2, "name": "Новинки", "slug": "new", "description": "Новые поступления"},
    {"id": 3, "name": "Классика", "slug": "classic", "description": "Классиковая кино"},
]

DEMO_USERS = [
    {"id": 1, "username": "user", "email": "user@example.com", "password": "1234", "is_active": True, "is_superuser": False},
    {"id": 2, "username": "moderator", "email": "moderator@example.com", "password": "1234", "is_active": True, "is_superuser": True},
]

def reset_and_seed_db(db_path: str = "movies.db") -> None:
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Удалена БД")

    Base.metadata.create_all(bind=engine)
    print("✓ Таблицы созданы")

    db = SessionLocal()
    try:
        for user_data in DEMO_USERS:
            user = User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                is_active=user_data["is_active"],
                is_superuser=user_data["is_superuser"],
            )
            db.add(user)
        db.commit()
        print(f"✓ {len(DEMO_USERS)} users: user/1234, moderator/1234")

        slug_to_id = {}
        for pick_data in PICKS_DATA:
            db.add(Pick(**pick_data))
        db.commit()
        print(f"✓ {len(PICKS_DATA)} подборок")

        for pick in db.query(Pick).all():
            slug_to_id[pick.slug] = pick.id

        for item in MOVIES_DATA:
            movie = Movie(
                id=item["id"],
                title=item["title"],
                overview=item["overview"],
                year=item["year"],
                genre=item["genre"],
                rating=item["rating"],
                poster_url=item.get("poster_url", ""),
                created_by=None,
            )
            db.add(movie)
            db.flush()

            for slug in item.get("picks", []):
                pick_id = slug_to_id.get(slug)
                if pick_id:
                    db.add(MoviePick(movie_id=movie.id, pick_id=pick_id))

        db.commit()
        print(f"✓ {len(MOVIES_DATA)} реальных фильмов (all with 1+ picks)")
        print("\n✅ Ок.")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed_db()
