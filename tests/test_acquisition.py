"""
Smoke tests for src/acquisition/download_source.py.

No network access. Verifies the module imports and exposes the
public callable with the expected signature.
"""

from __future__ import annotations

import inspect

import pytest

from src.acquisition import download_source


def test_module_imports() -> None:
    assert download_source is not None


def test_download_file_callable_exists() -> None:
    assert hasattr(download_source, "download_file")
    assert callable(download_source.download_file)


def test_download_file_signature() -> None:
    sig = inspect.signature(download_source.download_file)
    params = list(sig.parameters)
    assert params[:2] == ["url", "output_path"], (
        f"Unexpected signature: {sig}"
    )


def test_download_file_rejects_bad_url_without_network(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """
    Confirm the function does not silently succeed when the HTTP layer
    raises. We replace requests.get with a stub that raises immediately,
    so no real network call is made.
    """
    class _Boom(Exception):
        pass

    def _fake_get(*_args, **_kwargs):
        raise _Boom("stubbed network failure")

    monkeypatch.setattr(download_source.requests, "get", _fake_get)

    with pytest.raises(Exception) as exc_info:
        download_source.download_file(
            "https://example.invalid/x", tmp_path / "out.bin"
        )
    assert isinstance(exc_info.value, _Boom)
