# Decision 0016: JSON Contract Envelope v1

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH跨語言Contract第一版採：

```text
UTF-8 JSON
＋ JSON Schema Draft 2020-12
＋ versioned message envelope
＋ message-type-specific payload schema
```

不得建立一個容納所有情況的鬆散巨大schema。Task Specification仍是本次
行為與驗收SSOT；semantic specification定義payload語意；JSON Schema只驗證
資料形狀與型別。Wire message是可重建的短期runtime projection，不是永久
Evidence或authority。

System Map維持自己的規格與schema；DDH透過adapter消費，不要求System Map
使用本Envelope。

## Common Envelope

第一版common envelope至少分離：

```text
protocol
protocol_version
message_type
message_id
correlation_id
subject
payload
```

正式結果不得只用單一`pass` boolean。至少必須依適用Contract區分：

- terminal state；
- acceptance outcome；
- verification completeness；
- stable reason code；
- retryability。

Message內自稱的producer／execution identity不是可信authority。可信執行
身分必須由實際execution channel提供。

## Initial Transport Profile

第一版subprocess／backend交換採isolated invocation directory中的atomic file
profile：

```text
request.json
→ backend execution
→ result.pending
→ atomic replace to result.json
→ schema／identity／completeness validation
```

stdout／stderr只作有界診斷，不能兼任正式結果通道。未來只有在量測證明
此profile成為瓶頸時，才增加framed stream、local RPC或其他transport；payload
Contract不因此改變。

所有protocol artifacts都是短期runtime data，完成目前consumer需求後依既定
retention policy清除，不成為長期Evidence Retention。

## Interoperability Rules

- UTF-8，拒絕duplicate JSON keys。
- Authoritative core payload拒絕unknown fields。
- 可擴充資訊只能放在namespaced `extensions`。
- Exact decimal／money／high-precision value使用decimal string。
- Duration／size使用明示unit欄位。
- Missing與explicit `null`語意分開。
- Portable content identity不得包含machine absolute path、user name或random
  temporary path。
- 禁止pickle、任意object serialization或YAML tags作為wire format。
- Parser必須有payload size、nesting depth、array／string length等bounded
  limits。

## Versioning

- Incompatible field或semantic change提升major version。
- Additive optional information提升minor version。
- Unsupported major回報`protocol_incompatible`並fail closed。
- Unknown authoritative enum不得被猜測或降級處理。
- Schema、fixtures與cross-language conformance assets共同版本化。

## Content Digest

只有需要內容digest的Contract data才使用RFC 8785 JSON Canonicalization
Scheme產生canonical bytes，再以帶algorithm名稱的digest表示。第一個
reference profile採`sha256`。

Content digest只表示這份內容相同，不建立永久cross-version entity identity、
provenance receipt或freshness chain。Replacement／supersession必須明示。

## Required Scenarios

- Python／Rust／Go對相同fixture產生相同canonical digest。
- Unsupported major、duplicate key、unknown core field、invalid enum與
  oversized／overdeep payload被拒絕。
- Crash留下的`result.pending`不能被消費。
- Duplicate／late／out-of-order result不污染current subject。
- Candidate／environment mismatch fail closed。
- Unbounded tool output不污染control result。
- Concurrent invocation directories不互相讀寫。
- Windows／Linux的Unicode與logical path fixture保持一致。
- Fuzzed input不造成unbounded resource consumption或Harness crash。

