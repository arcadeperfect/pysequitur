from pysequitur.file_sequence import FileSequence
from pathlib import Path

# Import the Node class for recursive scanning
from pysequitur.crawl import Node


def collect_sequences(node):
    """Helper function to collect all sequences from a Node and its children recursively."""
    sequences = list(node.sequences)
    for child_node in node.nodes:
        sequences.extend(collect_sequences(child_node))
    return sequences


def test_recursive_scanner(parse_recursive_scanner_yaml):
    """
    Test the recursive scanner functionality to find sequences in nested directories.
    """
    test_env = parse_recursive_scanner_yaml()

    for env in test_env:
        print("\n\n\n\n")

        # Get the root test directory
        # test_dir = env["test_dir"] / "sequences"

        root_node = Node(env["test_dir"])

        

        # Collect all sequences from the node tree
        # sequences = collect_sequences(root_node)

        # # Validate results
        # # These are expected sequences in our directory structure
        # expected_sequences = {
        #     "/sequences/renders/shot01/comp.v001.####.exr": {
        #         "prefix": "comp.v001",
        #         "extension": "exr",
        #         "padding": 4,
        #         "frame_count": 5,
        #     },
        #     "/sequences/renders/shot01/matte_###_beauty.tif": {
        #         "prefix": "matte",
        #         "extension": "tif",
        #         "padding": 3,
        #         "frame_count": 3,
        #     },
        #     "/sequences/renders/shot03/passes/beauty/render-####.dpx": {
        #         "prefix": "render",
        #         "extension": "dpx",
        #         "padding": 4,
        #         "frame_count": 4,
        #         "missing_frames": [3],
        #     },
        #     "/sequences/archives/2023/january/project/sequence.####.mov": {
        #         "prefix": "sequence",
        #         "extension": "mov",
        #         "padding": 4,
        #         "frame_count": 3,
        #     },
        #     "/sequences/client/2023/q1/january/revision3/shot04/comp/v002/final/comp.####.exr": {
        #         "prefix": "comp",
        #         "extension": "exr",
        #         "padding": 4,
        #         "frame_count": 3,
        #     },
        #     "/sequences/special/frame_####_overlay.exr": {
        #         "prefix": "frame",
        #         "suffix": "_overlay",
        #         "extension": "exr",
        #         "padding": 4,
        #         "frame_count": 3,
        #     },
        #     "/sequences/special/frame.####.iff": {
        #         "prefix": "frame",
        #         "extension": "iff",
        #         "padding": 4,
        #         "frame_count": 3,
        #     },
        # }

        # # Check that we found at least the expected number of sequences
        # # Note: The mixed padding sequence might be detected differently depending on implementation
        # assert len(sequences) >= 7, (
        #     f"Expected at least 7 sequences, found {len(sequences)}"
        # )

        # # Verify each sequence was found with correct properties
        # for seq in sequences:
        #     # Convert path to string for comparison
        #     seq_path = str(seq.directory)

        #     # Check if this sequence matches any of our expected ones
        #     for path_pattern, props in expected_sequences.items():
        #         # Extract the directory part from the path pattern
        #         expected_dir = str(Path(path_pattern).parent)

        #         # Check if this sequence matches this expected sequence
        #         if (
        #             seq_path.endswith(expected_dir)
        #             and seq.prefix == props["prefix"]
        #             and seq.extension == props["extension"]
        #         ):
        #             # Found a match, verify its properties
        #             assert seq.padding == props["padding"], (
        #                 f"Expected padding {props['padding']}, got {seq.padding}"
        #             )
        #             assert seq.frame_count == props["frame_count"], (
        #                 f"Expected {props['frame_count']} frames, got {seq.frame_count}"
        #             )

        #             # Check for missing frames if applicable
        #             if "missing_frames" in props:
        #                 for missing in props["missing_frames"]:
        #                     assert missing in seq.missing_frames, (
        #                         f"Expected frame {missing} to be missing"
        #                     )

        #             # Mark this expected sequence as found
        #             expected_sequences[path_pattern]["found"] = True
        #             break

        # # Make sure all expected sequences were found
        # missing_sequences = [
        #     path
        #     for path, props in expected_sequences.items()
        #     if not props.get("found", False)
        # ]
        # assert not missing_sequences, (
        #     f"Failed to find expected sequences: {missing_sequences}"
        # )

        # # Test the single-frame "sequence" case - should not be considered a sequence
        # single_frame_sequences = [
        #     s for s in sequences if str(s.directory).endswith("shot02")
        # ]
        # assert len(single_frame_sequences) == 0, (
        #     "Single frame should not be detected as a sequence"
        # )

        # # The mixed padding case is complex and depends on implementation
        # # Check that we handle the mixed padding case - this test might need adjustment
        # mixed_padding_dir = test_dir / "renders" / "shot03" / "passes" / "diffuse"
        # mixed_sequences = [
        #     s for s in sequences if str(s.directory) == str(mixed_padding_dir)
        # ]

        # # Depending on implementation, this could be one or two sequences
        # if len(mixed_sequences) == 1:
        #     # If detected as one sequence, should have the larger padding
        #     assert mixed_sequences[0].padding == 4
        # elif len(mixed_sequences) == 2:
        #     # If detected as two sequences, should have different paddings
        #     paddings = [s.padding for s in mixed_sequences]
        #     assert sorted(paddings) == [3, 4]
