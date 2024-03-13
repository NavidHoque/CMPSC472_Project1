import logging
import threading
import time
import queue
from multiprocessing import Process, Event as ProcessEvent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomProcess:
    def __init__(self, process_name):
        self.process_name = process_name
        self.pause_event = ProcessEvent()
        self.pause_event.set()

    def run(self):
        logging.info(f"Custom Process {self.process_name} started.")
        while True:
            self.pause_event.wait()
            time.sleep(1)  

class CustomThread:
    def __init__(self, thread_name):
        self.thread_name = thread_name
        self.pause_event = threading.Event()
        self.pause_event.set()

    def run(self):
        logging.info(f"Custom Thread {self.thread_name} started.")
        while True:
            self.pause_event.wait()
            time.sleep(1)  

class ProcessController:
    def __init__(self):
        self.processes = {}
        self.names_to_pids = {}

    def create_process(self, process_name):
        if process_name in self.names_to_pids:
            logging.error(f"A process with the name '{process_name}' already exists.")
            return
        custom_process = CustomProcess(process_name)
        p = Process(target=custom_process.run)
        p.start()
        self.processes[p.pid] = {'process': p, 'pause_event': custom_process.pause_event, 'name': process_name}
        self.names_to_pids[process_name] = p.pid
        logging.info(f"Process '{process_name}' with PID {p.pid} created.")

    def pause_process(self, identifier):
        pid = self.names_to_pids.get(identifier, identifier)
        if pid in self.processes:
            self.processes[pid]['pause_event'].clear()
            logging.info(f"Process '{self.processes[pid]['name']}' with PID {pid} paused.")
        else:
            logging.error(f"Process with identifier '{identifier}' not found.")

    def resume_process(self, identifier):
        pid = self.names_to_pids.get(identifier, identifier)
        if pid in self.processes:
            self.processes[pid]['pause_event'].set()
            logging.info(f"Process '{self.processes[pid]['name']}' with PID {pid} resumed.")
        else:
            logging.error(f"Process with identifier '{identifier}' not found.")

    def terminate_process(self, identifier):
        pid = self.names_to_pids.get(identifier, identifier)
        if pid in self.processes:
            process_name = self.processes[pid]['name']
            self.processes[pid]['process'].terminate()
            self.processes[pid]['process'].join()
            del self.processes[pid]
            del self.names_to_pids[process_name]
            logging.info(f"Process '{process_name}' with PID {pid} terminated.")
        else:
            logging.error(f"Process with identifier '{identifier}' not found.")

    def list_processes(self):
        logging.info("List of running processes:")
        for pid, process_info in self.processes.items():
            status = "Paused" if not process_info['pause_event'].is_set() else "Running"
            logging.info(f"PID: {pid}, Name: {process_info['name']}, Status: {status}")

class ThreadController:
    def __init__(self):
        self.threads = {}
        self.names_to_tids = {}

    def create_thread(self, thread_name):
        if thread_name in self.names_to_tids:
            logging.error(f"A thread with the name '{thread_name}' already exists.")
            return
        custom_thread = CustomThread(thread_name)
        t = threading.Thread(target=custom_thread.run, name=thread_name)
        t.start()
        self.threads[t.ident] = {'thread': t, 'pause_event': custom_thread.pause_event, 'name': thread_name}
        self.names_to_tids[thread_name] = t.ident
        logging.info(f"Thread '{thread_name}' with TID {t.ident} created.")

    def pause_thread(self, identifier):
        tid = self.names_to_tids.get(identifier, identifier)
        if tid in self.threads:
            self.threads[tid]['pause_event'].clear()
            logging.info(f"Thread '{self.threads[tid]['name']}' with TID {tid} paused.")
        else:
            logging.error(f"Thread with identifier '{identifier}' not found.")

    def resume_thread(self, identifier):
        tid = self.names_to_tids.get(identifier, identifier)
        if tid in self.threads:
            self.threads[tid]['pause_event'].set()
            logging.info(f"Thread '{self.threads[tid]['name']}' with TID {tid} resumed.")
        else:
            logging.error(f"Thread with identifier '{identifier}' not found.")

    def list_threads(self):
        logging.info("List of running threads:")
        for tid, thread_info in self.threads.items():
            status = "Paused" if not thread_info['pause_event'].is_set() else "Running"
            logging.info(f"TID: {tid}, Name: {thread_info['name']}, Status: {status}")

class CommandLineInterface(threading.Thread):
    def __init__(self, process_controller, thread_controller):
        super().__init__()
        self.process_controller = process_controller
        self.thread_controller = thread_controller
        self.commands = queue.Queue()

    def run(self):
        while True:
            command = self.commands.get()
            if command[0] == "exit":
                logging.info("Exiting the CLI.")
                break
            self.execute_command(command)
            time.sleep(0.5)  

    def execute_command(self, command):
        if len(command) < 2:
            logging.error("Invalid command, include an operation and type")
            return

        operation, entity_type = command[0], command[1]

        if operation == "create" and len(command) >= 3:
            name = command[2]
            if entity_type == 'process':
                self.process_controller.create_process(name)
            elif entity_type == 'thread':
                self.thread_controller.create_thread(name)
        elif operation == "list":
            if entity_type == 'process':
                self.process_controller.list_processes()
            elif entity_type == 'thread':
                self.thread_controller.list_threads()
        elif len(command) >= 3:
            identifier = command[2]
            if entity_type == 'process':
                if operation == "pause":
                    self.process_controller.pause_process(identifier)
                elif operation == "resume":
                    self.process_controller.resume_process(identifier)
                elif operation == "terminate":
                    self.process_controller.terminate_process(identifier)
            elif entity_type == 'thread':
                if operation == "pause":
                    self.thread_controller.pause_thread(identifier)
                elif operation == "resume":
                    self.thread_controller.resume_thread(identifier)

    def submit_command(self, command):
        self.commands.put(command)
