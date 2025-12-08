// Simple in-memory "database" of users
const USERS = [
  { username: "user", password: "1234", role: "viewer" },
  { username: "admin", password: "1234", role: "admin" },
];

// Movie data
let MOVIES = [
  {
    id: 1,
    title: "Побег из Шоушенка",
    year: 1994,
    genre: "Драма",
    rating: 9.3,
    picks: ["hits", "classic"],
    poster: "https://picsum.https://avatars.mds.yandex.net/i?id=2bd4cb47eefa54d04e4a62294ecb9213_l-5231722-images-thumbs&n=13/seed/film1/200/300",
    overview:
      "Банкир Энди Дюфрейн, обвинённый в убийстве жены и её любовника, попадает в тюрьму Шоушенк.",
    review:
      "Фильм о силе надежды и достоинства, который мягко подводит к мощному катарсису и долго не отпускает после финала.",
    extraReviews: [
      "Один из тех редких случаев, когда душевность и драматизм идеально уравновешены.",
    ],
  },
  {
    id: 2,
    title: "Тёмный рыцарь",
    year: 2008,
    genre: "Боевик",
    rating: 9.0,
    picks: ["hits"],
    poster: "https://https://avatars.mds.yandex.net/i?id=643f98155234df70c1548839499d9e07_l-5234950-images-thumbs&n=13.photos/seed/film2/200/300",
    overview:
      "Бэтмен вступает в смертельную игру с Джокером, чья цель — погрузить город в хаос.",
    review:
      "Нолан превращает супергеройский фильм в мрачную криминальную драму с одним из лучших злодеев в истории кино.",
    extraReviews: [
      "Напряжение не спадает ни на минуту, а моральные дилеммы героев остаются в голове надолго.",
    ],
  },
  {
    id: 3,
    title: "Начало",
    year: 2010,
    genre: "Фантастика",
    rating: 8.8,
    picks: ["hits", "new"],
    poster: "https://picsum.https://biographe.ru/wp-content/uploads/2024/10/1233123.jpg/seed/film3/200/300",
    overview:
      "Профессиональный вор, специализирующийся на проникновении в сны, получает шанс на искупление.",
    review:
      "Интеллектуальный блокбастер, который предлагает зрителю собрать головоломку из снов и воспоминаний.",
    extraReviews: [
      "Фильм, к которому хочется возвращаться, чтобы заметить новые детали в каждом уровне сна.",
    ],
  },
  {
    id: 4,
    title: "Интерстеллар",
    year: 2014,
    genre: "Фантастика",
    rating: 8.6,
    picks: ["hits", "new"],
    poster: "https://picsum.https://avatars.mds.yandex.net/i?id=75504f4e1c79f075cf7c6a5206dc8081_l-5680191-images-thumbs&n=13/seed/film4/200/300",
    overview:
      "Команда исследователей отправляется через червоточину в поисках нового дома для человечества.",
    review:
      "Космическая драма о родительской любви и цене прогресса, совмещающая научные идеи и искренние эмоции.",
    extraReviews: [
      "Редкий пример фильма, где масштаб вселенной не перекрывает человеческую историю.",
    ],
  },
  {
    id: 5,
    title: "Форрест Гамп",
    year: 1994,
    genre: "Драма",
    rating: 8.9,
    picks: ["classic"],
    poster: "https://picsum.https://i.guim.co.uk/img/media/78eb1f6bd0f92d4d3cf19f5bddda1a902e2a6fcd/0_95_2371_1422/master/2371.jpg?width=1200&height=1200&quality=85&auto=format&fit=crop&s=4b18b0ace0dfc010f3a2fba9aa797665/seed/film5/200/300",
    overview:
      "История простодушного Форреста, который становится свидетелем важнейших событий в истории США.",
    review:
      "Трогательная притча о доброте и принятии, в которой хочется улыбаться и плакать одновременно.",
    extraReviews: [
      "Фильм, к которому возвращаются как к старому другу — он всегда дарит немного тепла.",
    ],
  },
  {
    id: 6,
    title: "Матрица",
    year: 1999,
    genre: "Фантастика",
    rating: 8.7,
    picks: ["classic"],
    poster: "https://picsum.https://avatars.mds.yandex.net/i?id=df2a62a8c3862c55001ef3ee27bcad43_l-4011747-images-thumbs&n=13/seed/film6/200/300",
    overview:
      "Программист Нео узнаёт, что реальность — всего лишь симуляция, созданная машинами.",
    review:
      "Революционный боевик, который подарил кино новый визуальный язык и заставил задуматься о природе реальности.",
    extraReviews: [
      "Удивительно, как фильм конца 90-х до сих пор остаётся свежим и актуальным.",
    ],
  },
  {
    id: 7,
    title: "Однажды в Голливуде",
    year: 2019,
    genre: "Комедия",
    rating: 7.7,
    picks: ["new"],
    poster: "https://picsum.https://cache3.youla.io/files/images/780_780/5d/b1/5db17fa55eaa9e13aa4482e6.jpg/seed/film7/200/300",
    overview:
      "Актёр Рик Далтон и его дублёр Клифф Бут пытаются найти себя в меняющемся Голливуде 60-х.",
    review:
      "Неторопливая, ностальгическая прогулка по мифическому Голливуду, где каждый кадр — любовное письмо кино.",
    extraReviews: [
      "Финал балансирует между жестокостью и сказкой, оставляя очень странное, но яркое послевкусие.",
    ],
  },
  {
    id: 8,
    title: "Паразиты",
    year: 2019,
    genre: "Драма",
    rating: 8.5,
    picks: ["hits", "new"],
    poster: "https://picsum.https://thumbnails.odycdn.com/card/s:1280:720/quality:85/plain/https://thumbs.odycdn.com/ca8c9d0d3423c2ebdf82f6ddcecd7bd9.jpg/seed/film8/200/300",
    overview:
      "Бедная семья постепенно захватывает места в доме богатых, притворяясь специалистами.",
    review:
      "Идеально выстроенная социальная сатира, которая незаметно превращается в мрачный триллер.",
    extraReviews: [
      "Каждый поворот сюжета выбивает почву из-под ног и заставляет пересмотреть симпатии к героям.",
    ],
  },
  {
    id: 9,
    title: "Бегущий по лезвию 2049",
    year: 2017,
    genre: "Фантастика",
    rating: 8.0,
    picks: ["new"],
    poster: "https://picsum.photos/seed/film9/200/300",
    overview:
      "Новый бегущий по лезвию раскрывает тайну, способную изменить отношения людей и репликантов.",
    review:
      "Медитативный неонуар, в котором визуал и звук работают как единое гипнотическое полотно.",
    extraReviews: [
      "Фильм требует терпения, но щедро награждает атмосферой и философскими вопросами.",
    ],
  },
  {
    id: 10,
    title: "Криминальное чтиво",
    year: 1994,
    genre: "Боевик",
    rating: 8.9,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film10/200/300",
    overview:
      "Переплетающиеся истории гангстеров, боксёра и грабителей в Лос-Анджелесе.",
    review:
      "Культовый фильм с фирменными диалогами и нелинейным монтажом, который до сих пор копируют.",
    extraReviews: [
      "Каждая сцена — отдельный маленький шедевр, который хочется цитировать.",
    ],
  },
  {
    id: 11,
    title: "Крёстный отец",
    year: 1972,
    genre: "Драма",
    rating: 9.2,
    picks: ["classic", "hits"],
    poster: "https://picsum.photos/seed/film11/200/300",
    overview:
      "Сага о мафиозном клане Корлеоне и передаче власти от отца к сыну.",
    review:
      "Образцовый образец гангстерской драмы, в которой семейная трагедия важнее криминала.",
    extraReviews: [
      "Медленный ритм только усиливает ощущение трагического падения героев.",
    ],
  },
  {
    id: 12,
    title: "Крёстный отец 2",
    year: 1974,
    genre: "Драма",
    rating: 9.0,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film12/200/300",
    overview:
      "Параллельная история молодого Вито и взросления Майкла Корлеоне.",
    review:
      "Редкий сиквел, который не уступает оригиналу и даже расширяет его трагедию.",
  },
  {
    id: 13,
    title: "Список Шиндлера",
    year: 1993,
    genre: "Драма",
    rating: 9.0,
    picks: ["classic", "hits"],
    poster: "https://picsum.photos/seed/film13/200/300",
    overview:
      "Немецкий промышленник спасает сотни евреев во время Холокоста.",
    review:
      "Жёсткая и честная картина о геноциде, которая не оставляет шанса остаться равнодушным.",
    extraReviews: [
      "Чёрно-белое изображение только усиливает документальное ощущение происходящего.",
    ],
  },
  {
    id: 14,
    title: "Зелёная миля",
    year: 1999,
    genre: "Драма",
    rating: 9.0,
    picks: ["hits", "classic"],
    poster: "https://picsum.photos/seed/film14/200/300",
    overview:
      "Тюремный надзиратель встречает осуждённого с необычным даром.",
    review:
      "Трогательное сочетание мистики и тюремной драмы, которое бьёт прямо в сердце.",
  },
  {
    id: 15,
    title: "Властелин колец: Братство Кольца",
    year: 2001,
    genre: "Фэнтези",
    rating: 8.8,
    picks: ["hits", "classic"],
    poster: "https://picsum.photos/seed/film15/200/300",
    overview:
      "Хоббит Фродо отправляется в опасное путешествие, чтобы уничтожить Кольцо Всевластья.",
    review:
      "Эпическое фэнтези, задавшее планку масштабных экранизаций на годы вперёд.",
  },
  {
    id: 16,
    title: "Властелин колец: Две крепости",
    year: 2002,
    genre: "Фэнтези",
    rating: 8.8,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film16/200/300",
    overview:
      "Братство распалось, но борьба с силами Саурона продолжается на разных фронтах.",
    review:
      "Средняя часть трилогии, в которой битвы становятся масштабнее, а ставки — выше.",
  },
  {
    id: 17,
    title: "Властелин колец: Возвращение короля",
    year: 2003,
    genre: "Фэнтези",
    rating: 8.9,
    picks: ["hits", "classic"],
    poster: "https://picsum.photos/seed/film17/200/300",
    overview:
      "Финальная битва за Средиземье и последняя попытка уничтожить Кольцо.",
    review:
      "Фееричный финал трилогии, который соединяет масштабные битвы и личные истории героев.",
  },
  {
    id: 18,
    title: "Бойцовский клуб",
    year: 1999,
    genre: "Драма",
    rating: 8.8,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film18/200/300",
    overview:
      "Офисный работник создаёт подпольный клуб, где мужчины избивают друг друга ради ощущения жизни.",
    review:
      "Провокационный фильм о кризисе идентичности и культуре потребления.",
  },
  {
    id: 19,
    title: "Пираты Карибского моря: Проклятие Чёрной жемчужины",
    year: 2003,
    genre: "Боевик",
    rating: 8.0,
    picks: ["hits"],
    poster: "https://picsum.photos/seed/film19/200/300",
    overview:
      "Экстравагантный капитан Джек Воробей ввязывается в приключение с проклятыми пиратами.",
    review:
      "Развлекательный приключенческий фильм, который держится на харизме Джонни Деппа.",
  },
  {
    id: 20,
    title: "Гладиатор",
    year: 2000,
    genre: "Боевик",
    rating: 8.5,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film20/200/300",
    overview:
      "Римский полководец становится рабом и выходит на арену, чтобы отомстить за семью.",
    review:
      "Исторический эпос с сильной эмоциональной линией и мощными батальными сценами.",
  },
  {
    id: 21,
    title: "Титаник",
    year: 1997,
    genre: "Драма",
    rating: 8.0,
    picks: ["classic", "hits"],
    poster: "https://picsum.photos/seed/film21/200/300",
    overview:
      "История любви на фоне крушения легендарного лайнера «Титаник».",
    review:
      "Мелодрама и катастрофа, сплетённые в один большой кинематографический аттракцион.",
  },
  {
    id: 22,
    title: "Индиана Джонс: В поисках утраченного ковчега",
    year: 1981,
    genre: "Боевик",
    rating: 8.4,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film22/200/300",
    overview:
      "Археолог Индиана Джонс пытается опередить нацистов в поисках Ковчега Завета.",
    review:
      "Эталонное приключенческое кино, где каждое препятствие — запоминающаяся сцена.",
  },
  {
    id: 23,
    title: "Назад в будущее",
    year: 1985,
    genre: "Фантастика",
    rating: 8.5,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film23/200/300",
    overview:
      "Подросток Марти МакФлай случайно отправляется в прошлое на машине времени.",
    review:
      "Идеальная смесь фантастики, комедии и семейной драмы, которая до сих пор смотрится на одном дыхании.",
  },
  {
    id: 24,
    title: "Терминатор 2: Судный день",
    year: 1991,
    genre: "Боевик",
    rating: 8.5,
    picks: ["classic", "hits"],
    poster: "https://picsum.photos/seed/film24/200/300",
    overview:
      "Киборг из будущего должен защитить мальчика Джона Коннора от более совершенной машины убийства.",
    review:
      "Один из лучших боевиков всех времён с революционными спецэффектами.",
  },
  {
    id: 25,
    title: "Чужой",
    year: 1979,
    genre: "Ужасы",
    rating: 8.4,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film25/200/300",
    overview:
      "Экипаж космического корабля сталкивается с неизвестной формой жизни.",
    review:
      "Клаустрофобный космический хоррор, который берёт не количеством монстров, а атмосферой.",
  },
  {
    id: 26,
    title: "Чужие",
    year: 1986,
    genre: "Боевик",
    rating: 8.3,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film26/200/300",
    overview:
      "Рипли возвращается на планету, где впервые столкнулась с ксеноморфом, но теперь там целая колония.",
    review:
      "Удачное превращение хоррора в военный боевик, не потерявший напряжения оригинала.",
  },
  {
    id: 27,
    title: "Город Бога",
    year: 2002,
    genre: "Драма",
    rating: 8.6,
    picks: ["hits"],
    poster: "https://picsum.photos/seed/film27/200/300",
    overview:
      "История роста преступности в трущобах Рио-де-Жанейро глазами подростков.",
    review:
      "Жестокая, но невероятно живая картина о том, как легко насилие становится нормой.",
  },
  {
    id: 28,
    title: "Красота по-американски",
    year: 1999,
    genre: "Драма",
    rating: 8.4,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film28/200/300",
    overview:
      "Кризис среднего возраста толкает главного героя на попытку изменить свою жизнь.",
    review:
      "Ироничный и грустный взгляд на «идеальную» пригородную жизнь и внутреннюю пустоту.",
  },
  {
    id: 29,
    title: "Большой Лебовски",
    year: 1998,
    genre: "Комедия",
    rating: 8.1,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film29/200/300",
    overview:
      "Флегматичный Чувак оказывается втянутым в детективную историю из-за ошибки с личностью.",
    review:
      "Абсурдная криминальная комедия, которая за годы превратилась в культ.",
  },
  {
    id: 30,
    title: "Амели",
    year: 2001,
    genre: "Комедия",
    rating: 8.3,
    picks: ["hits"],
    poster: "https://picsum.photos/seed/film30/200/300",
    overview:
      "Застенчивая Амели решает тайно помогать людям вокруг и менять их жизнь к лучшему.",
    review:
      "Визуальная сказка о маленьких радостях, которая поднимает настроение даже в хмурый день.",
  },
  {
    id: 31,
    title: "Молчание ягнят",
    year: 1991,
    genre: "Триллер",
    rating: 8.6,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film31/200/300",
    overview:
      "Молодая агент ФБР обращается за помощью к заключённому маньяку Ганнибалу Лектеру.",
    review:
      "Холодящий кровь триллер, который держится на дуэли двух сильных персонажей.",
  },
  {
    id: 32,
    title: "Семь",
    year: 1995,
    genre: "Триллер",
    rating: 8.6,
    picks: ["classic", "hits"],
    poster: "https://picsum.photos/seed/film32/200/300",
    overview:
      "Два детектива охотятся за серийным убийцей, вдохновляющимся семью смертными грехами.",
    review:
      "Мрачный и безжалостный фильм, финал которого сложно забыть.",
  },
  {
    id: 33,
    title: "Престиж",
    year: 2006,
    genre: "Драма",
    rating: 8.5,
    picks: ["hits"],
    poster: "https://picsum.photos/seed/film33/200/300",
    overview:
      "Два фокусника превращают соперничество в разрушительную одержимость.",
    review:
      "Стильный триллер о цене успеха, где каждый сюжетный «фокус» имеет свою жертву.",
  },
  {
    id: 34,
    title: "Остров проклятых",
    year: 2010,
    genre: "Триллер",
    rating: 8.1,
    picks: ["hits"],
    poster: "https://picsum.photos/seed/film34/200/300",
    overview:
      "Маршал США прибывает в психиатрическую клинику на острове, чтобы расследовать исчезновение пациентки.",
    review:
      "Напряжённый психологический триллер, играющий с восприятием реальности героя.",
  },
  {
    id: 35,
    title: "В джазе только девушки",
    year: 1959,
    genre: "Комедия",
    rating: 8.5,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film35/200/300",
    overview:
      "Два музыканта переодеваются женщинами, чтобы скрыться от гангстеров.",
    review:
      "Классическая комедия положений, которая до сих пор выглядит свежо и остроумно.",
  },
  {
    id: 36,
    title: "Таксист",
    year: 1976,
    genre: "Драма",
    rating: 8.3,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film36/200/300",
    overview:
      "Одинокий таксист постепенно теряет связь с реальностью на фоне ночного Нью-Йорка.",
    review:
      "Гнетущий портрет одиночества и внутреннего распада на фоне большого города.",
  },
  {
    id: 37,
    title: "Пролетая над гнездом кукушки",
    year: 1975,
    genre: "Драма",
    rating: 8.7,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film37/200/300",
    overview:
      "Харизматичный заключённый попадает в психиатрическую клинику и сталкивается с жестким порядком.",
    review:
      "Фильм о свободе и системе, который одновременно смешной и страшный.",
  },
  {
    id: 38,
    title: "Ла-Ла Ленд",
    year: 2016,
    genre: "Мюзикл",
    rating: 8.0,
    picks: ["new"],
    poster: "https://picsum.photos/seed/film38/200/300",
    overview:
      "Джазовый музыкант и актриса пытаются построить карьеру и сохранить отношения.",
    review:
      "Современный мюзикл о мечтах и компромиссах, влюблённый в классику Голливуда.",
  },
  {
    id: 39,
    title: "Безумный Макс: Дорога ярости",
    year: 2015,
    genre: "Боевик",
    rating: 8.1,
    picks: ["hits", "new"],
    poster: "https://picsum.photos/seed/film39/200/300",
    overview:
      "В постапокалиптической пустыне беглецы пытаются уйти от тирана на боевой фуре.",
    review:
      "Почти непрерывная погоня, превращённая в визуальное искусство.",
  },
  {
    id: 40,
    title: "Социальная сеть",
    year: 2010,
    genre: "Драма",
    rating: 7.7,
    picks: ["new"],
    poster: "https://picsum.photos/seed/film40/200/300",
    overview:
      "История создания Facebook и конфликта между его основателями.",
    review:
      "Динамичная драма о дружбе, амбициях и цене успеха в цифровую эпоху.",
  },
  {
    id: 41,
    title: "Гравитация",
    year: 2013,
    genre: "Фантастика",
    rating: 7.7,
    picks: ["new"],
    poster: "https://picsum.photos/seed/film41/200/300",
    overview:
      "Двое астронавтов пытаются выжить после катастрофы на орбите Земли.",
    review:
      "Иммерсивный космический триллер, который лучше всего работает на большом экране.",
  },
  {
    id: 42,
    title: "Выживший",
    year: 2015,
    genre: "Драма",
    rating: 7.8,
    picks: ["new"],
    poster: "https://picsum.photos/seed/film42/200/300",
    overview:
      "Охотник Хью Гласс, оставленный умирать, пытается добраться до тех, кто его предал.",
    review:
      "Жёсткая выживательная драма с потрясающими природными видами и физически ощутимым страданием героя.",
  },
  {
    id: 43,
    title: "Джанго освобождённый",
    year: 2012,
    genre: "Вестерн",
    rating: 8.4,
    picks: ["hits"],
    poster: "https://picsum.photos/seed/film43/200/300",
    overview:
      "Освобождённый раб объединяется с охотником за головами, чтобы спасти жену.",
    review:
      "Стильный и кровавый вестерн Тарантино с фирменными диалогами и саундтреком.",
  },
  {
    id: 44,
    title: "Мстители: Финал",
    year: 2019,
    genre: "Боевик",
    rating: 8.4,
    picks: ["hits", "new"],
    poster: "https://picsum.photos/seed/film44/200/300",
    overview:
      "Герои объединяются, чтобы исправить последствия щелчка Таноса.",
    review:
      "Эмоциональное завершение многолетней саги Marvel, работающее как большое прощание с героями.",
  },
  {
    id: 45,
    title: "Храброе сердце",
    year: 1995,
    genre: "Драма",
    rating: 8.3,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film45/200/300",
    overview:
      "Шотландский воин Уильям Уоллес поднимает восстание против английской короны.",
    review:
      "Патетический, но мощный исторический эпос с впечатляющими битвами.",
  },
  {
    id: 46,
    title: "Лица со шрамами",
    year: 1983,
    genre: "Драма",
    rating: 8.3,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film46/200/300",
    overview:
      "Иммигрант Тони Монтана поднимается на вершину криминального мира Майами.",
    review:
      "Грубое и хлёсткое исследование одержимости властью и деньгами.",
  },
  {
    id: 47,
    title: "Реквием по мечте",
    year: 2000,
    genre: "Драма",
    rating: 8.3,
    picks: ["hits"],
    poster: "https://picsum.photos/seed/film47/200/300",
    overview:
      "История нескольких людей, чьи мечты разрушаются под тяжестью зависимостей.",
    review:
      "Жестокий и визуально экспериментальный фильм, после которого сложно прийти в себя.",
  },
  {
    id: 48,
    title: "Под покровом ночи",
    year: 2016,
    genre: "Триллер",
    rating: 7.5,
    picks: ["new"],
    poster: "https://picsum.photos/seed/film48/200/300",
    overview:
      "Героиня читает мрачный роман бывшего мужа, который отражает их прошлое.",
    review:
      "Стильный неонуар о мести и чувствах вины, рассказанный через историю внутри истории.",
  },
  {
    id: 49,
    title: "Преступление и наказание (советская экранизация)",
    year: 1969,
    genre: "Драма",
    rating: 7.9,
    picks: ["classic"],
    poster: "https://picsum.photos/seed/film49/200/300",
    overview:
      "Экранизация романа Достоевского о преступлении, раскаянии и поиске смысла.",
    review:
      "Внимательное к тексту произведение, где акцент сделан на внутренней борьбе персонажей.",
  },
  {
    id: 50,
    title: "Нефть",
    year: 2007,
    genre: "Драма",
    rating: 8.1,
    picks: ["hits"],
    poster: "https://picsum.photos/seed/film50/200/300",
    overview:
      "Амбициозный нефтяник строит империю и теряет остатки человечности.",
    review:
      "Удивительно, как фильм конца 90-х до сих пор остаётся свежим и актуальным.",
  },
];

// State
let currentUser = null;
let currentPick = "all";
let currentGenre = "all";
let currentRatingFilter = "all";
let currentSearch = "";
let selectedMovieId = null;

// Elements
const body = document.body;
const moviesListEl = document.getElementById("moviesList");
const movieDetailsEl = document.getElementById("movieDetails");
const genreSelectEl = document.getElementById("genreSelect");
const searchInputEl = document.getElementById("searchInput");
const ratingButtons = document.querySelectorAll(".chip-button[data-rating]");
const pickButtons = document.querySelectorAll(".pill-button[data-pick]");
const themeToggleBtn = document.getElementById("themeToggle");
const authButton = document.getElementById("authButton");
const userBadge = document.getElementById("userBadge");
const userNameEl = document.getElementById("userName");
const userRoleEl = document.getElementById("userRole");
const logoutButton = document.getElementById("logoutButton");
const adminPanel = document.getElementById("adminPanel");
const adminAddForm = document.getElementById("adminAddForm");
const adminTitleInput = document.getElementById("adminTitle");
const adminYearInput = document.getElementById("adminYear");
const adminRatingInput = document.getElementById("adminRating");
const adminPosterInput = document.getElementById("adminPoster");
const adminOverviewInput = document.getElementById("adminOverview");
const adminReview1Input = document.getElementById("adminReview1");
const adminReview2Input = document.getElementById("adminReview2");
// Auth modal
const authModal = document.getElementById("authModal");
const closeAuthModalBtn = document.getElementById("closeAuthModal");
const tabButtons = document.querySelectorAll(".tab-button");
const tabPanels = document.querySelectorAll(".tab-panel");
const loginForm = document.getElementById("loginForm");
const loginUsernameInput = document.getElementById("loginUsername");
const loginPasswordInput = document.getElementById("loginPassword");
const loginErrorEl = document.getElementById("loginError");
const quickRoleButtons = document.querySelectorAll("[data-quick-role]");

// Initialization
initTheme();
initGenres();
renderMovies();
attachEventListeners();
selectDefaultMovie();
// ensure each movie has container for user reviews
MOVIES.forEach((m) => {
  if (!Array.isArray(m.userReviews)) {
    m.userReviews = [];
  } else {
    // normalize existing user reviews ratings to integers
    m.userReviews = m.userReviews.map((r) => ({
      ...r,
      rating: Math.round(Number(r.rating || 0)),
    }));
  }
});

function initTheme() {
  const saved = localStorage.getItem("kinovzor-theme");
  if (saved === "light") {
    body.classList.remove("theme-dark");
    body.classList.add("theme-light");
  } else {
    body.classList.remove("theme-light");
    body.classList.add("theme-dark");
  }
}

function initGenres() {
  const genres = Array.from(new Set(MOVIES.map((m) => m.genre))).sort();
  genres.forEach((g) => {
    const option = document.createElement("option");
    option.value = g;
    option.textContent = g;
    genreSelectEl.appendChild(option);
  });
}

function getFilteredMovies() {
  return MOVIES.filter((movie) => {
    if (currentPick !== "all" && !movie.picks.includes(currentPick)) {
      return false;
    }
    if (currentGenre !== "all" && movie.genre !== currentGenre) {
      return false;
    }
    if (currentRatingFilter !== "all" && movie.rating < Number(currentRatingFilter)) {
      return false;
    }
    if (currentSearch.trim()) {
      const term = currentSearch.trim().toLowerCase();
      if (!movie.title.toLowerCase().includes(term)) return false;
    }
    return true;
  });
}

function renderMovies() {
  moviesListEl.innerHTML = "";
  const movies = getFilteredMovies();

  if (movies.length === 0) {
    const empty = document.createElement("li");
    empty.className = "placeholder-text";
    empty.textContent = "По заданным фильтрам фильмы не найдены.";
    moviesListEl.appendChild(empty);
    movieDetailsEl.classList.add("empty");
    movieDetailsEl.innerHTML =
      '<p class="placeholder-text">Измените фильтры или поиск, чтобы увидеть фильмы.</p>';
    return;
  }

  movies.forEach((movie) => {
    const li = document.createElement("li");
    li.className = "movie-card";
    li.dataset.id = movie.id;

    const posterWrap = document.createElement("div");
    posterWrap.className = "movie-poster-wrapper";
    const posterImg = document.createElement("img");
    posterImg.className = "movie-poster";
    posterImg.src =
      movie.poster || "https://picsum.photos/seed/defaultposter/200/300";
    posterImg.alt = `${movie.title} постер`;
    posterWrap.appendChild(posterImg);

    const bodyWrap = document.createElement("div");
    bodyWrap.className = "movie-card-body";

    const header = document.createElement("div");
    header.className = "movie-card-header";

    const title = document.createElement("div");
    title.className = "movie-title";
    title.textContent = movie.title;

    const ratingBadge = document.createElement("div");
    ratingBadge.className = "badge-rating";
    // render integer ratings
    ratingBadge.textContent = Math.round(Number(movie.rating)).toFixed(0);

    header.appendChild(title);
    header.appendChild(ratingBadge);

    const metaRow = document.createElement("div");
    metaRow.className = "movie-meta";
    metaRow.innerHTML = `
      <span>${movie.year}</span>
      <span>•</span>
      <span>${movie.genre}</span>
    `;

    const footer = document.createElement("div");
    footer.className = "movie-card-footer";

    const picks = document.createElement("div");
    picks.className = "movie-picks";
    movie.picks.forEach((p) => {
      const pickChip = document.createElement("span");
      pickChip.className = "movie-pick-chip";
      pickChip.textContent = getPickLabel(p);
      picks.appendChild(pickChip);
    });

    const more = document.createElement("span");
    more.textContent = "Рецензии";
    more.style.cursor = "pointer";

    footer.appendChild(picks);
    footer.appendChild(more);

    bodyWrap.appendChild(header);
    bodyWrap.appendChild(metaRow);
    bodyWrap.appendChild(footer);

    li.appendChild(posterWrap);
    li.appendChild(bodyWrap);

    // click behavior: on mobile (narrow) toggle in-card expansion, otherwise use details panel
    li.addEventListener("click", () => {
      const isMobile = window.innerWidth <= 540;
      selectedMovieId = movie.id;
      if (isMobile) {
        const already = li.classList.contains("expanded");
        // collapse any other expanded card and remove their expanded content
        document.querySelectorAll(".movie-card.expanded").forEach((c) => {
          if (c !== li) {
            c.classList.remove("expanded");
            const extra = c.querySelector(".mobile-expanded");
            if (extra) extra.remove();
          }
        });
        if (already) {
          li.classList.remove("expanded");
          // remove expanded content
          const extra = li.querySelector(".mobile-expanded");
          if (extra) extra.remove();
        } else {
          li.classList.add("expanded");
          // build mobile expansion content
          const expanded = document.createElement("div");
          expanded.className = "mobile-expanded";
          expanded.style.marginTop = "8px";

          const overviewTitle = document.createElement("div");
          overviewTitle.className = "details-section-title";
          overviewTitle.textContent = "Сюжет";
          const overviewText = document.createElement("div");
          overviewText.className = "details-overview";
          overviewText.textContent = movie.overview || "";

          const reviewTitle = document.createElement("div");
          reviewTitle.className = "details-section-title";
          reviewTitle.textContent = "Рецензии";

          const reviewsContainer = document.createElement("div");

          // combine system + extra + user reviews
          const allReviews = [];
          if (movie.review) {
            allReviews.push({
              author: "КиноВзор",
              role: "system",
              rating: Math.round(Number(movie.rating)),
              text: movie.review,
            });
          }
          if (Array.isArray(movie.extraReviews)) {
            movie.extraReviews.forEach((text) => {
              if (!text) return;
              allReviews.push({
                author: "КиноВзор",
                role: "system",
                rating: Math.round(Number(movie.rating)),
                text,
              });
            });
          }
          if (Array.isArray(movie.userReviews)) {
            movie.userReviews.forEach((r) =>
              allReviews.push({
                author: r.author,
                role: r.role,
                rating: Math.round(Number(r.rating)),
                text: r.text,
              })
            );
          }

          if (allReviews.length === 0) {
            const emptyReview = document.createElement("div");
            emptyReview.className = "placeholder-text";
            emptyReview.textContent =
              "Пока нет рецензий. Станьте первым, кто оценит этот фильм.";
            reviewsContainer.appendChild(emptyReview);
          } else {
            allReviews.forEach((r) => {
              const item = document.createElement("div");
              item.className = "review-item";

              const headerRow = document.createElement("div");
              headerRow.className = "review-header";

              const authorEl = document.createElement("div");
              authorEl.className = "review-author";
              authorEl.textContent = r.author;

              const roleEl = document.createElement("div");
              roleEl.className = "review-role";
              if (r.role === "admin") {
                roleEl.textContent = "Админ";
              } else if (r.role === "viewer") {
                roleEl.textContent = "Зритель";
              } else {
                roleEl.textContent = "КиноВзор";
              }

              const ratingEl = document.createElement("div");
              ratingEl.className = "review-rating-badge";
              ratingEl.textContent = `${Math.round(Number(r.rating)).toFixed(0)} ★`;

              headerRow.appendChild(authorEl);
              headerRow.appendChild(roleEl);
              headerRow.appendChild(ratingEl);

              const textEl = document.createElement("div");
              textEl.className = "review-text";
              textEl.textContent = r.text;

              item.appendChild(headerRow);
              item.appendChild(textEl);

              reviewsContainer.appendChild(item);
            });
          }

          expanded.appendChild(overviewTitle);
          expanded.appendChild(overviewText);
          expanded.appendChild(reviewTitle);
          expanded.appendChild(reviewsContainer);

          // if logged in, add a compact review form inside expansion
          if (currentUser) {
            const form = document.createElement("form");
            form.className = "review-form";
            form.style.marginTop = "8px";

            const textRow = document.createElement("div");
            textRow.className = "review-form-row";
            const textLabel = document.createElement("label");
            textLabel.className = "form-label";
            textLabel.textContent = "Ваш отзыв";
            const textArea = document.createElement("textarea");
            textArea.rows = 2;
            textArea.placeholder = "Короткий отзыв...";
            textArea.className = "input";
            textRow.appendChild(textLabel);
            textRow.appendChild(textArea);

            const ratingRow = document.createElement("div");
            ratingRow.className = "review-form-rating-row";
            const ratingLabel = document.createElement("label");
            ratingLabel.className = "form-label";
            ratingLabel.textContent = "Оценка";
            const ratingSelect = document.createElement("select");
            ratingSelect.className = "input review-rating-select";
            for (let v = 10; v >= 1; v--) {
              const opt = document.createElement("option");
              opt.value = v;
              opt.textContent = v;
              ratingSelect.appendChild(opt);
            }
            ratingRow.appendChild(ratingLabel);
            ratingRow.appendChild(ratingSelect);

            const submitBtn = document.createElement("button");
            submitBtn.type = "submit";
            submitBtn.className = "primary-button full-width";
            submitBtn.textContent = "Оставить";

            form.appendChild(textRow);
            form.appendChild(ratingRow);
            form.appendChild(submitBtn);

            form.addEventListener("submit", (ev) => {
              ev.preventDefault();
              const text = textArea.value.trim();
              const rating = Math.round(Number(ratingSelect.value));
              if (!text || !rating) return;

              movie.userReviews.push({
                author: currentUser.username,
                role: currentUser.role,
                rating,
                text,
              });

              // re-render expanded content to show new review
              textArea.value = "";
              ratingSelect.value = "10";
              // collapse any expanded state and reopen this one to refresh
              document.querySelectorAll(".movie-card.expanded").forEach((c) => {
                if (c !== li) {
                  c.classList.remove("expanded");
                  const extra = c.querySelector(".mobile-expanded");
                  if (extra) extra.remove();
                }
              });
              li.classList.remove("expanded");
              const existing = li.querySelector(".mobile-expanded");
              if (existing) existing.remove();
              li.classList.add("expanded");
              // simple approach: call click to rebuild
              li.click();
            });

            expanded.appendChild(form);
          }

          li.appendChild(expanded);
          // ensure details panel also updates for larger viewports if user switches orientation
          renderMovieDetails(movie.id);
        }
      } else {
        renderMovieDetails(movie.id);
      }
    });

    moviesListEl.appendChild(li);
  });
}

function getPickLabel(code) {
  switch (code) {
    case "hits":
      return "Хит";
    case "new":
      return "Новинка";
    case "classic":
      return "Классика";
    default:
      return "";
  }
}

function renderMovieDetails(id) {
  const movie = MOVIES.find((m) => m.id === id);
  if (!movie) return;

  if (!Array.isArray(movie.userReviews)) {
    movie.userReviews = [];
  }

  movieDetailsEl.classList.remove("empty");
  movieDetailsEl.innerHTML = "";

  const wrapper = document.createElement("div");
  wrapper.className = "details-scroll";

  const header = document.createElement("div");
  header.className = "details-header";

  const headerTop = document.createElement("div");
  headerTop.className = "details-header-top";

  const posterWrap = document.createElement("div");
  posterWrap.className = "details-poster-wrapper";
  const posterImg = document.createElement("img");
  posterImg.className = "details-poster";
  posterImg.src =
    movie.poster || "https://picsum.photos/seed/defaultposter/200/300";
  posterImg.alt = `${movie.title} постер`;
  posterWrap.appendChild(posterImg);

  const titleBlockWrap = document.createElement("div");
  titleBlockWrap.style.flex = "1";
  const titleRow = document.createElement("div");
  titleRow.className = "details-title-row";

  const titleBlock = document.createElement("div");
  const titleEl = document.createElement("div");
  titleEl.className = "details-title";
  titleEl.textContent = movie.title;
  const yearEl = document.createElement("div");
  yearEl.className = "details-year";
  yearEl.textContent = movie.year;
  titleBlock.appendChild(titleEl);
  titleBlock.appendChild(yearEl);

  const ratingBadge = document.createElement("div");
  ratingBadge.className = "badge-rating";
  // integer display
  ratingBadge.textContent = Math.round(Number(movie.rating)).toFixed(0);

  titleRow.appendChild(titleBlock);
  titleRow.appendChild(ratingBadge);

  const metaRow = document.createElement("div");
  metaRow.className = "details-meta-row";
  metaRow.innerHTML = `
    <span>${movie.genre}</span>
    <span>•</span>
    <span>${movie.year}</span>
  `;

  const tagsRow = document.createElement("div");
  tagsRow.className = "details-tags";
  movie.picks.forEach((p) => {
    const chip = document.createElement("span");
    chip.className = "movie-pick-chip";
    chip.textContent = getPickLabel(p);
    tagsRow.appendChild(chip);
  });

  titleBlockWrap.appendChild(titleRow);
  titleBlockWrap.appendChild(metaRow);
  titleBlockWrap.appendChild(tagsRow);

  headerTop.appendChild(posterWrap);
  headerTop.appendChild(titleBlockWrap);

  header.appendChild(headerTop);

  const overviewTitle = document.createElement("div");
  overviewTitle.className = "details-section-title";
  overviewTitle.textContent = "Сюжет";

  const overviewText = document.createElement("div");
  overviewText.className = "details-overview";
  overviewText.textContent = movie.overview;

  const reviewTitle = document.createElement("div");
  reviewTitle.className = "details-section-title";
  reviewTitle.textContent = "Рецензии";

  const reviewsContainer = document.createElement("div");

  // build full review list: базовые + пользовательские
  const allReviews = [];

  if (movie.review) {
    allReviews.push({
      author: "КиноВзор",
      role: "system",
      rating: Math.round(Number(movie.rating)),
      text: movie.review,
    });
  }

  if (Array.isArray(movie.extraReviews)) {
    movie.extraReviews.forEach((text) => {
      if (!text) return;
      allReviews.push({
        author: "КиноВзор",
        role: "system",
        rating: Math.round(Number(movie.rating)),
        text,
      });
    });
  }

  movie.userReviews.forEach((r) =>
    allReviews.push({
      author: r.author,
      role: r.role,
      rating: Math.round(Number(r.rating)),
      text: r.text,
    })
  );

  if (allReviews.length === 0) {
    const emptyReview = document.createElement("div");
    emptyReview.className = "placeholder-text";
    emptyReview.textContent =
      "Пока нет рецензий. Станьте первым, кто оценит этот фильм.";
    reviewsContainer.appendChild(emptyReview);
  } else {
    allReviews.forEach((r) => {
      const item = document.createElement("div");
      item.className = "review-item";

      const headerRow = document.createElement("div");
      headerRow.className = "review-header";

      const authorEl = document.createElement("div");
      authorEl.className = "review-author";
      authorEl.textContent = r.author;

      const roleEl = document.createElement("div");
      roleEl.className = "review-role";
      if (r.role === "admin") {
        roleEl.textContent = "Админ";
      } else if (r.role === "viewer") {
        roleEl.textContent = "Зритель";
      } else {
        roleEl.textContent = "КиноВзор";
      }

      const ratingEl = document.createElement("div");
      ratingEl.className = "review-rating-badge";
      ratingEl.textContent = `${Math.round(Number(r.rating)).toFixed(0)} ★`;

      headerRow.appendChild(authorEl);
      headerRow.appendChild(roleEl);
      headerRow.appendChild(ratingEl);

      const textEl = document.createElement("div");
      textEl.className = "review-text";
      textEl.textContent = r.text;

      item.appendChild(headerRow);
      item.appendChild(textEl);

      reviewsContainer.appendChild(item);
    });
  }

  wrapper.appendChild(header);
  wrapper.appendChild(overviewTitle);
  wrapper.appendChild(overviewText);
  wrapper.appendChild(reviewTitle);
  wrapper.appendChild(reviewsContainer);

  // форма для добавления рецензии для залогиненных
  if (currentUser) {
    const form = document.createElement("form");
    form.className = "review-form";

    const formTitle = document.createElement("div");
    formTitle.className = "details-section-title";
    formTitle.textContent = "Добавить рецензию";
    form.appendChild(formTitle);

    const textRow = document.createElement("div");
    textRow.className = "review-form-row";
    const textLabel = document.createElement("label");
    textLabel.className = "form-label";
    textLabel.textContent = "Ваш отзыв";
    const textArea = document.createElement("textarea");
    textArea.rows = 3;
    textArea.placeholder = "Поделитесь впечатлениями о фильме...";
    textArea.className = "input";
    textRow.appendChild(textLabel);
    textRow.appendChild(textArea);

    const ratingRow = document.createElement("div");
    ratingRow.className = "review-form-rating-row";
    const ratingLabel = document.createElement("label");
    ratingLabel.className = "form-label";
    ratingLabel.textContent = "Оценка";
    const ratingSelect = document.createElement("select");
    ratingSelect.className = "input review-rating-select";
    for (let v = 10; v >= 1; v--) {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      ratingSelect.appendChild(opt);
    }
    ratingRow.appendChild(ratingLabel);
    ratingRow.appendChild(ratingSelect);

    const submitBtn = document.createElement("button");
    submitBtn.type = "submit";
    submitBtn.className = "primary-button full-width";
    submitBtn.textContent = "Оставить рецензию";

    form.appendChild(textRow);
    form.appendChild(ratingRow);
    form.appendChild(submitBtn);

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = textArea.value.trim();
      // store integer rating
      const rating = Math.round(Number(ratingSelect.value));
      if (!text || !rating) return;

      movie.userReviews.push({
        author: currentUser.username,
        role: currentUser.role,
        rating,
        text,
      });

      textArea.value = "";
      ratingSelect.value = "10";
      renderMovieDetails(movie.id);
    });

    wrapper.appendChild(form);
  }

  movieDetailsEl.appendChild(wrapper);
}

function selectDefaultMovie() {
  const list = getFilteredMovies();
  if (list.length > 0) {
    selectedMovieId = list[0].id;
    renderMovieDetails(selectedMovieId);
  }
}

function attachEventListeners() {
  searchInputEl.addEventListener("input", (e) => {
    currentSearch = e.target.value;
    renderMovies();
    selectDefaultMovie();
  });

  genreSelectEl.addEventListener("change", (e) => {
    currentGenre = e.target.value;
    renderMovies();
    selectDefaultMovie();
  });

  ratingButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      ratingButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentRatingFilter = btn.dataset.rating;
      renderMovies();
      selectDefaultMovie();
    });
  });

  pickButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      pickButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentPick = btn.dataset.pick;
      renderMovies();
      selectDefaultMovie();
    });
  });

  themeToggleBtn.addEventListener("click", () => {
    const isDark = body.classList.contains("theme-dark");
    if (isDark) {
      body.classList.remove("theme-dark");
      body.classList.add("theme-light");
      localStorage.setItem("kinovzor-theme", "light");
    } else {
      body.classList.remove("theme-light");
      body.classList.add("theme-dark");
      localStorage.setItem("kinovzor-theme", "dark");
    }
  });

  authButton.addEventListener("click", openAuthModal);
  closeAuthModalBtn.addEventListener("click", closeAuthModal);
  authModal.addEventListener("click", (e) => {
    if (e.target === authModal || e.target.classList.contains("modal-backdrop")) {
      closeAuthModal();
    }
  });

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab;
      tabButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      tabPanels.forEach((panel) => {
        panel.classList.toggle("active", panel.dataset.panel === tab);
      });
    });
  });

  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleLogin();
  });

  quickRoleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const role = btn.dataset.quickRole;
      handleQuickLogin(role);
    });
  });

  logoutButton.addEventListener("click", handleLogout);

  adminAddForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleAdminAddMovie();
  });
}

function openAuthModal() {
  authModal.classList.remove("hidden");
  loginErrorEl.classList.add("hidden");
  loginErrorEl.textContent = "";
  setTimeout(() => {
    loginUsernameInput.focus();
  }, 50);
}

function closeAuthModal() {
  authModal.classList.add("hidden");
}

function handleLogin() {
  const username = loginUsernameInput.value.trim();
  const password = loginPasswordInput.value;

  const user = USERS.find(
    (u) => u.username === username && u.password === password
  );

  if (!user) {
    loginErrorEl.textContent = "Неверный логин или пароль.";
    loginErrorEl.classList.remove("hidden");
    return;
  }

  currentUser = { username: user.username, role: user.role };
  updateAuthUI();
  closeAuthModal();
}

function handleQuickLogin(role) {
  if (role !== "viewer" && role !== "admin") return;
  currentUser = {
    username: role === "viewer" ? "Гость" : "Админ-гость",
    role: role,
  };
  updateAuthUI();
  closeAuthModal();
}

function handleLogout() {
  currentUser = null;
  updateAuthUI();
}

function updateAuthUI() {
  if (currentUser) {
    authButton.classList.add("hidden");
    userBadge.classList.remove("hidden");
    userNameEl.textContent = currentUser.username;
    userRoleEl.textContent =
      currentUser.role === "admin" ? "Роль: администратор" : "Роль: зритель";
    if (currentUser.role === "admin") {
      adminPanel.classList.remove("hidden");
    } else {
      adminPanel.classList.add("hidden");
    }
  } else {
    authButton.classList.remove("hidden");
    userBadge.classList.add("hidden");
    userNameEl.textContent = "";
    userRoleEl.textContent = "";
    adminPanel.classList.add("hidden");
  }

  // пересчитать форму рецензии при смене авторизации
  if (selectedMovieId != null) {
    renderMovieDetails(selectedMovieId);
  }
}

function handleAdminAddMovie() {
  if (!currentUser || currentUser.role !== "admin") return;

  const title = adminTitleInput.value.trim();
  const year = Number(adminYearInput.value);
  const rating = Number(adminRatingInput.value);
  const genre = adminGenreInput.value.trim() || "Драма";
  const poster = adminPosterInput.value.trim();
  const overview =
    adminOverviewInput.value.trim() || "Описание будет добавлено позже.";
  const review1 =
    adminReview1Input.value.trim() || "Рецензия будет добавлена позже.";
  const review2 = adminReview2Input.value.trim();

  const picks = [];
  adminPanel
    .querySelectorAll(".admin-picks input[type='checkbox']")
    .forEach((cb) => {
      if (cb.checked) picks.push(cb.value);
    });

  if (!title || !year || !rating) {
    return;
  }

  const newId =
    MOVIES.reduce((max, m) => (m.id > max ? m.id : max), 0) + 1;

  const newMovie = {
    id: newId,
    title,
    year,
    genre,
    rating,
    picks: picks.length ? picks : ["new"],
    poster: poster || `https://picsum.photos/seed/film${newId}/200/300`,
    overview,
    review: review1,
    extraReviews: review2 ? [review2] : [],
    userReviews: [],
  };

  MOVIES.push(newMovie);
  initGenres();
  renderMovies();
  selectedMovieId = newMovie.id;
  renderMovieDetails(newMovie.id);

  adminAddForm.reset();
}