from pogoiv.iv_calculator import IvCalculator

def get_all_iv_range(message):
    numbers = message.split(' ')
    pokename = str(numbers[1])
    pokecp = int(numbers[2])
    pokehp = int(numbers[3])
    pokepwcost = int(numbers[4])
    pokepowered = bool(numbers[5])
    calculator = IvCalculator()
    all_ivs = calculator.get_ivs_across_powerups(pokemon_name=pokename, powerup_stats=[(pokecp, pokehp, pokepwcost, pokepowered)])
    if all_ivs:
        return all_ivs
    else:
        return ['Check your values are correct and in the right order: name, cp, hp, powerup cost, True/False if powered']
