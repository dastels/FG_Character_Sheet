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
AC_TYPES = ["cmd", "flatfooted", "general", "touch"]
AC_SOURCES = [
    "abilitymod",
    "abilitymod2",
    "armor",
    "cmdabilitymod",
    "cmdbasemod",
    "cmdmisc",
    "deflection",
    "dodge",
    "ffmisc",
    "misc",
    "naturalarmor",
    "shield",
    "size",
    "temporary",
    "touchmisc",
]
################################################################################
# Helper functions
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


def extract_formatted_text(element):
    return extract_text(find_first_child_named(element, "p"))


def extract_nested_names(element):
    return [
        x
        for x in [
            extract_text(find_first_child_named(possibly_named_element, "name"))
            for possibly_named_element in element.childNodes
        ]
        if x
    ]


def first_sentence(text):
    period_index = text.find(".")
    return text if period_index == -1 else text[0 : period_index + 1]


################################################################################
# Extraction functions
################################################################################


def extract_name(character):
    return extract_text(find_first_child_named(character, "name"))


def extract_level(character):
    return extract_text(find_first_child_named(character, "level"))


def extract_class_level(character):
    return extract_text(find_first_child_named(character, "classlevel"))


def extract_race(character):
    return extract_text(find_first_child_named(character, "race"))


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
    return extract_nested_names(find_first_child_named(character, "languagelist"))


def extract_proficiencies(character):
    proficiencies = []
    for proficiency in character.getElementsByTagName("proficiencylist")[
        0
    ].getElementsByTagName("name"):
        proficiencies.append(extract_text(proficiency))
    return proficiencies


def extract_saves(character):
    saves = {}
    save_elements = find_first_child_named(character, "saves")
    for save_name in SAVE_NAMES:
        save_data = {}
        for data_element in [
            el
            for el in find_first_child_named(save_elements, save_name).childNodes
            if isinstance(el, xml.dom.minidom.Element)
        ]:
            save_data[data_element.tagName] = extract_text(data_element)
        saves[save_name] = save_data
    return saves


def extract_alignment(character):
    return extract_text(find_first_child_named(character, "alignment"))


def extract_size(character):
    return extract_text(find_first_child_named(character, "size"))


def extract_hp(character):
    hp = {}
    hp_element = find_first_child_named(character, "hp")
    for hp_name in HP_TYPES:
        hp[hp_name] = hp_element.getElementsByTagName(hp_name)[0].firstChild.wholeText
    return hp


def extract_initiative(character):
    init = {}
    init_element = find_first_child_named(character, "initiative")
    for init_name in INIT_TYPES:
        init[init_name] = extract_text(find_first_child_named(init_element, init_name))
    return init


def extract_speed(character):
    speed = {}
    speed_element = find_first_child_named(character, "speed")

    for data_element in [
        el for el in speed_element.childNodes if isinstance(el, xml.dom.minidom.Element)
    ]:
        speed[data_element.tagName] = extract_text(data_element)
    return speed


def extract_ac(character):
    ac_element = find_first_child_named(character, "ac")

    ac_sources = {}
    sources_element = find_first_child_named(ac_element, "sources")
    for ac_name in AC_SOURCES:
        ac_sources[ac_name] = extract_text(
            find_first_child_named(sources_element, ac_name)
        )

    ac_totals = {}
    totals_element = find_first_child_named(ac_element, "totals")
    for ac_name in AC_TYPES:
        ac_totals[ac_name] = extract_text(
            find_first_child_named(totals_element, ac_name)
        )

    return {"sources": ac_sources, "totals": ac_totals}


def extract_attack_bonuses(character):
    ab_element = find_first_child_named(character, "attackbonus")
    bonuses = {}
    bonuses["base"] = extract_text(find_first_child_named(ab_element, "base"))
    for bonus_element in [
        el
        for el in ab_element.childNodes
        if isinstance(el, xml.dom.minidom.Element) and el.tagName != "base"
    ]:
        bonus_data = {}
        for data_element in [
            el
            for el in bonus_element.childNodes
            if isinstance(el, xml.dom.minidom.Element)
        ]:
            bonus_data[data_element.tagName] = extract_text(data_element)
        bonuses[bonus_element.tagName] = bonus_data
    return bonuses


def extract_defenses(character):
    defense_element = find_first_child_named(character, "defenses")
    defenses = {}
    for defense_element in [
        el
        for el in defense_element.childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        defense_data = {}
        for data_element in [
            el
            for el in defense_element.childNodes
            if isinstance(el, xml.dom.minidom.Element)
        ]:
            defense_data[data_element.tagName] = extract_text(data_element)
        defenses[defense_element.tagName] = defense_data
    return defenses


def extract_encumbrance(character):
    encumbrance = {}
    encumbrance_element = find_first_child_named(character, "encumbrance")

    for data_element in [
        el
        for el in encumbrance_element.childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        encumbrance[data_element.tagName] = extract_text(data_element)
    return encumbrance


def extract_feats(character):
    feats = []
    for feat_element in [
        el
        for el in find_first_child_named(character, "featlist").childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        feats.append(
            {
                "name": extract_text(find_first_child_named(feat_element, "name")),
                "description": extract_text(
                    find_first_child_named(feat_element, "summary")
                ),
            }
        )
    return feats


def extract_traits(character):
    traits = []
    for trait_element in [
        el
        for el in find_first_child_named(character, "traitlist").childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        traits.append(
            {
                "name": extract_text(find_first_child_named(trait_element, "name")),
                "description": first_sentence(
                    extract_formatted_text(
                        find_first_child_named(trait_element, "text")
                    )
                ),
            }
        )
    return traits


def extract_skills(character):
    skills = {}
    for skill_element in [
        el
        for el in find_first_child_named(character, "skilllist").childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        base_skill_name = extract_text(find_first_child_named(skill_element, "label"))
        sub_skill_name = extract_text(find_first_child_named(skill_element, "sublabel"))

        skill_name = (
            base_skill_name
            if sub_skill_name is None
            else "{0} ({1})".format(base_skill_name, sub_skill_name)
        )
        skills[skill_name] = {
            "ranks": extract_text(find_first_child_named(skill_element, "ranks")),
            "ability_mod": extract_text(find_first_child_named(skill_element, "stat")),
            "misc_bonus": extract_text(find_first_child_named(skill_element, "misc")),
            "total": extract_text(find_first_child_named(skill_element, "total")),
            "class_skill": extract_text(
                find_first_child_named(skill_element, "state")
            ),  # ??
        }
    return skills


def extract_inventory(character):
    inventory = []
    for skill_element in [
        el
        for el in find_first_child_named(character, "inventorylist").childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        inventory.append(
            {
                "name": extract_text(find_first_child_named(skill_element, "name")),
                "type": extract_text(find_first_child_named(skill_element, "type")),
                "subtype": extract_text(
                    find_first_child_named(skill_element, "subtype")
                ),
                "cost": extract_text(find_first_child_named(skill_element, "cost")),
                "weight": extract_text(find_first_child_named(skill_element, "weight")),
                "slot": extract_text(find_first_child_named(skill_element, "slot")),
            }
        )
    return inventory


################################################################################
# Process the file
################################################################################

dom_tree = xml.dom.minidom.parse("Simone_with_wand.xml")
character = dom_tree.documentElement.getElementsByTagName("character")[0]

print("Name: {0}".format(extract_name(character)))

print("Level: {0}".format(extract_level(character)))

print("Class Level: {0}".format(extract_class_level(character)))

print("Race: {0}".format(extract_race(character)))

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

print("Speed:")
speed_data = extract_speed(character)
for name, value in speed_data.items():
    print("  {0}: {1}".format(name.capitalize(), value))

print("Abilities:")
abilities = extract_abilities(character)
for name in ABILITY_NAMES:
    print(
        "  {0}: {1} bonus: {2}".format(
            name.capitalize(), abilities[name][0], abilities[name][1]
        )
    )

ac_data = extract_ac(character)
print("AC Totals:")
for ac_name in AC_TYPES:
    print("  {0}: {1}".format(ac_name.capitalize(), ac_data["totals"][ac_name]))
print("AC Sources:")
for ac_name in AC_SOURCES:
    print("  {0}: {1}".format(ac_name.capitalize(), ac_data["sources"][ac_name]))


print("Languages:")
for l in extract_languages(character):
    print("  {0}".format(l))

print("Proficiencies:")
for l in extract_proficiencies(character):
    print("  {0}".format(l))

print("Saves:")
saves = extract_saves(character)
for save_name in SAVE_NAMES:
    print("  {0}".format(save_name.capitalize()))
    for name, value in saves[save_name].items():
        print("    {0}: {1}".format(name.capitalize(), value))

attack_bonuses = extract_attack_bonuses(character)
print("Attack Bonuses:")
for bonus_name, bonus_data in attack_bonuses.items():
    if bonus_name == "base":
        print("  Base: {0}".format(bonus_data))
    else:
        print("  {0}".format(bonus_name.capitalize()))
        for name, value in bonus_data.items():
            print("    {0}: {1}".format(name.capitalize(), value))


defenses = extract_defenses(character)
print("Defenses:")
for defense_name, defense_data in defenses.items():
    print("  {0}".format(defense_name.capitalize()))
    for name, value in defense_data.items():
        print("    {0}: {1}".format(name.capitalize(), value))

print("Encumbrance:")
encumbrance_data = extract_encumbrance(character)
for name, value in encumbrance_data.items():
    print("  {0}: {1}".format(name.capitalize(), value))

print("Feats:")
feat_data = extract_feats(character)
for feat in feat_data:
    print("  {0} - {1}".format(feat["name"], feat["description"]))

print("Traits:")
trait_data = extract_traits(character)
for trait in trait_data:
    print("  {0} - {1}".format(trait["name"], trait["description"]))

print("Skills:")
skill_data = extract_skills(character)
for skill, data in skill_data.items():
    print("  {0}".format(skill))
    for name, value in data.items():
        print("    {0}: {1}".format(name, value))

print("Inventory:")
for item in extract_inventory(character):
    print("  {0}".format(item["name"]))
    print("    type: {0}".format(item["type"]))
    print("    cost: {0}".format(item["cost"]))
    print("    weight: {0}".format(item["weight"]))
    if item["slot"]:
        print("    slot: {0}".format(item["slot"]))
