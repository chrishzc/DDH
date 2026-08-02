# Coding Harness and Agent Clean Code Self-Check Profile

**Contract ID：** `DDH-CODE-001`  
**Profile：** `Agent Clean Code Self-Check Profile v1`  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存 Agent coding self-check 與 mechanical boundary 分工；
不授權 runtime、linter、reviewer、schema 或 hook implementation  

---

## 1. 第一原則

Clean Code 五條守則是 coding Agent 的施工習慣與交付前自我檢查，不是假裝成
CI、AST validator 或 mechanical safety boundary。

```text
Agent Clean Code Self-Check
＋
high-confidence Mechanical Boundaries
```

兩者不得混稱。Agent 自述 PASS 是 claim，不能取代 pytest、scope／diff evidence、
TAQG admission 或 automatic review。

## 2. 執行流程

每個生成／修改程式碼的 Agent：

```text
receive subgoal／scope
→ load versioned Self-Check Profile
→ write code
→ review touched code against Rules 1～5
→ repair within scope
→ return bounded result／exceptions
```

沒有把握時先在 scope 內修正；需要跨檔案／Module 大幅重構時不能擴大施工，
只建立 bounded finding／scope proposal。

## 3. Rule 1：三秒命名

- 避免模糊縮寫、無意義編號與新增魔術數字。
- Variable／function／class 依語言慣例表達意圖與責任。
- 交付前重讀 touched identifiers。

明顯 placeholders 可以由 configurable profile 偵測；「三秒可理解」仍是語意
self-check／review，不宣稱 mechanical proof。

## 4. Rule 2：20 行樂高積木

- 新增或實質重寫 function 以 20 行為 soft default。
- 超過時先檢查 single responsibility／single abstraction level。
- 拆分提高可讀性時自動拆分。
- 拆分製造無意義 wrapper／indirection 時可以保留。

保留時使用有長期價值的 Why comment，例如：

```python
# Kept together because each branch mirrors one immutable protocol state,
# and splitting them would hide the transition table's exhaustiveness.
```

限制：

- untouched legacy function 不要求補註解；
- generated／vendor code 不適用；
- 不為 20 行製造大量一行 wrappers；
- 不建立 global line-21 hard failure。

## 5. Rule 3：防禦型單向出口

- Boundary／error conditions 優先 guard clause／early return／throw。
- 對等正常分支可以使用 `else`。
- 兩層 nesting 是 review signal，不是 syntax ban。
- 超過時先考慮抽取 responsibility。
- 不為消除 `else` 引入更難懂 polymorphism／state jump。

Complexity／nesting thresholds 可以由 versioned language／project profile 定義。

## 6. Rule 4：程式即文件

- Code 表達 What／How。
- Comments 說明 business reason、workaround、compatibility、external limitation
  或 non-obvious invariant。
- 禁止逐行重述 code。
- 不設定 comment count。

Rule 2 的有效 exception comment 是 Why，因此不與本規則衝突。

## 7. Rule 5：童軍營地法則

- 可整理 touched function／file 內與 task 直接相關的 smell。
- 每一行修改應可對應 goal、repair、test 或 scope-local cleanup。
- 不跨 Module／file「順便重構」無關行為。
- Scope 外問題只建立 bounded finding。

「每行是否相關」是 Agent self-check；actual write boundary 由 CIM mechanical
enforcement。

## 8. Bounded Self-Check Result

```yaml
clean_code_self_check:
  profile_version: clean-code-agent-v1
  touched_scope_checked: true
  rules:
    naming: pass
    function_responsibility: pass_with_exception
    guard_and_nesting: pass
    comments: pass
    touched_boundary: pass
  exceptions:
    - location: workspace/path_state.py::apply_transition
      rule: function_length_default
      reason: keeps exhaustive protocol transition table visible
```

Result 不包含 chain of thought，也不證明 mechanical completion。

## 9. Mechanical Boundaries

真正可阻擋：

- syntax／parse／build；
- configured type／lint errors；
- actual write scope／prohibited path；
- unauthorized external side effect；
- secret／credential mutation；
- confirmed architecture dependency／Module boundary；
- unauthorized generated／vendor write；
- required test deletion／skip／weakening；
- pytest oracle／threshold change without TAQG admission；
- file-wide suppression／disabled linter、type checker、test discovery；
- uncontrolled network／database／filesystem mutation。

Hard Gate 必須 high precision，不因純 aesthetic preference 阻擋。

## 10. Configurable Profiles

可以設定：

- function complexity／size／nesting／parameter count；
- Module／file size；
- naming patterns；
- duplicate code；
- public API documentation；
- import／dependency；
- test structure；
- formatter／linter。

Profile 必須 versioned、由 Task Specification／Projection 固定引用、區分 new／
legacy／generated／test code。Agent 不能施工中改 threshold；existing baseline
與 new／worsened violations 分開。

## 11. Automatic Review

Review semantic quality：

- intent-revealing names；
- mixed responsibilities／abstraction levels；
- hidden side effects；
- unclear Module responsibility；
- Why comment quality；
- over-abstraction／meaningless splits；
- scope-local cleanup／over-refactor。

Finding：

- `blocker`：具體 correctness、boundary、maintainability 或 testability defect。
- `advisory`：style improvement，不阻擋 functional acceptance。

Reviewer 不修改 code／tests。Pure preference 不能冒充 mechanical failure。

## 12. Legacy, Generated and Suppression

Legacy：

- 不先清全 repository；
- 不新增／惡化 violations；
- scope／budget 內改善 touched region；
- 大型重構使用獨立 Task Specification。

Generated／vendor：

- 原則修改 generator／template；
- direct output edit 需 Task Specification 允許；
- generated validation 與一般 source profile 分開；
- vendor 預設 read-only。

Suppression：

- Profile 允許；
- minimal scope；
- concrete Why；
- 不隱藏 correctness／security／boundary；
- 不停用 file／directory／suite；
- 納入 review／diff。

新 suppression policy 需要正式規格／治理 change。

## 13. Automatic Flow

```text
change
→ cheap incremental checks
→ structured finding
→ Agent repairs within scope
→ rerun affected checks
→ continue
```

Failure 提供 rule ID、exact location、mechanical evidence、severity、allowed
remediation、profile／baseline reference。

Tool crash、cache corruption、formatter conflict 走 automatic recovery；禁止
infinite formatter loop、full-repo scan for small change、full lint output injection
與 scope-external refactor。

## 14. 業務場景

### 28-line Pure Calculation

Low-complexity single responsibility function 不因超過 20 行直接阻擋。Profile
提示 size，Review 確認不需無意義拆分。

### 80-line Mixed Responsibility

API、JSON、DB、notification、retry 混在同一 function。Review 形成 concrete
blocker；若違反 Module boundary 同時觸發 Hard Gate。Agent scope 內拆分並重驗。

### 200-line Legacy Function

只修 boundary bug：不要求先重構全部；不得增加 complexity，新增 pytest，
安全時局部整理，大型重構另開 Task Specification。

### File-wide Suppression

Agent 加 file-wide `noqa` 隱藏 errors：Hard Gate 阻擋；必須修本次新增 errors
或依正式 policy 提出 minimal exception。

## 15. Stress Contract

- Large legacy repo 只報 new／worsened violations。
- Multi-language profiles 正確選用。
- Generated／vendor files 不被誤改。
- Formatter／linter／type checker conflicts 自動封閉。
- Tool crash／cache corruption 自動恢復。
- Agent不能用 suppression、rename 或 meaningless split gaming。
- Large AST／finding set 增量、有界輸出。
- Advisory 不阻擋 functional completion。
- Blocker 引用 concrete defect。
- Harness repair 無 infinite retry。
- Coding checks／summaries 不使 Agent token 隨 repository 線性增長。

## 16. 對應機械測試

```text
test_clean_code_profile_is_agent_self_check_not_claimed_mechanical_proof
test_twenty_lines_is_soft_default_with_bounded_why_exception
test_equal_normal_branches_can_use_else
test_comment_policy_requires_why_not_comment_count
test_scope_boundary_is_mechanical_even_when_cleanup_guidance_is_advisory
test_self_check_result_cannot_replace_tests_scope_or_review
test_existing_legacy_violations_are_separate_from_new_regressions
test_generated_vendor_and_suppression_rules_follow_versioned_profile
test_review_advisory_does_not_block_and_blocker_requires_concrete_defect
test_harness_tool_failure_recovers_without_human_checkpoint
test_large_incremental_coding_checks_are_bounded_and_zero_agent
```

## 17. Self-Evolution Boundary

OLE 可以改善 Self-Check presentation、examples、review summary 與 fixer ordering，
不能自行修改 Rules 1～5、profile authority、hard boundaries、severity semantics、
suppression policy、scope、tests、acceptance 或 human escalation。
