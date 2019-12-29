import pickle
from os import path, getcwd
from util import PATH_TO_DIR

characters_file_path = PATH_TO_DIR + "/characters.txt"
current_character_file_path = PATH_TO_DIR + "/currentCharacter.txt"

stats = ["str", "dex", "con", "int", "wis", "cha"]
saves = {stat + "save":stat for stat in stats}
skills = {
    "acrobatics":"dex",
    "arcana":"int",
    "animalhandling":"wis",
    "athletics":"str",
    "deception":"cha",
    "history":"int",
    "insight":"wis",
    "intimidation":"cha",
    "investigation":"int",
    "medicine":"wis",
    "nature":"int",
    "performance":"cha",
    "persuasion":"cha",
    "perception":"wis",
    "religion":"int",
    "sleightofhand":"dex",
    "stealth":"dex",
    "initiative":"dex"}

class Character:
    def __init__(self, name: str, mods: dict, proficiency_bonus: int, saveprofs: dict, skillprofs: dict):
        """
        name: character's name as str
        mods: map from score abbreviation (e.g. "dex") to modifier as int\n
        proficiency_bonus: proficienty bonus as int\n
        saveprofs: map from e.g. "strsave" to number of times proficiency is applied, as float\n
        skillprofs: map from e.g. "arcana" to number of times proficiency is applied, as float
        """
        self.name = name
        self.proficiency_bonus = proficiency_bonus
        self.modifiers = mods
        self.save_proficiencies = saveprofs
        self.skill_proficiencies = skillprofs
    
    def get_roll(self, macro: str) -> str:
        """
        macro: e.g. "acro" or "ints" or "dex"\n
        return: a die string, e.g. "1d20+2"
        """
        if macro in stats:
            bonus = self.modifiers[macro]
        elif macro in saves:
            bonus = self.modifiers[saves[macro]] + self.proficiency_bonus * self.save_proficiencies.get(macro, 0)
        elif macro in skills:
            bonus = self.modifiers[skills[macro]] + self.proficiency_bonus * self.skill_proficiencies.get(macro, 0)
        return "1d20{0:+d}".format(int(bonus))
    
    def __str__(self):
        s = "Name: {}\n".format(self.name)
        s += "Proficiency bonus: {}\n".format(self.proficiency_bonus)
        s += "|  " + "\t|  ".join(stats) + "\t|\n"
        s += "|  " + "\t|  ".join([str(self.modifiers[stat]) for stat in stats]) + "\t|\n"
        s += "save proficiencies:\n  " + "\n  ".join([save + (' x{}'.format(self.save_proficiencies[save]) if self.save_proficiencies[save] != 1 else "") for save in saves if self.save_proficiencies[save] != 0]) + "\n"
        s += "skill proficiencies:\n  " + "\n  ".join([skill + (' x{}'.format(self.skill_proficiencies[skill]) if self.skill_proficiencies[skill] != 1 else "") for skill in skills if self.skill_proficiencies[skill] != 0])
        return s
    
    def update(self, attribute: str, newval) -> bool:
        """Updates the specified attribute to have the new value. E.g. update("str", 2)"""
        if attribute in self.modifiers:
            self.modifiers[attribute] = int(newval)
        elif attribute in self.save_proficiencies:
            self.save_proficiencies[attribute] = float(newval)
        elif attribute in self.skill_proficiencies:
            self.skill_proficiencies[attribute] = float(newval)
        elif "bonus" in attribute or "prof" in attribute:
            self.proficiency_bonus = int(newval)
        else:
            return False
        return True
        
# Character usage

def load_characters() -> dict:
    """return: map from name to Character"""
    if not path.exists(characters_file_path):
        return {}
    with open(characters_file_path, "rb") as fp:
        return pickle.load(fp)

def save_characters(characters: dict):
    """Saves a map from name to Character to file"""
    with open(characters_file_path, "wb") as fp:
        return pickle.dump(characters, fp)

def get_character_roll(name: str, macro: str) -> str:
    """Loads the specified character and makes a roll. Returns none if invalid."""
    characters = load_characters()
    if name in characters and (macro in skills or macro in stats or macro in saves):
        return characters[name].get_roll(macro)
    else:
        return None

# Current character management and usage

def set_current_character(name: str):
    """Sets the current character to the given name."""
    with open(current_character_file_path, "w") as fp:
        fp.write(name)

def get_current_character_name() -> str:
    """Returns the name of the current character."""
    with open(current_character_file_path, "r") as fp:
        return fp.read()

def get_current_character_roll(macro: str) -> str:
    """Loads the current character and makes a roll. Returns none if invalid."""
    return get_character_roll(get_current_character_name(), macro)

# Character creation and saving

def save_character(character: Character):
    """Saves a character so it can be loaded in the future."""
    characters = load_characters()
    characters[character.name] = character
    save_characters(characters)

def make_character(name: str = None):
    """Makes a new character based on user input. Saves it upon completion."""
    if not name:
        name = input('name: ')
    else:
        print('name:', name)
    charprofbonus = int(input("proficiency bonus: "))
    charstats = {stat:int(input(stat + " modifier: ")) for stat in stats}
    saveprofs = {save:float(input(save + " proficiency: ")) for save in saves}
    skillprofs = {skill:float(input(skill + " proficiency: ")) for skill in skills}

    print("Successfully made", name)
    newchar = Character(name, charstats, charprofbonus, saveprofs, skillprofs)

    save_character(newchar)

def delete_character(name: str):
    """Deletes a character from file."""
    characters = load_characters()
    del characters[name]
    save_characters(characters)

def update_character(name: str):
    characters = load_characters()
    attribute = input("Attribute: ")
    newval = input("New value: ")
    characters[name].update(attribute, newval)
    save_characters(characters)
    print("Successfully updated", name)
