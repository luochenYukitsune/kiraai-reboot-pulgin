# 上下文重置插件

上下文重置插件，支持通过自然语言或指令清除当前会话的上下文记忆。

## 开发者

**luochenYukitsune**

## 功能特性

- 🔄 **自然语言调用**：LLM 理解用户意图后自动调用
- 🔄 **指令调用**：发送 `/reboot` 指令直接触发
- 🧹 **清除上下文**：调用 SessionManager 的 delete_session 方法
- ⚙️ **自定义指令**：可自定义触发指令前缀
- 🔐 **权限控制**：支持用户ID白名单权限控制
- 💬 **自定义反馈**：支持自定义成功、权限不足、错误时的反馈语句
- 📝 **详细日志**：可开关的调试日志输出

## 使用示例

### 指令方式
```
用户: /reboot
机器人: ✅ 已清除当前会话的上下文记忆，我们可以重新开始对话了！
```

### 自然语言方式
```
用户: 帮我重新开始对话
用户: 清除之前的记忆
用户: 忘记我们刚才说的内容
机器人: [调用 clear_context 工具] ✅ 已清除当前会话的上下文记忆，我们可以重新开始对话了！
```

## 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| command_prefix | string | /reboot | 触发清除上下文的指令 |
| enable_permission | switch | false | 是否启用权限控制 |
| allowed_users | list | [] | 允许执行的用户ID列表 |
| success_message | string | ✅ 已清除... | 清除成功时的反馈消息 |
| permission_denied_message | string | ❌ 权限不足... | 权限不足时的反馈消息 |
| error_message | string | ❌ 清除上下文失败: {error} | 错误时的反馈消息，可用 {error} 占位符 |
| verbose_log | switch | false | 是否输出详细日志 |

## 权限控制

启用权限控制后，只有在 `allowed_users` 列表中的用户才能执行清除上下文操作：

1. 在 WebUI 中启用「启用权限控制」
2. 在「允许的用户ID」中添加用户ID，每行一个
3. 未授权用户执行时会收到权限不足提示

## 自定义反馈

支持自定义三种场景的反馈消息：

- **成功反馈**：清除成功时显示
- **权限不足反馈**：用户无权限时显示
- **错误反馈**：发生错误时显示，可用 `{error}` 占位符显示具体错误信息

## 安装

将 `reboot_plugin` 文件夹复制到 KiraAI 的 `data/plugins/` 目录下，重启 KiraAI 即可。

## 开源协议

本项目采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 开源协议。

详见 [LICENSE](LICENSE) 文件。
