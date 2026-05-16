"""
字段匹配模式定义
定义 COC 和 DND 角色卡中各个字段的中英文匹配规则
"""

# ==================== COC 7th 字段模式 ====================

COC_FIELD_PATTERNS = {
    # 基础信息（[^,\n]+ 防止逗号分隔时吃掉后面的字段）
    "name": [r"姓名\s*[:：]\s*([^,\n]+)", r"角色名\s*[:：]\s*([^,\n]+)", r"角色名称\s*[:：]\s*([^,\n]*)"],
    "player_name": [r"玩家\s*[:：]\s*([^,\n]+)", r"玩家名\s*[:：]\s*([^,\n]+)", r"PLAYER\s*[:：]\s*([^,\n]*)"],
    "occupation": [r"职业\s*[:：]\s*([^,\n]+)", r"OCCUPATION\s*[:：]\s*([^,\n]*)"],
    "age": [r"年龄\s*[:：]\s*(\d+)", r"AGE\s*[:：]\s*(\d+)"],
    "gender": [r"性别\s*[:：]\s*([^,\n]+)", r"SEX\s*[:：]\s*([^,\n]*)"],

    # 七项属性（支持多种写法）
    "strength": [
        r"力量\s*[:：]?\s*(\d+)", r"STR\s*[:：]?\s*(\d+)",
        r"力量\s+(\d+)",
    ],
    "constitution": [
        r"体质\s*[:：]?\s*(\d+)", r"CON\s*[:：]?\s*(\d+)",
    ],
    "power": [
        r"意志\s*[:：]?\s*(\d+)", r"POW\s*[:：]?\s*(\d+)",
    ],
    "dexterity": [
        r"敏捷\s*[:：]?\s*(\d+)", r"DEX\s*[:：]?\s*(\d+)",
    ],
    "appearance": [
        r"外貌\s*[:：]?\s*(\d+)", r"APP\s*[:：]?\s*(\d+)",
    ],
    "size": [
        r"体型\s*[:：]?\s*(\d+)", r"SIZ\s*[:：]?\s*(\d+)",
    ],
    "intelligence": [
        r"智力\s*[:：]?\s*(\d+)", r"INT\s*[:：]?\s*(\d+)",
    ],
    "education": [
        r"教育\s*[:：]?\s*(\d+)", r"EDU\s*[:：]?\s*(\d+)",
    ],

    # 衍生属性
    "hp": [r"生命[值点]?\s*[:：]?\s*(\d+)", r"HP\s*[:：]?\s*(\d+)"],
    "mp": [r"魔法[值点]?\s*[:：]?\s*(\d+)", r"MP\s*[:：]?\s*(\d+)"],
    "san": [r"理智[值点]?\s*[:：]?\s*(\d+)", r"SAN\s*[:：]?\s*(\d+)"],
    "luck": [r"幸运\s*[:：]?\s*(\d+)", r"LUCK\s*[:：]?\s*(\d+)"],

    # 背景
    "personal_description": [r"个人描述\s*[:：]\s*(.+)"],
    "ideology_beliefs": [r"信念[与和]?意识形态\s*[:：]\s*(.+)", r"意识形态[与和]?信念\s*[:：]\s*(.*)"],
    "significant_people": [r"重要之人\s*[:：]\s*(.+)", r"重要人物\s*[:：]\s*(.*)"],
    "meaningful_locations": [r"意义非凡之地\s*[:：]\s*(.+)", r"重要地点\s*[:：]\s*(.*)"],
    "treasured_possessions": [r"宝贵之物\s*[:：]\s*(.+)", r"贵重物品\s*[:：]\s*(.*)"],
    "traits": [r"特质\s*[:：]\s*(.+)"],
    "injuries_scars": [r"伤疤[与和]?伤痕\s*[:：]\s*(.+)", r"伤势\s*[:：]\s*(.*)"],
    "phobias_manias": [r"恐惧[与和]?狂热\s*[:：]\s*(.+)", r"恐惧症\s*[:：]\s*(.*)"],
}

# COC 技能识别模式（技能名 + 数值）
COC_SKILL_PATTERN = r"([\u4e00-\u9fff()（）/\\]+)\s*[:：]?\s*(\d+)"

# ==================== DND 5e 字段模式 ====================

DND_FIELD_PATTERNS = {
    # 基础信息（[^,\n]+ 防止逗号分隔时吃掉后面的字段）
    "name": [r"姓名\s*[:：]\s*([^,\n]+)", r"角色名\s*[:：]\s*([^,\n]+)", r"角色名称\s*[:：]\s*([^,\n]*)"],
    "player_name": [r"玩家\s*[:：]\s*([^,\n]+)", r"PLAYER\s*[:：]\s*([^,\n]*)"],
    "race": [r"种族\s*[:：]\s*([^,\n]+)", r"RACE\s*[:：]\s*([^,\n]*)"],
    "class_name": [r"职业\s*[:：]\s*([^,\n]+)", r"CLASS\s*[:：]\s*([^,\n]*)"],
    "level": [r"等级\s*[:：]?\s*(\d+)", r"LEVEL\s*[:：]?\s*(\d+)"],
    "background": [r"背景\s*[:：]\s*([^,\n]+)", r"BACKGROUND\s*[:：]\s*([^,\n]*)"],
    "alignment": [r"阵营\s*[:：]\s*([^,\n]+)", r"ALIGNMENT\s*[:：]\s*([^,\n]*)"],
    "age": [r"年龄\s*[:：]?\s*(\d+)", r"AGE\s*[:：]?\s*(\d+)"],
    "gender": [r"性别\s*[:：]\s*([^,\n]+)", r"SEX\s*[:：]\s*([^,\n]*)"],

    # 六项属性
    "strength": [r"力量\s*[:：]?\s*(\d+)", r"STR\s*[:：]?\s*(\d+)"],
    "dexterity": [r"敏捷\s*[:：]?\s*(\d+)", r"DEX\s*[:：]?\s*(\d+)"],
    "constitution": [r"体质\s*[:：]?\s*(\d+)", r"CON\s*[:：]?\s*(\d+)"],
    "intelligence": [r"智力\s*[:：]?\s*(\d+)", r"INT\s*[:：]?\s*(\d+)"],
    "wisdom": [r"感知\s*[:：]?\s*(\d+)", r"WIS\s*[:：]?\s*(\d+)"],
    "charisma": [r"魅力\s*[:：]?\s*(\d+)", r"CHA\s*[:：]?\s*(\d+)"],

    # 战斗数据
    "hp_max": [r"最大生命[值点]?\s*[:：]?\s*(\d+)", r"HP\s*[:：]?\s*(\d+)"],
    "armor_class": [r"护甲等级\s*[:：]?\s*(\d+)", r"AC\s*[:：]?\s*(\d+)", r"防御\s*[:：]?\s*(\d+)"],
    "speed": [r"速度\s*[:：]?\s*(\d+)", r"SPEED\s*[:：]?\s*(\d+)"],
    "initiative": [r"先攻\s*[:：]?\s*([+-]?\d+)", r"INITIATIVE\s*[:：]?\s*([+-]?\d+)"],
    "proficiency_bonus": [r"熟练加值\s*[:：]?[+]?(\d+)", r"熟练[加值]?\s*[:：]?[+]?(\d+)"],

    # 背景故事
    "personality_traits": [r"个性[特点]?\s*[:：]\s*(.+)", r"人格特质\s*[:：]\s*(.*)"],
    "ideals": [r"理念\s*[:：]\s*(.+)", r"IDEALS\s*[:：]\s*(.*)"],
    "bonds": [r"羁绊\s*[:：]\s*(.+)", r"BONDS\s*[:：]\s*(.*)"],
    "flaws": [r"缺陷\s*[:：]\s*(.+)", r"FLAWS\s*[:：]\s*(.*)"],
    "backstory": [r"背景故事\s*[:：]\s*(.+)", r"背景\s*[:：]\s*(.*)"],
}

# DND 技能识别
DND_SKILL_PATTERN = r"([\u4e00-\u9fff]+)\s*[:：]?\s*([+-]?\d+)"
