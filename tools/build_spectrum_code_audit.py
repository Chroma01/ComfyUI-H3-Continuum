"""Developer-only generator for fixed, source-verified Spectrum audit profiles."""
import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import types


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-root", type=Path, required=True)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reverse", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("spectrum_audit_builder", root / "spectrum_signature.py")
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    result = {"format_version": 1, "python_minor": list(sys.version_info[:2]), "profiles": {}}
    providers = [("local", args.local_root), ("public", args.public_root)]
    if args.reverse:
        providers.reverse()
    for name, provider_root in providers:
        folder = provider_root / "comfyui_spectrum_h3"
        source, metadata_file = adapter._select_source_profile(folder)
        for filename, digest in source.items():
            if adapter._source_digest(folder / filename) != digest:
                raise ValueError("unaudited provider source: " + filename)
        metadata_bytes = (root / adapter._runtime_metadata_file(metadata_file)).read_bytes()
        metadata = json.loads(metadata_bytes)
        namespace = types.ModuleType("spectrum_code_audit_" + name)
        namespace.__path__ = [str(provider_root)]
        sys.modules[namespace.__name__] = namespace
        prefix = namespace.__name__ + ".comfyui_spectrum_h3"
        filenames = sorted(source, reverse=args.reverse)
        modules = {}
        for filename in filenames:
            module = importlib.import_module(prefix if filename == "__init__.py" else prefix + "." + Path(filename).stem)
            if Path(module.__file__).resolve() != (folder / filename).resolve():
                raise ValueError("unexpected provider module path")
            if not adapter._same_except_code_digest(adapter._module_callables(module), metadata["modules"][filename]):
                raise ValueError("legacy provider structure differs: " + filename)
            modules[filename] = adapter._module_callables(module, code_digest=adapter._stable_code_digest)
        result["profiles"][hashlib.sha256(metadata_bytes).hexdigest()] = {"source_sha256": source, "modules": modules}
    args.output.write_text(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n", encoding="ascii")
    print(json.dumps({"output": str(args.output), "python_minor": result["python_minor"],
                      "modules": [len(p["modules"]) for p in result["profiles"].values()]}))


if __name__ == "__main__":
    main()
