from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import User
from api_methods import get_current_temp, get_food_calories, get_train_calories
from calculation import calc_water, calc_calorie, get_value_from_gpt

router = Router()

global calorie
calorie = 0

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.\nВведите /help для списка команд.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/help - Доступные команды\n"
        "/set_profile - настройка профиля\n"
        "/log_water <количество> - добавить выпитую воду\n"
        "/log_food <название продукта> - добавить прием пищи\n"
        "/log_workout <тип тренировки> <время (мин)> - добавить тренировку\n"
        "/check_progress - прогресс дня\n"
    )

@router.message(Command("set_profile"))
async def cmd_profile(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите Ваш вес (в кг):")
    try:
        await state.set_state(User.weight)
    except:
        message.reply("Введите число")

@router.message(Command("check_progress"))
async def cmd_profile(message: Message, state: FSMContext):
    try:
        data_user = await state.get_data()
        drinked = data_user.get("logged_water")
        water_goal = data_user.get("water_goal")

        eaten = data_user.get("logged_calories")
        calorie_goal = data_user.get("calorie_goal")
        burned_calories = data_user.get("burned_calories")

        await message.answer(f"Прогресс:\nВода:\n - Выпито: {round(drinked)} мл из {round(water_goal)} мл.\n - Осталось: {round(water_goal - drinked)} мл.\n\nКалории:\n - Потреблено: {round(eaten)} ккал из {round(calorie_goal)} ккал.\n - Сожжено: {round(burned_calories)} ккал.\n - Баланс: {round(eaten - burned_calories)} ккал.")
    except:
        message.reply("Вы не настроили профиль.")
    

@router.message(Command("log_water"))
async def process_log_water(message: Message, state: FSMContext):
    try:
        data = message.text.split(' ')
        if len(data) != 2:
            await message.reply("Некорректная команда. Пример правильной команды: /log_water 300")
        else:
            data_user = await state.get_data()
            log_water = data_user.get("logged_water")
            log_water += float(data[1].replace(",", "."))
            goal_water = data_user.get("water_goal")
            await state.update_data(logged_water=log_water)
            left_water = round(goal_water - log_water)
            if left_water <= 0:
                await message.answer(f"Выпито {round(log_water)} мл. Вы достигли цели!")
            else:
                await message.answer(f"Выпито {round(log_water)} мл. Осталось {left_water} мл.")
    except:
        await message.answer(f"Вы не настроили профиль.")

@router.message(Command("log_food"))
async def process_log_calories(message: Message, state: FSMContext):
    try:
        data = message.text.split(' ')
        if len(data) < 2:
            await message.reply("Некорректная команда. Пример правильной команды: /log_food банан")
        else:
            food = message.text[10:]
            data_user = await state.get_data()
            log_calorie = data_user.get("logged_calories")
            goal_calorie = data_user.get("calorie_goal")

            res = get_food_calories(food)
            calories = get_value_from_gpt(res['result']['alternatives'][0]['message']['text'])

            if calories is ValueError:
                await message.reply(f"Непредвиденная ошибка. Проверьте правильность ввода еды.")
            else:
                await message.answer(f"{food.capitalize()} - {calories} ккал на 100 г. Сколько грамм Вы съели?")
                global calorie
                calorie = calories
                await state.set_state(User.logged_calories)

    except:
        await message.answer(f"Вы не настроили профиль.")

@router.message(Command("log_workout"))
async def process_log_train(message: Message, state: FSMContext):
    try:
        data = message.text.split(' ')
        if len(data) != 3:
            await message.reply("Некорректная команда. Пример правильной команды: /log_workout бег 30")
        else:
            data_user = await state.get_data()
            burned_calories = data_user.get("burned_calories")
            water_goal = data_user.get("water_goal")

            if float(data[2]) < 0 :
                await message.reply(f"Длительность тренировки должна быть больше 0")
                return

            res = get_train_calories(data[1])
            calories = get_value_from_gpt(res['result']['alternatives'][0]['message']['text'])

            if calories is ValueError:
                await message.reply(f"Непредвиденная ошибка. Проверьте правильность ввода команды.")
            else:
                
                burn_calorie = calories / 30 * float(data[2])
                await state.update_data(burned_calories=burn_calorie)
                new_water = round(float(data[2]) / 30 * 200)
                water_goal += new_water
                await state.update_data(water_goal=water_goal)
                await message.answer(f"{data[1].capitalize()} {data[2]} минут - {burn_calorie} ккал. Дополнительно: Выпейте {new_water} мл воды.")

    except:
        await message.answer(f"Вы не настроили профиль.")

@router.message(User.logged_calories)
async def process_plus_calories(message: Message, state: FSMContext):
    try:
        weight_food = float(message.text.replace(",", "."))
        if weight_food > 0:
            data_user = await state.get_data()
            log_calorie = data_user.get("logged_calories")
            global calorie
            new_calorie = round(calorie / 100 * weight_food)
            log_calorie += new_calorie

            await state.update_data(logged_calories=log_calorie)
            await message.answer(f"Записано: {new_calorie} ккал.")

        else:
            raise ValueError
    except ValueError:
        await message.reply("Введите число")

@router.message(User.weight)
async def process_name_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
        if weight > 0 and weight < 560:
            await state.update_data(weight=weight)
            await message.reply("Введите Ваш рост (в см):")
            await state.set_state(User.height)
        else:
            raise ValueError
    except ValueError:
        await message.reply("Введите число")

@router.message(User.height)
async def process_name_height(message: Message, state: FSMContext):
    try:
        height = float(message.text.replace(",", "."))
        if height > 50 and height < 252:
            await state.update_data(height=height)
            await message.reply("Введите Ваш возраст (в годах):")
            await state.set_state(User.age)
        else:
            raise ValueError
    except ValueError:
        await message.reply("Введите число")

@router.message(User.age)
async def process_name_age(message: Message, state: FSMContext):
    try:
        age = float(message.text.replace(",", "."))
        if age > 0 and age < 120:
            await state.update_data(age=age)
            await message.reply("Сколько минут активности у вас в день?")
            await state.set_state(User.activity_lvl)
        else:
            raise ValueError
    except ValueError:
        await message.reply("Введите число")

@router.message(User.activity_lvl)
async def process_name_lvl(message: Message, state: FSMContext):
    try:
        activity_lvl = float(message.text.replace(",", "."))
        if activity_lvl > -1 and activity_lvl < 1441:
            await state.update_data(activity_lvl=activity_lvl)
            await message.reply("В каком городе Вы находитесь?")
            await state.set_state(User.town)
        else:
            raise ValueError
    except ValueError:
        await message.reply("Введите число")

@router.message(User.town)
async def process_name_town(message: Message, state: FSMContext):
    try:
        await state.update_data(town=message.text)
        await state.set_state(User.calorie_goal)
        await process_name_calorie(message, state)
    except ValueError:
        await message.reply("Проверьте написание города на ошибки. Если все написано верно, то попробуйте ввести название на английском.")
    
@router.message(User.calorie_goal)
async def process_name_calorie(message: Message, state: FSMContext):
    try:
        data_user = await state.get_data()
        town = data_user.get("town")
        data = get_current_temp(town)
        temp = data['main']['temp']
        water = calc_water(data_user.get("weight"), data_user.get("activity_lvl"), temp)
        await state.update_data(water_goal=water)
        await message.answer(f"Ваша водная цель равна {str(water)} мл")

        calorie = calc_calorie(data_user.get("weight"), data_user.get("height"), data_user.get("age"), data_user.get("activity_lvl"))
        await state.update_data(calorie_goal=calorie)
        await message.answer(f"Ваша цель по калориям равна {str(calorie)} калорий")
        await state.update_data(logged_water=0)
        await state.update_data(logged_calories=0)
        await state.update_data(burned_calories=0)
        
    except:
        await message.answer("Ошибка в вычислениях")


    
    

def setup_handlers(dp):
    dp.include_router(router)