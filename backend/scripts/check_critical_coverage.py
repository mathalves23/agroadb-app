from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


THRESHOLDS: dict[str, float] = {
    "bootstrap.py": 80.0,
    "main.py": 70.0,
    "core/security.py": 70.0,
}


def main() -> int:
    coverage_file = Path("coverage.xml")
    if not coverage_file.exists():
        print(f"[coverage] Arquivo não encontrado: {coverage_file}", file=sys.stderr)
        return 1

    root = ET.parse(coverage_file).getroot()
    failures: list[str] = []

    for filename, minimum in THRESHOLDS.items():
        class_node = root.find(f".//class[@filename='{filename}']")
        if class_node is None:
            failures.append(f"[coverage] Arquivo crítico sem cobertura registrada: {filename}")
            continue

        line_rate = float(class_node.attrib.get("line-rate", "0"))
        percent = line_rate * 100
        if percent < minimum:
            failures.append(
                f"[coverage] {filename} abaixo do mínimo: {percent:.2f}% < {minimum:.0f}%"
            )
            continue

        print(f"[coverage] {filename}: {percent:.2f}% (mínimo {minimum:.0f}%)")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("[coverage] Cobertura crítica do backend validada com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
