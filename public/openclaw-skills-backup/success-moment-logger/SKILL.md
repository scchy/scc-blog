---
name: success-moment-logger
description: |
  记录今日成功时刻到飞书文档。
  触发方式：用户说"记录今日成功时刻 [内容]"
  会将内容追加到飞书文档：https://my.feishu.cn/docx/ABqhdBCaLoazpkxJGHec9Cvmn1c
---

# 成功时刻记录器

当用户说"记录今日成功时刻"时，将后面的内容记录到指定的飞书文档。

## 使用方法

用户：记录今日成功时刻 完成了XX功能，解决了YY问题

## 处理流程

1. 提取用户消息中"记录今日成功时刻"后面的内容
2. 获取当前日期时间
3. 使用 feishu_doc append 追加到文档

## 文档信息

- URL: https://my.feishu.cn/docx/ABqhdBCaLoazpkxJGHec9Cvmn1c
- doc_token: ABqhdBCaLoazpkxJGHec9Cvmn1c

## 记录格式

```
## YYYY-MM-DD HH:MM
- [内容]
```

## 工具调用

```json
{
  "action": "append",
  "doc_token": "ABqhdBCaLoazpkxJGHec9Cvmn1c",
  "content": "## 2026-03-25 11:50\n- 完成了XX功能，解决了YY问题"
}
```
