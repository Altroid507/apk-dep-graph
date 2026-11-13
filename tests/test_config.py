"""Тесты загрузчика CSV-конфигурации."""

import pytest

from config import load_config
from errors import ConfigError


def _write(tmp_path, content):
    """Записать тестовый CSV-файл."""
    path = tmp_path / "cfg.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_valid_config(tmp_path):
    """Корректный CSV разбирается в Config."""
    path = _write(tmp_path, (
        "package,musl\n"
        "repository,https://example.org/main\n"
        "test_mode,true\n"
        "package_version,1.2.5-r0\n"
        "output_image,out.svg\n"
        "ascii_tree,yes\n"
        "max_depth,3\n"
    ))
    cfg = load_config(path)
    assert cfg.package == "musl"
    assert cfg.test_mode is True
    assert cfg.ascii_tree is True
    assert cfg.max_depth == 3


def test_unknown_key_raises(tmp_path):
    """Неизвестный ключ — ошибка конфигурации."""
    path = _write(tmp_path, (
        "package,musl\nrepository,https://x\n"
        "package_version,1\nbogus,1\n"
    ))
    with pytest.raises(ConfigError):
        load_config(path)


def test_invalid_depth_raises(tmp_path):
    """max_depth вне диапазона — ошибка."""
    path = _write(tmp_path, (
        "package,musl\nrepository,https://x\n"
        "package_version,1\nmax_depth,-3\n"
    ))
    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_package_raises(tmp_path):
    """Пустой package — ошибка."""
    path = _write(tmp_path, "repository,https://x\npackage_version,1\n")
    with pytest.raises(ConfigError):
        load_config(path)


def test_invalid_bool_raises(tmp_path):
    """Некорректный булев флаг — ошибка."""
    path = _write(tmp_path, (
        "package,musl\nrepository,https://x\n"
        "package_version,1\ntest_mode,maybe\n"
    ))
    with pytest.raises(ConfigError):
        load_config(path)