"""
数据仓库模块 — 提供角色数据的增删改查操作
"""
import json
from .database import get_connection
from ..models.coc_character import COCCharacter
from ..models.dnd_character import DNDCharacter


class CharacterRepository:
    """角色数据仓库"""

    def __init__(self):
        self._conn = get_connection()

    def _get_table(self, mode):
        """根据模式返回表名"""
        if mode == "coc":
            return "coc_characters"
        elif mode == "dnd":
            return "dnd_characters"
        raise ValueError(f"未知模式: {mode}")

    def _get_model_class(self, mode):
        if mode == "coc":
            return COCCharacter
        elif mode == "dnd":
            return DNDCharacter
        raise ValueError(f"未知模式: {mode}")

    # ==================== CRUD ====================

    def add(self, mode, character):
        """添加一个新角色"""
        table = self._get_table(mode)
        data = character.to_dict()
        # 移除 id 和 timestamp，让数据库自动生成
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())

        cursor = self._conn.cursor()
        cursor.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
            values,
        )
        self._conn.commit()
        return cursor.lastrowid

    def update(self, mode, character):
        """更新一个已存在的角色"""
        table = self._get_table(mode)
        data = character.to_dict()
        char_id = data.pop("id", None)
        if char_id is None:
            raise ValueError("角色没有 ID，无法更新")

        # 更新时间戳
        from datetime import datetime
        data["updated_at"] = datetime.now().isoformat()

        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [char_id]

        cursor = self._conn.cursor()
        cursor.execute(
            f"UPDATE {table} SET {set_clause} WHERE id = ?",
            values,
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, mode, character_id):
        """删除指定角色"""
        table = self._get_table(mode)
        cursor = self._conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (character_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def get_by_id(self, mode, character_id):
        """根据 ID 获取单个角色"""
        table = self._get_table(mode)
        cls = self._get_model_class(mode)
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (character_id,))
        row = cursor.fetchone()
        if row:
            return cls.from_dict(dict(row))
        return None

    def get_all(self, mode):
        """获取某模式下的所有角色"""
        table = self._get_table(mode)
        cls = self._get_model_class(mode)
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {table} ORDER BY updated_at DESC")
        return [cls.from_dict(dict(row)) for row in cursor.fetchall()]

    def count(self, mode):
        """获取角色总数"""
        table = self._get_table(mode)
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]

    # ==================== 搜索 ====================

    def search(self, mode, keyword="", filters=None, sort_by="updated_at", sort_order="DESC"):
        """
        多维度搜索角色

        参数:
            mode: "coc" 或 "dnd"
            keyword: 搜索关键词（匹配姓名或职业）
            filters: 过滤条件字典
                - gender: 性别
                - age_min / age_max: 年龄范围
                - skill: 技能名（仅COC）
                - occupation: 职业
                - class_name: 职业名（仅DND）
                - race: 种族（仅DND）
            sort_by: 排序字段
            sort_order: "ASC" 或 "DESC"
        """
        table = self._get_table(mode)
        cls = self._get_model_class(mode)
        cursor = self._conn.cursor()

        conditions = []
        params = []

        # 关键词搜索（姓名/职业）
        if keyword:
            conditions.append("(name LIKE ? OR occupation LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        if filters:
            # 性别过滤
            gender = filters.get("gender")
            if gender:
                conditions.append("gender = ?")
                params.append(gender)

            # 年龄范围
            age_min = filters.get("age_min")
            if age_min is not None:
                conditions.append("age >= ?")
                params.append(age_min)
            age_max = filters.get("age_max")
            if age_max is not None:
                conditions.append("age <= ?")
                params.append(age_max)

            # 职业
            occupation = filters.get("occupation")
            if occupation:
                conditions.append("occupation LIKE ?")
                params.append(f"%{occupation}%")

            # DND 特有
            class_name = filters.get("class_name")
            if class_name:
                conditions.append("class_name LIKE ?")
                params.append(f"%{class_name}%")
            race = filters.get("race")
            if race:
                conditions.append("race LIKE ?")
                params.append(f"%{race}%")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # 防止 SQL 注入 — 排序字段白名单
        allowed_sort = {
            "name", "age", "gender", "occupation",
            "strength", "level", "created_at", "updated_at",
            "hp", "hp_max", "armor_class",
        }
        sort_col = sort_by if sort_by in allowed_sort else "updated_at"
        sort_dir = "DESC" if sort_order.upper() == "DESC" else "ASC"

        query = f"SELECT * FROM {table} {where_clause} ORDER BY {sort_col} {sort_dir}"
        cursor.execute(query, params)
        return [cls.from_dict(dict(row)) for row in cursor.fetchall()]

    # ==================== 技能搜索（COC 特有）====================

    def search_by_skill(self, mode, skill_name, min_val=0, max_val=100):
        """
        按技能值搜索角色（COC 技能存储在 JSON 中）
        """
        if mode != "coc":
            return []
        table = self._get_table(mode)
        cls = self._get_model_class(mode)
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        results = []
        for row in cursor.fetchall():
            d = dict(row)
            skills_str = d.get("skills", "{}")
            skills = json.loads(skills_str) if isinstance(skills_str, str) and skills_str else {}
            val = skills.get(skill_name, 0)
            if min_val <= val <= max_val:
                results.append(cls.from_dict(d))
        return results

    def close(self):
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
