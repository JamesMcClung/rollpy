import pickle
import currentCharacter

stats = ["str", "con", "dex", "int", "wis", "cha"]
saves = [stat + "s" for stat in stats]
skills = {"anim":"wis", "acro":"dex", "arca":"int", "athl":"str", "dece":"cha", "hist":"int", "inti":"cha", "inve":"int", "natu":"int", "perf":"cha", "pers":"cha", "reli":"int", "stea":"dex", "slei":"dex", "init":"dex"}

class Character:
    def __init__(self, name: str, stats: dict, prof: int, skills: dict, saves: dict):
        """
        name: character's name as str
        stats: map from score abbreviation as str to modifier as int\n
        prof: proficienty bonus as int\n
        skills: map from skill abbreviation as str to number of times prof bonus is applied as float\n
        saves: map from save abbreviation as str to number of times prof bonus is applied as float\n
        """
        self.name = name
        self.prof = prof
        self.stats = stats
        self.proficiencies = {}
        self.proficiencies.update(skills)
        self.proficiencies.update(saves)
    
    def get_roll(self, macro: str) -> str:
        """
        macro: e.g. "acro" or "ints" or "dex"\n
        return: a die string, e.g. "1d20+2"
        """
        if macro in stats:
            bonus = self.stats[macro]
        elif macro in saves:
            bonus = self.stats[macro[0:3]] + self.prof * self.proficiencies.get(macro, 0)
        else:
            bonus = self.stats[skills[macro]] + self.prof * self.proficiencies.get(macro, 0)
        return "1d20{0:+d}".format(bonus)

file_path = "characters.txt"

def load_characters() -> dict:
    """return: map from name to Character"""
    try:
        with open(file_path, "rb") as fp:
            return pickle.load(fp)
    except Exception:
        return None

def get_character_roll(name: str, macro: str) -> str:
    """Loads the specified character and makes a roll. Returns none if invalid."""
    characters = load_characters()
    if name in characters and (macro in skills or macro in stats or macro in saves):
        return characters[name].get_roll(macro)
    else:
        return None

def get_current_character_roll(macro: str) -> str:
    """Loads the current character and makes a roll. Returns none if invalid."""
    return get_character_roll(currentCharacter.current_character, macro)

def save_character(character: Character):
    """Saves a character so it can be loaded in the future."""
    characters = load_characters()
    if not characters:
        characters = {}
    characters[character.name] = character
    with open(file_path, "wb") as fp:
        pickle.dump(characters, fp)
        

# for creation of new characters
if False:
    _my_stats = {"str":-1, "dex":3, "con":1, "int":4, "wis":1, "cha":1}
    _my_proficiency_bonus = 4

    _my_skills = {"acro":1, "arca":1, "dece":2, "hist":1, "inti":1, "inve":2, "perf":1, "pers":1, "stea":1}
    _my_saves = {"dex":1, "int":1}
    name = "Oberon"

    oberon = Character(name, _my_stats, _my_proficiency_bonus, _my_skills, _my_saves)
    save_character(oberon)
    print("saved character:", name)