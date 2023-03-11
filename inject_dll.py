import ctypes
import sys
import time
import os
from pystyle import *

# Define the DLL code to be injected
dll_code = """
DLL CODE HERE
"""

# Write the code to a file
with open("injection.dll", "w") as f:
    f.write(dll_code)

# Get the process ID from the command line argument
if len(sys.argv) < 2:
    print(f"{Col.white}[{Col.purple}+{Col.white}] DLL Being Built..")
    time.sleep(2)
    print(f"{Col.white}[{Col.purple}+{Col.white}] DLL File Successfuly Built.")
    print(f"{Col.white}[{Col.purple}+{Col.white}] In Order To Use: python inject_dll.py <pid>")
    input()
pid = int(sys.argv[1])

# Open the target process
process_handle = ctypes.windll.kernel32.OpenProcess(
    ctypes.c_uint32(0x1F0FFF),  # All access
    ctypes.c_bool(False),
    ctypes.c_uint32(pid)
)

# Allocate memory for the DLL path in the target process
dll_path = ctypes.c_char_p("injection.dll".encode("utf-8"))
dll_path_size = ctypes.c_size_t(len(dll_path.value) + 1)
remote_dll_path = ctypes.windll.kernel32.VirtualAllocEx(
    process_handle,
    None,
    dll_path_size.value,
    ctypes.c_uint32(0x3000),  # Commit, read, write
    ctypes.c_uint32(0x04)  # Read, write
)

# Write the DLL path to the target process memory
ctypes.windll.kernel32.WriteProcessMemory(
    process_handle,
    remote_dll_path,
    dll_path,
    dll_path_size,
    None
)

# Load the DLL in the target process
thread_id = ctypes.windll.kernel32.CreateRemoteThread(
    process_handle,
    None,
    0,
    ctypes.windll.kernel32.GetProcAddress(ctypes.windll.kernel32.GetModuleHandleA("kernel32.dll"), "LoadLibraryA"),
    remote_dll_path,
    0,
    None
)

# Wait for the thread to exit
ctypes.windll.kernel32.WaitForSingleObject(thread_id, -1)
