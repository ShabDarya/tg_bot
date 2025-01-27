from aiogram.fsm.state import State, StatesGroup

class User(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity_lvl = State()
    town = State()
    calorie_goal = State()
    water_goal = State()
    logged_calories = State()
    logged_water = State()
    burned_calories = State()
    
