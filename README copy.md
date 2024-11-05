# PySequitur

Library for identifying and manipulating sequences of files. It is geared towards visual effects and animation related scenarios, although it can be used with any sequence of files. Emphasis on file system manipulation and flexible handing of anomalous sequences is the main differentiating feature from other similar libraries.

CLI and integration for Nuke coming soon.

No external dependencies, easy to use in VFX pipeline with no privileges.

## Features

- **File Sequence Handling**
  - Parse and manage frame-based file sequences
  - Support for many naming conventions and patterns
  - Handle missing or duplicate frames, inconsistent padding



- **Flexible Component System**
  - Parse filenames into components (prefix, delimiter, frame number, suffix, extension)
  - Modify individual components while preserving others
  - Match sequences against optionally specified components
  
- **Sequence Operations**
  - Rename sequences
  - Move sequences around
  - Delete sequences
  - Copy sequences
  - Offset frame numbers
  - Adjust or repair frame number padding

## Installation

```bash
# TODO: Add installation instructions once package is published
```

## Quick Start

```python

# Parse sequences from a directory

sequences = FileSequence.from_directory("/path/to/files")

# Create a virtual sequence from a list of file names

file_list = ["render_001.exr", "render_002.exr", "render_003.exr"]
sequence = FileSequence.from_file_list(file_list)

# Basic sequence operations

sequence.move("/new/directory")
sequence.rename("new_name")
sequence.offset_frames(100)  # Shift all frame numbers by 100
sequence.delete()
new_sequence = sequence.copy("/new/directory")

# Advanced rename operations

print(sequence.file_name) # -> "file.###.jpeg" 

sequence.rename(Components(prefix="image"))
print(sequence.file_name) # -> "image.###.jpeg"

sequence.rename(Components(delimiter="_", padding=5, extension="jpg"))
print(sequence.file_name) # -> "image_#####.jpg"
```

## Core Classes

### Components

Configuration class for specifying filename components during operations. Any parameter can be None.

```python
components = Components(
    prefix="file_name",
    delimiter=".",
    padding=4,
    suffix="_final",
    extension="exr"
)
```
Equals: "file_name.####_final.exr"


### FileSequence
Main class.
Manages collections of related Items as a single unit, where Items represent single files.

---
#### Parse list of FileSequences from directory:
```python
sequences = FileSequence.from_directory("/path/to/files")
```
Returns all valid sequences in the directory

---

#### Match FileSequences against components:
```python
my_components = Components(prefix="image", extension="exr")
sequences = FileSequence.from_components_in_directory(my_components, "/path/to/files")
```
Returns all sequences with prefix "image" and extension "exr"

---
#### Match FileSequence against a single sequence filename 

```python
sequence = FileSequence.from_sequence_filename_in_directory("image.####_final.exr", "/path/to/files")
```
Returns exactly one sequence that matches "image.####_final.exr"

---



# File Naming Convention

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