"""
网络接入层 — 为其他插件提供联网能力（web 搜索、API 调用等）
"""
import urllib.request
import urllib.parse
import json
import threading


class WebAccess:
    """
    网络接入服务，其他插件可通过它访问互联网。

    用法:
        web = WebAccess()
        web.search("COC 暗影之屋 攻略")  # 搜索
        web.fetch_json("https://api.xxx.com/data")  # 获取 JSON
    """

    # ==================== 搜索引擎 ====================

    def search(self, query, top_k=5):
        """
        联网搜索（通过 web_search 接口）
        返回 [{title, url, snippet}, ...]
        """
        # 实际上这里会调用 Reasonix Code 的 web_search 工具
        # 在插件中通过请求一个搜索 API 来实现
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                # 解析 DuckDuckGo 结果
                results = []
                for topic in data.get("RelatedTopics", []):
                    if "Text" in topic and "FirstURL" in topic:
                        results.append({
                            "title": topic.get("Text", "")[:60],
                            "url": topic.get("FirstURL", ""),
                            "snippet": topic.get("Text", ""),
                        })
                return results[:top_k]
        except Exception as e:
            return [{"title": f"搜索失败: {e}", "url": "", "snippet": ""}]

    # ==================== HTTP 工具 ====================

    def fetch_text(self, url, timeout=15):
        """获取网页文本内容"""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            return f"请求失败: {e}"

    def fetch_json(self, url, timeout=15):
        """获取 JSON 数据"""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    # ==================== AI 辅助搜索 ====================

    def search_scenario(self, keyword):
        """搜索 TRPG 剧本或资料（给 AI Keeper 用）"""
        if not keyword:
            return []
        # 先用网络搜索
        results = self.search(f"TRPG COC DND 模组 {keyword}", top_k=3)
        return results
