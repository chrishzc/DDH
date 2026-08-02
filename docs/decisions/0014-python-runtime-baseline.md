# Decision 0014: Python Runtime Baseline

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH Reference Runtime 的最低版本採 Python 3.13：

```toml
[project]
requires-python = ">=3.13"
```

第一版 required CI matrix 至少驗證：

- Python 3.13；
- 當時最新穩定 Python；
- Windows 與 Linux 的必要平台案例。

不得只在文件或安裝腳本描述最低版本。提高最低版本屬於 Runtime 相容政策
變更，必須有相容性報告與人類核准；Learning Steward 或其他自我演進機制
不得自行調整。

## Target Runtime Independence

DDH Runtime 的 Python 版本不限制 Verification Subject 使用的語言或 Python
版本。Verification Runner 應透過目標專案自己的 environment／tool adapter
執行 Verification Assets，再消費標準化結果。

例如 DDH 可在 Python 3.13 執行，同時呼叫使用 Python 3.9 virtual environment
的既有專案。DDH 不得因自身版本較新而暗中要求目標專案升級。

若驗證需要載入目標 interpreter，必須使用明示的相容 shim 或 project-side
adapter；不得把 DDH 3.13-only modules 注入較舊 interpreter。

## Required Business Scenarios

1. DDH 3.13 控制不同 Python 版本的目標專案執行既有測試。
2. Python 3.13 與最新穩定版完成相同核心 DDH 流程。
3. Windows 與 Linux 對相同結果契約給出一致判定。
4. DDH interpreter 版本不足時 fail fast，且不留下半執行狀態。
5. 目標 runtime 不可用時回報結構化 environment gap，不擅自安裝、不降低
   驗收。
6. pytest、generic command 與至少一種非 Python tool adapter 不要求 DDH 與
   Verification Subject 使用相同 runtime。

## Consequence

Legacy ADAD 的 `requires-python >=3.9` 不移植為 DDH 基線。Python 3.13 是
Reference Runtime 的產品選擇，不是 Verification Subject 的施工限制。

