"""
DND 5e 核心种族/职业/背景数据
"""
from collections import OrderedDict

# ==================== 种族 ====================

RACES = OrderedDict([
    ("人类", {
        "ability_bonus": {"力量": 1, "敏捷": 1, "体质": 1, "智力": 1, "感知": 1, "魅力": 1},
        "speed": 30,
        "features": ["额外语言: 任意一种", "技能: 无"],
        "size": "中型",
    }),
    ("精灵(高等)", {
        "ability_bonus": {"敏捷": 2, "智力": 1},
        "speed": 30,
        "features": ["黑暗视觉: 60ft", "精灵武器训练", "戏法: 戏法一个"],
        "size": "中型",
    }),
    ("精灵(木)", {
        "ability_bonus": {"敏捷": 2, "感知": 1},
        "speed": 35,
        "features": ["黑暗视觉: 60ft", "精灵武器训练", "隐匿隐藏"],
        "size": "中型",
    }),
    ("矮人(丘陵)", {
        "ability_bonus": {"体质": 2, "感知": 1},
        "speed": 25,
        "features": ["黑暗视觉: 60ft", "石工知识", "矮人抗性: 对毒素优势"],
        "size": "中型",
    }),
    ("矮人(山脉)", {
        "ability_bonus": {"体质": 2, "力量": 2},
        "speed": 25,
        "features": ["黑暗视觉: 60ft", "石工知识", "矮人护甲训练"],
        "size": "中型",
    }),
    ("半身人", {
        "ability_bonus": {"敏捷": 2, "魅力": 1},
        "speed": 25,
        "features": ["幸运: 自然1重掷", "勇敢: 对抗恐惧优势", "潜行熟练"],
        "size": "小型",
    }),
    ("龙裔", {
        "ability_bonus": {"力量": 2, "魅力": 1},
        "speed": 30,
        "features": ["龙息: 选择一种龙类", "伤害抗性: 对应龙类"],
        "size": "中型",
    }),
    ("半精灵", {
        "ability_bonus": {"魅力": 2, "自由": 2},
        "speed": 30,
        "features": ["黑暗视觉: 60ft", "精灵血统: 魅惑免疫", "额外技能: 任意两个"],
        "size": "中型",
    }),
    ("半兽人", {
        "ability_bonus": {"力量": 2, "体质": 1},
        "speed": 30,
        "features": ["黑暗视觉: 60ft", "凶恶攻击: 暴击额外伤害", "不屈: 倒地1HP"],
        "size": "中型",
    }),
    ("侏儒(森林)", {
        "ability_bonus": {"智力": 2, "敏捷": 1},
        "speed": 25,
        "features": ["黑暗视觉: 60ft", "侏儒狡诈: 智力豁免优势", "自然交谈"],
        "size": "小型",
    }),
])

# ==================== 职业 ====================

CLASSES = OrderedDict([
    ("战士", {
        "hit_dice": "1d10",
        "primary_ability": "力量或敏捷",
        "saving_throws": ["力量", "体质"],
        "armor_proficiencies": ["所有护甲", "盾牌"],
        "weapon_proficiencies": ["所有武器"],
        "skill_choices": 2,
        "skill_options": ["运动", "调查", "驯兽", "医疗", "察觉", "生存", "威吓", "历史"],
        "features": {
            1: ["战斗风格", "回气"],
            2: ["动作如潮"],
            3: [" martial archetype  martial  archetype"],
        },
        "equipment_packages": [
            ["链甲", "盾牌", "长剑", "手弩+20弩箭"],
            ["链甲", "巨剑", "手斧×2", "轻弩+20弩箭"],
        ],
    }),
    ("法师", {
        "hit_dice": "1d6",
        "primary_ability": "智力",
        "saving_throws": ["智力", "感知"],
        "armor_proficiencies": [],
        "weapon_proficiencies": ["匕首", "标枪", "硬头锤", "轻弩", "手杖"],
        "skill_choices": 2,
        "skill_options": ["历史", "奥秘", "调查", "宗教", "医疗", "洞察"],
        "spellcaster": True,
        "spellcasting_ability": "智力",
        "features": {
            1: ["法术位", "奥术传承", "法术书"],
        },
        "equipment_packages": [
            ["长棍", "法术书", "匕首", "施法材料包"],
            ["火把×10", "口粮×10", "水袋", "绳索"],
        ],
    }),
    ("游荡者", {
        "hit_dice": "1d8",
        "primary_ability": "敏捷",
        "saving_throws": ["敏捷", "智力"],
        "armor_proficiencies": ["轻甲"],
        "weapon_proficiencies": ["简易武器", "手弩", "长剑", "细剑", "短弓"],
        "skill_choices": 4,
        "skill_options": ["运动", "巧手", "隐匿", "调查", "察觉", "欺瞒", "威吓", "表演", "游说", "妙手"],
        "features": {
            1: ["专长: 巧手", "偷袭1d6", "盗贼黑话"],
        },
        "equipment_packages": [
            ["细剑", "短弓+20箭", "盗贼工具", "轻甲"],
            ["匕首×2", "短剑", "盗贼工具"],
        ],
    }),
    ("牧师", {
        "hit_dice": "1d8",
        "primary_ability": "感知",
        "saving_throws": ["感知", "魅力"],
        "armor_proficiencies": ["轻甲", "中甲", "盾牌"],
        "weapon_proficiencies": ["所有简易武器"],
        "skill_choices": 2,
        "skill_options": ["历史", "洞察", "医疗", "游说", "宗教"],
        "spellcaster": True,
        "spellcasting_ability": "感知",
        "features": {
            1: ["法术位", "神圣领域", "引导神力"],
        },
        "equipment_packages": [
            ["硬头锤", "板条甲", "盾牌", "圣徽"],
            ["钉头锤", "链甲", "圣徽"],
        ],
    }),
    ("游侠", {
        "hit_dice": "1d10",
        "primary_ability": "敏捷+感知",
        "saving_throws": ["力量", "敏捷"],
        "armor_proficiencies": ["轻甲", "中甲", "盾牌"],
        "weapon_proficiencies": ["所有武器"],
        "skill_choices": 3,
        "skill_options": ["运动", "调查", "自然", "察觉", "隐匿", "生存"],
        "features": {
            1: ["宿敌", "自然探索者"],
        },
        "equipment_packages": [
            ["链甲", "长剑", "长弓+20箭"],
            ["鳞甲", "短剑", "短弓+20箭"],
        ],
    }),
    ("圣武士", {
        "hit_dice": "1d10",
        "primary_ability": "力量+魅力",
        "saving_throws": ["感知", "魅力"],
        "armor_proficiencies": ["所有护甲", "盾牌"],
        "weapon_proficiencies": ["所有武器"],
        "skill_choices": 2,
        "skill_options": ["运动", "洞察", "威吓", "医疗", "游说", "宗教"],
        "features": {
            1: ["圣光", "圣疗"],
        },
        "equipment_packages": [
            ["链甲", "盾牌", "长剑", "圣徽"],
            ["巨剑", "链甲", "圣徽"],
        ],
    }),
])

# ==================== 背景 ====================

BACKGROUNDS = OrderedDict([
    ("平民英雄", {
        "skill_proficiencies": ["驯兽", "生存"],
        "feature": "乡亲们的好帮手: 在乡村地区可获得食物和住宿",
        "equipment": ["宠物(狗/猫)", "耐用衣服", "腰包(10gp)"],
    }),
    ("士兵", {
        "skill_proficiencies": ["运动", "威吓"],
        "feature": "军阶: 在军队中拥有一定地位和影响力",
        "equipment": ["军阶徽章", "战利品匕首", "骰子", "军服", "腰包(10gp)"],
    }),
    ("流浪儿", {
        "skill_proficiencies": ["巧手", "隐匿"],
        "feature": "城市暗巷: 在城市中快速移动和隐匿",
        "equipment": ["木棍", "宠物老鼠", "纪念品", "破旧衣服"],
    }),
    ("智者", {
        "skill_proficiencies": ["历史", "宗教"],
        "feature": "研究能力: 可获取或复制学术信息",
        "equipment": ["墨水瓶", "羽毛笔", "羊皮纸×10", "书籍", "普通衣服", "腰包(10gp)"],
    }),
    ("贵族", {
        "skill_proficiencies": ["历史", "游说"],
        "feature": "地位特权: 被上流社会欢迎",
        "equipment": ["精致衣服", "纹章戒指", "证件", "钱包(25gp)"],
    }),
    ("艺人", {
        "skill_proficiencies": ["杂技", "表演"],
        "feature": "受欢迎: 每次演出可解决住宿",
        "equipment": ["乐器", "纪念品", "戏服", "腰包(15gp)"],
    }),
    ("商人", {
        "skill_proficiencies": ["洞察", "游说"],
        "feature": "商业嗅觉: 能找到买家/卖家",
        "equipment": ["骡子", "商品", "皮包", "腰包(20gp)"],
    }),
])

# ==================== 工具函数 ====================


def get_races():
    return list(RACES.keys())


def get_classes():
    return list(CLASSES.keys())


def get_backgrounds():
    return list(BACKGROUNDS.keys())


def get_skill_options_for_class(class_name):
    cls = CLASSES.get(class_name)
    return cls["skill_options"] if cls else []


def get_starting_equipment(class_name, package_index=0):
    """返回某职业的起始装备包"""
    cls = CLASSES.get(class_name)
    if cls and cls["equipment_packages"]:
        idx = min(package_index, len(cls["equipment_packages"]) - 1)
        return cls["equipment_packages"][idx]
    return []


def calc_dnd_skill_bonus(ability_score):
    """计算属性调整值"""
    return (ability_score - 10) // 2
