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


def extract_deity(character):
    return extract_text(find_first_child_named(character, "deity"))


def extract_level(character):
    return extract_text(find_first_child_named(character, "level"))


def extract_classes(character):
    classes = []
    for class_element in [
        el
        for el in find_first_child_named(character, "classes").childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        classes.append(
            {
                "name": extract_text(find_first_child_named(class_element, "name")),
                "level": extract_text(find_first_child_named(class_element, "level")),
            }
        )
    return classes


def extract_race(character):
    return extract_text(find_first_child_named(character, "race"))


def extract_age(character):
    return extract_text(find_first_child_named(character, "age"))


def extract_appearance(character):
    return extract_text(find_first_child_named(character, "appearance"))


def extract_gender(character):
    return extract_text(find_first_child_named(character, "gender"))


def extract_height(character):
    return extract_text(find_first_child_named(character, "height"))


def extract_weight(character):
    return extract_text(find_first_child_named(character, "weight"))


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


def extract_diety(character):
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


def extract_weapons(character):
    weapons = []
    for weapon_element in [
        el
        for el in find_first_child_named(character, "weaponlist").childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        weapon = {}
        weapon["name"] = extract_text(find_first_child_named(weapon_element, "name"))
        weapon["attacks"] = extract_text(
            find_first_child_named(weapon_element, "attacks")
        )

        bonus_string = ""
        for bonus in range(1, int(weapon["attacks"]) + 1):
            if bonus > 1:
                bonus_string += "/"
            bonus_string += extract_text(
                find_first_child_named(weapon_element, "attack" + str(bonus))
            )
        weapon["attack_bonus"] = bonus_string
        weapon["crit_attack_range"] = extract_text(
            find_first_child_named(weapon_element, "critatkrange")
        )
        for damage_element in [
            el
            for el in find_first_child_named(weapon_element, "damagelist").childNodes
            if isinstance(el, xml.dom.minidom.Element)
        ]:
            weapon["crit_multiplier"] = extract_text(
                find_first_child_named(damage_element, "critmult")
            )
            weapon["damage_stat"] = find_first_child_named(damage_element, "stat")
            weapon["damage_stat_max"] = find_first_child_named(
                damage_element, "statmax"
            )
            weapon["damage_stat_multiplier"] = find_first_child_named(
                damage_element, "statmult"
            )
            weapon["damage_dice"] = extract_text(
                find_first_child_named(damage_element, "dice")
            )
            weapon["damage_bonus"] = extract_text(
                find_first_child_named(damage_element, "bonus")
            )
            weapon["damage_type"] = ",".join(
                [
                    type[0].upper()
                    for type in extract_text(
                        find_first_child_named(damage_element, "type")
                    )
                    .strip()
                    .split(",")
                ]
            )
        max_ammo = extract_text(find_first_child_named(weapon_element, "maxammo"))
        ammo = extract_text(find_first_child_named(weapon_element, "ammo"))
        weapon["ammo"] = (
            None
            if max_ammo == "0"
            else (str(int(max_ammo) - (int(ammo) if ammo else 0)) if max_ammo else None)
        )
        range_inc = extract_text(
            find_first_child_named(weapon_element, "rangeincrement")
        )
        weapon["range"] = None if range_inc == "0" else range_inc
        weapons.append(weapon)
    return weapons


def extract_special_abilities(character):
    return [
        extract_text(find_first_child_named(ability_element, "name"))
        for ability_element in [
            el
            for el in find_first_child_named(character, "specialabilitylist").childNodes
            if isinstance(el, xml.dom.minidom.Element)
        ]
    ]


def extract_spells(character):
    spells = {}
    spellset = find_first_child_named(character, "spellset")
    first_set = find_first_child_named(spellset, "id-00001")
    spells["dc"] = extract_text(
        find_first_child_named(find_first_child_named(first_set, "dc"), "total")
    )
    for level in [
        el
        for el in find_first_child_named(first_set, "levels").childNodes
        if isinstance(el, xml.dom.minidom.Element)
    ]:
        level_name = extract_text(find_first_child_named(level, "level"))
        spells[level_name] = []
        for spell_element in [
            el
            for el in find_first_child_named(level, "spells").childNodes
            if isinstance(el, xml.dom.minidom.Element)
        ]:
            spells[level_name].append(
                {
                    "name": extract_text(find_first_child_named(spell_element, "name")),
                    "range": extract_text(
                        find_first_child_named(spell_element, "range")
                    ),
                    "save": extract_text(find_first_child_named(spell_element, "save")),
                    "summary": extract_text(
                        find_first_child_named(spell_element, "shortdescription")
                    ),
                    "sr": extract_text(find_first_child_named(spell_element, "sr")),
                    "school": extract_text(
                        find_first_child_named(spell_element, "school")
                    )
                    .split()[0]
                    .lower(),
                    "duration": extract_text(
                        find_first_child_named(spell_element, "duration")
                    ),
                }
            )
    return spells


################################################################################
# Process the file
################################################################################

dom_tree = xml.dom.minidom.parse("Simone_with_personal.xml")
character = dom_tree.documentElement.getElementsByTagName("character")[0]

print("Name: {0}".format(extract_name(character)))

character_level = extract_level(character)
print("Level: {0}".format(character_level))

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

print("Age: {0}".format(extract_age(character)))

print("Appearance: {0}".format(extract_appearance(character)))

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

print("Special Abilities:")
for ability in extract_special_abilities(character):
    print("  {0}".format(ability))


def summarize_save(spell, dc):
    if spell["save"] is None:
        return ""
    elif "will" in spell["save"].lower():
        return "Will {0}".format(dc)
    elif "reflex" in spell["save"].lower():
        return "Ref {0}".format(dc)
    elif "fortitude" in spell["save"].lower():
        return "Fort {0}".format(dc)
    else:
        return ""


def contains_number(s):
    for digit in range(0, 10):
        if s.find(str(digit)) > -1:
            return True
    return False


def pluralize(unit, value):
    if value == 1 or unit[-1] == "s" or unit == "ft.":
        return unit
    elif unit[-1] == ".":
        return unit[:-1] + "s."
    else:
        return unit + "s"


def process_equation(duration, lvl):
    # print("PROCESSING {0}".format(duration))
    local_duration = duration.lower()
    level = int(lvl)

    if local_duration.endswith("(d)"):
        local_duration = local_duration[:-3]

    # extract the equation
    open_paran_index = local_duration.find("(")
    if open_paran_index > -1:
        closing_paren_index = local_duration.find(")")
        local_duration = local_duration[open_paran_index + 1 : closing_paren_index]

    # drop any preamble
    if local_duration.find(",") > -1:
        local_duration = local_duration.split(",")[1]

    if local_duration.find("up to") > -1:
        local_duration = local_duration.split("up to")[1].strip()
    elif local_duration.find("or") > -1:
        terms = local_duration.split("or")
        local_duration = (
            terms[0].strip() if contains_number(terms[0]) else terms[1].strip()
        )
        # print("--> {0}".format(local_duration))

    # check if it's a compound term
    plus_index = local_duration.find("+")
    if plus_index > -1:  # it's base + variable
        base_term = local_duration[:plus_index].strip()
        variable_term = local_duration[plus_index + 1 :].strip()
    elif local_duration.find("/") > -1:  # check if it's a variable term
        base_term = "0"
        variable_term = local_duration  # it is.. no base, but variable
    else:  # no variable term, just a constant
        base_term = local_duration
        variable_term = "0"

    # process the variable part
    if variable_term != "0":
        per_index = variable_term.find("/")  # we know it's there
        variable_item = variable_term[:per_index].strip()
        if variable_item.find(" ") > -1:
            variable_constant, variable_unit = variable_item.split()
        else:
            variable_constant = variable_item
            variable_unit = ""
        multiplier = variable_term[per_index + 1 :].strip()
    else:
        variable_constant = "0"
        variable_unit = ""
        multiplier = "0"

    if base_term.find(" ") > -1:
        constant, unit = base_term.split()[-2:]
    else:
        constant = base_term
        unit = ""

    # constant + variable_constant * multiplier
    try:
        constant = int(constant)
    except:
        pass
    variable_constant = int(variable_constant)
    if multiplier == "level":
        multiplier = level
    elif multiplier.endswith("levels"):
        multiplier = level / int(multiplier.split()[0].strip())
    else:
        multiplier = int(multiplier)
    if unit == "":
        unit = variable_unit

    # print(
    #     "CONSTANT: {0}, UNIT: {1}, VARIABLE_CONSTANT: {2}, MULTIPLIER: {3}".format(
    #         constant, unit, variable_constant, multiplier
    #     )
    # )

    if unit == "":
        return constant
    else:
        value = constant + (variable_constant * multiplier)
        return str("{0} {1}".format(value, pluralize(unit, value)))


print("Spells:")
spell_data = extract_spells(character)
for level in range(0, 10):
    print("  Level {0}".format(level))
    for spell in spell_data[str(level)]:
        print("    {0}".format(spell["name"]))
        print("      School: {0}".format(spell["school"]))
        print("      Save: {0}".format(summarize_save(spell, spell_data["dc"])))
        print("      SR?: {0}".format(spell["sr"].lower() if spell["sr"] else ""))
        print(
            "      Range: {0}".format(process_equation(spell["range"], character_level))
        )
        print(
            "      Duration: {0}".format(
                process_equation(spell["duration"], character_level)
            )
        )
        print("      Summary: {0}".format(spell["summary"]))
