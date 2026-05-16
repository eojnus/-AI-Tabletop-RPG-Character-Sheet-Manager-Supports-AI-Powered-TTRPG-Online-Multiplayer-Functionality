"""
角色基类 — 所有游戏模式的角色模型都继承自此类
"""
from datetime import datetime
import json


class BaseCharacter:
    """角色基类，定义通用接口"""

    def __init__(self):
        self.id = None
        self.name = "未命名"
        self.player_name = ""
        self.age = 20
        self.gender = ""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        """转为字典（用于数据库存储）"""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data):
        """从字典恢复角色"""
        raise NotImplementedError

    def get_card_summary(self):
        """获取卡片缩略信息（展示在九宫格上）"""
        raise NotImplementedError
