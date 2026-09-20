# Module 4 Contributions

## 责任范围

Module 4 是面向传统术数项目的个性化与私人知识库后端。它接收其他模块已经计算完成的
结构化结果，负责持久化、推荐、案例匹配、反馈、私人知识管理和隐私控制，不重新计算八字、
易卦、签文或公共知识图谱事实。

## 已实现功能

- 会话创建、恢复和按顺序读取事件历史。
- 通过 `X-Idempotency-Key` 实现事件幂等。
- 按 `0.35 / 0.30 / 0.20 / 0.10 / 0.05` 权重执行确定性推荐排序。
- 缺少部分特征时按剩余权重重新归一化，并返回信息不足警告。
- 匿名相似案例匹配，包含同意范围校验和结构化多特征相似度。
- 显式反馈和隐式反馈信号。
- 私有收藏、笔记、标签和来源版本引用。
- 用户数据 JSON 导出。
- 隐私设置、匿名案例授权和用户数据删除。
- 使用 `source_id` 保存公共知识来源引用。
- 对缺少 `source_id` 的旧数据集，从规范化 URL 生成稳定性一致的来源 ID。
- 所有私有查询严格按 `user_id` 隔离。

## 跨模块契约

- 接收 Module 1、Module 2A、Module 2B、Module 3 和前端事件。
- 保留 `source_id`、`source_refs`、`schema_version` 和事件顺序。
- 不修改 Module 3 的公共知识或公共图谱。
- 保持统一响应 envelope 和结构化错误格式。
- 为 `Slyvia0425/fortune` 前端提供兼容路由：
  - `POST /api/session/event`
  - `POST /api/user/notes`
- 兼容路由在 Module 4 内部转换为严格契约，不要求前端修改。

## 模型层

- 默认无模型模式：`EMBEDDING_PROVIDER=hash`、`LLM_PROVIDER=template`。
- 向量模型：`BAAI/bge-m3` 或 `bge-small-zh-v1.5`，通过 `sentence-transformers` 使用。
- Explanation 模型：支持 OpenAI-compatible 接口。
- 已验证远程 MacBook M5 Max 128 GB 上的 Ollama `qwen3.8:27b-q8_0`：
  - `100% GPU`
  - 约 47 GB 运行时大小
  - Windows 通过 SSH local forwarding 访问
- LLM 仅生成推荐解释和相似案例解释。
- LLM 不允许修改图表、卦象、签号、原文、确定性命中数据、分数或排序结果。

## 跨平台部署

- Windows 原生：`setup_windows.bat`、`test_windows.bat`、`start_windows.bat`。
- Linux 原生：`setup_linux.sh`、`test_linux.sh`、`start_linux.sh`。
- Linux CUDA/ML：`setup_linux_gpu.sh`。
- macOS 远程 Qwen：`scripts/setup_mac_qwen.sh`。
- Windows 到 Mac 隧道：`start_remote_mac_qwen_windows.bat`。
- Linux/macOS 到 Mac 隧道：`start_remote_mac_qwen_tunnel.sh`。
- 模式说明：`docs/deployment_modes.md`。
- 版本升级到 `0.2.0`，详细变更见 `CHANGELOG.md`。
## 存储与运行

- 默认本地 SQLite，可无 GPU 启动。
- 生产向量存储使用 PostgreSQL + pgvector。
- Alembic 初始修订：`20260918_0001`。
- `case_profiles.embedding` 为 PostgreSQL `vector(1024)`。
- 提供 Windows 安装、启动、测试、迁移、演示数据和 GPU 初始化脚本。
- 已实现并验证 WSL2、Docker Desktop、CUDA 容器、PostgreSQL 和 pgvector。

## 验证

- Ruff 通过。
- mypy 严格模式通过。
- 24 个 pytest 测试通过。
- 开发依赖和 ML 依赖两种安装方式均通过。
- 提供 `verify_end_to_end_windows.bat` 实时全流程验证：
  - 健康检查
  - 隐私
  - 前端兼容事件和笔记
  - 会话
  - 事件幂等
  - 推荐与远程 Qwen 解释
  - 反馈
  - 收藏、笔记、标签
  - 用户隔离
  - 导出
  - 相似案例与远程 Qwen 解释
  - 用户数据删除
- 全流程会在结束时删除临时验证用户的数据。

## 明确边界

- 不计算八字、易卦或签文事实。
- 不替代 Module 1、Module 2A、Module 2B 或 Module 3。
- 不修改其他成员的源代码。
- 不将用户私人笔记写入公共知识库。
- 不允许 LLM 改变任何确定性结果。