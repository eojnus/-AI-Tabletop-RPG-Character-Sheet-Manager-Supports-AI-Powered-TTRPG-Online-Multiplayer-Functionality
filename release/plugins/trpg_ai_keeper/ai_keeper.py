"""
AI Keeper 核心 — DeepSeek API 调用 + 游戏会话管理 + 系统提示词
"""
import json
import urllib.request
import urllib.error
import re

# ==================== API 配置 ====================

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-v4-flash"  # 当前使用模型

# ==================== 系统提示词模板 ====================

SYSTEM_PROMPT_COC = """你是一位精通 **克苏鲁的呼唤 7th** 的守秘人(Keeper)。
你需要遵守以下规则来主持这场游戏：

## 🎭 你的角色
- 你是 Keeper，负责描述场景、扮演 NPC、推动剧情
- 除了玩家扮演的角色外，队伍中的其他角色都由你来扮演和操控
- 保持神秘和恐怖的氛围，这是克苏鲁的核心

## 🎲 掷骰规则
- 当玩家需要进行技能检定时，请明确说出「请掷出 [技能名] 检定」
- 检定格式: 请掷出「侦查」检定，难度: 常规(60)
- 难度等级: 常规(60)、困难(40)、极难(20)
- 由玩家手动掷骰后，根据结果描述成功或失败

## 📊 角色管理
- 玩家的 HP、SAN、MP、幸运值由你根据规则计算和更新
- 当你判定角色受到伤害或失去理智时，请明确说明损失数值
- 格式示例: 「[角色名] 受到 1D6 点伤害，请扣除 4 点 HP」
- 「[角色名] 失去 1D3/1D6 点理智，当前 SAN 值减少」

## 📋 战斗规则
- 使用回合制战斗
- 描述每次行动的效果
- 射击和格斗需要先进行检定

## 📝 叙述风格
- 用生动的语言描述场景，营造克苏鲁式的恐怖氛围
- 给出足够的信息让玩家做出选择
- 每次回复后给出 2-3 个可行的行动选项
- 重要线索要明显提示但不要直白给出

记住: 你是一个专业的 TRPG 主持人，目标是让玩家获得最好的跑团体验！"""

SYSTEM_PROMPT_DND = """你是一位精通 **龙与地下城 5th** 的地下城主(Dungeon Master)。
你需要遵守以下规则来主持这场游戏：

## 🎭 你的角色
- 你是 DM，负责描述场景、扮演 NPC、推动剧情
- 除了玩家扮演的角色外，队伍中的其他角色都由你来扮演和操控
- 创造史诗般的冒险体验

## 🎲 掷骰规则
- 当玩家需要进行检定时，请明确说出「请掷出 [技能/豁免] 检定」
- 格式: 请掷出「察觉」检定，DC: 15
- 由玩家手动掷骰后，根据结果描述成功或失败
- 战斗时: 「请掷出攻击检定」/「请掷出伤害骰」

## 📊 角色管理
- 玩家的 HP、法术位、资源由你根据规则管理
- 战斗中明确说明敌方和自己的HP变化
- 格式: 「[角色名] 受到 8 点穿刺伤害，当前 HP: xx/xx」

## ⚔️ 战斗规则
- 使用回合制，先确定先攻顺序
- 每个回合描述敌人的行动和效果

## 📝 叙述风格
- 用生动的语言描述场景
- 每次回复后给出 2-3 个可行的行动选项
- 平衡战斗、探索、社交三种元素

记住: 你是一个经验丰富的 DM，要让每次冒险都令人难忘！"""


# ==================== 游戏会话 ====================

class GameSession:
    """一场游戏的会话数据"""

    def __init__(self):
        self.mode = None  # "coc" or "dnd"
        self.api_key = ""
        self.all_characters = []   # 所有选中的角色
        self.player_character = None  # 玩家扮演的角色
        self.npc_characters = []   # AI 扮演的队友
        self.scenario = None
        self.conversation_history = []
        self.turn_count = 0

    def init_characters(self, all_chars, player_char):
        """初始化角色信息"""
        self.all_characters = all_chars
        self.player_character = player_char
        self.npc_characters = [c for c in all_chars if c.id != player_char.id]

    def get_character_summary(self):
        """生成所有角色的摘要文本供 AI 参考"""
        lines = []
        lines.append(f"玩家角色: {self.player_character.name}")
        lines.append(f"  职业: {getattr(self.player_character, 'occupation', getattr(self.player_character, 'class_name', ''))}")
        if self.mode == "coc":
            lines.append(f"  HP:{getattr(self.player_character,'hp','?')} SAN:{getattr(self.player_character,'san','?')} MP:{getattr(self.player_character,'mp','?')}")
        else:
            lines.append(f"  HP:{getattr(self.player_character,'hp_current','?')}/{getattr(self.player_character,'hp_max','?')} AC:{getattr(self.player_character,'armor_class','?')}")

        if self.npc_characters:
            lines.append(f"\n其他队伍角色 (由你扮演):")
            for c in self.npc_characters:
                lines.append(f"  - {c.name} ({getattr(c,'occupation',getattr(c,'class_name',''))})")

        return "\n".join(lines)

    def get_scenario_prompt(self):
        """获取剧情摘要"""
        if self.scenario:
            return f"\n当前剧本: {self.scenario.get('title', '')}\n{self.scenario.get('intro', '')}\n"
        return "\n剧本由你即兴创作。"


# ==================== AI API 调用 ====================

def call_deepseek(api_key, messages, model=None, timeout=30):
    """调用 DeepSeek API"""
    actual_model = model or MODEL
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": actual_model,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 2048,
    }
    try:
        data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            DEEPSEEK_API_URL,
            data=data_bytes,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            usage = data.get("usage", {})
            return {
                "ok": True,
                "content": data["choices"][0]["message"]["content"],
                "model": data.get("model", actual_model),
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"ok": False, "content": f"⚠️ API 请求失败 (HTTP {e.code})", "model": "", "usage": {}}
    except urllib.error.URLError as e:
        return {"ok": False, "content": f"⚠️ API 请求失败: {str(e.reason)}", "model": "", "usage": {}}
    except (KeyError, json.JSONDecodeError) as e:
        return {"ok": False, "content": "⚠️ API 返回格式异常，请重试。", "model": "", "usage": {}}
    except Exception as e:
        return {"ok": False, "content": f"⚠️ 请求异常: {str(e)}", "model": "", "usage": {}}


def build_messages(session, player_input=""):
    """构建发送给 AI 的消息列表"""
    messages = []

    # 系统提示词
    if session.mode == "coc":
        messages.append({"role": "system", "content": SYSTEM_PROMPT_COC})
    else:
        messages.append({"role": "system", "content": SYSTEM_PROMPT_DND})

    # 游戏背景信息
    context = f"""
## 当前游戏信息
{session.get_character_summary()}
{session.get_scenario_prompt()}
"""
    messages.append({"role": "system", "content": context})

    # 对话历史（保留最近20轮）
    for msg in session.conversation_history[-40:]:
        messages.append(msg)

    # 当前输入
    if player_input:
        # 检查是否包含骰子结果
        messages.append({"role": "user", "content": player_input})

    return messages


def parse_dice_request(ai_response):
    """解析 AI 回复中是否包含掷骰请求"""
    patterns = [
        r"请掷[出]?[「『\"]([^」』\"]+)[」』\"]?\s*(?:检定|判定|骰)?",
        r"掷(?:出)?\s*([\u4e00-\u9fff]+)\s*(?:检定|判定)?",
        r"做一个?\s*([\u4e00-\u9fff]+)\s*(?:检定|判定)?",
        r"请?进行\s*([\u4e00-\u9fff]+)\s*(?:检定|判定)?",
    ]
    for pattern in patterns:
        m = re.search(pattern, ai_response)
        if m:
            return m.group(1).strip()
    return None


def update_character_from_ai(session, ai_response):
    """从 AI 回复中解析HP/SAN变化并更新角色卡"""
    char = session.player_character
    if not char:
        return []

    updates = []
    # HP 扣减
    hp_patterns = [
        r"(?:扣除|减少|受到|失去)\s*(\d+)\s*点?\s*(?:HP|生命|伤害)",
        r"HP\s*(?:减少|扣除|损失).*?(\d+)",
        r"当前\s*HP.*?(\d+)/(\d+)",
    ]
    for p in hp_patterns:
        m = re.search(p, ai_response)
        if m:
            try:
                dmg = int(m.group(1))
                if hasattr(char, 'hp') and char.hp:  # COC
                    char.hp = max(0, char.hp - dmg)
                    updates.append(f"HP {char.hp + dmg} → {char.hp}")
                elif hasattr(char, 'hp_current'):  # DND
                    char.hp_current = max(0, char.hp_current - dmg)
                    updates.append(f"HP {char.hp_current + dmg} → {char.hp_current}")
            except ValueError:
                pass
            break

    # SAN 扣减 (COC)
    san_patterns = [
        r"(?:扣除|减少|失去)\s*(\d+)\s*点?\s*(?:SAN|理智|san)",
        r"SAN\s*(?:减少|扣除).*?(\d+)",
    ]
    for p in san_patterns:
        m = re.search(p, ai_response)
        if m:
            try:
                loss = int(m.group(1))
                if hasattr(char, 'san'):
                    char.san = max(0, char.san - loss)
                    updates.append(f"SAN {char.san + loss} → {char.san}")
            except ValueError:
                pass
            break

    return updates
