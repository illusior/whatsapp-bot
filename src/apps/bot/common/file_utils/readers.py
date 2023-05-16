def line_from_file_generator(file_path: str):
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()


__all__ = [
    'line_from_file_generator'
]
