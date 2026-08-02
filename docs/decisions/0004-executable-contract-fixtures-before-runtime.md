# Decision 0004: Executable Contract Fixtures Before DDH Runtime

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Phase 0 `Executable Contract Fixtures` 是 DDH runtime 施工前的必要規格準備階段。

Phase 0 必須將已確認的文字 Contract 轉成未來可直接建立tool-neutral
Verification Assets／contract tests的 executable scenarios，但不實作 runtime，也不過早固定 JSON、database、
message bus、CLI 或其他技術格式。

## Required Coverage

每個適用 Contract 至少定義：

- normal business scenario；
- boundary／rejection scenario；
- invalidation／stale scenario；
- tool failure and automatic recovery；
- race／stress scenario；
- expected mechanical result；
- authority source；
- fields and decisions that automation cannot change。

Phase 0 必須覆蓋：

- Task Specification readiness 與 Work Package projection；
- System Map query consumption 與 bounded live-source fallback；
- Context Envelope；
- work partition、mutation boundary、handoff、join 與 Candidate freeze；
- Verification Asset admission、quality、currentness 與 anti-weakening；
- no-Agent verification execution、result classification 與 verdict；
- layered completion；
- automatic repair、no-progress、budget exhaustion 與 structured exception；
- L1 single-Agent 與 L2 parallel end-to-end acceptance cases。

## Completion Criteria

Phase 0 只有在下列條件成立時完成：

1. 每項 required behavior 都能追溯到 scenario。
2. 每個跨角色 handoff 都有成功、拒絕、失效與競態案例。
3. Prompt convention、validator、mechanical enforcement 與 external authority
   被明確區分。
4. L1 serial 與 L2 parallel 兩條 MVP 路徑都有完整測試藍圖。
5. Fixtures 足以反推後續 runtime 能力與Verification Assets，且沒有先鎖死實作格式。

Phase 0 是一次性的規格準備，不建立逐關人工 Checkpoint。Contract fixture
修正若不改變已確認語意，可在原 authority 內自動處理；語意、scope、risk 或
acceptance 改變仍需人類決策。
