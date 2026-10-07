"""Exercise the actual quality-gate script embedded in the workflow."""
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/cicd.yml"


@pytest.mark.parametrize("value,passes", [
    ("0.6499", False), ("0.65", True), ("0.9", True),
    ("nan", False), ("inf", False), ("1.1", False), ("", False),
])
def test_quality_gate(value, passes):
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8-sig"))
    command = workflow["jobs"]["quality-gate"]["steps"][0]["run"]
    script = command.split("\n", 1)[1].rsplit("PYEOF", 1)[0]
    result = subprocess.run([sys.executable, "-c", script],
                            env={**os.environ, "MODEL_F1": value}, capture_output=True)
    assert (result.returncode == 0) == passes


def test_release_depends_on_quality_gate():
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8-sig"))
    assert workflow["jobs"]["train"]["needs"] == "unit-test"
    assert workflow["jobs"]["quality-gate"]["needs"] == "train"
    assert workflow["jobs"]["release"]["needs"] == "quality-gate"
