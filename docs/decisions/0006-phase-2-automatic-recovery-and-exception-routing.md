# Decision 0006: Phase 2 Automatic Recovery and Exception Routing

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Phase 2 將常見施工與驗證失敗轉成 typed failure、bounded Failure Bundle 與固定
automatic recovery route。一般工具、Runner、Context、stale 或 scope 內產品／
test implementation 問題不得轉成人工逐關排錯。

Phase 2 仍以 single-Agent execution lane 為主；parallel worker loss、handoff
與 Join Barrier 留在 Phase 3。

## Required Failure Classes and Routes

| Failure class | Required route |
|---|---|
| `product_failed` | 主 Agent 在原 scope 修正，建立新 Candidate，重跑固定驗收 |
| `test_implementation_defect` | Test repair proposal → anti-weakening guard → independent review／probe → readmit |
| `test_semantics_uncertain` | 不得自行選 expected behavior；轉規格缺口 |
| `runner_failed` | 重建 temp／process／environment，使用 approved retry／fallback |
| `tool_backend_unavailable` | 切換已核准 backend；不得臨時創造新 policy |
| `context_insufficient` | Context Curator 按用途與預算增量提供必要 Context |
| `system_map_unavailable` | 對 affected scope 執行 bounded live-source fallback |
| `candidate_stale` | Change Guard 拒絕舊結果，重新 freeze／建立 subject |
| `test_asset_stale` | Test Auditor 重做 validity；歷史 PASS 不可沿用 |
| `impact_underestimated` | 擴張 verification closure，不擴張 write authority |
| `scope_expansion_required` | 保存 Candidate／diff，產生 structured exception |
| `external_side_effect_uncertain` | 不自動執行或重試，轉獨立高風險流程 |

## Failure Bundle

Failure Bundle 必須 bounded，至少引用：

- failure type／reason code；
- Candidate、Verification Subject、test asset identities；
- failed scenario IDs；
- first useful traceback與bounded output excerpt；
- affected nodes／resources與actual diff summary；
- System Map query／live-source confirmation；
- 已嘗試的recovery routes、retryability與remaining budget；
- allowed machine actions與任何required human authority。

不得把完整raw log、重複traceback或完整對話重新注入Agent Context。

## Retry and No-progress

每次retry至少需要一項新資訊或新策略：

- new Candidate；
- new test asset generation；
- new environment generation；
- additional approved Context；
- new impact discovery；
- different approved recovery strategy。

相同inputs、failure fingerprint與strategy不得重複執行。系統必須在budget耗盡前
辨識`no_progress`，保存Candidate／diff並產生structured exception。

## Human Escalation Boundary

只有下列情況需要人類：

- expected behavior／acceptance不明或要改變；
- architecture、schema、data／public contract改變；
- write scope擴張；
- verification threshold／risk policy改變；
- user budget增加；
- 需要尚未核准的新recovery policy；
- external／irreversible side effect；
- 所有approved safe routes耗盡。

## Acceptance

Phase 2 必須以可重跑scenarios證明：

- 產品、test implementation、Runner、Context、stale、impact underestimation與
  no-progress均有固定route；
- test repair不能降低驗收；
- stale PASS不能被Completion Judge接受；
- verification expansion不能偷渡write permission；
- unsafe cleanup保留workspace與user diff；
- routine tool failure不需要人類逐步指揮。
