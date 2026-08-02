# Wire Transport and Identity State Tables

## Atomic File Transport

| State | Event | Required result |
|---|---|---|
| request ready | backend starts | isolated invocation directory remains exclusive |
| backend running | writes `result.pending` | result is not consumable |
| pending complete | atomic replace succeeds | `result.json` becomes candidate result |
| pending complete | backend crashes | `incomplete`; pending is ignored／cleaned by policy |
| result present | schema／identity valid | result accepted for current subject |
| result present | subject／generation mismatch | stale／rejected |

## Typed Identity Change

| Change | Identity effect |
|---|---|
| Same subject retry | new invocation, same subject |
| Source change | new candidate and Verification Subject |
| Test／threshold／environment change | new Verification Subject |
| Task Specification change | new version and Work Package |
| Same bytes in a later generation | digest may match; lifecycle generation differs |

## Platform Disposition

| Platform | DDH MVP disposition |
|---|---|
| Windows 11 x86_64 | release blocking |
| Ubuntu 24.04 LTS x86_64 | release blocking |
| Python 3.13 | minimum required runtime |
| latest stable Python | forward-compatibility required |
| macOS／ARM64／WSL2／other Linux | preview |
| 32-bit／vendor-EOL／network-share writable candidate | unsupported |

