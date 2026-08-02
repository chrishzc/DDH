def load_manifest_path(canonical_path: str) -> str:
    if "\\" in canonical_path:
        raise ValueError("canonical_separator_required")
    return canonical_path

