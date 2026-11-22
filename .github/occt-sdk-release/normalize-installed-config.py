#!/usr/bin/env python3
import pathlib
import re
import sys


TRUE_IF_RE = re.compile(r"^\s*if\s*\(\s*TRUE\s*\)\s*$", re.IGNORECASE)
IF_RE = re.compile(r"^\s*if\s*\(", re.IGNORECASE)
ELSE_RE = re.compile(r"^\s*else\s*(?:\([^)]*\))?\s*$", re.IGNORECASE)
ENDIF_RE = re.compile(r"^\s*endif\s*(?:\([^)]*\))?\s*$", re.IGNORECASE)


def find_branch(lines, start):
    depth = 0
    else_index = None
    for index in range(start, len(lines)):
        line = lines[index]
        if ENDIF_RE.match(line):
            depth -= 1
            if depth == 0:
                if else_index is None:
                    raise RuntimeError("constant-TRUE branch has no else() arm")
                return else_index, index
            if depth < 0:
                break
        elif IF_RE.match(line):
            depth += 1
        elif depth == 1 and ELSE_RE.match(line):
            if else_index is not None:
                raise RuntimeError("constant-TRUE branch has multiple top-level else() arms")
            else_index = index
    raise RuntimeError("constant-TRUE branch has no matching endif()")


def normalize(path):
    with path.open("r", encoding="utf-8", newline=None) as stream:
        text = stream.read()
    lines = text.splitlines(keepends=True)

    matches = []
    for start, line in enumerate(lines):
        if not TRUE_IF_RE.match(line):
            continue
        lookahead = "".join(lines[start + 1 : start + 80])
        if "PACKAGE_PREFIX_DIR" not in lookahead or "OpenCASCADE_INSTALL_PREFIX" not in lookahead:
            continue
        else_index, end_index = find_branch(lines, start)
        install_branch = "".join(lines[start + 1 : else_index])
        build_branch = "".join(lines[else_index + 1 : end_index])
        if (
            "PACKAGE_PREFIX_DIR" in install_branch
            and "OpenCASCADE_INSTALL_PREFIX" in install_branch
            and "OpenCASCADE_INSTALL_PREFIX" in build_branch
        ):
            matches.append((start, else_index, end_index))

    if not matches:
        print(f"no dead build-tree branch found in {path}")
        return
    if len(matches) != 1:
        raise RuntimeError(f"expected one installed-package branch in {path}, found {len(matches)}")

    start, else_index, end_index = matches[0]
    normalized = "".join(lines[:start] + lines[start + 1 : else_index] + lines[end_index + 1 :])
    if normalized == text:
        raise RuntimeError(f"normalization did not change {path}")
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(normalized)
    print(f"removed unreachable build-tree branch from {path}")


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <OpenCASCADEConfig.cmake>", file=sys.stderr)
        return 2
    path = pathlib.Path(sys.argv[1])
    if not path.is_file():
        print(f"missing OpenCASCADEConfig.cmake: {path}", file=sys.stderr)
        return 1
    try:
        normalize(path)
    except (OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
