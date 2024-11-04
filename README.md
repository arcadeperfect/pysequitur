# File Sequence Management Library

A Python library for managing frame-based file sequences commonly used in visual effects, animation, and media pipelines. This library provides robust tools for parsing, analyzing, and manipulating file sequences with features like frame number management, sequence validation, and batch operations.

## Features

- **Comprehensive File Sequence Handling**
  - Parse and manage frame-based file sequences
  - Support for various naming conventions and patterns
  - Handle missing frames and inconsistent padding
  - Detect and manage duplicate frames

- **Flexible Component System**
  - Break down filenames into components (prefix, frame number, suffix, etc.)
  - Modify individual components while preserving others
  - Support for compound file extensions (e.g., tar.gz)

- **Sequence Operations**
  - Rename entire sequences
  - Move sequences between directories
  - Copy sequences with new names
  - Offset frame numbers
  - Adjust frame number padding

- **Validation and Problem Detection**
  - Identify missing frames
  - Detect inconsistent padding
  - Find duplicate frames
  - Check for filename spaces
  - Validate sequence consistency

## Installation

```bash
# TODO: Add installation instructions once package is published
```

## Quick Start

```python
# Create an Item from a single file
item = Item.From_Path("render_001.exr")

# Parse sequences from a directory
sequences = Parser.scan_directory("/path/to/files")

# Create a sequence from a list of files
file_list = ["render_001.exr", "render_002.exr", "render_003.exr"]
sequence = FileSequence.fromFileList(file_list)

# Basic sequence operations
sequence.move("/new/directory")
sequence.rename("new_name")
sequence.offset_frames(100)  # Shift all frame numbers by 100
```

## Core Classes

### Item
Represents a single file in a sequence, managing components like prefix, frame number, and extension.

```python
item = Item.From_Path("render_001.exr")
print(item.frame_number)  # 1
print(item.padding)       # 3
item.set_frame_number(2)  # Renames file to render_002.exr
```

### FileSequence
Manages collections of related Items as a single unit.

```python
sequence = FileSequence.fromDirectory("/path/to/files")
print(sequence.missing_frames)    # Shows gaps in the sequence
print(sequence.frame_count)       # Total number of frames
sequence.offset_frames(10)        # Shift all frame numbers by 10
```

### Parser
Static utility class for parsing filenames and discovering sequences.

```python
# Parse a single filename
item = Parser.parse_filename("render_001.exr")

# Find sequences in a directory
sequences = Parser.scan_directory("/path/to/files")

# Match specific components
components = Components(prefix="render", extension="exr")
matches = Parser.match_components(components, file_list)
```

### Components
Configuration class for specifying filename components during operations.

```python
components = Components(
    prefix="new_name",
    delimiter="_",
    padding=4,
    suffix="v1",
    extension="exr"
)
```

## File Naming Convention

The library parses filenames into the following components:
```
<prefix><delimiter><frame><suffix>.<extension>
```

Example: `render_001_final.exr`
- prefix: "render"
- delimiter: "_"
- frame: "001"
- suffix: "_final"
- extension: "exr"

## Problem Detection

The library can identify various issues in sequences:

```python
problems = sequence.problems
if Problems.MISSING_FRAMES in problems:
    print("Sequence has gaps")
if Problems.INCONSISTENT_PADDING in problems:
    print("Frame numbers have inconsistent padding")
```

## Error Handling

The library includes custom error types for specific scenarios:

- `AnomalousItemDataError`: Raised when inconsistent data is found in a sequence
- `FileNotFoundError`: Raised when attempting operations on non-existent files
- `ValueError`: Raised for invalid inputs or operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

TODO: Add license information

## Version History

TODO: Add version history once released