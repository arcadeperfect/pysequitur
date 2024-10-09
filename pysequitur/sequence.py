class Sequence:
    def __init__(self, name, files, first_frame, last_frame, extension, separator=None):
        self.name = name
        self.files = files
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.extension = extension
        self.separator = separator

    def __str__(self):
        return f"name: {self.name} | first_frame: {self.first_frame} | last_frame: {self.last_frame} | extension: {self.extension}"
    
    def __eq__(self, other):
    
        if not isinstance(other, Sequence):
            return False
        
        equal = True

        if self.name != other.name:
            equal = False

        if self.first_frame != other.first_frame:
            equal = False

        if self.last_frame != other.last_frame:
            equal = False

        if self.extension != other.extension:
            equal = False

        if self.files != other.files:
            equal = False

        return equal
    
