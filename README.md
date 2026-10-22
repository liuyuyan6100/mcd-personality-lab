# 麦门人格鉴定所 MCD Personality Lab

> 你的麦当劳订单，就是一份人格样本。——拉取历史订单，30 秒生成一张可分享的「麦门人格」鉴定卡。
> 1024 程序员节 · WorkBuddy × 麦当劳程序员创意开发大赛参赛作品

## 这是什么

「麦门人格鉴定所」是一个基于麦当劳中国官方 MCP（mcd-mcp）开发的 Skill：读取你的历史订单、餐品营养与积分账户数据，通过五维人格模型（犒赏力 / 猎奇度 / 夜猫指数 / 辣度耐受 / 甜度依赖）与九型麦门人格判定，生成一张移动端优先、可截图分享的单文件 HTML 鉴定卡——人格判词用「麦门文学」体写成。

**榜单上 104 个项目都在做「前瞻决策」（怎么买便宜、怎么吃健康），没有人做「回顾 + 人格」——这是本项目的切入点。**

**零门槛体验**：没有订单数据也能玩，内置 `--demo` 演示模式（合成数据，seed=1024 可复现），一条命令生成完整鉴定卡。

## 安装

```bash
git clone https://github.com/liuyuyan6100/mcd-personality-lab.git
cd mcd-personality-lab
```

无第三方依赖，Python 3.8+ 标准库即可运行。

## 使用

```bash
# 演示模式（内置合成数据，无需 MCP Token）
python src/run.py --demo

# 真实模式（需要麦当劳 MCP Token）
python src/run.py --token <YOUR_MCD_MCP_TOKEN>

# 自定义输出路径
python src/run.py --demo --output my-card.html
```

申请 MCP Token：https://open.mcd.cn/mcp （手机号登录 → 控制台 → 激活 → 复制）

运行后 stdout 返回 JSON 摘要（人格类型 / 五维分数 / 产物路径），产物为单个 HTML 文件，浏览器打开即可查看、截图分享。

## 演示

仓库内置两份真实跑通的产物：

| 文件 | 说明 |
|---|---|
| `output/mcd-personality-MCP-FCDE86BA-demo.html` | 演示模式产物：麦辣鸡型人格（52 单 / ¥1980.9 / 辣度耐受 74） |
| `output/mcd-personality-MCP-15F9CE1F.html` | 真实 Token 跑通产物：无订单账号正确降级为「麦门新信徒」待鉴定卡 |

## 九型麦门人格

麦辣鸡型 · 巨无霸型 · 麦乐鸡型 · 穷鬼套餐型 · 甜筒型 · 深夜食堂型 · 探险家型 · 早安型 · 板烧型（+ 麦门新信徒）

## 目标用户

- 想吃懂自己麦当劳消费人格的用户（"我在麦当劳是什么人设？"）
- 想要社交分享物料的内容创作者（人格鉴定卡天然适合截图传播）
- 想学习 MCP × Agent Skill 编排的开发者

## 技术栈

Python 3.8+（纯标准库）｜ 麦当劳中国官方 MCP Server（Streamable HTTP，mcp-mcp 1.0.0，35 Tools）｜ 单文件静态 HTML 鉴定卡（零前端依赖）

## 开发方式

本项目使用 WorkBuddy 驱动开发（自然语言指令 → 全自动编码/调试/产出），完整开发实录见 [workbuddy.md](workbuddy.md)。

## 参赛声明

见 [CONTEST_DECLARATION.md](CONTEST_DECLARATION.md)（官方原件，未改动）。MCP 使用说明见 [MCP_INTEGRATION.md](MCP_INTEGRATION.md)。

## 关于作者

刘宇燕（灵魂攻城狮）· WorkBuddy 驱动开发实践者

- 个人博客：[blog.aiclawonline.website](https://blog.aiclawonline.website/)——AI 工程实战、MCP/Agent 开发实录
- 公众号：「沐沐ai智能」——AI 实操交付与开发实录

<img src="assets/qrcode_wechat.png" width="180" alt="公众号 沐沐ai智能 二维码">

## License

MIT
