# Decision 0013: Modular Python Runtime and Tool-neutral Verification

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Runtime Direction

DDH第一版採：

```text
language-neutral Contracts
＋
single modular Python reference runtime
＋
Ports／Adapters
```

長期演進方向採方案B：只有在實際安全、process control、concurrency、
distribution或performance證據支持時，選擇性將Change Guard backend、
Verification process controller、managed-asset atomic apply或Trusted Executor
替換成Rust／Go implementation。

這不是未來整套重寫。Role Contracts、results、failure semantics與Ports保持
language-neutral；Python仍可保留Verification adapters。第一版不採多服務
distributed runtime。

## Package Boundary

第一版維持一個DDH distribution，內部分離：

- contracts；
- task specification／risk；
- seven role packages；
- ports；
- concrete adapters；
- operations；
- runtime composition；
- thin CLI／API entrypoints。

Roles只能依賴public Contracts／Ports，不能直接依賴concrete Git、Agent、
System Map、test tool或external SDK。Required capability缺失時回報
degraded／unavailable並走approved fallback；不得靜默使用語意較弱實作後宣稱
相同PASS。

## Tool-neutral Verification

DDH正式管理的對象是`Verification Asset`，不是固定pytest：

- pytest、unittest或其他language test framework；
- `npm test`、`go test`、`cargo test`；
- build／compile checks；
- lint／format validation；
- type checking；
- schema／contract checks；
- security scanners；
- integration／end-to-end checks；
- performance／load／stress／soak checks；
- CI pipeline中的可重跑checks；
- 其他具有固定input、environment、timeout、expected result與structured
  outcome的verification command。

pytest是Python-first reference adapter與主要早期dogfood工具，但不是MVP
authority或必要產品依賴。

## CI/CD Boundary

DDH可以：

- 在本機／isolation backend執行與CI相同的checks；
- 產生CI job／manifest；
- 觸發已核准、沒有外部產品副作用的remote verification；
- 消費綁定exact Candidate、environment與asset identities的structured CI
  results。

CI/CD pipeline若包含deployment、publication、production database、credential、
external network mutation或不可逆操作，該部分仍屬Phase 7 External Operation
Plan與Trusted Executor。Pipeline名稱不能授予external authority。

## Verification Asset Governance Amendment

原文件中的`pytest asset`、`Test Asset Catalog`與`pytest-as-evidence`，在正式
語意上分別擴張為：

```text
Verification Asset
Verification Asset Catalog
admitted rerunnable verification assets as executable evidence
```

`Test Auditor` canonical role name暫時保留；它審核所有正式Verification Assets
的traceability、quality、currentness與anti-weakening，不只pytest。

`Verification Runner`透過tool adapters執行fixed assets。每個adapter必須遵守
相同Subject binding、Environment Profile、Adaptive Bounded Timeout、output
protocol、result classification與invalidation semantics。

## Required Cross-tool Proof

第一版至少證明：

1. Python pytest adapter。
2. 一個非pytest command adapter，例如`npm test`、`go test`或generic fixed
   command fixture。
3. 相同Verification Protocol可聚合不同tools的required results。
4. Tool unavailable不能被當成PASS。
5. Remote CI result只有在exact Candidate／environment／asset binding完整時
   才可被Completion Judge消費。

Exact Python minimum version已由Decision 0014確認為Python 3.13；Rust／Go
extraction trigger已由Decision 0015確認為evidence-gated evolution；wire
format已由Decision 0016確認為JSON Contract Envelope v1。
