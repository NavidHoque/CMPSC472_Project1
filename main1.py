import os
from manager1 import ProcessController, ThreadController, CommandLineInterface
from parallel_text_processing1 import main as parallel_text_processing_main
from ipc1 import run_process_shared_memory_ipc, run_process_message_passing_ipc, run_thread_shared_memory_ipc, run_thread_message_passing_ipc

def main():
    process_manager = ProcessController()
    thread_manager = ThreadController()
    cli_manager = CommandLineInterface(process_manager, thread_manager)
    cli_manager.start()

    while True:
        print("\nMenu:")
        print("1. Run parallel text processing")
        print("2. Run process-based IPC with shared memory")
        print("3. Run process-based IPC with message passing")
        print("4. Run thread-based IPC with shared memory")
        print("5. Run thread-based IPC with message passing")
        print("6. Create process")
        print("7. Terminate process")
        print("8. List running processes")
        print("9. Create thread")
        print("10. Terminate thread")
        print("11. List running threads")
        print("12. Exit")

        choice = input("Enter your choice (1-12): ")

        if choice == "1":
            file_path = input("Enter the full path of the file to process: ")
            parallel_text_processing_main(file_path)
        elif choice == "2":
            run_process_shared_memory_ipc()
        elif choice == "3":
            run_process_shared_memory_ipc()
        elif choice == "4":
            run_thread_shared_memory_ipc()
        elif choice == "5":
            run_thread_message_passing_ipc()
        elif choice == "6":
            name = input("Enter the name for the process: ")
            process_manager.create_process(name)
        elif choice == "7":
            identifier = input("Enter the PID or name of the process to terminate: ")
            process_manager.terminate_process(identifier)
        elif choice == "8":
            process_manager.list_processes()
        elif choice == "9":
            name = input("Enter the name for the thread: ")
            thread_manager.create_thread(name)
        elif choice == "10":
            identifier = input("Enter the TID or name of the thread to terminate: ")
            thread_manager.terminate_thread(identifier)
        elif choice == "11":
            thread_manager.list_threads()
        elif choice == "12":
            cli_manager.submit_command(["exit"])
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 12.")

if __name__ == "__main__":
    main()
