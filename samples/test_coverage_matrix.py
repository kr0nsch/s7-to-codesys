"""Матрица покрытия в samples/scl/README.md соответствует корпусу; базовые свойства корпуса."""

from __future__ import annotations

import os
import re

import coverage_matrix


def test_readme_matrix_is_up_to_date() -> None:
    assert coverage_matrix.main(["--check"]) == 0, "python samples/coverage_matrix.py --write"


def test_corpus_size_and_encoding() -> None:
    names = sorted(n for n in os.listdir(coverage_matrix.SCL_DIR) if n.endswith(".scl"))
    assert 15 <= len(names) <= 20
    assert names == sorted(name for _, name in coverage_matrix.FILES)
    for name in names:
        with open(os.path.join(coverage_matrix.SCL_DIR, name), "rb") as fh:
            data = fh.read()
        assert not data.startswith(b"\xef\xbb\xbf") and b"\r" not in data and b"\t" not in data, name
        text = data.decode("utf-8")
        assert text.startswith("// ===="), f"{name}: файл начинается с комментария-описания"
        # идентификаторы ASCII: кириллица допустима только в комментариях и строках
        for line in text.split("\n"):
            code = re.sub(r"'[^']*'", "''", line.split("//", 1)[0])
            assert code.isascii(), f"{name}: не-ASCII вне комментария: {line!r}"
