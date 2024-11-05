# PySequitur

Library for identifying and manipulating sequences of files. It is geared towards visual effects and animation related scenarios, although it can be used with any sequence of files. Emphasis on file system manipulation and flexible handing of anomalous sequences is the main differentiating feature from other similar libraries.

CLI and integration for Nuke coming soon.

Zero external dependencies make it easy to use with no privileges to modify the environment, such as in a VFX pipeline.

## Features

- **File Sequence Handling**
  - Parse and manage frame-based file sequences
  - Support for various naming conventions and patterns
  - Handle missing frames and inconsistent padding
  - Detect and manage duplicate frames

- **Flexible Component System**
  - Break down filenames into components (prefix, frame number, suffix, etc.)
  - Modify individual components while preserving others
  
- **Sequence Operations**
  - Rename entire sequences
  - Move sequences between directories
  - Delete sequences
  - Create a copy of a sequence with a new name
  - Offset frame numbers
  - Adjust or repair frame number padding

- **Validation and Problem Detection**
  - Identify missing frames
  - Detect inconsistent padding
  - Find duplicate frames
  - Validate sequence consistency

## Installation

```bash
# TODO: Add installation instructions once package is published
```

## Quick Start

```python

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

### FileSequence
Main user facing class.
Manages collections of related Items as a single unit, where Items represent single files.

```python
sequence = FileSequence.fromDirectory("/path/to/files")
print(sequence.missing_frames)    # Shows gaps in the sequence
print(sequence.frame_count)       # Total number of frames
sequence.offset_frames(10)        # Shift all frame numbers by 10
```


### Item
Generally not instantiated directly. The Parser will generate them when parsing a sequence.
Represents a single file in a sequence.

```python
item = Item.From_Path("render_001.exr")
print(item.frame_number)  # 1
print(item.padding)       # 3
item.set_frame_number(2)  # Renames file to render_002.exr
```

### Parser
Static utility class for parsing filenames and discovering sequences, from various input forms.

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

MIT

## Version History

unreleased