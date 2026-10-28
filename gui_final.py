# gui_final_demo_autoscroll.py
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from send2trash import send2trash
import os
import logging
import time
import shutil
import tempfile
import platform
import psutil

# ===== Logging setup =====
logging.basicConfig(filename="deletion_log.txt",
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ===== TEMP folder path =====
temp_folder = r"C:\Users\HP\AppData\Local\Temp"

# ===== Global variables =====
files_found = []
current_index = 0
batch_count = 0
batch_logs = []

# ===== Student 1: Scan temp files =====
def scan_temp_files():
    global files_found, current_index
    files_found = []
    current_index = 0
    output_text.delete('1.0', tk.END)
    output_text.insert(tk.END, "Scanning temporary files...\n\n")
    root.update()

    for root_dir, dirs, files in os.walk(temp_folder):
        for file in files:
            files_found.append(os.path.join(root_dir, file))

    total_files = len(files_found)
    output_text.insert(tk.END, f"Total temporary files found: {total_files}\n\n")
    show_next_batch()

    with open("all_temp_files.txt", "w") as f:
        for file in files_found:
            f.write(file + "\n")

    output_text.insert(tk.END, "\nScan complete!\n")

# ===== Student 2: Show next batch with auto-scroll =====
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
    # Auto-scroll to latest entry
    output_text.see(tk.END)

# ===== Student 3: Safe delete with live colored output =====
def safe_delete():
    global current_index, batch_count, batch_logs
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

    deleted_files = []
    failed_files = []

    batch_count += 1
    start_idx = (batch_count - 1) * 20
    end_idx = start_idx + 20
    batch_files = files[start_idx:end_idx]

    if not batch_files:
        messagebox.showinfo("Info", "No more files to delete.")
        return

    output_text.tag_config("deleted", foreground="green")
    output_text.tag_config("failed", foreground="red")
    output_text.insert(tk.END, f"\n--- Deleting Batch {batch_count} ---\n")
    output_text.see(tk.END)
    root.update_idletasks()

    progress['maximum'] = len(batch_files)
    progress['value'] = 0

    for i, f in enumerate(batch_files, start=1):
        try:
            if temp_folder not in f:
                raise Exception("Outside TEMP folder")
            send2trash(f)
            output_text.insert(tk.END, f"Deleted: {f}\n", "deleted")
            logging.info(f"Deleted: {f}")
            deleted_files.append(f)
        except PermissionError:
            output_text.insert(tk.END, f"Failed (In Use): {f}\n", "failed")
            logging.error(f"Failed (In Use): {f}")
            failed_files.append(f"PermissionError: {f}")
        except FileNotFoundError:
            output_text.insert(tk.END, f"Failed (Not Found): {f}\n", "failed")
            logging.error(f"Failed (Not Found): {f}")
            failed_files.append(f"NotFound: {f}")
        except Exception as e:
            output_text.insert(tk.END, f"Failed ({str(e)}): {f}\n", "failed")
            logging.error(f"Failed ({str(e)}): {f}")
            failed_files.append(f"{str(e)}: {f}")

        # 🔹 Live progress + autoscroll
        progress['value'] = i
        output_text.see(tk.END)
        root.update()
        time.sleep(0.01)  # ⏳ smoother + faster

    batch_summary = f"Batch {batch_count}: Deleted {len(deleted_files)}, Failed {len(failed_files)}"
    batch_logs.append({"summary": batch_summary, "deleted": deleted_files, "failed": failed_files})
    messagebox.showinfo("Deletion Summary", batch_summary)
    output_text.insert(tk.END, batch_summary + "\n\n")
    output_text.see(tk.END)

# ===== Extra buttons =====
def rescan_files():
    show_next_batch()

def clear_output():
    output_text.delete('1.0', tk.END)

# ===== Student 4: Cleanup & Disk Space =====
def bytes_to_gb(value):
    return round(value / (1024**3), 2)

def get_free_space():
    total, used, free = shutil.disk_usage("C:/")
    return bytes_to_gb(free)

def cleanup_temp_safe():
    temp_dir = tempfile.gettempdir()
    freed_space = 0
    for root_dir, dirs, files in os.walk(temp_dir):
        for f in files:
            try:
                freed_space += os.path.getsize(os.path.join(root_dir, f))
                send2trash(os.path.join(root_dir, f))
            except:
                pass
    return bytes_to_gb(freed_space)

import threading

def run_cleanup():
    def cleanup_task():
        before_label.config(text="Before Cleanup: Checking space...")
        after_label.config(text="After Cleanup: Please wait...")
        root.update_idletasks()

        before = get_free_space()
        before_label.config(text=f"Before Cleanup: {before} GB free")

        freed = 0
        temp_dir = tempfile.gettempdir()

        for root_dir, dirs, files in os.walk(temp_dir):
            for f in files:
                try:
                    file_path = os.path.join(root_dir, f)
                    freed += os.path.getsize(file_path)
                    send2trash(file_path)  # safe delete
                except:
                    pass

        after = get_free_space()
        after_label.config(text=f"After Cleanup: {after} GB free")

        freed_gb = bytes_to_gb(freed)
        messagebox.showinfo(
            "Cleanup Completed",
            f"Free space before: {before} GB\nFreed: {freed_gb} GB\nFree space after: {after} GB"
        )

    threading.Thread(target=cleanup_task, daemon=True).start()

# ===== Student 5: Show Logs with green summary =====
def show_logs():
    logs_window = tk.Toplevel(root)
    logs_window.title("Deletion Logs")
    logs_window.geometry("700x500")

    log_text = scrolledtext.ScrolledText(logs_window, width=80, height=30)
    log_text.pack(padx=10, pady=10)

    log_text.tag_config("summary", foreground="green")
    log_text.tag_config("deleted", foreground="black")
    log_text.tag_config("failed", foreground="black")

    for batch in batch_logs:
        for f in batch['deleted']:
            log_text.insert(tk.END, f"Deleted: {f}\n", "deleted")
        for f in batch['failed']:
            log_text.insert(tk.END, f"Failed: {f}\n", "failed")
        log_text.insert(tk.END, batch['summary'] + "\n\n", "summary")

    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)

# ===== GUI Setup =====
root = tk.Tk()
root.title("Automatic Cleanup Assistant")
root.geometry("900x700")

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

output_text = tk.Text(top_frame, height=25, width=100)
output_text.pack()
output_text.config(bg="#1e1e1e", fg="white", font=("Consolas", 10))  # 🌙 Dark background look

progress = ttk.Progressbar(top_frame, length=700, mode='determinate')
progress.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

scan_btn = tk.Button(button_frame, text="Scan Files", command=scan_temp_files, width=20, bg="lightblue")
scan_btn.pack(side="left", padx=5)

delete_btn = tk.Button(button_frame, text="Delete Files", command=safe_delete, width=20, bg="lightcoral")
delete_btn.pack(side="left", padx=5)

rescan_btn = tk.Button(button_frame, text="Next Batch", command=rescan_files, width=15, bg="lightgreen")
rescan_btn.pack(side="left", padx=5)

clear_btn = tk.Button(button_frame, text="Clear Output", command=clear_output, width=15, bg="lightyellow")
clear_btn.pack(side="left", padx=5)

showlogs_btn = tk.Button(button_frame, text="Show Logs", command=show_logs, width=15, bg="lightgray")
showlogs_btn.pack(side="left", padx=5)

cleanup_frame = tk.Frame(root, pady=10)
cleanup_frame.pack()

total_space, _, _ = shutil.disk_usage("C:/")
total_space = bytes_to_gb(total_space)

before_label = tk.Label(cleanup_frame, text="Before Cleanup: - GB free", font=("Arial", 12))
before_label.pack(pady=5)

after_label = tk.Label(cleanup_frame, text="After Cleanup: - GB free", font=("Arial", 12))
after_label.pack(pady=5)

progress_cleanup = ttk.Progressbar(cleanup_frame, length=300, mode='determinate')
progress_cleanup.pack(pady=10)

cleanup_btn = tk.Button(cleanup_frame, text="Run Safe Cleanup", command=run_cleanup, font=("Arial", 12), bg="lightblue")
cleanup_btn.pack(pady=5)

# ===== Student 6: System Information Feature =====
def show_system_info():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:/')
        os_name = platform.system()
        os_version = platform.release()

        info = (
            f"🖥️ System Information\n\n"
            f"Operating System: {os_name} {os_version}\n"
            f"CPU Usage: {cpu_percent}%\n"
            f"Memory Usage: {memory.percent}%\n"
            f"Total Disk Space: {disk.total / (1024**3):.2f} GB\n"
            f"Free Disk Space: {disk.free / (1024**3):.2f} GB"
        )

        messagebox.showinfo("System Info", info)

    except Exception as e:
        messagebox.showerror("Error", f"Unable to fetch system info:\n{e}")

system_info_btn = tk.Button(button_frame, text="Show System Info", command=show_system_info, width=18, bg="lightgreen")
system_info_btn.pack(side="left", padx=5)

root.mainloop()
