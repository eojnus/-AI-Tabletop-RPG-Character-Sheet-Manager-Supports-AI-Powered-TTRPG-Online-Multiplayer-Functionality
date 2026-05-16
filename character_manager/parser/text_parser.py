"""
文本解析器 — 将粘贴的格式化文字自动识别为角色数据
"""
import re
from ..models.coc_character import COCCharacter, COC_SKILL_DEFAULTS
from ..models.dnd_character import DNDCharacter, DND_SKILL_NAMES, DND_SKILL_ABILITY
from .field_patterns import (
    COC_FIELD_PATTERNS, COC_SKILL_PATTERN,
    DND_FIELD_PATTERNS, DND_SKILL_PATTERN,
)


class TextParser:
    """
    文本解析器
    用法:  parser = TextParser()
           result = parser.parse(text, mode="coc")
           # result 是 {"character": COCCharacter, "parsed_fields": [...], "errors": [...]}
    """

    def __init__(self):
        self.parsed_fields = []  # 记录识别到的字段

    def parse(self, text, mode="coc"):
        """
        解析文本为角色对象

        参数:
            text: 粘贴的原始文本
            mode: "coc" 或 "dnd"

        返回:
            {"character": 角色对象, "parsed_fields": [已识别的字段清单], "errors": [警告信息]}
        """
        text = text.strip()
        self.parsed_fields = []
        errors = []

        if mode == "coc":
            character = self._parse_coc(text, errors)
        elif mode == "dnd":
            character = self._parse_dnd(text, errors)
        else:
            raise ValueError(f"未知模式: {mode}")

        return {
            "character": character,
            "parsed_fields": self.parsed_fields,
            "errors": errors,
        }

    # ==================== COC 解析 ====================

    def _preprocess_lines(self, text):
        """预处理：将逗号分隔的多字段行拆分成独立行"""
        lines = text.split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 检查是否包含多个字段（用逗号分隔的键:值对）
            # 如果有多个冒号+逗号模式，按逗号拆分
            parts = re.split(r"[，,](?=\s*[\u4e00-\u9fffA-Za-z]+\s*[:：])", line)
            for part in parts:
                part = part.strip()
                if part:
                    result.append(part)
        return result

    def _parse_coc(self, text, errors):
        char = COCCharacter()
        lines = self._preprocess_lines(text)

        for line in lines:
            line = line.strip()
            if not line:
                continue

            matched = False
            # 尝试匹配所有字段
            for field_name, patterns in COC_FIELD_PATTERNS.items():
                for pattern in patterns:
                    m = re.search(pattern, line)
                    if m:
                        value = m.group(1).strip()
                        self._set_coc_field(char, field_name, value)
                        self.parsed_fields.append(field_name)
                        matched = True
                        break
                if matched:
                    break

            if matched:
                continue

            # 尝试匹配技能（循环提取行内所有技能）
            for skill_m in re.finditer(COC_SKILL_PATTERN, line):
                if not skill_m:
                    continue
                skill_name = skill_m.group(1).strip()
                try:
                    skill_value = int(skill_m.group(2))
                    # 验证技能名是否在默认技能字典中
                    found = False
                    for default_skill in COC_SKILL_DEFAULTS:
                        if skill_name in default_skill or default_skill in skill_name:
                            char.update_skill(default_skill, skill_value)
                            self.parsed_fields.append(f"skill:{default_skill}")
                            found = True
                            break
                    if not found:
                        # 可能是用户自定义技能，也加上
                        char.update_skill(skill_name, skill_value)
                        self.parsed_fields.append(f"skill:{skill_name}")
                except ValueError:
                    pass

        # 验证关键信息
        if char.name == "未命名":
            errors.append("⚠️ 未识别到角色姓名，已使用默认名「未命名」")
        if char.occupation == "":
            errors.append("💼 未识别到职业")

        # 重新计算衍生属性
        char._calc_derived()
        # 重新计算闪避和母语
        char.skills["闪避"] = char.dexterity // 2
        char.skills["母语"] = char.education

        return char

    def _set_coc_field(self, char, field_name, value):
        """给 COC 角色设置字段值"""
        numeric_fields = {
            "strength", "constitution", "power", "dexterity",
            "appearance", "size", "intelligence", "education",
            "hp", "mp", "san", "luck", "age",
        }
        if field_name in numeric_fields:
            try:
                setattr(char, field_name, int(re.sub(r"\D", "", value)))
            except ValueError:
                pass
        else:
            setattr(char, field_name, value)

    # ==================== DND 解析 ====================

    def _parse_dnd(self, text, errors):
        char = DNDCharacter()
        lines = self._preprocess_lines(text)

        for line in lines:
            line = line.strip()
            if not line:
                continue

            matched = False
            for field_name, patterns in DND_FIELD_PATTERNS.items():
                for pattern in patterns:
                    m = re.search(pattern, line)
                    if m:
                        value = m.group(1).strip()
                        self._set_dnd_field(char, field_name, value)
                        self.parsed_fields.append(field_name)
                        matched = True
                        break
                if matched:
                    break

            if matched:
                continue

            # DND 技能匹配（循环提取行内所有技能）
            for skill_m in re.finditer(DND_SKILL_PATTERN, line):
                if not skill_m:
                    continue
                skill_name = skill_m.group(1).strip()
                try:
                    skill_val_text = skill_m.group(2)
                    # 检查是纯数字（表示熟练）还是带符号的调整值
                    if skill_val_text.startswith("+") or skill_val_text.startswith("-"):
                        # 这是调整值，不是熟练等级 — 暂时忽略，识别为普通属性
                        pass
                    else:
                        skill_val = int(skill_val_text)
                        for dnd_skill in DND_SKILL_NAMES:
                            if skill_name in dnd_skill or dnd_skill in skill_name:
                                char.skills[dnd_skill] = skill_val
                                self.parsed_fields.append(f"skill:{dnd_skill}")
                                break
                except ValueError:
                    pass

        if char.name == "未命名":
            errors.append("⚠️ 未识别到角色姓名，已使用默认名「未命名」")
        if char.race == "人类":
            errors.append("👤 未识别到种族，使用默认「人类」")
        if char.class_name == "战士":
            errors.append("⚔️ 未识别到职业，使用默认「战士」")

        return char

    def _set_dnd_field(self, char, field_name, value):
        """给 DND 角色设置字段值"""
        numeric_fields = {
            "strength", "dexterity", "constitution", "intelligence",
            "wisdom", "charisma", "level", "age",
            "hp_max", "armor_class", "speed", "initiative",
            "proficiency_bonus",
        }
        if field_name in numeric_fields:
            try:
                setattr(char, field_name, int(re.sub(r"\D", "", value)))
            except ValueError:
                pass
        else:
            setattr(char, field_name, value)

    # ==================== 自动检测模式 ====================

    @staticmethod
    def detect_mode(text):
        """
        自动检测文本是 COC 还是 DND 格式
        返回: "coc"、"dnd" 或 None（不确定）
        """
        text_upper = text.upper()

        # COC 特征关键词
        coc_signals = ["SAN", "理智", "克苏鲁", "侦查", "图书馆使用",
                       "POW", "信用评级", "闪避", "斗殴"]
        coc_score = sum(1 for s in coc_signals if s in text_upper or s in text)

        # DND 特征关键词
        dnd_signals = ["AC", "护甲等级", "先攻", "熟练加值", "法术位",
                       "种族", "阵营", "生命骰", "豁免"]
        dnd_score = sum(1 for s in dnd_signals if s in text_upper or s in text)

        if coc_score > dnd_score:
            return "coc"
        elif dnd_score > coc_score:
            return "dnd"
        return None  # 不确定，让用户选择
