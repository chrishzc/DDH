# Decision 0022: MVP Supported Platform Matrix

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH採`release-blocking`、`preview／best-effort`與`unsupported`三級platform
support。

MVP release-blocking matrix：

```text
vendor-supported Windows 11 x86_64
＋ Ubuntu 24.04 LTS x86_64
```

兩者驗證DDH Python 3.13最低版本與當時最新穩定Python。Platform support指
DDH Harness語意，不要求Verification Subject使用相同runtime、OS或shell。

## Required Environments

Windows reference：

- vendor-supported Windows 11 x86_64；
- local NTFS；
- direct argv為core execution path；
- Windows process-tree／Job Object capability；
- PowerShell與Windows-specific path／encoding smoke。

Linux reference：

- Ubuntu 24.04 LTS x86_64；
- local ext4或CI等價local filesystem；
- direct argv為core execution path；
- Unix-like process group／signal capability。

Core不得依賴POSIX shell或PowerShell字串拼接。只有Verification Asset明示
shell semantics時才使用對應adapter。

## Preview／Best-effort

- macOS Apple Silicon／x86_64；
- Linux ARM64；
- WSL2 on Linux-native filesystem；
- 其他vendor-supported Linux distributions；
- Windows 10 ESU／LTSC；
- ReFS／Dev Drive等local filesystem。

Preview failures不阻擋一般release，但不能宣稱full support或PASS。

## Unsupported for MVP

- 32-bit runtime／OS；
- vendor-EOL OS；
- Cygwin／MSYS2作DDH host；
- writable candidate on UNC／SMB／NFS share；
- WSL `/mnt/c`作high-assurance mutation workspace；
- mobile／embedded；
- 無法驗證process、filesystem與cleanup semantics的remote shell。

Unsupported filesystem可作read-only discovery；mutation回報
`filesystem_profile_unsupported`。

## CI Matrix

每個PR至少執行：

- Windows 11 x86_64＋Python 3.13；
- Ubuntu 24.04 x86_64＋Python 3.13。

Release前執行Windows／Ubuntu與Python 3.13／latest stable四格matrix，以及
L2 parallel、crash／timeout、late writer、path alias、atomic result／asset
apply、branch view、System Map fallback與required fault／stress profiles。

## Required Cross-platform Semantics

- case sensitivity與path collision；
- separator、drive與logical relative path；
- symlink／junction／reparse；
- open-file rename／delete；
- atomic replace與partial-write recovery；
- child process tree／process group cleanup；
- signal／cancel／timeout／drain；
- CRLF／LF、UTF-8與BOM；
- temporary-root ownership；
- executable bit與shell invocation；
- locale、timezone與filesystem encoding。

## Required Scenarios

- Same fixture在Windows／Ubuntu得到相同Contract verdict。
- Case-only collision不漏判。
- Windows background child有界清除。
- Unsafe temporary cleanup改為quarantine。
- WSL `/mnt/c`不冒充Linux-native filesystem。
- UNC workspace不進入high-assurance mutation。
- DDH 3.13可驅動不同runtime的target project。
- Preview failure不偽裝supported PASS。
- Required capability缺失時阻擋release。

