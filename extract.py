from xml.dom.minidom import parse
import xml.dom.minidom

ABILITY_NAMES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]
SAVE_NAMES = ["fortitude", "reflex", "will"]
HP_TYPES = ["nonlethal", "temporary", "wounds", "total"]
INIT_TYPES = ["abilitymod", "misc", "temporary", "total"]

################################################################################
# Extraction functions
################################################################################


def find_first_child_named(element, name):
    for c in element.childNodes:
        if isinstance(c, xml.dom.minidom.Element) and c.nodeName == name:
            return c
    return None


def find_children_named(element, name):
    return [
        c
        for c in element.childNodes
        if isinstance(c, xml.dom.minidom.Element) and c.nodeName == name
    ]


def extract_text(element):
    return (
        element.firstChild.wholeText
        if isinstance(element, xml.dom.minidom.Element)
        else None
    )


def extract_abilities(character):
    abilities = {}
    abilities_element = find_first_child_named(character, "abilities")
    for ability_name in ABILITY_NAMES:
        ability_element = abilities_element.getElementsByTagName(ability_name)[0]
        abilities[ability_name] = (
            extract_text(find_first_child_named(ability_element, "score")),
            extract_text(find_first_child_named(ability_element, "bonus")),
        )
    return abilities


def extract_languages(character):
    return [
        x
        for x in [
            extract_text(find_first_child_named(language, "name"))
            for language in find_first_child_named(character, "languagelist").childNodes
        ]
        if x
    ]


def extract_proficiencies(character):
    proficiencies = []
    for proficiency in character.getElementsByTagName("proficiencylist")[
        0
    ].getElementsByTagName("name"):
        proficiencies.append(proficiency.firstChild.wholeText)
    return proficiencies


def extract_saves(character):
    saves = {}
    save_elements = character.getElementsByTagName("saves")[0]
    for save_name in SAVE_NAMES:
        saves[save_name] = (
            save_elements.getElementsByTagName(save_name)[0]
            .getElementsByTagName("total")[0]
            .firstChild.wholeText
        )
    return saves


def extract_alignment(character):
    return extract_text(find_first_child_named(character, "alignment"))


def extract_size(character):
    return extract_text(find_first_child_named(character, "size"))


def extract_hp(character):
    hp = {}
    hp_element = character.getElementsByTagName("hp")[0]
    for hp_name in HP_TYPES:
        hp[hp_name] = hp_element.getElementsByTagName(hp_name)[0].firstChild.wholeText
    return hp


def extract_initiative(character):
    init = {}
    init_element = character.getElementsByTagName("initiative")[0]
    for init_name in INIT_TYPES:
        init[init_name] = init_element.getElementsByTagName(init_name)[
            0
        ].firstChild.wholeText
    return init


################################################################################
# Process the file
################################################################################

dom_tree = xml.dom.minidom.parse("Simone.xml")
character = dom_tree.documentElement.getElementsByTagName("character")[0]

print("Initiative:")
init_data = extract_initiative(character)
for init_name in INIT_TYPES:
    print("  {0}: {1}".format(init_name.capitalize(), init_data[init_name]))

print("HP:")
hp_data = extract_hp(character)
for hp_name in HP_TYPES:
    print("  {0}: {1}".format(hp_name.capitalize(), hp_data[hp_name]))

print("Alignment: {0}".format(extract_alignment(character)))

print("Size: {0}".format(extract_size(character)))

print("Abilities:")
abilities = extract_abilities(character)
for name in ABILITY_NAMES:
    print(
        "  {0}: {1} bonus: {2}".format(
            name.capitalize(), abilities[name][0], abilities[name][1]
        )
    )

print("Languages:")
for l in extract_languages(character):
    print("  {0}".format(l))

print("Proficiencies:")
for l in extract_proficiencies(character):
    print("  {0}".format(l))

print("Saves:")
saves = extract_saves(character)
for save_name in SAVE_NAMES:
    print("  {0}: {1}".format(save_name.capitalize(), saves[save_name]))
