# Cike Nexus Backend

基于 **FastAPI + SQLModel + Alembic** 构建的 Agent（智能体）平台后端服务，围绕「智能体应用 / 工具（MCP & Skill）/ 知识库 / 会话 / 组织架构」建模。

## 技术栈

| 组件 | 选型 | 说明 |
| --- | --- | --- |
| 语言 | Python `>=3.14` | 见 `.python-version` |
| 包管理 | [uv](https://docs.astral.sh/uv/) | 构建后端为 `uv build` |
| Web 框架 | FastAPI (`[standard]`) | 依赖注入 + 自动 OpenAPI 文档 |
| ORM | SQLModel (SQLAlchemy + Pydantic) | 实体同时充当表模型与校验模型 |
| 数据库 | MySQL（`pymysql` 驱动） | 连接串通过环境变量注入 |
| 迁移 | Alembic | `alembic/versions` 下存放版本脚本 |
| LLM | LangChain / LangChain-OpenAI | 目前仅引入依赖，业务尚未接入 |

## 目录结构

```
.
├── main.py                          # FastAPI 应用入口，注册路由
├── alembic.ini                      # Alembic 配置（含 sqlalchemy.url）
├── alembic/
│   ├── env.py                       # 以 SQLModel.metadata 作为 target_metadata
│   └── versions/                    # 迁移脚本
└── src/cike_nexus/
    ├── routers/                     # 接口层：APIRouter，只做参数绑定与转发
    ├── applications/                # 应用层：业务服务（Service），通过 Depends 注入
    ├── dtos/                        # 传输层：入参 / 出参模型（Pydantic）
    ├── data/
    │   ├── DbContext.py             # engine 与 get_session 会话工厂
    │   ├── abstracts/               # AuditedEntity / FullAuditedEntity 审计基类
    │   ├── entities/                # 数据库实体（table=True）
    │   ├── value_objects/           # 值对象，序列化后落 JSON 列
    │   └── enums/                   # 枚举
    └── utilities/                   # 通用工具，如 PasswordHasher
```

## 分层约定

请求自上而下流转：`Router → Service → Session/Entity`。

- **Router**（`routers/`）：定义路径、方法与出入参类型，不写业务逻辑。以 `Annotated[XxxService, Depends(XxxService)]` 注入服务。
- **Service**（`applications/`）：承载业务规则，构造函数注入 `Session`（`Depends(DbContext.get_session)`），业务校验失败直接抛 `HTTPException`。
- **DTO**（`dtos/`）：对外契约与实体解耦。`AuditedDto` 会把 `id` 序列化为字符串，避免雪花/大整数 ID 在 JS 端精度丢失。
- **Entity**（`data/entities/`）：继承审计基类，`id` 使用 `BigInteger`，查询字段普遍建索引。

### 审计基类

- `AuditedEntity`：`id`、`create_at`、`update_at`、`created_by`、`updated_by`
- `FullAuditedEntity`：在上述基础上增加 `is_deleted`（软删除标记）

会话消息类实体（`AgentConversationMessage`、`AgentConversationMessageContent`）继承 `AuditedEntity`（不支持软删除），其余实体继承 `FullAuditedEntity`。

## 数据模型

| 实体 | 表 | 职责 |
| --- | --- | --- |
| `User` | `user` | 用户账号，`password` 存储 PBKDF2 摘要 |
| `Department` | `department` | 部门 |
| `DepartmentUser` | `departmentuser` | 部门与用户的关联 |
| `AgentApplication` | `agentapplication` | 智能体应用：提示词 `instructions` + `default_model`(JSON) |
| `Tool` | `tool` | 工具定义：`type` + `config`(JSON) + 启停开关 |
| `AgentTool` | `agenttool` | 智能体与工具的关联 |
| `AgentConversation` | `agentconversation` | 会话，归属某个 `agent_id` |
| `AgentConversationMessage` | `agentconversationmessage` | 会话消息，`role` 取 `user` / `ai`，记录 `duration_seconds` |
| `AgentConversationMessageContent` | `agentconversationmessagecontent` | 消息内容分片，按 `content_type` 区分文本/JSON |
| `UserAgentConversation` | `useragentconversation` | 用户与会话的关联 |
| `Knowledge` | — | 知识库：嵌入模型、向量集合与向量服务标识 |
| `KnowledgeRelation` | — | 知识库关联，`correlation_type`：1=agent，2=department |

> 关联关系通过显式的中间表实体表达，实体上不声明 `Relationship`，跨表查询在 Service 中用 `select` 组合。

### 工具类型与配置

`ToolType` 决定 `Tool.config` 的实际结构，反序列化时由 `_parse_config` 按 `type` 分派：

| `ToolType` | 配置值对象 | 字段 |
| --- | --- | --- |
| `StdioMCP` | `StdioMcpToolConfigValue` | `command`、`args`、`env` |
| `HttpMCP` | `HttpMcpToolConfigValue` | `url`、`headers`、`timeout` |
| `SKILL` | `SkillToolConfigValue` | `url` |

`AgentApplication.default_model` 使用 `ModelConfigValue`：`model`、`temperature`、`top_p`。

## 接口

应用入口 `main.py` 中挂载：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/` | 健康检查 |
| `POST` | `/api/users` | 新增用户，返回用户 ID；用户名重复返回 `409` |
| `GET` | `/api/users?id=` | 查询用户详情（**尚未实现**，当前返回空 DTO） |

启动后可访问 `http://127.0.0.1:8000/docs` 查看 Swagger UI。

## 密码存储

`utilities/PasswordHasher.py` 采用 PBKDF2-HMAC-SHA256：

- 迭代 `200_000` 次，派生密钥 32 字节，随机盐 16 字节
- 存储格式：`pbkdf2_sha256$<iterations>$<base64(salt)>$<base64(hash)>`
- 校验使用 `hmac.compare_digest` 做常数时间比较，防时序攻击
- 算法标识内嵌于摘要中，便于后续升级迭代次数或更换算法

## 快速开始

### 1. 同步依赖

```shell
uv sync
```

### 2. 配置数据库连接

项目根目录 `.env`（由 `DbContext` 通过 `load_dotenv()` 读取）：

```dotenv
SQL_CONNECTION_STRING = "mysql+pymysql://<user>:<password>@<host>:<port>/cike-nexus?charset=utf8mb4"
```

> 密码中的特殊字符需 URL 编码；在 `.env` / `alembic.ini` 中 `%` 需写成 `%%` 转义。
> Alembic 使用的是 `alembic.ini` 里的 `sqlalchemy.url`，与 `.env` 是两套配置，修改数据库时**两处都要改**。

### 3. 执行迁移

```shell
uv run alembic upgrade head
```

修改实体后生成新的迁移脚本：

```shell
uv run alembic revision --autogenerate -m "描述"
```

> 新增实体后，必须在 `alembic/env.py` 的 import 列表中登记，否则 `--autogenerate` 感知不到该表。

### 4. 启动服务

```shell
uv run fastapi dev main.py
```

生产模式：

```shell
uv run fastapi run main.py
```

## 开发规范

- 文件名与类名保持一致，采用 `PascalCase`（如 `UserService.py`、`AddUserDto.py`）。
- 实体字段统一用 `Field(description=...)` 标注中文含义，字符串字段显式给 `max_length`。
- 大整数（ID、外键）统一 `sa_type=BigInteger`；对外输出时由 DTO 序列化为字符串。
- 新增业务模块时按 `dtos/<module>/`、`applications/<module>/`、`routers/<Module>Router.py` 三处对齐建目录，并在 `main.py` 注册路由。
- 删除采用软删除语义：置 `is_deleted=True`，查询时需过滤。

## 当前进度与待办

- [x] 用户新增接口、密码哈希、审计基类、初始化迁移
- [ ] `GET /api/users` 查询逻辑（`UserRouter.get` 仍为占位实现）
- [ ] `dtos/FullAuditedDto.py` 的 `AuditedDto` 未继承 `BaseModel`，`field_serializer` 暂不生效
- [ ] `Knowledge` / `KnowledgeRelation` 未登记到 `alembic/env.py`，初始迁移中无对应表
- [ ] 认证鉴权（登录、Token）、审计字段自动填充
- [ ] 智能体、工具（MCP / Skill）、知识库、会话相关接口与 LangChain 编排
- [ ] `python-dotenv` 为传递依赖，建议在 `pyproject.toml` 中显式声明
