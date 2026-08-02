# Decision 0012: Legacy ADAD Migration Reference Baseline

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH選擇性移植legacy ADAD能力時，主要reference baseline固定為：

```text
repository:
  C:\Users\chris\Desktop\project\ADAD

commit:
  53a26b43d7fd5b0a22f93842a637dfb27b64e232

subject:
  Release ADAD 1.6.5
```

唯讀核對時，local `development`與`origin/development`均指向該commit。

## Dirty Working Tree Boundary

Legacy ADAD current working tree包含大量tracked modifications與untracked source、
tests、Checkpoint及研究文件。它只可作secondary discovery evidence：

- 發現candidate capability；
- 提取failure／business／stress scenario；
- 了解歷史摩擦與未完成方向；
- 找出值得在DDH重新規格化的test pattern。

它不能被描述為：

- clean release；
- deployed capability；
- approved current baseline；
- 可直接複製的canonical source；
- 因存在pytest就已證明可移植的能力。

## Extraction Rule

- 以commit `53a26b4`評估穩定runtime primitives。
- Dirty-tree candidate必須先建立DDH語意、Phase 0 fixtures與acceptance，再決定
  重寫或抽取。
- 不整體搬移`adad_core.py`、Task lifecycle、Source Lock、Checkpoint、
  freshness／receipt／proof-recovery chain或System Map SSOT語意。
- 每項選擇性抽取仍需獨立確認input、output、failure semantics、platform
  behavior與tests。

本決策只固定未來唯讀參考來源，不授權checkout、worktree、copy、migration或
runtime implementation。
