# PySequitur

Library for identifying and manipulating sequences of files. It is geared towards visual effects and animation related scenarios, although it can be used with any sequence of files. Emphasis on file system manipulation and flexible handling of anomalous sequences is the main differentiating feature from other similar libraries.

No external dependencies, easy to use in VFX pipelines with no privileges.

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

- **Safe by Default**
  - Operations return a plan that can be inspected before execution
  - Conflict detection prevents accidental overwrites

## Installation

```bash
pip install pysequitur
```

Or with Poetry:

```bash
poetry add pysequitur
```

## Quick Start

```python
from pathlib import Path
from pysequitur import SequenceFactory, Components

# Parse sequences from a directory
sequences = SequenceFactory.from_directory(Path("/path/to/files"))

# Parse from a list of filenames
file_list = ["render_001.exr", "render_002.exr", "render_003.exr"]
sequences = SequenceFactory.from_filenames(file_list)

# Match sequences by components
sequences = SequenceFactory.from_directory_with_components(
    Components(prefix="render", extension="exr"),
    Path("/path/to/files")
)

# Match by sequence string pattern
sequence = SequenceFactory.from_directory_with_sequence_string(
    "render_####.exr",
    Path("/path/to/files")
)
```

## Operations

All operations return a result that can be inspected before execution:

```python
# Preview what will happen
result = sequence.rename(Components(prefix="new_name"))
print(result.plan)  # See the planned operations
print(result.plan.has_conflicts)  # Check for conflicts

# Execute when ready
new_sequence = result.apply()

# Or use tuple unpacking for more control
new_sequence, plan = sequence.rename(Components(prefix="new_name"))
if not plan.has_conflicts:
    plan.execute()
```

### Available Operations

```python
# Rename
new_seq = sequence.rename(Components(prefix="new_name")).apply()

# Move to new directory
new_seq = sequence.move(Path("/new/directory")).apply()

# Copy (optionally with new name)
new_seq = sequence.copy(new_directory=Path("/backup")).apply()

# Offset frame numbers
new_seq = sequence.offset_frames(100).apply()

# Change padding
new_seq = sequence.with_padding(4).apply()

# Delete (returns plan directly, no new sequence)
plan = sequence.delete()
plan.execute()
```

### Chaining Operations with SequenceBuilder

```python
from pysequitur import SequenceBuilder

# Chain multiple operations into a single plan
result = (
    SequenceBuilder(sequence)
    .rename(Components(prefix="new_name"))
    .offset_frames(1000)
    .move(Path("/final/location"))
    .build()
)

# Preview the combined plan
print(result.plan)

# Execute all at once
result.apply()
```

## Core Classes

### Components

Configuration class for specifying filename components. Any parameter can be None to preserve the original value.

```python
components = Components(
    prefix="file_name",
    delimiter=".",
    padding=4,
    suffix="_final",
    extension="exr",
)
# Represents: "file_name.####_final.exr"
```

### FileSequence

Manages collections of related Items that form an image sequence.

```python
sequence = SequenceFactory.from_directory(Path("/renders"))[0]

# Properties
sequence.prefix          # "render"
sequence.extension       # "exr"
sequence.first_frame     # 1
sequence.last_frame      # 100
sequence.missing_frames  # [5, 6, 7] (if gaps exist)
sequence.padding         # 4
sequence.sequence_string # "render_####.exr"

# Access frames
item = sequence[1001]        # Get frame 1001
subset = sequence[1001:1010] # Get frame range
```

### Item

Represents a single file in a sequence.

```python
from pysequitur import Item

item = Item.from_path(Path("/renders/render_0001.exr"))
item.frame_number  # 1
item.filename      # "render_0001.exr"
item.exists        # True/False
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

## License

MIT License - see [LICENSE](LICENSE) for details.
