"""
骰子工具 — 自动掷骰，用于属性生成、技能检定等
"""
import random


def roll(dice_str):
    """
    掷骰子，支持标准表达式
    例: roll("3d6") → [3,5,2]   roll("1d20") → [15]
         roll("2d6+3") → [4,5] 总和=12
    """
    import re
    m = re.match(r"(\d*)d(\d+)([+-]\d+)?", dice_str.lower().replace(" ", ""))
    if not m:
        return [], 0

    count = int(m.group(1)) if m.group(1) else 1
    sides = int(m.group(2))
    modifier = int(m.group(3)) if m.group(3) else 0

    results = [random.randint(1, sides) for _ in range(count)]
    total = sum(results) + modifier
    return results, total


def roll_3d6_x5():
    """COC 属性生成法: 3d6×5 → 结果范围 15~90"""
    results, total = roll("3d6")
    return results, total * 5


def roll_2d6_plus_6_x5():
    """COC 可选属性生成: (2d6+6)×5 → 结果范围 40~90"""
    results, _ = roll("2d6")
    total = sum(results) + 6
    return results, total * 5


def roll_4d6_drop_lowest():
    """DND 属性生成: 4d6 去最低"""
    results = [random.randint(1, 6) for _ in range(4)]
    results.sort()
    return results, sum(results[1:])  # 去掉最低


def roll_standard_array():
    """DND 标准属性数组"""
    return [15, 14, 13, 12, 10, 8]


def roll_coc_attributes(method="3d6x5"):
    """完整产生 COC 八项属性"""
    attr_names = [
        "力量", "体质", "意志", "敏捷",
        "外貌", "体型", "智力", "教育"
    ]
    results = {}
    details = {}

    for name in attr_names:
        if method == "3d6x5":
            if name in ("体型", "智力", "教育"):
                rolls, val = roll_2d6_plus_6_x5()
            else:
                rolls, val = roll_3d6_x5()
        elif method == "2d6+6x5":
            rolls, val = roll_2d6_plus_6_x5()
        else:
            rolls, val = roll_3d6_x5()

        results[name] = val
        details[name] = (rolls, val)

    return results, details


def roll_dnd_attributes(method="4d6"):
    """完整产生 DND 六项属性"""
    attr_names = ["力量", "敏捷", "体质", "智力", "感知", "魅力"]
    results = {}
    details = {}

    if method == "standard_array":
        arr = roll_standard_array()
        for i, name in enumerate(attr_names):
            results[name] = arr[i]
            details[name] = ([], arr[i])
    elif method == "point_buy":
        # 购点法：初始所有属性为8，用27点购买，每点花费见下表
        # 初始返回 8, 8, 8, 8, 8, 8
        for name in attr_names:
            results[name] = 8
            details[name] = ([], 8)
    else:
        for name in attr_names:
            rolls, val = roll_4d6_drop_lowest()
            results[name] = val
            details[name] = (rolls, val)

    return results, details
