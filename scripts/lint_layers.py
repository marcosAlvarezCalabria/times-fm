#!/usr/bin/env python3
"""
Linter Estructural de Capas e Invariantes Arquitectónicas
Valida dependencias unidireccionales y emite mensajes con instrucciones de remediación para agentes.
"""

import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Orden jerárquico estricto de capas (de menor a mayor nivel)
LAYER_ORDER = {
    "types": 0,
    "config": 1,
    "repository": 2,
    "service": 3,
    "runtime": 4,
    "ui": 5,
}

MAX_FILE_LINES = 250

# Patrones de importación para JS/TS y Python
JS_IMPORT_PATTERN = re.compile(
    r"""(?:import\s+(?:[\w*\s{},$]+\s+from\s+)?|export\s+(?:[\w*\s{},$]+\s+from\s+)?|require\s*\(\s*)['"]([^'"]+)['"]"""
)
PY_IMPORT_PATTERN = re.compile(
    r"""^\s*(?:from\s+([a-zA-Z0-9_.]+)\s+import|import\s+([a-zA-Z0-9_.]+))"""
)

def extract_imports(line: str, ext: str):
    targets = []
    if ext in (".ts", ".js", ".tsx", ".jsx", ".mjs"):
        for m in JS_IMPORT_PATTERN.finditer(line):
            targets.append(m.group(1))
    elif ext == ".py":
        for m in PY_IMPORT_PATTERN.finditer(line):
            val = m.group(1) or m.group(2)
            if val:
                targets.append(val)
    return targets

def analyze_file(filepath: Path, base_dir: Path):
    violations = []
    
    # Extraer información de capas desde la ruta
    rel_path = filepath.relative_to(base_dir)
    parts = rel_path.parts
    
    # Esperamos estructura: src/domains/<domain>/<layer>/...
    if len(parts) >= 4 and parts[0] == "src" and parts[1] == "domains":
        domain = parts[2]
        layer = parts[3]
        
        if layer in LAYER_ORDER:
            current_level = LAYER_ORDER[layer]
            
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                
            # Validar tamaño del archivo
            if len(lines) > MAX_FILE_LINES:
                violations.append({
                    "file": str(rel_path),
                    "line": len(lines),
                    "rule": "FILE_SIZE_EXCEEDED",
                    "msg": f"El archivo tiene {len(lines)} líneas (máximo permitido: {MAX_FILE_LINES}).",
                    "remedy": f"Divide el archivo {filepath.name} en submódulos o extrae funciones helper para mantener la legibilidad del agente."
                })
                
            for idx, line in enumerate(lines, start=1):
                targets = extract_imports(line, filepath.suffix)
                for import_target in targets:
                    for target_layer, target_level in LAYER_ORDER.items():
                        layer_regex = rf"(?:^|[./\\]){target_layer}(?:$|[./\\])"
                        if re.search(layer_regex, import_target):
                            if target_level > current_level:
                                violations.append({
                                    "file": str(rel_path),
                                    "line": idx,
                                    "rule": "ILLEGAL_LAYER_DEPENDENCY",
                                    "msg": f"La capa '{layer}' (nivel {current_level}) intenta importar desde la capa superior '{target_layer}' (nivel {target_level}): {line.strip()}",
                                    "remedy": (
                                        f"REMEDIO PARA EL AGENTE: Las dependencias solo van hacia adelante: "
                                        f"types -> config -> repository -> service -> runtime -> ui. "
                                        f"No importes de '{target_layer}'. Extrae la interfaz, DTO o tipo necesario "
                                        f"a 'src/domains/{domain}/types/' e impórtalo desde allí."
                                    )
                                })
    return violations

def main():
    base_dir = Path.cwd()
    src_dir = base_dir / "src"
    
    if not src_dir.exists():
        print("[LINT OK] No se encontró directorio 'src'. Nada que validar.")
        sys.exit(0)
        
    all_violations = []
    
    for ext in ("*.ts", "*.js", "*.py", "*.go", "*.rs"):
        for filepath in src_dir.rglob(ext):
            violations = analyze_file(filepath, base_dir)
            all_violations.extend(violations)
            
    if all_violations:
        print(f"\n=======================================================")
        print(f"[ERROR] FALLO DE LINTER ESTRUCTURAL: {len(all_violations)} violación(es) detectada(s)")
        print(f"=======================================================\n")
        for v in all_violations:
            print(f"[{v['rule']}] {v['file']}:{v['line']}")
            print(f"  Detalle: {v['msg']}")
            print(f"  --> {v['remedy']}\n")
        print("Instrucción para el agente: Aplica las acciones de remediación indicadas arriba y vuelve a ejecutar este script.")
        sys.exit(1)
    else:
        print("\n[LINT OK] Todas las invariantes arquitectónicas y reglas de capas se cumplen con éxito.")
        sys.exit(0)

if __name__ == "__main__":
    main()
