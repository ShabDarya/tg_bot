
def calc_water(weight, activity, temp):
    water = weight * 30 + 500 * activity / 30
    if temp > 25:
        water += 750
    return round(water)

def calc_calorie(weight, height, age, activity):
    calorie = weight * 10 + 6.25 * height - 5 * age + 10 * activity #за минуту ходьбы тратится примерно 10 калорий, поэтому такая формула
    return round(calorie)

def get_value_from_gpt(t):
    t = t.split(' ')
    value = -1
    for part in t:
        if '–' in part:
            values = part.split('–')
            value = (float(values[0]) + float(values[1]))/2
            return value
        else:
            try:
                value = float(part)
                return value
            except:
                continue   
    if value == -1:
        return ValueError
    return value