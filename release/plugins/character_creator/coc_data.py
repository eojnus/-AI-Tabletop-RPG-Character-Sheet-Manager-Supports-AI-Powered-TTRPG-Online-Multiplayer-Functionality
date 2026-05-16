"""
COC 7th 核心职业数据 — 含技能列表、信用评级范围、技能点算法
"""
from collections import OrderedDict

# ==================== 职业数据库 ====================

# 每项: 技能字段名（必须与角色模型的 skills key 一致）
OCCUPATIONS = OrderedDict([
    ("会计师", {
        "skills": ["会计", "法律", "图书馆使用", "聆听", "说服", "侦查"],
        "credit_range": (30, 70),
        "skill_points_edu": 4,    # EDU × 4
        "skill_points_other": 0,  # 无其他
        "other_stat": None,
    }),
    ("演员", {
        "skills": ["艺术/工艺", "乔装", "话术", "恐吓", "心理学", "说服"],
        "credit_range": (20, 60),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("探险家", {
        "skills": ["格斗(斗殴)", "射击(步枪/霰弹枪)", "急救", "导航", "生存", "攀爬", " Swimming潜水"],
        "credit_range": (40, 80),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("考古学家", {
        "skills": ["考古学", "历史", "图书馆使用", "其他语言", "科学", "侦查"],
        "credit_range": (10, 40),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("艺术家", {
        "skills": ["艺术/工艺", "历史", "心理学", "侦查", "自然"],
        "credit_range": (10, 40),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("作家", {
        "skills": ["自然", "其他语言", "母语", "心理学", "侦查"],
        "credit_range": (10, 40),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("医生", {
        "skills": ["急救", "医学", "其他语言", "心理学", "科学", "侦查"],
        "credit_range": (30, 70),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("工程师", {
        "skills": ["电器维修", "机械维修", "操作重型机械", "科学", "侦查"],
        "credit_range": (30, 60),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("联邦探员", {
        "skills": ["格斗(斗殴)", "射击(手枪)", "法律", "说服", "心理学", "侦查"],
        "credit_range": (40, 80),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("黑客", {
        "skills": ["计算机使用", "电器维修", "电子学", "其他语言", "妙手"],
        "credit_range": (10, 40),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("记者", {
        "skills": ["历史", "图书馆使用", "母语", "心理学", "说服"],
        "credit_range": (10, 40),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("法官", {
        "skills": ["历史", "法律", "图书馆使用", "心理学", "说服"],
        "credit_range": (50, 90),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("律师", {
        "skills": ["会计", "法律", "图书馆使用", "心理学", "说服"],
        "credit_range": (30, 70),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("图书馆员", {
        "skills": ["会计", "图书馆使用", "其他语言", "母语"],
        "credit_range": (10, 40),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("退役军人", {
        "skills": ["格斗(斗殴)", "射击(手枪)", "射击(步枪/霰弹枪)", "急救", "生存", "潜行"],
        "credit_range": (20, 50),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("传教士", {
        "skills": ["会计", "历史", "恐吓", "其他语言", "说服"],
        "credit_range": (0, 30),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("音乐家", {
        "skills": ["艺术/工艺", "倾听", "心理学", "妙手"],
        "credit_range": (10, 50),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("护士", {
        "skills": ["急救", "医学", "心理学", "科学", "聆听"],
        "credit_range": (20, 50),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("私家侦探", {
        "skills": ["格斗(斗殴)", "射击(手枪)", "法律", "图书馆使用", "心理学", "说服", "侦查"],
        "credit_range": (20, 50),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("教授", {
        "skills": ["图书馆使用", "其他语言", "母语", "心理学", "科学"],
        "credit_range": (30, 70),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("精神分析学家", {
        "skills": ["医学", "心理学", "精神分析", "科学", "说服"],
        "credit_range": (30, 70),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("科学家", {
        "skills": ["其他语言", "母语", "科学", "侦查"],
        "credit_range": (20, 60),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("士兵", {
        "skills": ["格斗(斗殴)", "射击(手枪)", "射击(步枪/霰弹枪)", "急救", "潜行", "生存"],
        "credit_range": (10, 40),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("窃贼", {
        "skills": ["攀爬", "锁匠", "妙手", "潜行", "跳跃", "侦查"],
        "credit_range": (5, 40),
        "skill_points_edu": 0,
        "skill_points_other": 4,
        "other_stat": "dexterity",  # DEX × 4
    }),
    ("部落成员", {
        "skills": ["攀爬", "格斗(斗殴)", "聆听", "自然", "生存", "侦查", "投掷"],
        "credit_range": (0, 15),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
    ("医生(法医)", {
        "skills": ["急救", "医学", "其他语言", "心理学", "科学(法医学)", "侦查"],
        "credit_range": (20, 50),
        "skill_points_edu": 4,
        "skill_points_other": 0,
        "other_stat": None,
    }),
])

# ==================== 技能默认初始值 ====================

SKILL_BASE_VALUES = {
    "会计": 5, "人类学": 1, "估价": 5, "考古学": 1,
    "取悦": 15, "攀爬": 20, "信用评级": 0,
    "克苏鲁神话": 0, "乔装": 5, "闪避": 0,
    "驾驶": 20, "电器维修": 10, "话术": 5,
    "格斗(斗殴)": 25, "射击(手枪)": 20, "射击(步枪/霰弹枪)": 25,
    "急救": 30, "历史": 5, "恐吓": 15, "跳跃": 20,
    "其他语言": 1, "母语": 0,
    "法律": 5, "图书馆使用": 20, "聆听": 20, "锁匠": 1,
    "机械维修": 10, "医学": 1, "自然": 10, "导航": 10,
    "神秘学": 5, "操作重型机械": 1,
    "说服": 10, "驾驶(飞行器)": 1, "精神分析": 1,
    "心理学": 10, "骑术": 5, "科学": 1,
    "妙手": 10, "侦查": 25, "潜行": 20, "生存": 10,
    "游泳": 20, "投掷": 20, "追踪": 10,
    "艺术/工艺": 5, "计算机使用": 5, "电子学": 1,
    "科学(化学)": 1, "科学(生物学)": 1, "科学(天文学)": 1,
    "科学(地质学)": 1, "科学(物理学)": 1, "科学(法医学)": 1,
    "科学(数学)": 1, "摄影": 5, "伪造": 5,
    "读唇": 1, "射击(冲锋枪)": 15, "炮术": 1,
}

# ==================== 工具函数 ====================


def get_occupations():
    """获取所有职业名列表"""
    return list(OCCUPATIONS.keys())


def get_occupation_skills(occupation_name):
    """获取某职业的技能列表"""
    occ = OCCUPATIONS.get(occupation_name)
    if occ:
        return occ["skills"]
    return []


def calc_occupation_skill_points(occupation_name, character):
    """计算职业技能点数"""
    occ = OCCUPATIONS.get(occupation_name)
    if not occ:
        return 0
    edu = getattr(character, "education", 50)
    if occ["skill_points_other"] > 0 and occ["other_stat"]:
        other_val = getattr(character, occ["other_stat"], 50)
        return edu * occ["skill_points_edu"] + other_val * occ["skill_points_other"]
    return edu * occ["skill_points_edu"]


def calc_personal_skill_points(character):
    """计算个人兴趣技能点数 = INT × 2"""
    return getattr(character, "intelligence", 50) * 2
