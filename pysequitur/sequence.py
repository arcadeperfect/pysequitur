class Sequence:
    def __init__(self, name, files, first_frame, last_frame, extension):
        self.name = name
        self.files = files
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.extension = extension

    def __str__(self):
        return f"name: {self.name} first_frame: {self.first_frame} last_frame: {self.last_frame} extension: {self.extension}"
