from random import randint


def roll_dice(quantity: int, num_sides: int) -> str:
    dice = []
    for die in range(quantity):
        dice.append(__roll(num_sides))
    return ", ".join(dice)


def __roll(num_sides: int) -> str:
    return str(randint(1, num_sides))


def quantity_to_speech(quantity: str) -> str:
    return f"{quantity} dice" if int(quantity) != 1 else "1 die"


def validate_quantity(quantity: str):
    return 1 <= int(quantity) <= 10


def validate_sides(num_sides: str):
    return 2 <= int(num_sides) <= 20
