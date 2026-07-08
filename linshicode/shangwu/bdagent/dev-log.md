# bdagent 开发日志

> **⚠️ 新会话从这里开始读：最新交接是本文末尾「大改动（2026-07-07 晚）：清空+重取历史 / Approach B / 淋浪人员名册」一节。**
> **前面的「生产群管理后台」「语料库三件套」等是更早的历史。**

## 会话交接记录（2026-07-03 ~ 2026-07-06）

> 本会话完整对话历史（JSONL，供新会话追溯细节）：
> `C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent-shangwu\aa9a9d46-93f2-4e3c-a57b-bf8164cfdb61.jsonl`
>
> 另有持久化项目记忆（跨会话自动加载，含全部踩坑记录）：
> `C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent\memory\project_bdagent.md`

---

## 一、这个会话干了什么（按时间顺序）

### 1. 项目定调
- bdagent 定为**独立子项目**（不挂主网关 LinlangAssistant，不用 Python import 集成），飞书机器人形式
- 对外功能规划：①收集客户基础信息 ②安排拉会 ③沉淀客户知识库 ④TTO/TAP数据（已搁置）
- 对内功能规划：①倩逸预算拆解→提案网页（oxyenergy试点）②同化商品详情页KV ③部署到linknlatch.com子页面 ④结项报告 ⑤续单 ⑥案例转换
- MVP 策略：对外先做"收集客户基础信息"，对内等倩逸的预算拆解逻辑文档（**至今没拿到，对内6项全部未开工**）

### 2. agent 本体搭建（根目录，~500行）
- 独立 venv（`bdagent/.venv`，Python 3.11），`lark-oapi` 官方SDK，**长连接(WebSocket)模式**，不需要公网域名
- 链路：收消息 → 存群聊天记录 → 关键词("客户"/"录入")或 DeepSeek 语义判断 → 发表单卡片（公司/联系人/预算/需求）→ 用户提交 → 存 SQLite `clients` 表 → 回确认
- 已在真实飞书群实测跑通（群：崔博能,段雨萌，chat_id `oc_62798dd79c28005d78101e9483253478`）

### 3. 训练台搭建（bot/ 文件夹，~500行 + 前端）
- 目的：用两个飞书自定义机器人webhook（客户bot/运营bot）+ DeepSeek 角色扮演，模拟客户对话来测试真实 bdagent
- **关键架构决策**：自定义机器人webhook只能发不能收，无法真正让两个bot在群里互相触发。所以由训练台后端**在进程内直接调用 bdagent 真实的 handlers 函数**（`on_message`/`decide_and_send`/`on_card_action`），测的是真实决策代码；webhook只负责把对话可视化发进测试群
- 控制台：FastAPI（`bot/server.py`，127.0.0.1:8899）+ 三栏网页（左会话列表/中角色选择/右聊天框）
- 功能：新建会话（DeepSeek生成客户人设backstory）、手动发言、AI代打单轮、**自动聊天循环**（严格轮流，2.5秒/轮，20轮安全上限）、结束会话
- 会话模型：`sessions` + `session_messages` 表；生产=一个飞书群一个会话（懒创建）；训练台=同一测试群可并存多个逻辑会话，`is_simulated=1` 隔离，测试数据不污染真实客户表

### 4. 测出并修复的真实bug（都验证过修复生效）
1. **卡片JSON 1.0旧写法陷阱**：input直接放顶层elements+独立action按钮 → 卡片能发、能填、提交不报错，但回调里 `form_value` 是空的。已改成卡片2.0规范：`schema:"2.0"` + `body.elements` + `form`容器 + `action_type:"form_submit"`
2. **DeepSeek推理模型 max_tokens 陷阱**：`deepseek-v4-pro` 是推理模型，答案前先消耗 reasoning token；`max_tokens=5` 会在思考中途截断，content拿到空字符串且不报错。已改 500
3. **模型名大小写**：DeepSeek API 只认全小写 `deepseek-v4-flash`，传 `DeepSeek-V4-Flash` 直接400
4. **前端会话切换竞态**：快速切换会话时，旧会话的慢响应（尤其AI回复要几秒）回来后会覆盖新会话的显示。已在 `loadSession`/`sendMessage`/`aiReply` 三处加 `requestedId !== currentId` 过期丢弃
5. **客户人设角色漂移**：bdagent沉默不回应时，客户bot下一轮会脑补"对方"的回复混进自己发言里。已改 persona.py：历史标注改成"你(客户)/对方(淋浪商务)"，明确禁止替对方说话
6. **同一会话重复弹卡**：`wants_client_card` 只看单条消息，客户后面再提预算会被重复当新客户。已在 `decide_and_send` 加 `pending_card`/`client_recorded` 双重防护（**此修复对生产 bdagent 同样生效**）

### 5. 最后一项【进行中，未完成】
- **运营侧改用真实 bdagent 身份发真实卡片**（代替运营bot webhook冒充）：代码已写完（`simulator.py` 的 `_ops_uses_real_api()` 分支，`.env` 已配 `TEST_GROUP_CHAT_ID`），**但最后的真实API测试被用户打断，尚未验证跑通**。新会话接手第一件事建议先问用户是否继续测这一步
- 旧的运营bot webhook路径保留为兜底（`TEST_GROUP_CHAT_ID` 留空时启用）

---

## 二、当前状态快照（2026-07-06 交接时）

| 项 | 状态 |
|---|---|
| 对外①收集客户信息 | ✅ 完成，真实群实测通过 |
| 对外②安排拉会 | ❌ 未开始（需飞书日历API） |
| 对外③客户知识库 | 🟡 半成品：聊天记录已存库，但无检索/RAG |
| 对外④TTO/TAP | ⏸️ 用户明确搁置 |
| 对内全部6项 | ❌ 未开始，阻塞：倩逸预算拆解逻辑文档没拿到 |
| 训练台手动/AI/自动聊天 | ✅ 完成并实测 |
| 训练台运营侧真实API改造 | 🟡 代码完成，测试未跑（被打断） |
| 两个后台进程 | ⛔ 都已停（会话重启带没的），启动方式见 readme.md |
| 数据库 | 测试数据已清理干净 |

## 三、遗留事项 / 新会话待办

1. 【优先问用户】运营侧真实API改造要不要继续测（会往真实测试群发消息）
2. 【催办】倩逸的预算拆解逻辑文档——对内6项的总阻塞
3. "同化商品详情页KV"的具体含义用户一直没澄清
4. bdagent 目前对非录入意图的消息完全沉默（没有通用对话能力），自动聊天时运营侧大部分轮次不说话——要不要加兜底应答，等用户定
5. DeepSeek API key 曾直接贴在对话里，建议用户去后台轮换（已提醒过）
6. 安全注意：`.env` 含真实密钥，已被 `.gitignore` 保护；`shangwu/` 整个目录目前也在 `.gitignore` 里（用户自己加的），意味着 bdagent 代码**尚未纳入git版本控制**

## 四、技术栈速查

- Python 3.11 独立venv：`bdagent/.venv`（不共用主项目的）
- 飞书：`lark-oapi`，长连接模式，事件 `im.message.receive_v1` + `card.action.trigger`
- LLM：DeepSeek（意图判断用 `deepseek-v4-pro`，客户人设扮演用 `deepseek-v4-flash`），OpenAI兼容协议
- 存储：SQLite `data/bdagent.sqlite3`（占位，最终要换公司数据库，接口都收在 `storage.py`）
- 训练台：FastAPI + uvicorn（127.0.0.1:8899）+ 原生JS单页

---

# 会话记录（2026-07-06 下午）：三方模型重构

> 本节之前的内容是旧的"两方模型"时期记录，其中"运营==bdagent"的说法已过时，仅作历史参考。
>
> 本会话完整对话历史（JSONL，供新会话追溯细节）：
> `C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent-shangwu\bcb6d612-1285-43c7-be4b-d9e17b384d01.jsonl`
>
> 持久化项目记忆（跨会话自动加载，角色模型/权限/踩坑都在里面）：
> `C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent\memory\project_bdagent.md`

## 一、角色模型纠偏（用户澄清，本次一切改动的出发点）

**正确模型是三方**：群里有客户、运营（真人，公司主要人员）、bdagent（辅助运营的机器人）。
`bot/kehu` 模拟客户，`bot/yunying` 模拟**运营真人**——不是 bdagent 的传声筒。
此前实现把"运营"和 bdagent 合并成了一个角色（训练台 `ai_reply(运营)` 直接调 bdagent 决策、
bdagent 的回复 prompt 写成"商务同事本人"），是理解偏差。

bdagent 行为策略（用户拍板）：**主动弹卡 + 被点名（文本含"机器人"）才聊天，其余时间沉默旁听记录**。

## 二、本次改动

1. 新增 `bot/yunying/persona.py`：运营真人人设「小淋」（deepseek-v4-flash 角色扮演）
2. `handlers.py`：`decide_and_send` 加 `addressed` 参数 + `mentions_bot()`；bdagent 发言的
   speaker 标签从"运营"改为"机器人"；生产 `on_message` 传 `addressed=True`（生产群必须@它才收得到）
3. `llm.py`：`generate_ops_reply` 改名 `generate_bot_reply`，prompt 改成"辅助运营的机器人助理"口吻
4. `bot/simulator.py`：三方重构——`ai_reply(运营)` 调 yunying 人设；新增 `_bdagent_observe()`
   把每条（客户/运营）消息喂给 bdagent 真实决策代码；`manual_message(运营)` 不再用真实API冒充 bdagent
5. `bot/kehu/persona.py`：客户人设感知三方角色（prompt + `_label` 加"机器人"映射）
6. `bot/static/index.html`：第三身份"机器人"紫色气泡（运营蓝色、客户白色）；角色栏说明更新
7. `readme.md` / `config.py` 注释同步三方语义

## 三、多视角审查（Workflow，31个agent）确认并修复的 7 个问题

1. **[high] send_card 失败仍置 pending_card=1** → `feishu.send_text/send_card` 改为返回 bool，
   发送成功才置位（否则群里没卡但状态锁死，录入功能对该群永久失效且无恢复路径）
2. **[medium] on_card_action 无幂等** → 新增 `storage.try_consume_pending_card()`（原子 UPDATE
   WHERE pending_card=1），提交前先消费；重复点击/过期残留卡回 toast"这张表单已经处理过啦"。
   这同时封掉了"测试群残留真卡片被真人点击→以 is_simulated=0 污染真实客户表"的路径
3. **[medium] 存量数据未迁移** → `init_db()` 加一次性迁移（schema_migrations 表打标记）：
   生产会话里旧 bdagent 发言 speaker='运营'→'机器人'（已验证：4条迁移完成）
4. **[medium] manual_message/ai_reply 不校验会话状态** → 新增 `_require_active()` 守卫：
   已结束会话拒绝写入；自动聊天运行中拒绝外部手动/AI调用（防止和循环线程双重提交表单）
5. **[low] 两个 persona 的"对话刚开始"开场分支是死代码** → 修正拼接顺序，首轮真正走开场提示
6. **[low] `_ops_uses_real_api` 改名残留** → 改为 `_bdagent_uses_real_api`，config.py 旧注释更正
7. persona 偶发把历史标签抄进回复开头（"你(客户): xxx"）→ 生成后正则剥前缀

## 四、真实API端到端测试（ALL PASS，往真实测试群发过消息）

手动流程：运营开口机器人沉默 → 客户报需求主动弹真卡 → 自动填表"已录入客户" →
录入后再提预算不重复弹卡、保持沉默 → 点名"机器人"才回话（回复正确把跟进留给小淋）→
运营AI回复是人设发言。自动聊天：客户/运营轮流、bdagent 旁听插话，三方轮转正常。
DB 验证：测试客户全部 is_simulated=1，真实客户表零污染；speaker 迁移生效。
前端浏览器验证：三色气泡渲染正确。

**踩坑**：第一次跑测试时 8899 端口被一个当天上午用系统 Python（非venv）启动的旧代码进程占着，
新服务器绑定失败（uvicorn 打了 ERROR 但进程"看起来"在跑），测试全打到旧进程上、现象诡异。
以后测试前先 `Get-NetTCPConnection -LocalPort 8899` 确认端口归属。

## 五、当前状态 / 遗留

- 测试群里残留 2 张真实登记卡片（测试发的），点击会被幂等保护拒绝，无害，可不管
- 库里 2 个升级前的真实群会话仍是 active + pending_card=1（旧卡片如果还在群里，真人填了会正常录入）
- 旧遗留事项不变：催办倩逸预算拆解文档（对内6项总阻塞）、"同化商品详情页KV"含义待澄清、
  DeepSeek key 建议轮换

## 六、交接给新会话（2026-07-06 会话结束时快照）

**本会话按时间顺序干了这些事：**
1. 用户纠正角色模型（三方：客户/运营真人/bdagent 辅助），据此重构训练台（改动清单见上文"二"）
2. 31-agent Workflow 多视角审查，确认并修复 7 个问题（见上文"三"）
3. 真实API端到端测试 ALL PASS（见上文"四"；踩坑：8899端口被旧进程占用）
4. 实测并开通飞书云文档权限：wiki 读 + bitable 读写；多维表格**《商务agent》**
   （wiki token `MZQkwAf7xiEeI8kFrPWci196nyf`，表 `tblbPUaMC8WB6Zoi`，视图 `vew603gmeJ`）
   已给 bdagent「可编辑」授权，读字段/读写删记录全部实测通过。该表当时只有1个文本主字段、5条记录
5. 项目首次推送 GitHub：commit `c1672d0`（23文件）+ `4fd4367`（docs），直推 main
   （仓库 https://github.com/linknlatchmcn/LinLangAgent ，密钥扫描确认 .env/.venv/data 未上库）

**进程状态：两个进程都会随本会话关闭而停**（训练台跑在本会话后台任务里）。
重启方式见 readme.md；启动前先确认 8899 端口没被旧进程占着。agent 本体 main.py 本会话从未启动。

**新会话可直接上手的活（按优先级建议）：**
1. 「录入客户 → 同步写多维表格《商务agent》」：权限已全部打通，只差在 `handlers.on_card_action`
   录入成功后加一段 bitable 写入（wiki get_node 解析 app_token → bitable/v1 records create；
   注意表格字段结构还没按 company/contact/budget/need 设计，建字段也可以用 API 做）
2. 催倩逸的预算拆解逻辑文档——对内6项的总阻塞，一直没拿到
3. 对外②安排拉会（飞书日历权限未申请）/ 对外③客户知识库检索，等用户选

---

# 会话记录（2026-07-06 晚）：客户录入同步多维表格

> 接上一节交接的优先级 1 任务。本会话完整对话历史（JSONL）：
> `C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent-shangwu\982d38de-d65b-4dcc-9ae2-d5fa8c33d24d.jsonl`

## 一、干了什么

「录入客户 → 同步写多维表格《商务agent》」已完成并真实API测试通过：

1. 新增 `bitable.py`：wiki token 解析 app_token（`wiki get_node` → `obj_token`，进程内缓存）；
   自动补齐表字段（主字段重命名为"公司名称"，缺的字段自动创建：联系人/预算/需求描述/提交人/来源群/录入时间(日期型)）；
   `sync_client()` 写记录并把 record_id 回写 SQLite；`sync_client_async()` 后台 daemon 线程封装
2. `handlers.on_card_action`：录入成功、主流程收尾（send_text/记消息/置 client_recorded）之后
   起线程同步；**仅真实录入同步，训练台 `is_simulated=1` 的数据不写表格**
3. `storage.py`：`clients` 表新增 `bitable_record_id` 列（含旧库 ALTER TABLE 兼容）。
   **漏同步判据：`is_simulated=0` 且 `bitable_record_id` 为空**，可凭此事后补写
4. `config.py` / `.env.example`：`BITABLE_WIKI_TOKEN`（wiki 节点 token，非 app_token）+
   `BITABLE_TABLE_ID`，默认值即《商务agent》表；两个都置空则关闭同步
5. 同步失败只记日志不打断录入流程（SQLite 有底账），失败时**清掉 app_token 缓存**，
   下一条记录重新走"解析+补字段"实现自愈

## 二、多视角审查（Workflow，54个agent）：16 findings，确认4个（去重后3个），已全部修复

1. **[medium] `_ready_app_token` 缓存永不失效**：首次成功后运营同事改表（删列/改主字段名）会导致
   后续同步全部静默失败直到重启，自愈逻辑 `_ensure_fields` 被缓存挡住够不着
   → 修复：`sync_client` 失败时 `_invalidate_ready()` 清缓存，下一条自动重走解析+补字段
2. **[low] 主字段改名后 `names` 快照未更新**：新表主字段恰好叫"联系人"等保留名时会漏建字段且
   之后每条写入必败 → 修复：改名成功后 `names.discard(旧名); names.add("公司名称")`
3. **[low] lark SDK token 缓存过期清理无锁（`LocalCache.get` 先 get 后 del 无锁）**：本次改动首次让
   生产进程出现双线程同刻调 lark API，token 恰好过期时有极小概率 KeyError 炸掉卡片回调
   → 修复：同步线程挪到 `on_card_action` 主流程收尾之后再起，错开取 token 时刻

被推翻的 12 个里值得记两条背景："record_id 为空=漏同步"的补写前提在极端窗口（记录已建成、
回写 SQLite 前线程被杀）会产生重复记录——人工补写时先对一眼表格即可；字段列表分页（>100字段）
未处理——这张表 7 个字段，不现实。

## 三、真实API测试（两轮，均 ALL PASS，未发群消息、未动表里已有记录）

- 主链路：解析 app_token → 建字段（验证 7 字段齐全、主字段=公司名称、录入时间=日期型）→
  写记录 → 读回逐字段核对 → SQLite backref 核对 → 删测试记录 + 删本地测试行
- 自愈链路：人为污染缓存为坏 token → 第一条失败(91402 NOTEXIST)且缓存被清 → 第二条自动恢复写入成功 → 清理
- **注意：《商务agent》表的字段结构本次已真实改掉**（主字段改名"公司名称"+新建6字段），
  表里原有 5 条记录未动

## 四、交接给新会话（2026-07-06 晚会话结束时快照）

- 优先级 1（录入→多维表格同步）**已完成**。生产 main.py 本会话未启动，改动尚未在真实群跑过
  完整"提交卡片→表格出现记录"链路（API 层面等价链路已测通），下次启动 main.py 后可顺手验证一条
- 剩余待办不变：
  1. 催倩逸的预算拆解逻辑文档——对内6项总阻塞
  2. 对外②安排拉会（飞书日历权限未申请）/ 对外③客户知识库检索，等用户选
  3. "同化商品详情页KV"含义待澄清
  4. DeepSeek key 建议轮换（key 曾贴在对话里）
- 可选后续：漏同步补写脚本（查 `is_simulated=0 AND bitable_record_id IS NULL` 逐条 `bitable.sync_client`，
  跑之前先人工对一眼表格防重复）

---

# 会话记录（2026-07-07）：语料库三件套（FAQ应答/表单扩展/拉会话术）

> 本会话完整对话历史（JSONL）：
> `C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent-shangwu\982d38de-d65b-4dcc-9ae2-d5fa8c33d24d.jsonl`

## 一、背景

倩逸 2026-07-06 给了《商务Agent语料库.md》（放在 bdagent 根目录）。内容是**对外**语料：
商家FAQ（合作模式三档/单条售卖$5/$20/$35报价）、客户信息搜集清单、拉会话术、建联SOP。
**注意：文档"对内-预算拆解逻辑"一节是空的，对内6项的阻塞并没有解除，还要继续催。**
拉会@的负责人姓名用户确认是**季倩逸**（文档里"倩亦"是笔误）。

知识库路线决策（用户问 grep vs RAG）：语料才1千多字，**全量塞 prompt**，不做检索；
语料长大后先升级 SQLite FTS5 关键词检索；向量RAG除非量大到关键词不够用，且真到那步
复用 linlang-assistant 的 Qdrant，不在 bdagent 里自建。

## 二、本次改动

1. **`knowledge.py`（新）**：语料按 mtime 缓存热加载——倩逸直接改 md 文件即生效，不用改代码/重启
2. **`llm.py`**：`generate_bot_reply`（点名回复）system prompt 注入语料库，业务问题按口径答，
   语料没有的仍然只说"商务同事跟进"；新增 `faq_auto_reply`（未点名消息：命中语料FAQ则按口径
   回复，否则输出SILENT保持沉默；flash模型，temperature 0.3）
3. **`handlers.decide_and_send`**：未点名分支从"直接沉默"改为"客户消息先过 FAQ 判断"；
   运营的发言不抢答（看 history 末尾 speaker）
4. **表单 4→10 字段**（`cards.py` 改为 FORM_FIELDS 清单驱动）：新增 品牌名称/产品TK链接/
   是否开店出新手村/店销是否1000+/佣金比例/主体入库配合；`storage.clients` 加同名6列
   （含旧库ALTER迁移）；`bitable.py` 表格自动加6列、写入映射 `_FORM_TO_FIELD`
5. **拉会话术第一版**（`handlers._meeting_followup`）：录入成功后紧跟一条
   "基本情况已经了解，请问什么时间方便安排一个会议？…@季倩逸 麻烦跟进确认会议时间"；
   `feishu.find_member_open_id` 按姓名反查群成员 open_id 发真实 `<at>`，不在群里退化纯文本@；
   @对象配置 `MEETING_CONFIRMER_NAME`（默认季倩逸，置空关闭）。client_recorded 幂等保证只发一次
6. **训练台适配**：kehu backstory prompt 生成新字段（TK Shop 场景），
   `_submit_form_from_backstory` 改为按 `cards.FORM_FIELDS` 自动映射（以后加字段自动跟上）

## 三、测试（ALL PASS）

- 综合脚本：卡片结构10字段/语料热加载/FAQ真实DeepSeek调用（合作模式&单条报价数字逐一核对无编造、
  闲聊沉默）/点名入库流程回答正确（"免费"）/模拟payload全链路（2条消息+新字段落库+重复提交幂等拒绝）/
  未点名FAQ接话&运营不抢答/测试群成员反查/bitable 13字段齐全+全字段写读删
- 真实发送：10字段新卡片飞书 schema 校验通过（测试卡留在测试群，点提交会被幂等拒绝，无害）；
  `<at>`标签消息发送成功（@崔博能验证格式）
- **意外收获：季倩逸本人在测试群里**（open_id 已能查到），拉会@在测试群就能真实生效

## 四、遗留 / 待用户动作

1. **【用户】飞书开放平台申请「接收群聊中所有消息」权限**——生产群目前只收 @机器人 的消息，
   FAQ 不点名自动应答和(未来的)客户时间回复捕捉都要这个权限才能在生产完整生效
2. 【用户】催倩逸补语料库"对内-预算拆解逻辑"一节（对内6项总阻塞，本次没解除）
3. 生产 main.py 仍未常驻部署（用户说先不急）；启动后建议真实录一条验证全链路
4. 拉会第二版方向：捕捉客户回复的时间并@季倩逸带上时间（需1里的权限+一个时间识别判断）；
   飞书日历API自动建日程更后面
5. 语料库md已纳入git（含报价信息，仓库是私有的；如不想上库告诉我改成gitignore+服务器单独放）

---

# 会话记录（2026-07-07 下午）：生产群管理后台

> 本会话完整对话历史（JSONL）：
> `C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent-shangwu\982d38de-d65b-4dcc-9ae2-d5fa8c33d24d.jsonl`

## 一、需求（用户提的后台）

给 bdagent 做一个仿飞书三栏的**生产群管理后台**（8898，与训练台8899独立）：
①左群列表+右聊天记录 ②按群配置：消息收集模式(默默/主动问询)、回复模式(被@回复、无人回复安抚)
③群成员角色标注(技术/达人运营/商务对接运营) ④每群总开关(关=只记录不回复)。

## 二、本次改动（新增/改）

- **storage.py**：新增三表 `group_settings`(按群开关) / `group_member_roles`(成员角色) /
  `reply_watch`(未回复计时)，及全套访问器；`get_chat_history` 跨会话取一个群完整消息流
- **admin/server.py（新）**：FastAPI 127.0.0.1:8898，`/api/groups`、`/api/groups/{id}`、
  `PUT settings`、`PUT members/{oid}/role`
- **admin/static/index.html（新）**：三栏后台。左=机器人所在群，中=聊天记录(客户白/运营蓝/机器人紫气泡)，
  右=设置开关+成员角色。设置改完立即生效，机器人进程实时读库
- **watcher.py（新）**：无人回复安抚线程(60秒一轮)。客户消息超过 X 分钟没有"标了角色的员工"回复→
  群里发"XXX正在飞快赶来"+语料能答的顺带答+私信提醒对应角色同事(LLM按问题分类挑人)
- **handlers.py**：`decide_and_send` 受 settings 门控(bot_enabled/collection_mode/reply_on_mention/
  instant_faq)；`on_message` 员工/客户判定(标了角色=员工，发言记"运营"并清计时)+未回复计时
- **feishu.py**：`list_bot_chats`/`get_chat_name`/`send_text_to_user`(私信)/`get_chat_members`
- **llm.py**：`classify_question_role`(技术/达人运营/商务对接运营，拿不准落商务)
- **main.py**：启动 watcher 线程

## 三、多视角审查（Workflow，103个agent）确认并修复的问题（去重后13个）

3 个 high：
1. **开启安抚开关瞬间对陈旧消息误发安抚**（向真实客户群）：on_message 原来无条件计时，关着的群
   也积压旧行，开开关时 waited=几天立即触发 → 改为**只在 reminder_enabled 时才计时**，且
   **打开开关时 clear 该群积压计时**（storage.update_group_settings）
2. **_fetch_members 不分页**：>20人的群拉不全成员，员工标不了角色被误判成客户 → 安抚误触发 →
   加 page_token 翻页(page_size 100)
3. **成员昵称 XSS**：esc() 没转义单引号，客户可控昵称注入后台 onchange → 改 data-* 属性 +
   addEventListener + textContent 注入名字（浏览器实测注入串不执行、以纯文本显示）

medium/low：
4. **mark_reminded 只按 chat_id**：会误消费"员工回复后客户追问"的新计时 → WHERE 加 awaiting_since 绑定
5. **_soothe 先置位后发送**：发送失败则该轮安抚永久丢失 → 改**先发群安抚，成功才 mark_reminded，
   失败 unmark_reminded 下轮重试**；私信时长用真实 awaiting_since 算(不是阈值)
6. **watcher 重开 lark token 缓存无锁竞态**（SDK LocalCache.get 无锁 del）→ feishu.py 加全局
   `lark_lock`(RLock) 串行化所有飞书 API 调用，bitable.py 也用同一把锁，彻底消除竞态
7. **5秒轮询重建右栏打断编辑**：改为轮询只刷聊天记录(panel=false)，设置/成员只在切群+保存后重建
8. **on_card_action 不受 bot_enabled**：停用的群残留卡片提交仍发消息 → 停用时数据照常入库但不发群消息
9. answered 防复读：即时答过的问题安抚时不再复答同一语料；find_member_open_id 遍历加 list() 快照；
   PUT settings 非数字忽略防500；role:null 归空串；reminder_minutes 前端 Math.min(1440) 对齐后端

被推翻的11个里值得记：init_db 迁移跨进程非原子(双进程首启小概率，可接受)、机器人被踢后 reply_watch
残行(会发一次幽灵DM，low)。

## 四、测试（全通过）

- test_watcher_fixes：mark_reminded绑定/新计时不被旧快照吞/开开关清陈旧/发送失败回滚+成功置位/
  answered防复读/未答附FAQ/lark_lock可重入/真实分页拉成员 —— 9项ALL PASS
- test_admin_backend：群列表/门控/角色标注/LLM分类/安抚真实发送/防重复 —— ALL PASS
- test_corpus_features：回归全过(未点名FAQ改为受 instant_faq 门控)
- 浏览器实测(chrome-devtools)：XSS注入串不执行、单引号名字下拉正常、轮询不重建正在编辑的成员下拉、
  panel=true才重建、控制台无报错

## 五、当前状态 / 遗留

- 机器人 main.py + 后台 admin/server.py 都跑在本会话后台(会话结束即停)。后台 http://127.0.0.1:8898
- **待用户**：①飞书申请「接收群聊中所有消息」权限——默默收集/无人回复检测的完整价值靠它(现只收@消息)
  ②催倩逸补语料库"对内-预算拆解逻辑"(对内6项总阻塞) ③常驻部署(用户说先不急)
- 安抚/秒答FAQ 默认每群关，需在后台按群打开；员工要在后台标角色，安抚才知道@谁+私信谁

## 追记（当天晚些，用户开通了「接收群聊中所有消息」权限后）

用户在飞书后台发布了 `im:message.group_msg` 权限并生效（实测：发一条不@机器人的
"随便说句话"，进库了）。**这立刻暴露一个潜伏bug**：`on_message` 里 `addressed=True`
是硬编码的（基于"生产只收得到@消息"的旧假设）。权限一开，机器人收到群里每一条消息，
全被当成"被@"→ 见句就回（实测机器人真回了那条"随便说句话"）。
**已修**：新增 `_is_bot_addressed(message)`——私聊永远算；群里看 `message.mentions`
数组里有没有名字含"机器人"的（飞书@的可见文本是占位符 `@_user_N`，真名在 mentions 里）。
`on_message` 改用它。单元测试覆盖：私聊/无@/@别人/@机器人/@多人含机器人。已重启机器人。
**连带好处**：现在全量消息进来，无人回复安抚、秒答FAQ、员工/客户计时都能真正在生产生效了
（之前只有@消息进得来，这些功能形同虚设）。
**注意成本**：主动问询模式下，每条非关键词客户消息现在都会触发一次 DeepSeek 意图判断
（`wants_client_card`），直到该群录过客户为止。群一旦聊起来这是持续的LLM调用，
量大再优化（可考虑只在关键词/被@时判断）。

## 再追记：历史区分"真·@"和"手打@"(用户观察)

用户指出：飞书里"真·@"(mention，蓝色+下划线)和手打"@某某"(普通黑字)是两回事，之前
两者存进库长得一模一样(都是纯文本 @名字)分不出。真@时飞书 event 的 message.mentions
数组里有这条，手打就没有——这个信号之前没存。
**已补**：session_messages 加 mentions 列(JSON存真@到的人名)；on_message 从 message.mentions
取真@人名一起存；on_card_action 的拉会@季倩逸(真<at>)也标上。后台 renderMsgText 把 mentions
里的 @名字 渲染成蓝色+下划线(深色气泡用浅蓝)，手打@保持普通文字。XSS安全(先转义再包span)。
只影响新消息，旧消息 mentions 为空→都渲染成普通文字。

## 大改动（2026-07-07 晚）：清空+重取历史 / Approach B 身份现算 / 淋浪人员名册

用户三连需求：①清空两个真实群聊天记录再从飞书重取 ②身份改"读取时按当前名册现算"(Approach B) ③加全局淋浪人员名册(命中=自家人+职务，喂LLM"淋浪+职务+姓名")。

**为什么这么设计**：历史是只增按时间的流水，不用 git 那套内容diff，用"每群一个游标(水位线)"断点续传；身份是我们的业务判定(飞书只给 open_id)，冻结在写入时会导致"改名册要重取"，改成读取时现算就一劳永逸；名册全局配一次(自家人在所有群是同一批)，比逐群标角色省事且能喂给LLM更强的上下文。

**改动**：
- storage：session_messages 加 sender_open_id/sender_name/is_bot/feishu_message_id(唯一索引)/feishu_create_time；staff_roster 名册表+CRUD+match_roster(open_id优先,姓名兜底,已钉open_id的条目只认该id防重名)；resolve_identity(读取时把消息解析成 speaker类别+who显示+llm富标签)；get_session/get_chat_history 读取时现算并按 feishu_create_time 排序；chat_sync_state 游标+clear_chat_messages
- sync_history.py(新)：message.list(ByCreateTimeAsc,start_time秒,翻页)拉历史+message_id去重+游标推进+catch_up_all启动追赶；一次性拉成员名字避免逐条API
- handlers：Approach B 存身份+feishu ids；机器人发言带真实 message_id(send_* 改为返回 message_id 供去重)；重复事件(append返回False)直接return
- feishu：send_text/send_card/send_text_to_user 返回 message_id(仍是真值，`if send_text` 不受影响)
- watcher：_pick_person 改用群成员+名册；llm：历史用富标签；main：启动追赶线程
- admin：名册CRUD端点+成员按名册解析+POST sync端点+GET /history(轻量轮询)；前端名册管理UI+成员选职务=加名册+同步按钮+消息显示who/真实时间+轮询不打断翻看

**104-agent 审查确认29个(去重后6类)，全部修复**：
1. [high×多] 机器人自己发的消息同步后翻倍(NULL message_id 和回拉的真实id不去重)→send_* 返回真实 message_id 存下来，去重生效(实测重取后0重复)
2. [medium×多] 历史按入库id排序导致时序错乱(回填的旧消息id更大)→改按 feishu_create_time 排序+显示；机器人/训练台消息入库时也给时间基准
3. [medium×多] 同名客户被 by_name 兜底误判成自家人→已钉open_id的名册条目只认该id，重名客户(不同open_id)不再命中
4. [medium] 同步对离群成员每条消息全量拉成员→一次性拉好成员名字map
5. [medium] 5秒轮询重拉成员+把翻看位置拽回顶部→轮询走轻量 /history 端点、无变化不重建DOM、保留滚动位置
6. [low] 事件重投重复回复→append去重返回False时return；@提及前缀名误标→按长度降序替换；移除风险自动钉open_id(改由后台选职务时钉)

**真实执行清空+重取(已完成)**：测试2 清27→重取24(客户10/机器人14)，测试 清5→重取126(早期训练webhook历史全是app发的→机器人)。DB核验：0重复message_id、0个NULL_id、唯一索引生效。浏览器实测：历史显示真实发送时间、@提及保留标蓝、把崔博能加进名册→他10条消息瞬间从"客户"白气泡变"淋浪·商务对接运营·崔博能"蓝气泡(0重取，Approach B生效)。

**已知限制(审查提到，v1接受)**：①离群成员重取时查不到名字→其历史暂显示为"客户"(测试群成员都在，不影响)；②群里若有其它飞书应用，其历史消息会被当成"机器人"(测试群无其它app)；③名册按姓名为主键，成员改群昵称后成员面板的删除按名可能对不上(靠钉住的open_id仍能正确解析身份)。

**当前状态**：名册已放一个示例(崔博能=商务对接运营)，用户可在后台增删改；季倩逸/段雨萌等自家人待用户按真实职务补进名册(补完历史身份自动跟着变)。机器人+后台跑新代码在线。
