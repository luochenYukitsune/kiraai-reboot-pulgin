"""
上下文重置插件

支持两种方式清除当前会话的上下文：
1. 自然语言调用：LLM 理解用户意图后调用 clear_context 工具
2. 指令调用：用户发送 /reboot 指令直接触发

功能：调用 SessionManager 的 delete_session 方法清除会话上下文
"""

from core.plugin import BasePlugin, logger, on, Priority, register_tool
from core.chat.message_utils import KiraMessageEvent, KiraMessageBatchEvent
from core.chat.message_elements import Text


class RebootPlugin(BasePlugin):
    """上下文重置插件"""

    def __init__(self, ctx, cfg: dict):
        super().__init__(ctx, cfg)
        self.verbose_log: bool = bool(cfg.get("verbose_log", False))
        self.command_prefix: str = cfg.get("command_prefix", "/reboot")

    async def initialize(self):
        logger.info(f"[Reboot] 初始化完成 | 指令前缀:{self.command_prefix} | 详细日志:{self.verbose_log}")
    
    async def terminate(self):
        logger.info("[Reboot] 已卸载")

    def _log(self, msg: str):
        if self.verbose_log:
            logger.info(f"[Reboot] {msg}")

    def _get_sid(self, event) -> str:
        """获取会话 ID"""
        if hasattr(event, "sid"):
            return event.sid
        if hasattr(event, "session") and hasattr(event.session, "sid"):
            return event.session.sid
        return "default"

    async def _clear_session_context(self, sid: str) -> str:
        """清除会话上下文的核心方法"""
        try:
            self._log(f"正在清除会话上下文: {sid}")
            
            if self.ctx.session_mgr is None:
                return "错误：会话管理器不可用"
            
            self.ctx.session_mgr.delete_session(sid)
            
            self._log(f"会话上下文已清除: {sid}")
            return f"已清除当前会话的上下文记忆"
            
        except Exception as e:
            logger.error(f"[Reboot] 清除上下文失败: {e}")
            return f"清除上下文失败: {e}"

    @on.im_message(priority=Priority.HIGH)
    async def handle_command(self, event: KiraMessageEvent):
        """处理 /reboot 指令"""
        try:
            text = ""
            for elem in event.message.chain:
                if isinstance(elem, Text):
                    text += elem.text
            
            text = text.strip().lower()
            
            if text != self.command_prefix.lower():
                return
            
            self._log(f"收到指令: {text}")
            
            sid = self._get_sid(event)
            result = await self._clear_session_context(sid)
            
            event.message.chain = [Text(result)]
            event.message.is_mentioned = True
            event.discard(force=True)
            event.stop()
            
        except Exception as e:
            logger.error(f"[Reboot] 处理指令失败: {e}")

    @register_tool(
        name="clear_context",
        description="清除当前会话的上下文记忆。当用户想要重新开始对话、清除记忆、重置上下文、忘记之前的内容时调用此工具。",
        params={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    async def clear_context(self, event: KiraMessageBatchEvent, **kwargs) -> str:
        """LLM 工具：清除当前会话上下文"""
        try:
            sid = self._get_sid(event)
            self._log(f"工具调用清除上下文: {sid}")
            
            result = await self._clear_session_context(sid)
            return result
            
        except Exception as e:
            logger.error(f"[Reboot] 工具调用失败: {e}")
            return f"清除上下文失败: {e}"
