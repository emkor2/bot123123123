import telebot

# Токен вашего Телеграм-бота
TOKEN = '8317553980:AAG5I0sbfbtWCO_rzyZDUfxh_-4EHe8lRtI'
bot = telebot.TeleBot(TOKEN)

# Хранилища состояний тестов
test_state = {}
conflict_state = {}
behavior_style_state = {}


# Приветственное сообщение
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    itembtn1 = telebot.types.KeyboardButton('Согласен')
    itembtn2 = telebot.types.KeyboardButton('Не согласен')
    markup.add(itembtn1, itembtn2)

    bot.send_message(message.chat.id, "Здравствуйте, предлагаю пройти вам тест на тип личности.", reply_markup=markup)


# Обработка старта теста
@bot.message_handler(func=lambda message: message.text in ['Согласен', 'Не согласен'])
def handle_start_buttons(message):
    chat_id = message.chat.id

    if message.text == 'Согласен':
        # Начинаем прохождение теста
        test_state[chat_id] = {'question_number': 1, 'answers': []}
        ask_personality_question(chat_id)
    elif message.text == 'Не согласен':
        show_commands(chat_id)


# Обработка ответов на вопросы теста
@bot.message_handler(func=lambda message: message.chat.id in test_state)
def process_personality_answer(message):
    chat_id = message.chat.id
    user_answer = message.text

    state = test_state[chat_id]
    state['answers'].append(user_answer)
    state['question_number'] += 1

    if state['question_number'] <= 7:
        ask_personality_question(chat_id)
    else:
        finish_personality_test(chat_id)


# Вопросы теста на тип личности
def ask_personality_question(chat_id):
    questions = [
        ("Как вам больше нравится проводить свободное время?",
         ["Погулять по парку в одиночестве",
          "Встретиться с другом в кафе",
          "Пойти на шумную вечеринку",
          "Почитать книгу или посмотреть фильм"]),

        ("Какое слово из предложенных описывает вас лучше всего?",
         ["Серьезный",
          "Энергичный",
          "Эмоциональный",
          "Задумчивый"]),

        ("Трудно ли вам открыто выражать свои эмоции?",
         ["Чаще нет, чем да",
          "Легко",
          "Чаще да, чем нет",
          "Очень тяжело"]),

        ("Легко ли вас разозлить?",
         ["Меня почти невозможно вывести из себя",
          "Зависит от ситуации",
          "Да",
          "Все что угодно может вывести меня из себя"]),

        ("Как вам больше нравится работать?",
         ["Дома",
          "В офисе",
          "Гибридная работа",
          "Без разницы"]),

        ("Часто ли у вас меняется настроение без веских на то причин?",
         ["Очень редко",
          "Когда как",
          "Часто",
          "Затрудняюсь ответить"]),

        ("У вас больше трех близких друзей?",
         ["Да",
          "Нет",
          "Как раз три",
          "У меня очень много друзей, не смогу посчитать"])
    ]

    state = test_state.get(chat_id)
    question_num = state['question_number']

    if question_num <= len(questions):
        current_question = questions[question_num - 1]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for option in current_question[1]:
            markup.add(option)

        bot.send_message(chat_id, f"Вопрос {question_num}: {current_question[0]}", reply_markup=markup)
    else:
        finish_personality_test(chat_id)


# Завершение теста на тип личности
def finish_personality_test(chat_id):
    answers = test_state.get(chat_id)['answers']
    personality_type, description = analyze_personality_answers(answers)

    del test_state[chat_id]

    response = f"Тест пройден!\nВаш тип личности: {personality_type}\nОписание: {description}"
    bot.send_message(chat_id, response)
    show_commands(chat_id)


# Анализ результатов теста на тип личности
def analyze_personality_answers(answers):
    introvert_score = extrovert_score = emotional_score = stable_score = flexible_score = rigid_score = social_score = 0

    for answer in answers:
        if answer in ['Погулять по парку в одиночестве', 'Серьезный', 'Чаще да, чем нет']:
            introvert_score += 1
        elif answer in ['Встретиться с другом в кафе', 'Энергичный', 'Легко']:
            extrovert_score += 1
        elif answer in ['Пойти на шумную вечеринку', 'Эмоциональный', 'Часто']:
            emotional_score += 1
        elif answer in ['Почитать книгу или посмотреть фильм', 'Задумчивый', 'Очень тяжело']:
            stable_score += 1
        elif answer in ['Меня почти невозможно вывести из себя', 'Дома', 'Очень редко']:
            flexible_score += 1
        elif answer in ['Зависит от ситуации', 'В офисе', 'Когда как']:
            rigid_score += 1
        elif answer == 'У меня очень много друзей, не смогу посчитать':
            social_score += 1

    # Подсчет результатов
    results = {
        'Интровертированный': introvert_score,
        'Экстравертированный': extrovert_score,
        'Эмоционально-стабильный': stable_score + flexible_score,
        'Подвижный': rigid_score,
        'Социально активный': social_score,
        'Эмоциональный': emotional_score
    }

    # Определение типа личности
    result = sorted(results.items(), key=lambda x: x[1], reverse=True)[0][0]

    # Краткая справка о каждом типе личности
    descriptions = {
        'Интровертированный': 'Вы предпочитаете покой и комфорт своего личного пространства, цените тихие занятия и глубокие размышления.',
        'Экстравертированный': 'Вы активны и общительны, получаете энергию от социальных взаимодействий и позитивно относитесь к новым знакомствам.',
        'Эмоционально-стабильный': 'Вы эмоционально устойчивы и хорошо переносите стрессы, умеете контролировать свои эмоции.',
        'Подвижный': 'Вы адаптивны и подвижны, легко перестраиваетесь и чувствуете себя уверенно в любых обстоятельствах.',
        'Социально активный': 'Вы общительны и социально ориентированы, поддерживая многочисленные дружеские связи и занимая активную жизненную позицию.',
        'Эмоциональный': 'Вы сильно погружены в мир эмоций, обладаете способностью остро чувствовать происходящие события и воспринимать их близко к сердцу.'
    }

    return result, descriptions.get(result, '')


# Показ списка команд после завершения теста
def show_commands(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_help_conflicts = telebot.types.KeyboardButton("Справка о конфликтах")
    btn_resolution = telebot.types.KeyboardButton("Помощь решения")
    btn_typical_scenarios = telebot.types.KeyboardButton("Типовые ситуации")
    btn_literature_list = telebot.types.KeyboardButton("Список литературы")
    btn_detect_conflict = telebot.types.KeyboardButton("Определение типа конфликта")
    btn_behavior_style = telebot.types.KeyboardButton("Тест на стиль поведения в конфликте")  # новая кнопка
    markup.row(btn_help_conflicts, btn_resolution)
    markup.row(btn_typical_scenarios, btn_literature_list)
    markup.row(btn_detect_conflict, btn_behavior_style)

    bot.send_message(chat_id, "Отлично, вот список моих команд:", reply_markup=markup)


# Обработчик нажатий на кнопки после завершения теста
@bot.message_handler(func=lambda message: message.text in ["Справка о конфликтах", "Помощь решения", "Типовые ситуации",
                                                           "Список литературы", "Определение типа конфликта",
                                                           "Тест на стиль поведения в конфликте"])
def handle_post_test_buttons(message):
    chat_id = message.chat.id
    text = message.text

    if text == 'Справка о конфликтах':
        conflicts_info = """Конфликты неизбежно возникают в повседневных отношениях, особенно в школах и вузах. Важно научиться управлять ими грамотно и своевременно.

#### Типы конфликтов:
- **Внутриличностные конфликты**: внутренние переживания и трудности выбора, неуверенность в собственных силах или планах.
- **Межличностные конфликты**: разногласия между учениками, студентами и преподавателями, основанные на различиях в восприятии и ожиданиях.
- **Групповые конфликты**: споры между группами студентов или классов, возникающие из-за конкуренции или неравенства.

#### Этапы развития конфликта:
1. Скрытый период: зарождение раздражения и накопления негативных эмоций.
2. Открытость выражения: непосредственный разговор, дискуссия или конфликт.
3. Решение: достижение согласия или временное затишье.

#### Причины возникновения конфликтов:
- Несправедливость оценки достижений педагогов.
- Недопонимание требований учебного плана.
- Зависть или соперничество между учениками.
- Роли и обязанности, воспринимаемые неравномерно.

Важно оперативно выявлять причины конфликтов и находить конструктивное решение."""
        bot.send_message(chat_id, conflicts_info)
    elif text == 'Помощь решения':
        resolution_advice = """Советы и приемы для эффективного управления конфликтами:

- Используйте активное слушание: внимательно слушайте и принимайте мнение оппонента.
- Формируйте конструктивный диалог: говорите о своих чувствах и потребностях, используя фразы типа \"Я считаю...\" или \"Я чувствую...\" .
- Найдите общие цели: определите общую выгоду и поставьте целью удовлетворение интересов обоих сторон.
- Применяйте креативные подходы: попробуйте найти нестандартные решения ваших трудностей.

Полезные фразы для разрешения конфликтов:
- **\"Я заметил(-а), что наше мнение отличается… Давайте обсудим нашу позицию?\"** — выразите заинтересованность.
- **\"Мне кажется важным учитывать твой взгляд на вещи, давай попытаемся найти компромисс?\"** — обозначьте стремление к сотрудничеству.
- **\"Можно ли рассказать поподробнее, почему ты думаешь иначе?\"** — выясните суть разногласий.
- **\"Возможно, нам стоит взглянуть на ситуацию глазами друг друга?\"** — предложите поставить себя на место другого.
- **\"Мы оба хотим наилучшего результата, давай вместе решим, как этого добиться?\"** — акцентируйте внимание на общем желании."""
        bot.send_message(chat_id, resolution_advice)
    elif text == 'Типовые ситуации':
        typical_scenarios = """Типовые конфликтные ситуации в школе и университете:

1. **Неприятие наставлений учителя**: ученик раздражён частым повторением совета или замечаниями преподавателя.
   * Решение:* спокойно поговорите с учителем, изложите свою позицию и попросите конкретного обоснования претензий.

2. **Столкновение с одноклассником по проекту**: группа не приходит к согласию по поводу выполнения группового задания, возникает напряженность.
   * Решение:* проведите собрание группы, выслушайте мнения всех участников и установите единую стратегию выполнения задания.

3. **Замечание преподавателя по работе**: ученик расстраивается из-за низкой оценки за выполненное задание.
   * Решение:* обсудите полученный балл с преподавателем, уточнив требования и возможные способы повышения успеваемости.

4. **Незаслуженная похвала другому ученику**: появляется зависть к успехам сокурсника или одноклассника.
   * Решение:* научитесь гордиться чужими достижениями, осознавая собственную индивидуальность и потенциал.

5. **Несогласие с методами воспитания родителей**: подросток критикует строгие ограничения или наказание дома.
   * Решение:* обсудите свое мнение с родителем, убедительно аргументируя необходимость свободы и самостоятельности.

Каждую ситуацию можно предотвратить своевременным обсуждением и открытым диалогом."""
        bot.send_message(chat_id, typical_scenarios)
    elif text == 'Список литературы':
        books_description = """Рекомендуемые книги по психологии конфликтов и эффективным взаимоотношениям:

1. **Козлов Н.И.** — «Психология конфликтов»: глубокий разбор причин возникновения конфликтов и эффективных методов их предотвращения и разрешения.

2. **Зимбардо Ф.** — «Социальная психология»: подробное рассмотрение основ социальной динамики и влияния общественных норм на формирование конфликтов.

3. **Маслоу А.Г.** — «Мотивация и личность»: классический труд, рассматривающий структуру человеческой личности и способы совладения с внутренними конфликтами и тревогами.

Эти книги позволят расширить знания и применить полученные инструменты для гармонизации личной и образовательной сферы."""
        bot.send_message(chat_id, books_description)
    elif text == 'Определение типа конфликта':
        conflict_state[chat_id] = {'question_number': 1, 'answers': []}
        ask_conflict_question(chat_id)
    elif text == 'Тест на стиль поведения в конфликте':
        behavior_style_state[chat_id] = {'question_number': 1, 'answers': []}
        ask_behavior_style_question(chat_id)


# Обработка ответов на вопросы диагностики конфликта
@bot.message_handler(func=lambda message: message.chat.id in conflict_state)
def process_conflict_answer(message):
    chat_id = message.chat.id
    user_answer = message.text

    state = conflict_state[chat_id]
    state['answers'].append(user_answer)
    state['question_number'] += 1

    if state['question_number'] <= 5:
        ask_conflict_question(chat_id)
    else:
        finish_conflict_diagnosis(chat_id)


# Вопросы для определения типа конфликта
def ask_conflict_question(chat_id):
    questions = [
        ("Кто является участником конфликта?",
         ["Только я", "Я и мой близкий человек", "Группа лиц"]),

        ("В чём причина конфликта?",
         ["Личное мнение или предпочтения", "Профессиональные разногласия", "Нарушение установленных норм"]),

        ("Как долго длится конфликт?",
         ["Несколько часов/дней", "Недели/месяцы", "Постоянно"]),

        ("Влияют ли внешние обстоятельства на конфликт?",
         ["Нет, только мои собственные реакции", "Да, влияют объективные факторы",
          "И мое состояние, и внешний фактор"]),

        ("Какой основной эффект оказывает конфликт на мою жизнь?",
         ["Создает сильное внутреннее напряжение", "Вызывает стресс, снижает продуктивность",
          "Значимых последствий нет"])
    ]

    state = conflict_state.get(chat_id)
    question_num = state['question_number']

    if question_num <= len(questions):
        current_question = questions[question_num - 1]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for option in current_question[1]:
            markup.add(option)

        bot.send_message(chat_id, f"Вопрос {question_num}: {current_question[0]}", reply_markup=markup)
    else:
        finish_conflict_diagnosis(chat_id)


# Завершение диагностики конфликта
def finish_conflict_diagnosis(chat_id):
    answers = conflict_state.get(chat_id)['answers']
    conflict_type, solution = determine_conflict_type_and_solution(answers)

    del conflict_state[chat_id]

    response = f"Пройдена диагностика конфликта!\nОпределённый тип конфликта: {conflict_type}.\nСовет по разрешению: {solution}"
    bot.send_message(chat_id, response)
    show_commands(chat_id)  # возвращение к списку команд


# Обработка ответов на вопросы диагностики стиля поведения
@bot.message_handler(func=lambda message: message.chat.id in behavior_style_state)
def process_behavior_style_answer(message):
    chat_id = message.chat.id
    user_answer = message.text

    state = behavior_style_state[chat_id]
    state['answers'].append(user_answer)
    state['question_number'] += 1

    if state['question_number'] <= 10:
        ask_behavior_style_question(chat_id)
    else:
        finish_behavior_style_test(chat_id)


# Вопросы для определения стиля поведения в конфликте
def ask_behavior_style_question(chat_id):
    questions = [
        ("Как вы обычно поступаете, сталкиваясь с проблемой?",
         ["Ищу компромисс", "Всегда отстаиваю свою позицию", "Ухожу от конфликта", "Прошу помощи у других"]),

        ("Как вы ведете себя, когда собеседник ведет себя агрессивно?",
         ["Контролирую эмоции и сохраняю спокойствие", "Начинаю защищаться и контратаку",
          "Молчу и пытаюсь уйти от дискуссии", "Обращаюсь за поддержкой"]),

        ("Какова ваша реакция, когда ваши усилия не приносят желаемого результата?",
         ["Продолжаю пытаться разными способами", "Перестраиваюсь и принимаю ситуацию", "Оставляю попытки",
          "Исключаю риск неудачи"]),

        ("Как вы действуете, если уверены в собственной правоте?",
         ["Активно доказываю свою точку зрения", "Готов пойти на уступки", "Стараюсь избежать прямого конфликта",
          "Обращаюсь за советом"]),

        ("Что чаще всего заставляет вас вступать в конфликт?",
         ["Обида или злость", "Желание доказать свою точку зрения", "Страх потери власти",
          "Необходимость защитить интересы"]),

        ("Как вы воспринимаете проигрыш в споре?",
         ["Оцениваю опыт и продолжаю двигаться дальше", "Огорчаюсь и сомневаюсь в себе", "Настроен бороться до конца",
          "Прекращаю любое дальнейшее участие"]),

        ("Как вы считаете, насколько важен компромисс в решении конфликтов?",
         ["Компромисс необходим", "Лучше настоять на своем", "Избегаю компромисса", "Рискну любыми средствами"]),

        ("Как вы реагируете на критику в свой адрес?",
         ["Восприятие критики положительно", "Остро воспринимаю критику", "Просто игнорирую", "Просят разъяснения"]),

        ("Что вы делаете, когда видите, что ситуация выходит из-под контроля?",
         ["Сразу вмешиваюсь", "Наблюдаю и анализирую", "Предаюсь панике", "Обращаюсь за посторонней помощью"]),

        ("Что важнее для вас в конфликте: победа или сохранение отношений?",
         ["Победа важнее", "Сохранение отношений важнее", "Главное — компромисс", "Решаю по ситуации"])
    ]

    state = behavior_style_state.get(chat_id)
    question_num = state['question_number']

    if question_num <= len(questions):
        current_question = questions[question_num - 1]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for option in current_question[1]:
            markup.add(option)

        bot.send_message(chat_id, f"Вопрос {question_num}: {current_question[0]}", reply_markup=markup)
    else:
        finish_behavior_style_test(chat_id)


# Завершение теста на стиль поведения в конфликте
def finish_behavior_style_test(chat_id):
    answers = behavior_style_state.get(chat_id)['answers']
    style, improvement_tip = analyze_behavior_style(answers)

    del behavior_style_state[chat_id]

    response = f"Тест пройден!\nВаш стиль поведения в конфликте: {style}\nСовет по улучшению: {improvement_tip}"
    bot.send_message(chat_id, response)
    show_commands(chat_id)  # возвращение к главному меню после теста


# Универсальная обработка сообщений вне кнопок
@bot.message_handler(func=lambda message: True)
def universal_message_handler(message):
    chat_id = message.chat.id
    # Перенаправляем пользователя назад к началу, если сообщение не соответствует никакой кнопке
    send_welcome(message)


# Анализ стиля поведения в конфликте
def analyze_behavior_style(answers):
    cooperative_score = competitive_score = avoidant_score = dependent_score = adaptive_score = 0

    for answer in answers:
        if answer in ['Ищу компромисс', 'Контролирую эмоции и сохраняю спокойствие',
                      'Продолжаю пытаться разными способами', 'Активно доказываю свою точку зрения']:
            cooperative_score += 1
        elif answer in ['Всегда отстаиваю свою позицию', 'Начинаю защищаться и контратаку',
                        'Настроен бороться до конца', 'Лучше настоять на своем']:
            competitive_score += 1
        elif answer in ['Ухожу от конфликта', 'Молчу и пытаюсь уйти от дискуссии', 'Оставляю попытки',
                        'Избегаю компромисса']:
            avoidant_score += 1
        elif answer in ['Прошу помощи у других', 'Обращаюсь за поддержкой', 'Обращаюсь за советом',
                        'Обращаюсь за посторонней помощью']:
            dependent_score += 1
        elif answer in ['Оцениваю опыт и продолжаю двигаться дальше', 'Предаюсь панике',
                        'Стараюсь избежать прямого конфликта', 'Решаю по ситуации']:
            adaptive_score += 1

    # Определение стиля поведения
    styles = {
        'Кооперативный': cooperative_score,
        'Соревновательный': competitive_score,
        'Уклоняющийся': avoidant_score,
        'Зависимый': dependent_score,
        'Адаптивный': adaptive_score
    }

    # Определение стиля и совета
    result = sorted(styles.items(), key=lambda x: x[1], reverse=True)[0][0]

    tips = {
        'Кооперативный': 'Старайтесь чаще ставить себя на место других, чтобы достигнуть лучшего взаимопонимания и доверия.',
        'Соревновательный': 'Помните, что иногда уступки необходимы для долгосрочного успеха. Научитесь слышать мнение других.',
        'Уклоняющийся': 'Научитесь открыто говорить о своих проблемах и возражениях, ведь молчание лишь усугубляет ситуацию.',
        'Зависимый': 'Работайте над уверенностью в себе и умением принимать самостоятельные решения.',
        'Адаптивный': 'Сосредоточьтесь на развитии устойчивости к стрессовым ситуациям и способности быстро восстанавливаться после неудач.'
    }

    return result, tips.get(result, '')


# Определение типа конфликта и соответствующего совета
def determine_conflict_type_and_solution(answers):
    # Определим ключевые показатели
    personal_score = sum([1 if a in ['Только я', 'Личное мнение или предпочтения',
                                     'Нет, только мои собственные реакции',
                                     'Создает сильное внутреннее напряжение'] else 0 for a in answers])
    interpersonal_score = sum([1 if a in ['Я и мой близкий человек', 'Профессиональные разногласия',
                                          'Да, влияют объективные факторы',
                                          'Вызывает стресс, снижает продуктивность'] else 0 for a in answers])
    group_score = sum([1 if a in ['Группа лиц', 'Нарушение установленных норм', 'И мое состояние, и внешний фактор',
                                  'Значимых последствий нет'] else 0 for a in answers])

    # Выбор типа конфликта
    if personal_score > interpersonal_score and personal_score > group_score:
        conflict_type = 'Внутриличностный'
        solution = 'Попытайтесь проанализировать свои чувства и потребности, постарайтесь найти поддержку у близкого человека или специалиста.'
    elif interpersonal_score > personal_score and interpersonal_score > group_score:
        conflict_type = 'Межличностный'
        solution = 'Постарайтесь наладить диалог с оппонентом, выразите свои чувства и предложите совместные пути решения проблемы.'
    else:
        conflict_type = 'Групповой'
        solution = 'Соберите всех участников и сообща обсудите существующие проблемы, найдите баланс интересов и примите решение, удовлетворяющее большинство.'

    return conflict_type, solution


# Запускаем бота
if __name__ == "__main__":
    bot.polling(none_stop=True)