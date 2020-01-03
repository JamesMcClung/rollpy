import pickle
from os import path, getcwd
from util import PATH_TO_DIR, ParseException
import modifier
from macros import assert_valid_macro

characters_file_path = PATH_TO_DIR + "/characters.txt"
current_character_file_path = PATH_TO_DIR + "/currentCharacter.txt"

stats = ["str", "dex", "con", "int", "wis", "cha"]
saves = {stat + "save":stat for stat in stats}
mods = {stat + "mod":stat for stat in stats}
skills = {
    "acrobatics":"dex",
    "animalhandling":"wis",
    "arcana":"int",
    "athletics":"str",
    "deception":"cha",
    "history":"int",
    "insight":"wis",
    "intimidation":"cha",
    "investigation":"int",
    "medicine":"wis",
    "nature":"int",
    "perception":"wis",
    "performance":"cha",
    "persuasion":"cha",
    "religion":"int",
    "sleightofhand":"dex",
    "stealth":"dex",
    "survival":"wis",
    "initiative":"dex"}

class Character:
    def __init__(self, name: str, modifiers: dict, proficiency_bonus: int, saveprofs: dict, skillprofs: dict):
        """
        name: character's name as str
        modifiers: map from score abbreviation (e.g. "dex") to modifier as int\n
        proficiency_bonus: proficienty bonus as int\n
        saveprofs: map from e.g. "strsave" to number of times proficiency is applied, as float\n
        skillprofs: map from e.g. "arcana" to number of times proficiency is applied, as float
        """
        self.name = name
        self.proficiency_bonus = proficiency_bonus
        self.modifiers = modifiers
        self.save_proficiencies = saveprofs
        self.skill_proficiencies = skillprofs
        self.macros = {}
    
    def get_roll(self, macro: str) -> str:
        """
        macro: e.g. "acro" or "ints" or "dex", or a character-specific macro\n
        return: a die string, e.g. "1d20+2"
        """
        # check character-specfic macro
        if macro in self.macros:
            return self.macros[macro]

        # check attributes
        bonus = None
        if macro in stats:
            bonus = self.modifiers[macro]
        elif macro in saves:
            bonus = self.modifiers[saves[macro]] + self.proficiency_bonus * self.save_proficiencies.get(macro, 0)
        elif macro in skills:
            bonus = self.modifiers[skills[macro]] + self.proficiency_bonus * self.skill_proficiencies.get(macro, 0)
        if not bonus is None:
            return "1d20{0:+d}".format(int(bonus))
        
        # check if modifier (the dnd kind, not the rollpy kind)
        if macro in mods:
            return modifier.get_bonus_modifier(self.modifiers[mods[macro]])
        elif macro == "prof":
            return modifier.get_bonus_modifier(self.proficiency_bonus)
        
        # no matches for macro
        return None
    
    def __str__(self):
        s = "Name: {}\n".format(self.name)
        s += "Proficiency bonus: {}\n".format(self.proficiency_bonus)
        s += "|  " + "\t|  ".join(stats) + "\t|\n"
        s += "|  " + "\t|  ".join([str(self.modifiers[stat]) for stat in stats]) + "\t|\n"
        s += "Save proficiencies:\n  " + "\n  ".join([save + (' x{}'.format(self.save_proficiencies[save]) if self.save_proficiencies[save] != 1 else "") for save in saves if self.save_proficiencies[save] != 0]) + "\n"
        s += "Skill proficiencies:\n  " + "\n  ".join([skill + (' x{}'.format(self.skill_proficiencies[skill]) if self.skill_proficiencies[skill] != 1 else "") for skill in skills if self.skill_proficiencies[skill] != 0])

        if self.macros:
            s += "\nMacros:\n  "
            s += "\n  ".join([macro + ": " + value for macro, value in self.macros.items()])
        return s
    
    def update(self, attribute: str, newval):
        """Updates the specified attribute to have the new value. E.g. update("str", 2)"""
        if attribute in stats:
            self.modifiers[attribute] = int(newval)
        elif attribute in saves:
            self.save_proficiencies[attribute] = float(newval)
        elif attribute in skills:
            self.skill_proficiencies[attribute] = float(newval)
        elif "bonus" in attribute or "prof" in attribute:
            self.proficiency_bonus = int(newval)
        else:
            raise KeyError(attribute)
    
    def add_macro(self, macro: str, value: str):
        """Adds the macro to the character. This can be used to override attribute macros, or just to add new functionality altogether."""
        self.macros[macro] = value
    
    def delete_macro(self, macro: str):
        del self.macros[macro]
        
# Character usage

def _load_characters() -> dict:
    """return: map from name to Character"""
    if not path.exists(characters_file_path):
        return {}
    with open(characters_file_path, "rb") as fp:
        return pickle.load(fp)
    
# load the characters only once at the start of execution
characters = _load_characters()

def save_characters(characters: dict):
    """Saves a map from name to Character to file"""
    with open(characters_file_path, "wb") as fp:
        return pickle.dump(characters, fp)

def get_character_roll(name: str, macro: str) -> str:
    """Loads the specified character and makes a roll. Returns none if invalid."""
    if name in characters:
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
    del characters[name]
    save_characters(characters)

def update_character(name: str):
    print("Updating", name)
    attribute = input("Attribute: ")
    newval = input("New value: ")
    characters[name].update(attribute, newval)
    save_characters(characters)
    print("Successfully updated", name)

def rename_character(oldname: str, newname: str = None):
    if not oldname in characters:
        print("Failure: no character is named '{}'".format(oldname))
        return

    if not newname:
        newname = input("New name for {}: ".format(oldname))
    if newname in characters:
        yes, no = 'y', 'n'
        overwrite = input("'{}' is already a character. Overwrite {}? ({}/{}): ".format(newname, newname, yes, no))
        while overwrite != yes and overwrite != no:
            overwrite = input("Please enter '{}' for yes or '{}' for no: ".format(yes, no))
        if overwrite == no:
            print("Did not rename {}.".format(oldname))
            return

    characters[newname] = characters.pop(oldname)
    if get_current_character_name() == oldname:
        set_current_character(newname)
    save_characters(characters)
    print("Successfully renamed {} to {}".format(oldname, newname))


def make_character_macro(name: str, macro: str = None, value: str = None):
    """Makes or remakes a macro for the specified character. If no macro is provided, the user is asked. If value is provided, so too must macro."""
    if macro:
        print("Making macro '{}' for {}".format(macro, name))
    else:
        print("Making macro for", name)
        macro = input("Macro: ")
    assert_valid_macro(macro)
    if not value:
        value = input("Value: ")
    characters[name].add_macro(macro, value)
    save_characters(characters)
    print("Successfully added macro '{}' with value '{}' to {}".format(macro, value, name))

def delete_character_macro(name: str, macro: str = None):
    """Deletes a macro from the specified character. If no macro is provided, the user is asked."""
    if macro:
        print("Deleting macro '{}' from {}".format(macro, name))
    else:
        macro = input('Macro to delete from {}:'.format(name))

    try:
        characters[name].delete_macro(macro)
        save_characters(characters)
        print("Successfully deleted macro '{}' from {}".format(macro, name))
    except KeyError:
        raise ParseException("Failure: {} does not have the macro '{}'".format(name, macro))