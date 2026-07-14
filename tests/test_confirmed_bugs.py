"""Regression tests for bugs found in the v0.2.0 review.

Each test asserts the CORRECT behaviour, so every test in this module is
expected to FAIL against the current code — they pin down confirmed bugs
before the fixes land. File/line references point at the offending code.

Run just these with:
    pytest tests/test_confirmed_bugs.py -v
"""

from pathlib import Path

import pytest

from pysequitur import (
    FileSequence,
    Item,
    SequenceBuilder,
    SequenceFactory,
)
from pysequitur.file_sequence import Components, SequenceParser
from pysequitur.shot_extractor import extract_shot_from_single_path


def _make(directory: Path, names: list[str]) -> FileSequence:
    for n in names:
        (directory / n).touch()
    return SequenceFactory.from_directory(directory)[0]


# --------------------------------------------------------------------------
# CRITICAL
# --------------------------------------------------------------------------

def test_sequence_rename_preserves_padding_when_padding_is_none(tmp_path):
    """BUG file_sequence.py:339 — Components.with_frame_number replaces
    padding=None with len(str(frame)), so FileSequence.rename destroys padding:
    render_0001.exr -> new_1.exr. None must preserve the original padding."""
    seq = _make(tmp_path, [f"render_{i:04d}.exr" for i in range(1, 4)])

    _new, plan = seq.rename(Components(prefix="new"))

    dests = [op.destination.name for op in plan.operations]
    assert dests == ["new_0001.exr", "new_0002.exr", "new_0003.exr"], dests


def test_offset_by_one_on_contiguous_sequence_has_no_conflicts(tmp_path):
    """BUG file_sequence.py:155 — would_overwrite checks the current disk and
    flags a plan's own source files as conflicts. offset_frames(1) on any
    contiguous sequence spuriously reports conflicts and requires force=True
    (which then also disables protection against real external overwrites).
    An internal-only shuffle must not be a conflict."""
    seq = _make(tmp_path, [f"a_{i:04d}.exr" for i in range(1, 4)])  # 1,2,3

    _new, plan = seq.offset_frames(1)  # -> 2,3,4 (only touches its own files)

    assert not plan.has_conflicts, [str(c) for c in plan.conflicts]


def test_two_operations_sharing_a_destination_are_detected(tmp_path):
    """BUG file_sequence.py:123 — OperationPlan.conflicts never checks whether
    two operations in the same plan target the same destination. Duplicate
    frames with different padding collapse onto one target under with_padding
    and plain execute() silently destroys a file (3 files -> 2)."""
    items = tuple(
        Item.from_file_name(n)
        for n in ("render_001.exr", "render_0001.exr", "render_002.exr")
    )
    seq = FileSequence(items)

    _new, plan = seq.with_padding(5)  # 001 & 0001 both -> render_00001.exr

    assert plan.has_conflicts, [op.destination.name for op in plan.operations]


def test_apply_surfaces_operation_failure(tmp_path):
    """BUG file_sequence.py:237 — OperationPlan.execute swallows per-op
    exceptions and ItemResult/SequenceResult.apply() discard the
    ExecutionResult, returning a 'new' sequence describing files that don't
    exist. A failed move (missing dir, create_directory=False) must surface."""
    seq = _make(tmp_path, [f"e_{i:04d}.exr" for i in range(1, 3)])
    missing_dir = tmp_path / "nope" / "deeper"

    with pytest.raises(Exception):
        seq.move(missing_dir).apply()


# --------------------------------------------------------------------------
# MEDIUM
# --------------------------------------------------------------------------

def test_sequence_delimiter_none_is_not_stringified():
    """BUG file_sequence.py:933 — FileSequence.delimiter does
    str(value) on a None consistent value, yielding the literal 'None', so
    sequence_string becomes 'renderNone####.exr'."""
    items = tuple(
        Item.from_components(Components(prefix="render", extension="exr"), n)
        for n in (1, 2)
    )
    seq = FileSequence(items)

    assert seq.delimiter != "None"
    assert "None" not in seq.sequence_string, seq.sequence_string


def test_below_min_frames_file_is_reported_as_rogue():
    """BUG file_sequence.py:1528 — groups smaller than min_frames are dropped
    from sequences but never added to rogues, so files silently vanish."""
    names = ["lonely_0001.exr", "pair_0001.exr", "pair_0002.exr"]

    result = SequenceParser.from_file_list(names, 2)

    accounted = {p.name for p in result.rogues}
    for seq in result.sequences:
        accounted |= {item.filename for item in seq.items}
    assert "lonely_0001.exr" in accounted, accounted


def test_empty_filename_does_not_crash_parser():
    """BUG file_sequence.py:1473 — the hidden-file check file[0] raises
    IndexError on an empty filename in the list."""
    result = SequenceFactory.from_filenames(["", "a_0001.exr", "a_0002.exr"])

    assert [s.sequence_string for s in result] == ["a_####.exr"]


def test_shot_extractor_does_not_mistake_version_for_shot():
    """BUG shot_extractor.py:33 — the (?<!v)\\d+ lookbehind only guards the
    first digit, so a version like v25 leaks '5' as the shot number. A path
    with only a version and no shot must not return version digits."""
    shot, _ = extract_shot_from_single_path("/show/seq/render_v25/final.exr")

    assert shot == "000", shot


def test_case_only_rename_is_not_a_false_conflict(tmp_path):
    """BUG file_sequence.py:557 — on a case-insensitive filesystem (macOS)
    would_overwrite treats the item's own file as an existing destination, so
    a case-only rename is falsely flagged and refuses to execute."""
    seq = _make(tmp_path, ["shot_1001.exr", "shot_1002.exr"])  # pad==len -> isolated

    _new, plan = seq.rename(Components(prefix="SHOT"))

    assert not plan.has_conflicts, [str(c) for c in plan.conflicts]
    plan.execute()
    assert (tmp_path / "SHOT_1001.exr").exists()


# --------------------------------------------------------------------------
# LOW
# --------------------------------------------------------------------------

def test_empty_slice_result_repr_does_not_raise(tmp_path):
    """BUG file_sequence.py:773 — __repr__ calls first_frame/last_frame which
    raise on an empty sequence, so printing an out-of-range slice crashes."""
    seq = _make(tmp_path, [f"b_{i:04d}.exr" for i in range(1, 4)])

    empty = seq[1000:1005]  # no such frames -> empty FileSequence

    repr(empty)  # must not raise


def test_negative_frame_number_is_rejected():
    """BUG file_sequence.py:730 — rename(Components(frame_number=-5)) bypasses
    validation and yields render_-005.exr, which reparses as frame 5 with a
    '-' delimiter. A negative frame number is invalid and must be rejected."""
    item = Item.from_file_name("render_0005.exr")

    with pytest.raises(ValueError):
        item.rename(Components(frame_number=-5))


def test_builder_delete_then_execute_actually_deletes(tmp_path):
    """BUG file_sequence.py:1915 — SequenceBuilder.delete() returns a detached
    OperationPlan instead of recording the deletion on the builder, so a
    subsequent builder.execute() silently skips it and reports success."""
    seq = _make(tmp_path, [f"c_{i:04d}.exr" for i in range(1, 4)])

    builder = SequenceBuilder(seq)
    builder.delete()
    builder.execute()

    remaining = sorted(p.name for p in tmp_path.iterdir())
    assert remaining == [], remaining
