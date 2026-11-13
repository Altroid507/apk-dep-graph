"""Тесты вспомогательных функций парсера APKINDEX."""

from apk_parser import (
    _parse_record,
    _split_records,
    _strip_version_constraint,
)


def test_split_and_parse_record():
    """Запись корректно делится и парсится."""
    text = "P:musl\nV:1.2.5-r0\nD:libc\n\nP:busybox\nV:1.36\n"
    records = _split_records(text)
    parsed = _parse_record(records[0])
    assert parsed["P"] == "musl"
    assert parsed["D"] == "libc"


def test_strip_version_constraint():
    """Версионные ограничения удаляются."""
    assert _strip_version_constraint("musl=1.2") == "musl"
    assert _strip_version_constraint("musl>1.0") == "musl"
    assert _strip_version_constraint("musl~1.2.3") == "musl"