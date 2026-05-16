"""
DND 5e 角色数据模型
包含六项属性、技能、法术、装备、职业特性等
"""
import json
from datetime import datetime
from .base import BaseCharacter


DND_SKILL_NAMES = [
    "运动", "巧手", "隐匿", "奥秘", "历史", "调查",
    "自然", "宗教", "驯兽", "洞察", "医疗", "察觉",
    "生存", "欺瞒", "威吓", "表演", "游说",
]

DND_ABILITY_SHORT = {
    "力量": "str", "敏捷": "dex", "体质": "con",
    "智力": "int", "感知": "wis", "魅力": "cha",
}

# 技能对应的属性
DND_SKILL_ABILITY = {
    "运动": "str", "巧手": "dex", "隐匿": "dex",
    "奥秘": "int", "历史": "int", "调查": "int",
    "自然": "int", "宗教": "int", "驯兽": "wis",
    "洞察": "wis", "医疗": "wis", "察觉": "wis",
    "生存": "wis", "欺瞒": "cha", "威吓": "cha",
    "表演": "cha", "游说": "cha",
}


class DNDCharacter(BaseCharacter):
    """DND 5e 版角色卡"""

    def __init__(self):
        super().__init__()
        # === 基础信息 ===
        self.race = "人类"
        self.class_name = "战士"
        self.level = 1
        self.background = ""
        self.alignment = "绝对中立"

        # === 六项属性（标准值10）===
        self.strength = 10      # STR
        self.dexterity = 10     # DEX
        self.constitution = 10  # CON
        self.intelligence = 10  # INT
        self.wisdom = 10        # WIS
        self.charisma = 10      # CHA

        # === 战斗数据 ===
        self.hp_max = 10
        self.hp_current = 10
        self.temporary_hp = 0
        self.armor_class = 10
        self.initiative = 0
        self.speed = 30
        self.proficiency_bonus = 2
        self.hit_dice = "1d10"

        # === 技能熟练（0=未熟练, 1=熟练, 2=专精）===
        self.skills = {}
        for s in DND_SKILL_NAMES:
            self.skills[s] = 0

        # === 豁免熟练 ===
        self.saving_throws = {
            "str": False, "dex": False, "con": False,
            "int": False, "wis": False, "cha": False,
        }

        # === 特性、法术、装备（JSON 存储）===
        self.features_traits = "[]"
        self.spells = "[]"
        self.spell_slots = "{}"
        self.equipment = "[]"
        self.weapons = "[]"
        self.armor = ""

        # === 背景故事 ===
        self.personality_traits = ""
        self.ideals = ""
        self.bonds = ""
        self.flaws = ""
        self.backstory = ""

    def get_ability_modifier(self, score):
        """计算属性调整值"""
        return (score - 10) // 2

    def get_skill_bonus(self, skill_name):
        """计算某技能的总加值"""
        base_mod = self.get_ability_modifier(
            getattr(self, DND_SKILL_ABILITY.get(skill_name, "str"))
        )
        prof = self.skills.get(skill_name, 0)
        return base_mod + prof * self.proficiency_bonus

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "player_name": self.player_name,
            "race": self.race,
            "class_name": self.class_name,
            "level": self.level,
            "background": self.background,
            "alignment": self.alignment,
            "age": self.age,
            "gender": self.gender,

            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,

            "hp_max": self.hp_max,
            "hp_current": self.hp_current,
            "temporary_hp": self.temporary_hp,
            "armor_class": self.armor_class,
            "initiative": self.initiative,
            "speed": self.speed,
            "proficiency_bonus": self.proficiency_bonus,
            "hit_dice": self.hit_dice,

            "skills": json.dumps(self.skills, ensure_ascii=False),
            "saving_throws": json.dumps(self.saving_throws, ensure_ascii=False),

            "features_traits": self.features_traits,
            "spells": self.spells,
            "spell_slots": self.spell_slots,
            "equipment": self.equipment,
            "weapons": self.weapons,
            "armor": self.armor,

            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
            "backstory": self.backstory,

            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        c = cls()
        c.id = data.get("id")
        c.name = data.get("name", "未命名")
        c.player_name = data.get("player_name", "")
        c.race = data.get("race", "人类")
        c.class_name = data.get("class_name", "战士")
        c.level = data.get("level", 1)
        c.background = data.get("background", "")
        c.alignment = data.get("alignment", "绝对中立")
        c.age = data.get("age", 20)
        c.gender = data.get("gender", "")

        c.strength = data.get("strength", 10)
        c.dexterity = data.get("dexterity", 10)
        c.constitution = data.get("constitution", 10)
        c.intelligence = data.get("intelligence", 10)
        c.wisdom = data.get("wisdom", 10)
        c.charisma = data.get("charisma", 10)

        c.hp_max = data.get("hp_max", 10)
        c.hp_current = data.get("hp_current", 10)
        c.temporary_hp = data.get("temporary_hp", 0)
        c.armor_class = data.get("armor_class", 10)
        c.initiative = data.get("initiative", 0)
        c.speed = data.get("speed", 30)
        c.proficiency_bonus = data.get("proficiency_bonus", 2)
        c.hit_dice = data.get("hit_dice", "1d10")

        skills_str = data.get("skills", "{}")
        if isinstance(skills_str, str):
            c.skills = json.loads(skills_str) if skills_str else {}
        else:
            c.skills = skills_str

        st_str = data.get("saving_throws", "{}")
        if isinstance(st_str, str):
            c.saving_throws = json.loads(st_str) if st_str else {}
        else:
            c.saving_throws = st_str

        c.features_traits = data.get("features_traits", "[]")
        c.spells = data.get("spells", "[]")
        c.spell_slots = data.get("spell_slots", "{}")
        c.equipment = data.get("equipment", "[]")
        c.weapons = data.get("weapons", "[]")
        c.armor = data.get("armor", "")

        c.personality_traits = data.get("personality_traits", "")
        c.ideals = data.get("ideals", "")
        c.bonds = data.get("bonds", "")
        c.flaws = data.get("flaws", "")
        c.backstory = data.get("backstory", "")

        created = data.get("created_at")
        updated = data.get("updated_at")
        if created:
            c.created_at = datetime.fromisoformat(created) if isinstance(created, str) else created
        if updated:
            c.updated_at = datetime.fromisoformat(updated) if isinstance(updated, str) else updated

        return c

    def get_card_summary(self):
        """九宫格缩略信息"""
        mod_str = f"{self.get_ability_modifier(self.strength):+d}"
        mod_dex = f"{self.get_ability_modifier(self.dexterity):+d}"
        mod_con = f"{self.get_ability_modifier(self.constitution):+d}"
        return {
            "name": self.name,
            "subtitle": f"Lv.{self.level} {self.race} {self.class_name}",
            "mode": "DND",
            "lines": [
                f"HP: {self.hp_current}/{self.hp_max}  AC: {self.armor_class}",
                f"STR{mod_str} DEX{mod_dex} CON{mod_con}",
                f"熟练: +{self.proficiency_bonus}  速度: {self.speed}ft",
            ]
        }
