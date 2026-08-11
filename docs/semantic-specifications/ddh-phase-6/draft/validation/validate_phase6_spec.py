from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
SPEC="DDH-P6-SPEC-001@1.0.0"
GROUPS={"terminal_handoff","ledger_and_prefilter","candidate_retention","memory_boundary","controlled_evolution","failure_and_completion"}

def pairs(items:list[tuple[str,Any]])->dict[str,Any]:
    result={}
    for key,value in items:
        if key in result: raise ValueError(f"duplicate JSON key: {key}")
        result[key]=value
    return result

def load(path:Path)->Any:
    return json.loads(path.read_bytes().decode("utf-8"),object_pairs_hook=pairs)

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def close(values:dict[str,str])->str:
    text="\n".join(f"{path}:{values[path]}" for path in sorted(values))
    return hashlib.sha256(text.encode()).hexdigest()

def main()->int:
    errors=[]
    manifest=load(ROOT/"manifest.json")
    expected={"specification_id":"DDH-P6-SPEC-001","version":"1.0.0","status":"ready_for_confirmation","implementation_authority":"none_until_exact_human_confirmation","external_side_effect_budget":0,"completion_claim":"phase6_specification_package_only"}
    for field,value in expected.items():
        if manifest.get(field)!=value: errors.append(f"manifest {field} must be {value}")
    if manifest.get("confirmation",{}).get("confirmed") is not False: errors.append("confirmation must remain false")
    assets=manifest.get("assets",[])
    if len(assets)!=8: errors.append("manifest must contain exactly eight closure assets")
    actual={}
    for item in assets:
        relative=item.get("path")
        if not isinstance(relative,str) or Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append("invalid asset path"); continue
        path=ROOT/relative
        if not path.is_file(): errors.append(f"missing asset: {relative}"); continue
        actual[relative]=digest(path)
        if actual[relative]!=item.get("sha256"): errors.append(f"asset digest mismatch: {relative}")
    if close(actual)!=manifest.get("closure_digest"): errors.append("closure digest mismatch")

    catalog=load(ROOT/"acceptance-scenarios.json")
    scenarios=catalog.get("scenarios",[])
    ids=[item.get("scenario_id") for item in scenarios]
    if catalog.get("specification")!=SPEC: errors.append("acceptance specification mismatch")
    if len(ids)!=len(set(ids)) or len(ids)<25: errors.append("acceptance scenarios must be unique and at least 25")
    if set(catalog.get("required_capability_groups",[]))!=GROUPS or not GROUPS<={item.get("capability_group") for item in scenarios}: errors.append("capability groups incomplete")
    required={"scenario_id","capability_group","class","given","when","expected"}
    if any(required-item.keys() for item in scenarios): errors.append("scenario fields incomplete")

    profile=load(ROOT/"bootstrap-profile.json")
    if profile.get("ledger_hard_cap_bytes")!=65536 or profile.get("routine_agent_token_budget")!=0 or profile.get("external_operation_budget")!=0: errors.append("bootstrap bounds mismatch")
    snapshot=load(ROOT/"phase5-source-snapshot.json")
    if snapshot.get("commit_identity")!="37d0a3fc145641842f1b1f6d07648e55dae8c902" or snapshot.get("phase5_specification")!="DDH-P5-SPEC-001@1.0.0": errors.append("Phase 5 baseline identity mismatch")
    for item in snapshot.get("files",[]):
        path=REPO/item.get("path","")
        if not path.is_file() or digest(path)!=item.get("sha256"): errors.append(f"Phase 5 snapshot mismatch: {item.get('path')}")
    combined="\n".join((ROOT/name).read_text(encoding="utf-8") for name in ("goal.md","runtime-requirements.md","learning-contract.md","implementation-boundary.md"))
    for phrase in ("zero-Agent","64 KiB","analysis_expired_without_memory_change","Guidance Card","cannot publish","rollback","side-effect budget is zero"):
        if phrase not in combined: errors.append(f"required authority phrase missing: {phrase}")
    result={"specification":SPEC,"terminal_state":"succeeded" if not errors else "failed","acceptance_outcome":"passed" if not errors else "failed","verification_completeness":"complete" if not errors else "incomplete","checked_assets":len(actual),"checked_scenarios":len(scenarios),"checked_capability_groups":len(GROUPS),"checked_phase5_snapshot_files":len(snapshot.get("files",[])),"total_error_count":len(errors),"errors":errors}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not errors else 1

if __name__=="__main__": raise SystemExit(main())
