"""
WebSocket 客户端 — 玩家连接到房主的服务器
"""
import asyncio
import json
import threading
from .protocol import *

try:
    import websockets
except ImportError:
    websockets = None


class GameClient:
    """游戏客户端（玩家用）"""

    def __init__(self):
        self._ws = None
        self._loop = None
        self._thread = None
        self.connected = False
        self.player_id = None
        self.players = []         # 房间内所有玩家
        self._callbacks = {}

    # ==================== 事件注册 ====================

    def on(self, event, callback):
        self._callbacks.setdefault(event, []).append(callback)

    def _emit(self, event, data):
        for cb in self._callbacks.get(event, []):
            try:
                cb(data)
            except Exception as e:
                print(f"[Client] 回调错误 {event}: {e}")

    # ==================== 连接管理 ====================

    def connect(self, host, port=9876, nick="玩家", char_id=None):
        """连接到房主"""
        if websockets is None:
            raise ImportError("需要安装 websockets 库: pip install websockets")

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run, args=(host, port, nick, char_id), daemon=True
        )
        self._thread.start()
        return True

    def _run(self, host, port, nick, char_id):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect_loop(host, port, nick, char_id))

    async def _connect_loop(self, host, port, nick, char_id):
        uri = f"ws://{host}:{port}"
        try:
            async with websockets.connect(uri, max_size=65536) as ws:
                self._ws = ws
                self.connected = True

                # 发送加入消息
                await ws.send(pack(make_msg(MSG_JOIN, nick=nick, char_id=char_id)))

                # 接收消息
                async for raw in ws:
                    msg = unpack(raw)
                    await self._handle_message(msg)

        except Exception as e:
            self.connected = False
            self._emit("disconnected", {"reason": str(e)})

    async def _handle_message(self, msg):
        """处理服务器消息"""
        msg_type = msg.get("type")

        if msg_type == MSG_WELCOME:
            self.player_id = msg.get("player_id")
            self.players = msg.get("players", [])
            self._emit("connected", {"player_id": self.player_id})

        elif msg_type == MSG_PLAYER_LIST:
            self.players = msg.get("players", [])
            self._emit("player_list", self.players)

        elif msg_type == MSG_PLAYER_JOIN:
            self._emit("player_join", msg.get("player", {}))

        elif msg_type == MSG_PLAYER_LEAVE:
            pid = msg.get("player_id")
            self.players = [p for p in self.players if p["id"] != pid]
            self._emit("player_leave", {"player_id": pid})

        elif msg_type == MSG_BROADCAST_CHAT:
            self._emit("chat", msg)

        elif msg_type == MSG_BROADCAST_ROLL:
            self._emit("roll", msg)

        elif msg_type == MSG_AI_REPLY:
            self._emit("ai_reply", msg)

        elif msg_type == MSG_STATUS:
            self._emit("status_update", msg.get("char_data", {}))

        elif msg_type == MSG_PONG:
            pass

        elif msg_type == MSG_ERROR:
            self._emit("error", msg)

    # ==================== 消息发送 ====================

    def send_chat(self, text):
        """发送聊天消息"""
        self._send_async(make_msg(MSG_CHAT, text=text))

    def send_roll(self, dice, result, detail=""):
        """发送掷骰结果"""
        self._send_async(make_msg(MSG_ROLL, dice=dice, result=result, detail=detail))

    def send_quick_msg(self, text):
        """发送快捷语"""
        self._send_async(make_msg(MSG_QUICK_MSG, text=text))

    def _send_async(self, msg):
        if not self._ws or not self._loop:
            return
        asyncio.run_coroutine_threadsafe(
            self._ws.send(pack(msg)), self._loop
        )

    # ==================== 连接关闭 ====================

    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)

    def get_player_by_id(self, player_id):
        for p in self.players:
            if p["id"] == player_id:
                return p
        return None
