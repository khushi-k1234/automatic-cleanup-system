# gui_batch_scan.py
import tkinter as tk
from tkinter import messagebox, ttk
from send2trash import send2trash
import os
import logging
import time

# ===== Logging setup =====
logging.basicConfig(filename="deletion_log.txt",
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ===== TEMP folder path =====
temp_folder = r"C:\Users\HP\AppData\Local\Temp"

# ===== Global variables =====
files_found = []
current_index = 0  # batch index

# ===== Scan function =====
def scan_temp_files():
    global files_found, current_index
    files_found = []
    current_index = 0
    output_text.delete('1.0', tk.END)
    output_text.insert(tk.END, "Scanning temporary files...\n\n")
    root.update()
    
    for root_dir, dirs, files in os.walk(temp_folder):
        for file in files:
            file_path = os.path.join(root_dir, file)
            files_found.append(file_path)
    
    total_files = len(files_found)
    output_text.insert(tk.END, f"Total temporary files found: {total_files}\n\n")
    
    show_next_batch()
    
    # Save all files
    with open("all_temp_files.txt", "w") as f:
        for file in files_found:
            f.write(file + "\n")
    
    output_text.insert(tk.END, "\nScan complete!\n")

# ===== Show next batch =====
def show_next_batch():
    global current_index
    output_text.insert(tk.END, f"Showing files {current_index+1} to {min(current_index+20,len(files_found))}:\n")
    for f in files_found[current_index:current_index+20]:
        output_text.insert(tk.END, f + "\n")
    current_index += 20
    if current_index < len(files_found):
        output_text.insert(tk.END, f"\n{len(files_found)-current_index} more files remaining.\n")
    else:
        output_text.insert(tk.END, "\nAll files displayed.\n")

# ===== Safe delete function =====
def safe_delete():
    global current_index
    try:
        with open("all_temp_files.txt", "r") as f:
            files = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        messagebox.showerror("Error", "Please scan files first!")
        return

    if not files:
        messagebox.showinfo("Info", "No files to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete current 20 files?")
    if not confirm:
        return

    deleted_count = 0
    failed_count = 0

    start_idx = max(0, current_index-20)
    batch_files = files[start_idx:current_index]

    output_text.delete('1.0', tk.END)
    output_text.insert(tk.END, "Deleting files...\n\n")

    progress['maximum'] = len(batch_files)
    progress['value'] = 0
    root.update_idletasks()

    for i, f in enumerate(batch_files, start=1):
        try:
            if temp_folder in f:
                send2trash(f)
                output_text.insert(tk.END, f"Deleted: {f}\n", 'success')
                logging.info(f"Deleted: {f}")
                deleted_count += 1
            else:
                output_text.insert(tk.END, f"Failed (Outside TEMP folder): {f}\n", 'error')
                logging.error(f"Failed (Outside TEMP folder): {f}")
                failed_count += 1
        except PermissionError:
            output_text.insert(tk.END, f"Failed (In Use): {f}\n", 'error')
            logging.error(f"Failed (In Use): {f}")
            failed_count += 1
        except Exception as e:
            output_text.insert(tk.END, f"Failed ({str(e)}): {f}\n", 'error')
            logging.error(f"Failed ({str(e)}): {f}")
            failed_count += 1

        progress['value'] = i
        root.update_idletasks()
        time.sleep(0.05)

    messagebox.showinfo("Deletion Complete", f"Deleted: {deleted_count}, Failed: {failed_count}")

# ===== Extra buttons =====
def rescan_files():
    show_next_batch()

def clear_output():
    output_text.delete('1.0', tk.END)

# ===== GUI Setup =====
root = tk.Tk()
root.title("Automatic Cleanup Assistant")
root.geometry("800x550")

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

output_text = tk.Text(top_frame, height=25, width=95)
output_text.pack()

progress = ttk.Progressbar(top_frame, length=650, mode='determinate')
progress.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Buttons
scan_btn = tk.Button(button_frame, text="Scan Files", command=scan_temp_files, width=20, bg="lightblue")
scan_btn.pack(side="left", padx=5)

delete_btn = tk.Button(button_frame, text="Delete Files", command=safe_delete, width=20, bg="lightcoral")
delete_btn.pack(side="left", padx=5)

rescan_btn = tk.Button(button_frame, text="Next Batch", command=rescan_files, width=15, bg="lightgreen")
rescan_btn.pack(side="left", padx=5)

clear_btn = tk.Button(button_frame, text="Clear Output", command=clear_output, width=15, bg="lightyellow")
clear_btn.pack(side="left", padx=5)

# Text tags
output_text.tag_config('success', foreground='green')
output_text.tag_config('error', foreground='red')

root.mainloop()
