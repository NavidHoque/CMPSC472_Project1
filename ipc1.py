import multiprocessing as mp
import threading as th
import time
import numpy as np
from multiprocessing import shared_memory as shm, Process, Queue as ProcQueue
from queue import Queue


def modify_shared_memory_array(name, shape, dtype):
    existing_shm = shm.SharedMemory(name=name)
    np_array = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    np_array += 1  
    existing_shm.close()

def run_process_shared_memory_ipc():
    arr = np.zeros(10)
    shm_obj = shm.SharedMemory(create=True, size=arr.nbytes)
    np_array_original = np.ndarray(arr.shape, dtype=arr.dtype, buffer=shm_obj.buf)
    np.copyto(np_array_original, arr)
    p = Process(target=modify_shared_memory_array, args=(shm_obj.name, arr.shape, arr.dtype))
    p.start()
    p.join()
    print(np_array_original)
    shm_obj.unlink()  


def sender_process(queue):
    for i in range(10):
        queue.put(f"Message {i}")

def receiver_process(queue):
    while True:
        message = queue.get()
        if message == "END":
            break
        print(f"Received: {message}")

def run_process_message_passing_ipc():
    queue = ProcQueue()
    p1 = Process(target=sender_process, args=(queue,))
    p2 = Process(target=receiver_process, args=(queue,))
    p1.start()
    p2.start()
    p1.join()
    queue.put("END")
    p2.join()


shared_data_thread = []

def thread_function_ipc(name):
    for i in range(5):
        shared_data_thread.append(f"Data from {name}: {i}")
        time.sleep(1)

def run_thread_shared_memory_ipc():
    threads = []
    for index in range(2):
        x = th.Thread(target=thread_function_ipc, args=(f"Thread-{index}",))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        thread.join()
    print(shared_data_thread)


def thread_producer_ipc(queue):
    for i in range(10):
        queue.put(f"Message {i}")

def thread_consumer_ipc(queue):
    while True:
        message = queue.get()
        if message == "END":
            break
        print(f"Received: {message}")

def run_thread_message_passing_ipc():
    queue = Queue()
    t1 = th.Thread(target=thread_producer_ipc, args=(queue,))
    t2 = th.Thread(target=thread_consumer_ipc, args=(queue,))
    t1.start()
    t2.start()
    t1.join()
    queue.put("END")
    t2.join()

if __name__ == "__main__":
    start_time = time.perf_counter()
    print("Process-Based IPC with Shared Memory")
    run_process_shared_memory_ipc()
    print("Elapsed time:", time.perf_counter() - start_time, "seconds\n")

    start_time = time.perf_counter()
    print("Process-Based IPC with Message Passing")
    run_process_message_passing_ipc()
    print("Elapsed time:", time.perf_counter() - start_time, "seconds\n")

    start_time = time.perf_counter()
    print("Thread-Based IPC with Shared Memory")
    run_thread_shared_memory_ipc()
    print("Elapsed time:", time.perf_counter() - start_time, "seconds\n")

    start_time = time.perf_counter()
    print("Thread-Based IPC with Message Passing")
    run_thread_message_passing_ipc()
    print("Elapsed time:", time.perf_counter() - start_time, "seconds")
