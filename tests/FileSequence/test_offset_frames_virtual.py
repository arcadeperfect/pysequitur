import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_offset_frames_virtual(tmp_path):
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence(items)

    # # Test positive offset virtual
    virtual_sequence = sequence.offset_frames(10, virtual=True)

    # # Assert virtual_sequence is a new instance
    assert virtual_sequence is not sequence

    # # Assert virtual sequence has correct frame numbers
    assert all(
        item.frame_number == i
        for item, i in zip(virtual_sequence.items, range(1011, 1014))
    )

    # Assert original sequence is unchanged
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1001, 1004))
    )

    # Assert original files still exist and haven't been renamed
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    assert not any(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1011, 1014)
    )

    # Test negative offset virtual
    virtual_sequence = sequence.offset_frames(-10, virtual=True)

    # Assert virtual sequence has correct frame numbers
    assert all(
        item.frame_number == i
        for item, i in zip(virtual_sequence.items, range(991, 994))
    )

    # Assert original sequence and files still unchanged
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1001, 1004))
    )
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))

    # Test that other properties are preserved in virtual sequence
    for orig_item, virtual_item in zip(sequence.items, virtual_sequence.items):
        assert virtual_item.prefix == orig_item.prefix
        assert virtual_item.extension == orig_item.extension
        assert virtual_item.padding == orig_item.padding
        assert virtual_item.directory == orig_item.directory

    # Test error on negative frames
    with pytest.raises(ValueError):
        sequence.offset_frames(
            -1002, virtual=True
        )  # Would result in negative frame numbers
