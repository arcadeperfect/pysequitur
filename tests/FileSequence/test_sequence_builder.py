"""Tests for SequenceBuilder fluent API."""

import pytest
from pathlib import Path
from pysequitur import Item, FileSequence, Components, SequenceBuilder, SequenceResult, OperationPlan


class TestSequenceBuilderBasics:
    """Test basic initialization and properties."""

    def test_initialization(self, tmp_path):
        """Builder initializes with sequence and empty plan."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        files = []
        for i in range(1001, 1004):
            f = original_dir / f"test.{i:04d}.exr"
            f.touch()
            files.append(f)

        items = tuple(Item.from_path(f) for f in files)
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)

        assert builder.current_sequence is sequence
        assert isinstance(builder.plan, OperationPlan)
        assert len(builder.plan.operations) == 0

    def test_current_sequence_property(self, tmp_path):
        """current_sequence reflects state after operations."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1004):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in original_dir.glob("*.exr"))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        builder.rename(Components.build().with_prefix("renamed"))

        # current_sequence should reflect the rename
        assert builder.current_sequence.prefix == "renamed"
        assert builder.current_sequence is not sequence

    def test_plan_property_accumulates(self, tmp_path):
        """plan accumulates operations from multiple calls."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        initial_ops = len(builder.plan.operations)

        builder.rename(Components.build().with_prefix("step1"))
        after_rename = len(builder.plan.operations)

        builder.with_padding(6)
        after_padding = len(builder.plan.operations)

        assert initial_ops == 0
        assert after_rename == 2  # 2 files renamed
        assert after_padding == 4  # 2 more padding changes


class TestSequenceBuilderChaining:
    """Test fluent method chaining."""

    def test_rename_returns_self(self, tmp_path):
        """rename() returns the builder for chaining."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        result = builder.rename(Components.build().with_prefix("new"))

        assert result is builder

    def test_move_returns_self(self, tmp_path):
        """move() returns the builder for chaining."""
        original_dir = tmp_path / "original"
        target_dir = tmp_path / "target"
        original_dir.mkdir()
        target_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        result = builder.move(target_dir)

        assert result is builder

    def test_copy_returns_self(self, tmp_path):
        """copy() returns the builder for chaining."""
        original_dir = tmp_path / "original"
        target_dir = tmp_path / "target"
        original_dir.mkdir()
        target_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        result = builder.copy(new_directory=target_dir)

        assert result is builder

    def test_offset_frames_returns_self(self, tmp_path):
        """offset_frames() returns the builder for chaining."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        result = builder.offset_frames(1000)

        assert result is builder

    def test_with_padding_returns_self(self, tmp_path):
        """with_padding() returns the builder for chaining."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        result = builder.with_padding(6)

        assert result is builder

    def test_folderize_returns_self(self, tmp_path):
        """folderize() returns the builder for chaining."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        result = builder.folderize("subfolder")

        assert result is builder

    def test_full_chain(self, tmp_path):
        """Multiple operations can be chained fluently."""
        original_dir = tmp_path / "original"
        target_dir = tmp_path / "target"
        original_dir.mkdir()
        target_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        # Chain multiple operations
        result = (
            SequenceBuilder(sequence)
            .rename(Components.build().with_prefix("shot_010"))
            .offset_frames(1000)
            .with_padding(6)
            .build()
        )

        assert isinstance(result, SequenceResult)
        assert result.sequence.prefix == "shot_010"
        assert result.sequence.first_frame == 2001
        assert result.sequence.padding == 6


class TestSequenceBuilderBuild:
    """Test build() method."""

    def test_build_returns_sequence_result(self, tmp_path):
        """build() returns a SequenceResult with sequence and plan."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        builder.rename(Components.build().with_prefix("new"))

        result = builder.build()

        assert isinstance(result, SequenceResult)
        assert result.sequence.prefix == "new"
        assert len(result.plan.operations) == 2

    def test_build_without_operations(self, tmp_path):
        """build() with no operations returns empty plan."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        result = builder.build()

        assert result.sequence is sequence
        assert len(result.plan.operations) == 0


class TestSequenceBuilderExecute:
    """Test execute() method."""

    def test_execute_performs_operations(self, tmp_path):
        """execute() performs all accumulated operations."""
        original_dir = tmp_path / "original"
        target_dir = tmp_path / "target"
        original_dir.mkdir()
        target_dir.mkdir()

        files = []
        for i in range(1001, 1004):
            f = original_dir / f"test.{i:04d}.exr"
            f.touch()
            files.append(f)

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        # Build and execute a rename + move
        result = (
            SequenceBuilder(sequence)
            .rename(Components.build().with_prefix("final"))
            .move(target_dir)
            .execute()
        )

        assert result.success
        # Original files should be gone
        assert not any(f.exists() for f in files)
        # New files should exist in target
        assert (target_dir / "final.1001.exr").exists()
        assert (target_dir / "final.1002.exr").exists()
        assert (target_dir / "final.1003.exr").exists()

    def test_execute_returns_execution_result(self, tmp_path):
        """execute() returns ExecutionResult."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        builder.with_padding(6)

        result = builder.execute()

        from pysequitur import ExecutionResult
        assert isinstance(result, ExecutionResult)


class TestSequenceBuilderDelete:
    """Test delete() terminal operation."""

    def test_delete_returns_operation_plan(self, tmp_path):
        """delete() returns OperationPlan, not builder."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        result = builder.delete()

        assert isinstance(result, OperationPlan)
        assert not isinstance(result, SequenceBuilder)

    def test_delete_includes_accumulated_operations(self, tmp_path):
        """delete() includes prior accumulated operations."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        # Rename then delete
        builder = SequenceBuilder(sequence)
        builder.rename(Components.build().with_prefix("renamed"))
        plan = builder.delete()

        # Plan should include rename ops + delete ops
        # 2 rename operations + 2 delete operations = 4 total
        assert len(plan.operations) == 4

    def test_delete_executes_correctly(self, tmp_path):
        """delete() plan can be executed to delete files."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        files = []
        for i in range(1001, 1003):
            f = original_dir / f"test.{i:04d}.exr"
            f.touch()
            files.append(f)

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        # Just delete without other operations
        plan = SequenceBuilder(sequence).delete()
        plan.execute()

        assert not any(f.exists() for f in files)


class TestSequenceBuilderCopyBehavior:
    """Test copy() operation behavior in builder."""

    def test_copy_continues_with_destination(self, tmp_path):
        """After copy(), builder tracks the copy destination."""
        original_dir = tmp_path / "original"
        target_dir = tmp_path / "target"
        original_dir.mkdir()
        target_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        builder.copy(new_directory=target_dir)

        # current_sequence should now point to target directory
        assert builder.current_sequence.directory == target_dir

    def test_copy_then_rename(self, tmp_path):
        """copy() followed by rename() affects the copy, not original."""
        original_dir = tmp_path / "original"
        target_dir = tmp_path / "target"
        original_dir.mkdir()
        target_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        result = (
            SequenceBuilder(sequence)
            .copy(new_directory=target_dir)
            .rename(Components.build().with_prefix("copied"))
            .build()
        )

        # The final sequence should be renamed copies in target
        assert result.sequence.prefix == "copied"
        assert result.sequence.directory == target_dir


class TestSequenceBuilderConflicts:
    """Test conflict detection in accumulated plan."""

    def test_plan_has_conflicts_property(self, tmp_path):
        """Accumulated plan exposes has_conflicts."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        # Create a file that would conflict
        (original_dir / "conflict.1001.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("test.*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        builder.rename(Components.build().with_prefix("conflict"))

        # Should detect conflict with existing conflict.1001.exr
        assert builder.plan.has_conflicts

    def test_plan_conflicts_property(self, tmp_path):
        """Accumulated plan exposes conflicts list."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        # Create conflicting files
        (original_dir / "conflict.1001.exr").touch()
        (original_dir / "conflict.1002.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("test.*.exr")))
        sequence = FileSequence(items)

        builder = SequenceBuilder(sequence)
        builder.rename(Components.build().with_prefix("conflict"))

        assert len(builder.plan.conflicts) == 2


class TestSequenceBuilderMultipleOperations:
    """Test complex multi-operation workflows."""

    def test_rename_offset_move(self, tmp_path):
        """Complex workflow: rename -> offset -> move."""
        original_dir = tmp_path / "original"
        target_dir = tmp_path / "final"
        original_dir.mkdir()
        target_dir.mkdir()

        for i in range(1001, 1004):
            (original_dir / f"plate.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        result = (
            SequenceBuilder(sequence)
            .rename(Components.build().with_prefix("shot_010_comp"))
            .offset_frames(1000)
            .move(target_dir)
            .build()
        )

        # Verify projected state
        assert result.sequence.prefix == "shot_010_comp"
        assert result.sequence.first_frame == 2001
        assert result.sequence.last_frame == 2003
        assert result.sequence.directory == target_dir

        # Execute and verify files
        result.plan.execute()
        assert (target_dir / "shot_010_comp.2001.exr").exists()
        assert (target_dir / "shot_010_comp.2002.exr").exists()
        assert (target_dir / "shot_010_comp.2003.exr").exists()

    def test_copy_with_new_name_and_padding(self, tmp_path):
        """Workflow: copy with new name and different padding."""
        original_dir = tmp_path / "original"
        archive_dir = tmp_path / "archive"
        original_dir.mkdir()
        archive_dir.mkdir()

        for i in range(1, 4):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        result = (
            SequenceBuilder(sequence)
            .copy(
                new_name=Components.build().with_prefix("backup"),
                new_directory=archive_dir
            )
            .with_padding(6)
            .build()
        )

        # Verify projected state
        assert result.sequence.prefix == "backup"
        assert result.sequence.padding == 6
        assert result.sequence.directory == archive_dir

        # Execute
        result.plan.execute()

        # Originals should still exist
        assert (original_dir / "test.0001.exr").exists()
        # Copies should exist with new name and padding
        assert (archive_dir / "backup.000001.exr").exists()
        assert (archive_dir / "backup.000002.exr").exists()
        assert (archive_dir / "backup.000003.exr").exists()

    def test_folderize_and_rename(self, tmp_path):
        """Workflow: folderize then rename."""
        original_dir = tmp_path / "original"
        original_dir.mkdir()

        for i in range(1001, 1003):
            (original_dir / f"test.{i:04d}.exr").touch()

        items = tuple(Item.from_path(f) for f in sorted(original_dir.glob("*.exr")))
        sequence = FileSequence(items)

        result = (
            SequenceBuilder(sequence)
            .folderize("organized")
            .rename(Components.build().with_prefix("final"))
            .build()
        )

        # Verify projected state
        assert result.sequence.prefix == "final"
        assert result.sequence.directory == original_dir / "organized"

        # Execute
        result.plan.execute()

        assert (original_dir / "organized" / "final.1001.exr").exists()
        assert (original_dir / "organized" / "final.1002.exr").exists()

