"""
上下文重置插件

支持两种方式清除当前会话的上下文：
1. 自然语言调用：LLM 理解用户意图后调用 clear_context 工具
2. 指令调用：用户发送 /reboot 指令直接触发

功能：调用 SessionManager 的 delete_session 方法清除会话上下文
支持权限控制：可配置允许执行的用户ID列表
"""

from typing import List

from core.plugin import BasePlugin, logger, on, Priority, register_tool
from core.chat.message_utils import KiraMessageEvent, KiraMessageBatchEvent
from core.chat import MessageChain
from core.chat.message_elements import Text


class RebootPlugin(BasePlugin):
    """上下文重置插件"""

    def __init__(self, ctx, cfg: dict):
        super().__init__(ctx, cfg)
        self.verbose_log: bool = bool(cfg.get("verbose_log", False))
        self.command_prefix: str = cfg.get("command_prefix", "/reboot")
        self.allowed_users: List[str] = cfg.get("allowed_users", [])
        self.enable_permission: bool = bool(cfg.get("enable_permission", False))
        self.success_message: str = cfg.get("success_message", "✅ 已清除当前会话的上下文记忆，我们可以重新开始对话了！")
        self.permission_denied_message: str = cfg.get("permission_denied_message", "❌ 权限不足：您没有清除上下文的权限")
        self.error_message: str = cfg.get("error_message", "❌ 清除上下文失败: {error}")

    async def initialize(self):
        logger.info(f"[Reboot] 初始化完成 | 指令前缀:{self.command_prefix} | 权限控制:{self.enable_permission} | 详细日志:{self.verbose_log}")
    
    async def terminate(self):
        logger.info("[Reboot] 已卸载")

    def _log(self, msg: str):
        if self.verbose_log:
            logger.debug(f"[Reboot] {msg}")

    def _get_sid(self, event) -> str:
        """获取会话 ID"""
        if hasattr(event, "sid"):
            return event.sid
        if hasattr(event, "session") and hasattr(event.session, "sid"):
            return event.session.sid
        return "default"

    def _get_user_id(self, event) -> str:
        """获取用户 ID"""
        try:
            if hasattr(event, "message") and hasattr(event.message, "sender"):
                return str(event.message.sender.user_id)
            elif hasattr(event, "messages") and event.messages and hasattr(event.messages[0], "sender"):
                return str(event.messages[0].sender.user_id)
        except Exception:
            pass
        return "unknown"

    def _get_user_name(self, event) -> str:
        """获取用户昵称"""
        try:
            if hasattr(event, "message") and hasattr(event.message, "sender"):
                return event.message.sender.nickname or "未知"
            elif hasattr(event, "messages") and event.messages and hasattr(event.messages[0], "sender"):
                return event.messages[0].sender.nickname or "未知"
        except Exception:
            pass
        return "未知"

    def _check_permission(self, event) -> bool:
        """检查用户是否有权限执行"""
        if not self.enable_permission:
            return True

        if not self.allowed_users:
            return False

        user_id = self._get_user_id(event)
        return user_id in self.allowed_users

    async def _clear_session_context(self, sid: str) -> str:
        """清除会话上下文的核心方法"""
        try:
            self._log(f"正在清除会话上下文: {sid}")
            
            if getattr(self.ctx, 'session_mgr', None) is None:
                return "❌ 错误：会话管理器不可用"
            
            self.ctx.session_mgr.delete_session(sid)
            
            self._log(f"会话上下文已清除: {sid}")
            return self.success_message
            
        except Exception as e:
            logger.error(f"[Reboot] 清除上下文失败: {e}")
            return self.error_message.format(error=str(e))

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
            
            user_id = self._get_user_id(event)
            user_name = self._get_user_name(event)
            sid = self._get_sid(event)
            
            self._log(f"收到指令: {text} | 用户: {user_name}({user_id}) | 会话: {sid}")
            
            if not self._check_permission(event):
                self._log(f"权限拒绝: 用户 {user_id} 无权执行")
                event.discard(force=True)
                event.stop()
                await self.ctx.message_processor.send_message_chain(
                    session=sid,
                    chain=MessageChain([Text(self.permission_denied_message)])
                )
                return
            
            result = await self._clear_session_context(sid)
            
            self._log(f"清除成功: {user_name}({user_id})")
            event.discard(force=True)
            event.stop()
            await self.ctx.message_processor.send_message_chain(
                session=sid,
                chain=MessageChain([Text(result)])
            )
            
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
            user_id = self._get_user_id(event)
            sid = self._get_sid(event)
            
            self._log(f"工具调用清除上下文: {sid} | 用户: {user_id}")
            
            if not self._check_permission(event):
                self._log(f"权限拒绝: 用户 {user_id} 无权执行")
                return self.permission_denied_message
            
            result = await self._clear_session_context(sid)
            return result
            
        except Exception as e:
            logger.error(f"[Reboot] 工具调用失败: {e}")
            return self.error_message.format(error=str(e))
