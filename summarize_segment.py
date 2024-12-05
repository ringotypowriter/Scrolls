def split_text_by_lines(file_path, lines_per_chunk):
    """
    Reads a file and splits its content into chunks with a specified number of lines.

    Parameters:
        file_path (str): The path to the input file containing the text.
        lines_per_chunk (int): The number of lines per chunk.

    Returns:
        list of str: A list where each element is a chunk containing the specified number of lines.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Split the lines into chunks
        chunks = [
            ''.join(lines[i:i + lines_per_chunk])
            for i in range(0, len(lines), lines_per_chunk)
        ]
        return chunks
    except Exception as e:
        print(f"Error reading or processing the file: {e}")
        return []


# Example usage
file_path = 'path_to_your_file.txt'
lines_per_chunk = 10  # Adjust the number of lines per chunk
chunks = split_text_by_lines(file_path, lines_per_chunk)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i + 1}:\n{chunk}\n{'-' * 40}")

# 读取文件中的长文本
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)