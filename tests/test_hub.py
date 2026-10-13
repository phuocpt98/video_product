"""scripts/hub.py _move: một lệnh edit duy nhất, chỉ gỡ nhãn to:* đang có (gh được giả)."""
import importlib.util
import json
import pathlib

spec = importlib.util.spec_from_file_location("hub", pathlib.Path(__file__).resolve().parents[1] / "scripts/hub.py")


def load(monkeypatch, labels):
    hub = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hub)
    calls = []

    def fake_gh(*args, check=True):
        calls.append(args)
        return json.dumps({"labels": [{"name": n} for n in labels]}) if args[1] == "view" else ""

    monkeypatch.setattr(hub, "gh", fake_gh)
    return hub, calls


def test_move_single_edit(monkeypatch):
    hub, calls = load(monkeypatch, ["to:claude", "bug"])
    hub._move(7, "muse")
    edits = [c for c in calls if c[1] == "edit"]
    assert len(edits) == 1
    assert edits[0] == ("issue", "edit", "7", "--add-label", "to:muse", "--remove-label", "to:claude")


def test_move_noop_when_already_there(monkeypatch):
    hub, calls = load(monkeypatch, ["to:muse"])
    hub._move(7, "muse")
    assert not [c for c in calls if c[1] == "edit"]
