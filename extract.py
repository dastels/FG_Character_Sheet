from xml.dom.minidom import parse
import xml.dom.minidom
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


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


def damage_sign_of(value):
    if value < 0:
        return "-"
    elif value > 0:
        return "+"
    else:
        return ""


def abs_value_of(value):
    if value == 0:
        return ""
    else:
        return abs(value)


def dump(character_file):
    dom_tree = xml.dom.minidom.parse(character_file)
    character = dom_tree.documentElement.getElementsByTagName("character")[0]

    print("Name: {0}".format(extract_name(character)))

    character_level = extract_level(character)
    print("Level: {0}".format(character_level))

    print("Classes:")
    for char_class in extract_classes(character):
        print("  {0} {1}".format(char_class["name"], char_class["level"]))

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

    print("Deity: {0}".format(extract_deity(character)))

    print("Size: {0}".format(extract_size(character)))

    print("Age: {0}".format(extract_age(character)))

    print("Appearance: {0}".format(extract_appearance(character)))

    print("Gender: {0}".format(extract_gender(character)))

    print("Height: {0}".format(extract_height(character)))

    print("Weight: {0}".format(extract_weight(character)))

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
                "      Range: {0}".format(
                    process_equation(spell["range"], character_level)
                )
            )
            print(
                "      Duration: {0}".format(
                    process_equation(spell["duration"], character_level)
                )
            )
            print("      Summary: {0}".format(spell["summary"]))

    print("Weapons:")
    for weapon in extract_weapons(character):
        print("  {0}".format(weapon["name"]))
        print("    Attack Bonus: {0}".format(weapon["attack_bonus"]))
        damage_bonus = int(weapon["damage_bonus"])
        print(
            "    Damage: {0}{1}{2}".format(
                weapon["damage_dice"],
                damage_sign_of(damage_bonus),
                abs_value_of(damage_bonus),
            )
        )
        print("    Crit Range: {0}".format(weapon["crit_attack_range"]))
        print("    Crit Multipler: {0}".format(weapon["crit_multiplier"]))
        print("    Type: {0}".format(weapon["damage_type"]))
        if weapon["range"]:
            print("    Range: {0}".format(weapon["range"]))
        if weapon["ammo"]:
            print("    Ammo: {0}".format(weapon["ammo"]))


# dump("Simone_with_personal.xml")


def extract_sub_skill(skill):
    op_index = skill.find("(")
    cp_index = skill.find(")")
    return skill[op_index + 1 : cp_index]


def partition(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def to_pdf(filename):
    dom_tree = xml.dom.minidom.parse(filename)
    character = dom_tree.documentElement.getElementsByTagName("character")[0]

    character_name = extract_name(character)
    character_level = extract_level(character)

    # Character page
    packet = io.BytesIO()

    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)

    # Character page

    # basic
    can.drawString(50, 698, character_name)
    can.setFontSize(size=10)
    can.drawString(175, 676, extract_race(character))
    can.drawString(50, 655, extract_alignment(character))
    can.drawString(175, 655, extract_deity(character))

    # Initiative
    initiative = extract_initiative(character)
    can.drawString(315, 703, initiative["abilitymod"])
    if initiative["misc"] != "0":
        can.drawString(450, 703, initiative["misc"])
    can.drawString(540, 715, initiative["total"])

    # Classes
    for i, cl in enumerate(extract_classes(character)):
        can.drawString(50, 615 - (i * 15), cl["name"])
        can.drawString(275, 615 - (i * 15), cl["level"])

    # Speeds
    can.drawString(395, 644, extract_speed(character)["total"])

    # Ability Scores
    count = 0
    for name, ability in extract_abilities(character).items():
        can.setFont("Helvetica-Bold", 18)
        if len(ability[0]) == 1:
            can.drawString(225, 508 - (count * 35), ability[0])
        else:
            can.drawString(220, 508 - (count * 35), ability[0])
        can.setFont("Helvetica", 10)
        can.drawString(260, 512 - (count * 35), ability[1])
        count += 1

    # Armor Class
    ac = extract_ac(character)
    can.setFont("Helvetica-Bold", 18)
    can.drawString(357, 293, ac["totals"]["general"])
    can.setFont("Helvetica", 10)
    can.drawString(225, 283, ac["totals"]["flatfooted"])
    can.drawString(270, 283, ac["totals"]["touch"])
    can.drawString(315, 283, ac["totals"]["cmd"])

    # HP
    hp = extract_hp(character)
    can.setFont("Helvetica-Bold", 18)
    can.drawString(535, 293, hp["total"])

    # Saves
    saves = extract_saves(character)
    can.setFont("Helvetica-Bold", 18)
    for i, save_name in enumerate(SAVE_NAMES):
        value = saves[save_name]["total"]
        if len(value) == 1:
            can.drawString(363, 162 - (i * 39), value)
        else:
            can.drawString(358, 162 - (i * 39), value)

    # Offense Page
    can.showPage()

    ab = extract_attack_bonuses(character)

    # Attack bonuses

    can.setFont("Helvetica-Bold", 18)
    can.drawString(510, 695, ab["base"])

    can.setFont("Helvetica", 10)
    can.drawString(215, 662, ab["base"])
    can.drawString(262, 662, ab["melee"]["abilitymod"])
    can.drawString(310, 662, ab["melee"]["size"])
    can.drawString(360, 662, ab["melee"]["misc"])
    can.setFont("Helvetica-Bold", 18)
    can.drawString(410, 660, ab["melee"]["total"])

    can.setFont("Helvetica", 10)
    can.drawString(215, 620, ab["base"])
    can.drawString(262, 620, ab["ranged"]["abilitymod"])
    can.drawString(310, 620, ab["ranged"]["size"])
    can.drawString(360, 620, ab["ranged"]["misc"])
    can.setFont("Helvetica-Bold", 18)
    can.drawString(410, 619, ab["ranged"]["total"])

    can.setFont("Helvetica", 10)
    can.drawString(215, 580, ab["base"])
    can.drawString(262, 580, ab["grapple"]["abilitymod"])
    can.drawString(310, 580, ab["grapple"]["size"])
    can.drawString(360, 580, ab["grapple"]["misc"])
    can.setFont("Helvetica-Bold", 18)
    can.drawString(410, 578, ab["grapple"]["total"])

    can.setFont("Helvetica", 10)

    # Attacks

    count = 0
    for weapon in extract_weapons(character):
        can.drawString(40, 510 - (count * 53.5), weapon["name"])
        can.drawString(180, 505 - (count * 53.5), weapon["attack_bonus"])
        damage_bonus = int(weapon["damage_bonus"])
        can.drawString(
            260,
            505 - (count * 53.5),
            "{0}{1}{2}".format(
                weapon["damage_dice"],
                damage_sign_of(damage_bonus),
                abs_value_of(damage_bonus),
            ),
        )
        can.drawString(350, 505 - (count * 53.5), weapon["crit_attack_range"])
        can.drawString(395, 505 - (count * 53.5), weapon["crit_multiplier"])
        can.drawString(438, 505 - (count * 53.5), weapon["damage_type"])
        if weapon["range"]:
            can.drawString(480, 505 - (count * 53.5), weapon["range"])
        if weapon["ammo"]:
            can.drawString(525, 505 - (count * 53.5), weapon["ammo"])
        count += 1

    # Skills Page
    can.showPage()

    skill_locations = {
        "Acrobatics": 704,
        "Appraise": 690,
        "Bluff": 676,
        "Climb": 662,
        "Craft": 649,
        "Diplomacy": 620,
        "Disable Device": 607,
        "Disguise": 593,
        "Escape Artist": 579,
        "Fly": 565,
        "Handle Animal": 552,
        "Heal": 538,
        "Intimidate": 524,
        "Knowledge (Arcana)": 510,
        "Knowledge (Dungeoneering)": 496,
        "Knowledge (Engineering)": 482,
        "Knowledge (Geography)": 468,
        "Knowledge (History)": 454,
        "Knowledge (Local)": 441,
        "Knowledge (Nature)": 427,
        "Knowledge (Nobility)": 413,
        "Knowledge (Planes)": 399,
        "Knowledge (Religion)": 385,
        "Linguistics": 372,
        "Perception": 358,
        "Perform": 344,
        "Profession": 317,
        "Ride": 289,
        "Sense Motive": 275,
        "Sleight of Hand": 262,
        "Spellcraft": 248,
        "Stealth": 234,
        "Survival": 220,
        "Swim": 206,
        "Use Magic Device": 192,
    }

    number_of_crafts = 0
    number_of_performs = 0
    number_of_professions = 0
    skill_data = extract_skills(character)
    for skill, data in skill_data.items():
        y = 0
        if skill.startswith("Craft"):
            y = skill_locations["Craft"]
            can.setFont("Helvetica", 8)
            can.drawString(85, y - (14 * number_of_crafts), extract_sub_skill(skill))
            number_of_crafts += 1
        elif skill.startswith("Perform"):
            y = skill_locations["Perform"]
            can.setFont("Helvetica", 8)
            can.drawString(95, y - (14 * number_of_performs), extract_sub_skill(skill))
            number_of_performs += 1
        elif skill.startswith("Profession"):
            y = skill_locations["Profession"]
            can.setFont("Helvetica", 8)
            can.drawString(
                105, y - (14 * number_of_professions), extract_sub_skill(skill)
            )
            number_of_professions += 1
        elif skill in skill_locations:
            y = skill_locations[skill]

        if y > 0:
            if data["class_skill"] == "1":
                can.drawString(44, y, "x")
            can.setFont("Helvetica", 10)
            if data["ranks"] != "0":
                can.drawString(162, y, data["ranks"])
            if data["ability_mod"] != "0":
                can.drawString(235, y, data["ability_mod"])
            if data["misc_bonus"] != "0":
                can.drawString(378, y, data["misc_bonus"])
            if data["total"] != "0":
                can.drawString(450, y, data["total"])

    # Feats/Traits Page
    can.showPage()
    for i, feat in enumerate(extract_feats(character)):
        can.setFont("Helvetica", 10)
        can.drawString(40, 700 - (i * 14.5), feat["name"])
        can.setFont("Helvetica", 8)
        can.drawString(165, 700 - (i * 14.5), feat["description"])
    for i, trait in enumerate(extract_traits(character)):
        can.setFont("Helvetica", 10)
        can.drawString(40, 225 - (i * 14.5), trait["name"])
        can.setFont("Helvetica", 8)
        can.drawString(165, 225 - (i * 14.5), trait["description"])

    can.setFont("Helvetica", 10)
    for i, langs in enumerate(partition(extract_languages(character), 8)):
        can.drawString(40, 104 - (i * 14), ", ".join(langs))

    # Spells Page
    can.showPage()
    line = 0
    spell_data = extract_spells(character)
    can.setFont("Helvetica", 8)
    for level in range(0, 10):
        for spell in spell_data[str(level)]:
            can.setFont("Helvetica", 8)
            y = 708 - (line * 15.1)
            can.drawString(50, y, str(level))
            can.drawString(80, y, spell["name"])
            can.drawString(170, y, spell["school"])
            can.drawString(235, y, summarize_save(spell, spell_data["dc"]))
            can.drawString(
                278, y, spell["sr"].split()[0].lower() if spell["sr"] else ""
            )
            can.drawString(300, y, process_equation(spell["range"], character_level))
            duration = process_equation(spell["duration"], character_level)
            can.setFont("Helvetica", 8 if duration[0] in "0123456789" else 6)
            can.drawString(345, y, duration)
            can.setFont("Helvetica", 6)
            can.drawString(390, y, spell["summary"])
            line += 1

    # Inventory Page
    can.showPage()

    can.setFont("Helvetica", 8)
    number_of_weapons = 0
    number_of_goods = 0
    number_of_magic = 0
    number_of_rings = 0
    for item in extract_inventory(character):
        if item["type"] == "Goods and Services":
            pass
            # can.drawString(303, 200 - (number_of_goods * 15), item["name"])
            # can.drawString(476, 196 - (number_of_goods * 15), item["cost"])
            # can.drawString(520, 196 - (number_of_goods * 15), item["weight"])
            # number_of_goods += 1
        elif item["type"] == "Weapon":
            can.drawString(40, 270 - (number_of_weapons * 15), item["name"])
            can.drawString(212, 266 - (number_of_weapons * 15), item["cost"])
            can.drawString(256, 266 - (number_of_weapons * 15), item["weight"])
            number_of_weapons += 1
        elif item["type"] == "Wand" or item["type"] == "Potion":
            can.drawString(303, 270 - (number_of_magic * 15), item["name"])
            can.drawString(476, 266 - (number_of_magic * 15), item["cost"])
            can.drawString(520, 266 - (number_of_magic * 15), item["weight"])
            number_of_magic += 1
        elif item["slot"]:
            if item["slot"] == "ring":
                can.drawString(435, 507 - (number_of_rings * 14), item["name"])
                number_of_rings += 1

        # print("  {0}".format(item["name"]))
        # print("    type: {0}".format(item["type"]))
        # print("    cost: {0}".format(item["cost"]))
        # print("    weight: {0}".format(item["weight"]))
        # if item["slot"]:
        #     print("    slot: {0}".format(item["slot"]))

    # Gear Page
    can.showPage()
    line = 0
    can.setFont("Helvetica", 8)
    for item in extract_inventory(character):
        if item["type"] == "Goods and Services":
            can.drawString(40, 713 - (line * 15), item["name"])
            can.drawString(212, 713 - (line * 15), item["cost"])
            can.drawString(256, 713 - (line * 15), item["weight"])
            line += 1

    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open("Player_Character_Folio.pdf", "rb"))
    output = PdfFileWriter()

    character_page = existing_pdf.getPage(2)
    character_page.mergePage(new_pdf.getPage(0))
    output.addPage(character_page)

    offense_page = existing_pdf.getPage(4)
    offense_page.mergePage(new_pdf.getPage(1))
    output.addPage(offense_page)

    skill_page = existing_pdf.getPage(5)
    skill_page.mergePage(new_pdf.getPage(2))
    output.addPage(skill_page)

    feat_page = existing_pdf.getPage(6)
    feat_page.mergePage(new_pdf.getPage(3))
    output.addPage(feat_page)

    spell_page = existing_pdf.getPage(8)
    spell_page.mergePage(new_pdf.getPage(4))
    output.addPage(spell_page)

    inventory_page = existing_pdf.getPage(9)
    inventory_page.mergePage(new_pdf.getPage(5))
    output.addPage(inventory_page)

    gear_page = existing_pdf.getPage(10)
    gear_page.mergePage(new_pdf.getPage(6))
    output.addPage(gear_page)

    # finally, write "output" to a real file
    outputStream = open("{0}.pdf".format(character_name), "wb")
    output.write(outputStream)
    outputStream.close()


to_pdf("Simone_with_personal.xml")
