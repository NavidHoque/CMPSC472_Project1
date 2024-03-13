import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import psutil

def process_segment(start_index, end_index, file_path):
    """Process a segment of the file to convert characters to uppercase and count them."""
    char_counts = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        file.seek(start_index)
        segment_text = file.read(end_index - start_index)
        segment_text = segment_text.upper()
        for char in segment_text:
            if char.isalpha():
                char_counts[char] = char_counts.get(char, 0) + 1
    return char_counts

def merge_char_counts(char_counts_list):
    """Merge character counts from all segments."""
    merged_counts = {}
    for char_counts in char_counts_list:
        for char, count in char_counts.items():
            merged_counts[char] = merged_counts.get(char, 0) + count
    return merged_counts

def main(file_path):
    start_time = time.time_ns()
    current_process = psutil.Process()
    initial_cpu_usage = current_process.cpu_percent(interval=None)
    initial_memory_usage = current_process.memory_info().rss

    file_size = os.path.getsize(file_path)
    num_workers = 4
    chunk_size = file_size // num_workers
    futures = []

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for i in range(num_workers):
            start_index = i * chunk_size
            end_index = start_index + chunk_size if i < num_workers - 1 else file_size
            futures.append(executor.submit(process_segment, start_index, end_index, file_path))

        results = [future.result() for future in as_completed(futures)]

    final_char_counts = merge_char_counts(results)

    print(final_char_counts)

    end_time = time.time_ns()
    final_cpu_usage = current_process.cpu_percent(interval=None)
    final_memory_usage = current_process.memory_info().rss
    cpu_usage_change = final_cpu_usage - initial_cpu_usage
    memory_usage_increase = final_memory_usage - initial_memory_usage

    print(f"Processing completed in {end_time - start_time:.2f} nanoseconds.")
    print(f"CPU usage change: {cpu_usage_change}%")
    print(f"Memory usage increase: {memory_usage_increase / (1024 ** 2):.2f} MB")

if __name__ == "__main__":
    file_to_process = "example.txt"
    main(file_to_process)
