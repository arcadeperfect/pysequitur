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
from pathlib import Path
from pysequitur import FileSequence, Components

# Parse sequences from a directory
sequences = FileSequence.find_sequences_in_path(Path("/path/to/files"))

# Create a virtual sequence from a list of file names
file_list = ["render_001.exr", "render_002.exr", "render_003.exr"]
sequence = FileSequence.find_sequences_in_filename_list(file_list)[0]

# Basic sequence operations
sequence.move_to(Path("/new/directory"))
sequence.rename_to(Components(prefix="new_name"))
sequence.offset_frames(100)  # Shift all frame numbers by 100
sequence.delete_files()
new_sequence = sequence.copy_to(Components(prefix="new_name"), Path("/new/directory"))

# Match sequences by components
components = Components(prefix="render", extension="exr")
matches = FileSequence.match_components_in_path(components, Path("/path/to/files"))

# Match sequence by pattern string
sequence = FileSequence.match_sequence_string_in_directory("render_####.exr", Path("/path/to/files"))
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
    extension="exr",
    frame_number=None  # Optional frame number for specific frame operations
)
```
Equals: "file_name.####_final.exr"

### FileSequence
Main class.
Manages collections of related Items as a single unit, where Items represent single files.

Key Features:
- Static methods for finding sequences in directories or filename lists
- Match sequences against Components or sequence string patterns
- Sequence manipulation operations (rename, move, copy, delete)
- Frame operations (offset, padding adjustment)
- Sequence analysis (missing frames, duplicates, problems detection)
- Existence status checking (TRUE, FALSE, PARTIAL)

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

---

See examples folder for more usage scenarios
