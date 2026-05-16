"""
WebSocket 服务器 — 房主机内嵌，接受玩家连接
"""
import asyncio
import json
import threading
from .protocol import *

try:
    import websockets
except ImportError:
    websockets = None


class GameServer:
    """游戏服务器（嵌入房主进程）"""

    def __init__(self, host="0.0.0.0", port=9876):
        self.host = host
        self.port = port
        self.players = {}         # websocket -> player_info
        self.player_counter = 0
        self._server = None
        self._loop = None
        self._thread = None
        self._callbacks = {}      # event -> [callbacks]

    # ==================== 事件注册 ====================

    def on(self, event, callback):
        """监听事件: chat, roll, join, leave"""
        self._callbacks.setdefault(event, []).append(callback)

    def _emit(self, event, data):
        for cb in self._callbacks.get(event, []):
            try:
                cb(data)
            except Exception as e:
                print(f"[Server] 回调错误 {event}: {e}")

    # ==================== 服务器生命周期 ====================

    def start(self):
        """启动服务器（在后台线程）"""
        if websockets is None:
            raise ImportError("需要安装 websockets 库: pip install websockets")

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self.port

    def _run(self):
        asyncio.set_event_loop(self._loop)
        self._server = websockets.serve(
            self._handle_client, self.host, self.port,
            max_size=65536,
        )
        self._loop.run_until_complete(self._server)
        self._loop.run_forever()

    def stop(self):
        """停止服务器"""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)

    # ==================== 客户端处理 ====================

    async def _handle_client(self, websocket):
        """处理单个客户端连接"""
        player_id = None
        try:
            async for raw in websocket:
                msg = unpack(raw)
                msg_type = msg.get("type")

                if msg_type == MSG_JOIN:
                    player_id = self._on_join(websocket, msg)

                elif msg_type == MSG_LEAVE:
                    break

                elif msg_type == MSG_PING:
                    await self._send(websocket, make_msg(MSG_PONG))

                elif msg_type == MSG_CHAT:
                    self._emit("chat", {
                        "player_id": player_id,
                        "player": self.players.get(websocket, {}).get("nick", "未知"),
                        "text": msg.get("text", ""),
                    })
                    await self._broadcast(make_msg(MSG_BROADCAST_CHAT,
                        player_id=player_id,
                        player=self.players.get(websocket, {}).get("nick", "未知"),
                        text=msg.get("text", ""),
                    ))

                elif msg_type == MSG_ROLL:
                    self._emit("roll", {
                        "player_id": player_id,
                        "player": self.players.get(websocket, {}).get("nick", "未知"),
                        "dice": msg.get("dice", ""),
                        "result": msg.get("result", 0),
                        "detail": msg.get("detail", ""),
                    })
                    await self._broadcast(make_msg(MSG_BROADCAST_ROLL,
                        player_id=player_id,
                        player=self.players.get(websocket, {}).get("nick", "未知"),
                        dice=msg.get("dice", ""),
                        result=msg.get("result", 0),
                        detail=msg.get("detail", ""),
                    ))

                elif msg_type == MSG_QUICK_MSG:
                    text = msg.get("text", "")
                    self._emit("chat", {
                        "player_id": player_id,
                        "player": self.players.get(websocket, {}).get("nick", "未知"),
                        "text": text,
                    })
                    await self._broadcast(make_msg(MSG_BROADCAST_CHAT,
                        player_id=player_id,
                        player=self.players.get(websocket, {}).get("nick", "未知"),
                        text=text,
                    ))

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if player_id and websocket in self.players:
                info = self.players.pop(websocket)
                self._emit("leave", info)
                await self._broadcast(make_msg(MSG_PLAYER_LEAVE, player_id=player_id))
                await self._broadcast_players()

    def _on_join(self, websocket, msg):
        """处理玩家加入"""
        self.player_counter += 1
        player_id = f"p{self.player_counter}"
        nick = msg.get("nick", f"玩家{self.player_counter}")
        char_id = msg.get("char_id")

        self.players[websocket] = {
            "id": player_id,
            "nick": nick,
            "char_id": char_id,
            "online": True,
        }

        # 发送欢迎消息
        asyncio.run_coroutine_threadsafe(
            self._send(websocket, make_msg(MSG_WELCOME,
                player_id=player_id,
                players=self._player_list(),
            )),
            self._loop,
        )

        # 广播新人加入
        asyncio.run_coroutine_threadsafe(
            self._broadcast(make_msg(MSG_PLAYER_JOIN, player={
                "id": player_id, "nick": nick, "char_id": char_id,
            })),
            self._loop,
        )

        # 广播更新玩家列表
        asyncio.run_coroutine_threadsafe(
            self._broadcast_players(),
            self._loop,
        )

        self._emit("join", {"id": player_id, "nick": nick, "char_id": char_id})
        return player_id

    # ==================== 消息发送 ====================

    async def _send(self, websocket, msg):
        """给单个客户端发消息"""
        try:
            await websocket.send(pack(msg))
        except Exception:
            pass

    async def _broadcast(self, msg):
        """广播给所有客户端"""
        if not self.players:
            return
        data = pack(msg)
        disconnected = []
        for ws in list(self.players.keys()):
            try:
                await ws.send(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.players.pop(ws, None)

    async def _broadcast_players(self):
        """广播玩家列表"""
        await self._broadcast(make_msg(MSG_PLAYER_LIST, players=self._player_list()))

    def _player_list(self):
        """获取玩家列表（不含自己）"""
        return [
            {"id": p["id"], "nick": p["nick"], "char_id": p["char_id"], "online": p["online"]}
            for p in self.players.values()
        ]

    # ==================== AI 回复广播 ====================

    def broadcast_ai_reply(self, content, player_name="Keeper"):
        """AI 回复广播（供 AI Keeper 插件调用）"""
        if not self.players:
            return
        asyncio.run_coroutine_threadsafe(
            self._broadcast(make_msg(MSG_AI_REPLY,
                player=player_name, content=content)),
            self._loop,
        )

    def broadcast_status(self, char_data):
        """广播角色状态更新"""
        if not self.players:
            return
        asyncio.run_coroutine_threadsafe(
            self._broadcast(make_msg(MSG_STATUS, char_data=char_data)),
            self._loop,
        )

    def get_player_count(self):
        return len(self.players)
