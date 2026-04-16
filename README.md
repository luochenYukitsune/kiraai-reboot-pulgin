# 上下文重置插件

上下文重置插件，支持通过自然语言或指令清除当前会话的上下文记忆。

## 开发者

**luochenYukitsune**

## 功能特性

- 🔄 **自然语言调用**：LLM 理解用户意图后自动调用
- 🔄 **指令调用**：发送 `/reboot` 指令直接触发
- 🧹 **清除上下文**：调用 SessionManager 的 delete_session 方法
- ⚙️ **自定义指令**：可自定义触发指令前缀
- 📝 **详细日志**：可开关的调试日志输出

## 使用示例

### 指令方式
```
用户: /reboot
机器人: 已清除当前会话的上下文记忆
```

### 自然语言方式
```
用户: 帮我重新开始对话
用户: 清除之前的记忆
用户: 忘记我们刚才说的内容
机器人: [调用 clear_context 工具] 已清除当前会话的上下文记忆
```

## 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| command_prefix | string | /reboot | 触发清除上下文的指令 |
| verbose_log | switch | false | 是否输出详细日志 |

## 安装

将 `reboot_plugin` 文件夹复制到 KiraAI 的 `data/plugins/` 目录下，重启 KiraAI 即可。

## 开源协议

本项目采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 开源协议。

详见 [LICENSE](LICENSE) 文件。
