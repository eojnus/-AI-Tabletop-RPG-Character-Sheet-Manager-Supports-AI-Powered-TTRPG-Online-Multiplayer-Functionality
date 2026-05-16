"""
COC 7th 角色数据模型
包含七项属性、技能、衍生属性、装备、背景故事
"""
import json
from datetime import datetime
from .base import BaseCharacter


# ======== COC 7th 技能初始值（未分配时的默认值）========
COC_SKILL_DEFAULTS = {
    "会计": 5, "人类学": 1, "估价": 5, "考古学": 1,
    "取悦": 15, "攀爬": 20, "信用评级": 0,
    "克苏鲁神话": 0, " disguise 乔装": 5, "闪避": 0,  # 闪避 = DEX/2，动态计算
    "驾驶": 20, "电器维修": 10, "话术": 5,
    "格斗(斗殴)": 25, "射击(手枪)": 20, "射击(步枪/霰弹枪)": 25,
    "急救": 30, "历史": 5, "恐吓": 15, "跳跃": 20,
    "其他语言": 1, "母语": 0,  # 母语 = EDU，动态计算
    "法律": 5, "图书馆使用": 20, "聆听": 20, "锁匠": 1,
    "机械维修": 10, "医学": 1, "自然": 10, "导航": 10,
    " occult 神秘学": 5, "操作重型机械": 1,
    "说服": 10, "驾驶(飞行器)": 1, "精神分析": 1,
    "心理学": 10, "骑术": 5, "科学": 1,
    "妙手": 10, "侦查": 25, "潜行": 20, "生存": 10,
    "游泳": 20, "投掷": 20, "追踪": 10,
    # 扩展技能
    "艺术/工艺": 5, "摄影": 5, "计算机使用": 5,
    "电子学": 1, "伪造": 5, "读唇": 1,
    "枪械(冲锋枪)": 15, "炮术": 1,
}


class COCCharacter(BaseCharacter):
    """COC 7th 版角色卡"""

    def __init__(self):
        super().__init__()
        # === 七项属性（默认值50）===
        self.strength = 50       # STR 力量
        self.constitution = 50   # CON 体质
        self.power = 50          # POW 意志
        self.dexterity = 50      # DEX 敏捷
        self.appearance = 50     # APP 外貌
        self.size = 50           # SIZ 体型
        self.intelligence = 50   # INT 智力
        self.education = 50      # EDU 教育

        # === 衍生属性 ===
        self._calc_derived()

        # === 技能（字典 key=技能名, value=技能值）===
        self.skills = {}
        self._init_skills()

        # === 背景 ===
        self.personal_description = ""
        self.ideology_beliefs = ""
        self.significant_people = ""
        self.meaningful_locations = ""
        self.treasured_possessions = ""
        self.traits = ""
        self.injuries_scars = ""
        self.phobias_manias = ""
        self.arcane_tomes = ""
        self.spells_and_artifacts = ""
        self.encounters_with_strange_entities = ""

        # === 装备（存 JSON 字符串）===
        self.weapons = "[]"
        self.equipment = "[]"
        self.cash = ""
        self.occupation = ""

    def _init_skills(self):
        """用各技能的默认初始值填充 skills 字典"""
        for skill_name, default_val in COC_SKILL_DEFAULTS.items():
            self.skills[skill_name] = default_val
        # 特殊处理：闪避 = DEX / 2
        self.skills["闪避"] = self.dexterity // 2
        # 母语 = EDU
        self.skills["母语"] = self.education

    def _calc_derived(self):
        """根据属性计算衍生值"""
        self.hp = (self.constitution + self.size) // 10
        self.mp = self.power // 5
        self.san = self.power
        self.luck = 50
        self.build = 0
        self.dodge = self.dexterity // 2
        # 计算 Move
        if self.strength < self.size and self.dexterity < self.size:
            self.move = 7
        elif self.strength > self.size and self.dexterity > self.size:
            self.move = 9
        else:
            self.move = 8
        # 计算 Build
        str_siz = self.strength + self.size
        if str_siz >= 65:
            self.build = 1
        elif str_siz >= 85:
            self.build = 2
        elif str_siz >= 115:
            self.build = 3
        else:
            self.build = 0

    def update_skill(self, name, value):
        """更新单个技能的值"""
        self.skills[name] = value

    def get_skill(self, name):
        """获取技能值，找不到返回0"""
        return self.skills.get(name, 0)

    def to_dict(self):
        """转为字典，用于数据库存储"""
        return {
            "id": self.id,
            "name": self.name,
            "player_name": self.player_name,
            "occupation": self.occupation,
            "age": self.age,
            "gender": self.gender,
            "strength": self.strength,
            "constitution": self.constitution,
            "power": self.power,
            "dexterity": self.dexterity,
            "appearance": self.appearance,
            "size": self.size,
            "intelligence": self.intelligence,
            "education": self.education,
            "hp": self.hp,
            "mp": self.mp,
            "san": self.san,
            "luck": self.luck,
            "build": self.build,
            "dodge": self.dodge,
            "move": self.move,
            "skills": json.dumps(self.skills, ensure_ascii=False),
            "personal_description": self.personal_description,
            "ideology_beliefs": self.ideology_beliefs,
            "significant_people": self.significant_people,
            "meaningful_locations": self.meaningful_locations,
            "treasured_possessions": self.treasured_possessions,
            "traits": self.traits,
            "injuries_scars": self.injuries_scars,
            "phobias_manias": self.phobias_manias,
            "arcane_tomes": self.arcane_tomes,
            "spells_and_artifacts": self.spells_and_artifacts,
            "encounters": self.encounters_with_strange_entities,
            "weapons": self.weapons,
            "equipment": self.equipment,
            "cash": self.cash,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        """从数据库字典恢复角色对象"""
        c = cls()
        c.id = data.get("id")
        c.name = data.get("name", "未命名")
        c.player_name = data.get("player_name", "")
        c.occupation = data.get("occupation", "")
        c.age = data.get("age", 20)
        c.gender = data.get("gender", "")
        c.strength = data.get("strength", 50)
        c.constitution = data.get("constitution", 50)
        c.power = data.get("power", 50)
        c.dexterity = data.get("dexterity", 50)
        c.appearance = data.get("appearance", 50)
        c.size = data.get("size", 50)
        c.intelligence = data.get("intelligence", 50)
        c.education = data.get("education", 50)
        c._calc_derived()

        # 技能
        skills_str = data.get("skills", "{}")
        if isinstance(skills_str, str):
            c.skills = json.loads(skills_str) if skills_str else {}
        else:
            c.skills = skills_str

        c.hp = data.get("hp", c.hp)
        c.mp = data.get("mp", c.mp)
        c.san = data.get("san", c.san)
        c.luck = data.get("luck", 50)
        c.build = data.get("build", c.build)
        c.dodge = data.get("dodge", c.dodge)
        c.move = data.get("move", c.move)

        c.personal_description = data.get("personal_description", "")
        c.ideology_beliefs = data.get("ideology_beliefs", "")
        c.significant_people = data.get("significant_people", "")
        c.meaningful_locations = data.get("meaningful_locations", "")
        c.treasured_possessions = data.get("treasured_possessions", "")
        c.traits = data.get("traits", "")
        c.injuries_scars = data.get("injuries_scars", "")
        c.phobias_manias = data.get("phobias_manias", "")
        c.arcane_tomes = data.get("arcane_tomes", "")
        c.spells_and_artifacts = data.get("spells_and_artifacts", "")
        c.encounters_with_strange_entities = data.get("encounters", "")
        c.weapons = data.get("weapons", "[]")
        c.equipment = data.get("equipment", "[]")
        c.cash = data.get("cash", "")

        created = data.get("created_at")
        updated = data.get("updated_at")
        if created:
            c.created_at = datetime.fromisoformat(created) if isinstance(created, str) else created
        if updated:
            c.updated_at = datetime.fromisoformat(updated) if isinstance(updated, str) else updated

        return c

    def get_card_summary(self):
        """获取九宫格上显示的缩略信息"""
        return {
            "name": self.name,
            "subtitle": self.occupation or "无职业",
            "mode": "COC",
            "lines": [
                f"HP: {self.hp}  SAN: {self.san}  MP: {self.mp}",
                f"STR:{self.strength} CON:{self.constitution} POW:{self.power}",
                f"DEX:{self.dexterity} APP:{self.appearance} SIZ:{self.size}",
                f"INT:{self.intelligence} EDU:{self.education}",
            ]
        }
