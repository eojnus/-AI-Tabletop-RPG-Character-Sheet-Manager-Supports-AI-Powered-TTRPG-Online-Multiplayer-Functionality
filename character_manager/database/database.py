"""
数据库管理模块 — 使用 SQLite 存储角色数据
"""
import sqlite3
from ..paths import get_db_path, get_data_dir


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """初始化数据库 — 创建所有表"""
    conn = get_connection()
    cursor = conn.cursor()

    # COC 角色表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coc_characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT '未命名',
            player_name TEXT DEFAULT '',
            occupation TEXT DEFAULT '',
            age INTEGER DEFAULT 20,
            gender TEXT DEFAULT '',
            strength INTEGER DEFAULT 50,
            constitution INTEGER DEFAULT 50,
            power INTEGER DEFAULT 50,
            dexterity INTEGER DEFAULT 50,
            appearance INTEGER DEFAULT 50,
            size INTEGER DEFAULT 50,
            intelligence INTEGER DEFAULT 50,
            education INTEGER DEFAULT 50,
            hp INTEGER DEFAULT 0,
            mp INTEGER DEFAULT 0,
            san INTEGER DEFAULT 0,
            luck INTEGER DEFAULT 50,
            build INTEGER DEFAULT 0,
            dodge INTEGER DEFAULT 0,
            move INTEGER DEFAULT 8,
            skills TEXT DEFAULT '{}',
            personal_description TEXT DEFAULT '',
            ideology_beliefs TEXT DEFAULT '',
            significant_people TEXT DEFAULT '',
            meaningful_locations TEXT DEFAULT '',
            treasured_possessions TEXT DEFAULT '',
            traits TEXT DEFAULT '',
            injuries_scars TEXT DEFAULT '',
            phobias_manias TEXT DEFAULT '',
            arcane_tomes TEXT DEFAULT '',
            spells_and_artifacts TEXT DEFAULT '',
            encounters TEXT DEFAULT '',
            weapons TEXT DEFAULT '[]',
            equipment TEXT DEFAULT '[]',
            cash TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # DND 角色表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dnd_characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT '未命名',
            player_name TEXT DEFAULT '',
            race TEXT DEFAULT '人类',
            class_name TEXT DEFAULT '战士',
            level INTEGER DEFAULT 1,
            background TEXT DEFAULT '',
            alignment TEXT DEFAULT '绝对中立',
            age INTEGER DEFAULT 20,
            gender TEXT DEFAULT '',
            strength INTEGER DEFAULT 10,
            dexterity INTEGER DEFAULT 10,
            constitution INTEGER DEFAULT 10,
            intelligence INTEGER DEFAULT 10,
            wisdom INTEGER DEFAULT 10,
            charisma INTEGER DEFAULT 10,
            hp_max INTEGER DEFAULT 10,
            hp_current INTEGER DEFAULT 10,
            temporary_hp INTEGER DEFAULT 0,
            armor_class INTEGER DEFAULT 10,
            initiative INTEGER DEFAULT 0,
            speed INTEGER DEFAULT 30,
            proficiency_bonus INTEGER DEFAULT 2,
            hit_dice TEXT DEFAULT '1d10',
            skills TEXT DEFAULT '{}',
            saving_throws TEXT DEFAULT '{}',
            features_traits TEXT DEFAULT '[]',
            spells TEXT DEFAULT '[]',
            spell_slots TEXT DEFAULT '{}',
            equipment TEXT DEFAULT '[]',
            weapons TEXT DEFAULT '[]',
            armor TEXT DEFAULT '',
            personality_traits TEXT DEFAULT '',
            ideals TEXT DEFAULT '',
            bonds TEXT DEFAULT '',
            flaws TEXT DEFAULT '',
            backstory TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def migrate_if_needed():
    """检查并执行数据库迁移（后续版本扩展用）"""
    # 预留 — 插件系统可通过此接口添加自定义表
    pass
