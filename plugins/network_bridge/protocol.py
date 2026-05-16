"""
网络协议定义 — 所有网络消息的格式规范
"""

# ==================== 消息类型枚举 ====================

# 客户端 → 服务器
MSG_JOIN = "join"             # 加入房间: {name, nick, char_id}
MSG_LEAVE = "leave"           # 离开房间
MSG_CHAT = "chat"             # 聊天消息: {text}
MSG_ROLL = "roll"             # 掷骰: {dice, result, detail}
MSG_QUICK_MSG = "quick_msg"   # 快捷语
MSG_PING = "ping"             # 心跳

# 服务器 → 客户端
MSG_WELCOME = "welcome"       # 加入成功: {player_id, players}
MSG_PLAYER_JOIN = "player_join"   # 新人加入: {player}
MSG_PLAYER_LEAVE = "player_leave" # 有人离开: {player_id}
MSG_PLAYER_LIST = "player_list"   # 玩家列表: {players}
MSG_BROADCAST_CHAT = "broadcast_chat"  # 广播聊天
MSG_BROADCAST_ROLL = "broadcast_roll"  # 广播掷骰
MSG_AI_REPLY = "ai_reply"     # AI 回复广播
MSG_STATUS = "status"         # 状态更新: {hp, san, ...}
MSG_SYNC_CHARS = "sync_chars" # 同步角色列表
MSG_PONG = "pong"             # 心跳回复
MSG_ERROR = "error"           # 错误消息
MSG_KICKED = "kicked"         # 被踢出


def make_msg(msg_type, **kwargs):
    """构造消息"""
    return {"type": msg_type, **kwargs}


def pack(msg):
    """打包为 JSON 字符串"""
    import json
    return json.dumps(msg, ensure_ascii=False)


def unpack(data):
    """解包 JSON"""
    import json
    return json.loads(data)


# ==================== 快捷语 ====================

QUICK_MESSAGES = [
    ("🎲", "到！"),
    ("👀", "观察四周"),
    ("🔍", "进行调查"),
    ("🤔", "让我想想"),
    ("👍", "赞成"),
    ("👎", "反对"),
    ("🎯", "我要掷骰"),
    ("🛡️", "准备战斗"),
    ("🏃", "撤退！"),
    ("💬", "和 NPC 对话"),
    ("📝", "记下这个线索"),
    ("🙏", "请求帮助"),
]
