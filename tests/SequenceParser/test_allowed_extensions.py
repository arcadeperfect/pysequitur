from pysequitur.file_sequence import SequenceParser


def test_allowed_extensions(parse_sequence_yaml):
    """Test sequence parsing for both unlinked and linked sequences"""
    test_env_list = parse_sequence_yaml()

    for case in test_env_list:
        allowed_extensions = ["dpx", "tif", "exr"]

        sequences = SequenceParser.from_file_list(
            case["files"], 2, allowed_extensions=allowed_extensions
        ).sequences

        assert len(sequences) <= 1, (
            f"Expected 1 sequence but found {len(sequences)}. {error_context}"  # noqa: F821 # type: ignore
        )

        print(case["extension"])

        if case["extension"] in allowed_extensions:
            print(f"extension {case['extension']} was allowed")
            assert len(sequences) == 1
        else:
            print(f"extension {case['extension']} was not allowed")
            assert len(sequences) == 0

    for case in test_env_list:
        allowed_extensions = ["exr"]

        sequences = SequenceParser.from_file_list(
            case["files"], 2, allowed_extensions=allowed_extensions
        ).sequences

        assert len(sequences) <= 1, (
            f"Expected 1 sequence but found {len(sequences)}. {error_context}"  # noqa: F821 # type: ignore
        )

        print(case["extension"])

        if case["extension"] in allowed_extensions:
            print(f"extension {case['extension']} was allowed")
            assert len(sequences) == 1
        else:
            print(f"extension {case['extension']} was not allowed")
            assert len(sequences) == 0

    for case in test_env_list:
        allowed_extensions = ["jpg"]

        sequences = SequenceParser.from_file_list(
            case["files"], 2, allowed_extensions=allowed_extensions
        ).sequences

        assert len(sequences) <= 1, (
            f"Expected 1 sequence but found {len(sequences)}. {error_context}"  # noqa: F821 # type: ignore
        )

        print(case["extension"])

        if case["extension"] in allowed_extensions:
            print(f"extension {case['extension']} was allowed")
            assert len(sequences) == 1
        else:
            print(f"extension {case['extension']} was not allowed")
            assert len(sequences) == 0

    for case in test_env_list:
        allowed_extensions = ["JPG", ".exr", ".DPX"]

        sequences = SequenceParser.from_file_list(
            case["files"], 2, allowed_extensions=allowed_extensions
        ).sequences

        assert len(sequences) <= 1, (
            f"Expected 1 sequence but found {len(sequences)}. {error_context}"  # noqa: F821 # type: ignore
        )

        print(case["extension"])

        if case["extension"].lower().lstrip(".") in [
            ext.lower().lstrip(".") for ext in allowed_extensions
        ]:
            print(f"extension {case['extension']} was allowed")
            assert len(sequences) == 1
        else:
            print(f"extension {case['extension']} was not allowed")
            assert len(sequences) == 0
