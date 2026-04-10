# Lore Agent 最新提交评审交接（给执行型 AI）

## 评审目标

本文件用于将本地最新提交（HEAD）中的高优先级问题，清晰交接给另一个 AI 进行修复。

- 提交：4d437ba
- 标题：feat: P0-P5 competitive gap closure
- 评审范围：本次提交涉及的新增能力（ingest_source / build_graph / entity extraction / contradiction detection / multi-perspective）

## 已完成验证

- 相关测试已执行并通过：
  - python -m pytest tests/test_build_graph.py tests/test_multi_perspective.py tests/test_common.py -q
  - 结果：55 passed

说明：当前问题属于“行为一致性与覆盖盲区”，不一定触发现有测试失败。

## 发现的问题（按严重级别）

### 1) 中风险：矛盾检测使用固定索引路径，忽略调用方索引参数

- 文件位置：
  - scripts/close_knowledge_loop.py:63
  - scripts/close_knowledge_loop.py:418
  - scripts/close_knowledge_loop.py:505
- 现象：
  - 主流程支持 --index-output 自定义索引路径；
  - 但 build_knowledge_card 内调用 check_contradictions 时使用 DEFAULT_INDEX 常量，导致读取路径与流程参数不一致。
- 风险：
  - 在自定义索引路径、多环境或测试隔离场景下，See Also 可能漏检或误检。
- 最小修复要求：
  - 给 build_knowledge_card 增加 index_path 参数；
  - 在 close_knowledge_loop.main 中传入 args.index_output；
  - 在 mcp_server 入口传入 get_index_path()；
  - 移除对 DEFAULT_INDEX 的硬编码依赖（至少在矛盾检测调用链中）。

### 2) 中风险：无 supporting_claims 时直接跳过矛盾检测，导致新入口能力失效

- 文件位置：
  - scripts/close_knowledge_loop.py:103
  - mcp_server.py:230
  - mcp_server.py:293
  - mcp_server.py:306
- 现象：
  - check_contradictions 在 claims 为空时直接返回；
  - capture_answer 与 ingest_source 默认都写入空 supporting_claims，再调用 build_knowledge_card。
- 风险：
  - “保存时发现潜在冲突/重复”在这两个主要入口基本不会触发。
- 最小修复要求：
  - 不要把 claims 非空作为矛盾检测的硬条件；
  - 当 claims 为空时，至少使用 query 或 answer 文本作为检索输入，维持一致能力。

### 3) 低风险：实体抽取输入接线不一致，且存在未使用变量

- 文件位置：
  - scripts/close_knowledge_loop.py:408
  - scripts/close_knowledge_loop.py:409
- 现象：
  - 先构建 full_text，但实际调用 extract_entities(main_answer)；
  - full_text 变量未被使用。
- 风险：
  - 实体仅来自 Answer 段，Supporting Claims / Inferences 等上下文未参与抽取，降低链接覆盖率。
- 最小修复要求：
  - 改为 extract_entities(full_text)，或删除 full_text 并明确设计为仅抽取主答案。

## 建议修复顺序

1. 先修复问题 1（路径一致性）
2. 再修复问题 2（能力可达性）
3. 最后处理问题 3（质量优化）

## 建议补充测试

### A. 路径一致性回归测试

- 目标：确保矛盾检测读取的是调用方传入的索引路径，而不是默认常量。
- 可选做法：
  - 在 tests/test_multi_perspective.py 或 tests/test_close_knowledge_loop.py 中，构造临时 index_path；
  - mock bm25_retrieve，断言收到的 index_path 与传入参数一致。

### B. 无 claims 仍触发矛盾检测

- 目标：当 supporting_claims 为空时，仍能得到 related cards。
- 可选做法：
  - 构造 answer_data 仅含 answer；
  - mock bm25_retrieve 返回一个高分命中；
  - 断言输出卡片包含 See Also 段落。

### C. 实体抽取覆盖多段文本

- 目标：支持从 Answer + Supporting Claims 等多段内容抽取实体。
- 可选做法：
  - 构造 main_answer 不含实体、claims 含实体；
  - 断言最终 Entities 包含 claims 中实体。

## 对执行型 AI 的交付要求

- 仅做最小必要变更，不重构无关模块。
- 变更后至少运行：
  - python -m pytest tests/test_multi_perspective.py tests/test_common.py -q
- 输出必须包含：
  - 修改了哪些文件；
  - 每个问题如何被修复；
  - 测试结果摘要。

## 备注

- 本评审结论来源于对提交 diff 的静态审查 + 相关测试验证。
- 当前工作树无未提交变更冲突（审查时状态）。