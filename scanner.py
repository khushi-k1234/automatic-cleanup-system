import os
from send2trash import send2trash
import logging

# ===== Student 1: Scan Temporary Files =====
temp_folder = r"C:\Users\HP\AppData\Local\Temp"

def scan_temp_files():
    print("Scanning temporary files...\n")
    files_found = []

    for root, dirs, files in os.walk(temp_folder):
        for file in files:
            file_path = os.path.join(root, file)
            files_found.append(file_path)

    total_files = len(files_found)
    print(f"Total temporary files found: {total_files}\n")

    # Show only first 20 files for demo
    for f in files_found[:20]:
        print(f)

    if total_files > 20:
        print("...and more files listed in 'all_temp_files.txt'\n")

    # Save all files to text file
    with open("all_temp_files.txt", "w") as f:
        for file in files_found:
            f.write(file + "\n")
    print("All files saved to 'all_temp_files.txt'.\n")

    return files_found

# ===== Student 2: Safe Deletion =====
logging.basicConfig(filename="deletion_log.txt",
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def safe_delete(files_to_delete, limit=20):
    if not files_to_delete:
        print("No files to delete.")
        return

    print(f"Preparing to delete first {min(limit, len(files_to_delete))} files...\n")
    confirm = input("Are you sure you want to delete these files? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deletion cancelled.\n")
        return

    deleted_count = 0
    failed_count = 0

    for f in files_to_delete[:limit]:
        try:
            if temp_folder in f:
                send2trash(f)
                print(f"Deleted: {f}")
                logging.info(f"Deleted: {f}")
                deleted_count += 1
            else:
                print(f"Skipped (outside TEMP folder): {f}")
        except Exception as e:
            print(f"Failed to delete: {f} -> {e}")
            logging.error(f"Failed: {f} -> {e}")
            failed_count += 1

    print(f"\nDeletion complete. Deleted: {deleted_count}, Failed: {failed_count}")
    print("Full log saved in 'deletion_log.txt'.\n")

# ===== Main Demo =====
if __name__ == "__main__":
    files = scan_temp_files()       # Student 1
    safe_delete(files)              # Student 2
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from send2trash import send2trash
import os
import logging
import time

# ===== Logging setup =====
logging.basicConfig(filename="deletion_log.txt",
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ===== Temp folder path =====
temp_folder = r"C:\Users\HP\AppData\Local\Temp"

# ===== GUI Functions =====

def scan_temp_files():
    files_found = []
    output_text.delete('1.0', tk.END)
    output_text.insert(tk.END, "Scanning temporary files...\n\n")
    root.update()  # GUI update
    
    for root_dir, dirs, files in os.walk(temp_folder):
        for file in files:
            file_path = os.path.join(root_dir, file)
            files_found.append(file_path)
    
    total_files = len(files_found)
    output_text.insert(tk.END, f"Total temporary files found: {total_files}\n\n")
    
    # Show first 20 files
    for f in files_found[:20]:
        output_text.insert(tk.END, f + "\n")
    
    if total_files > 20:
        output_text.insert(tk.END, "\n...and more files saved in 'all_temp_files.txt'\n")
    
    # Save all files
    with open("all_temp_files.txt", "w") as f:
        for file in files_found:
            f.write(file + "\n")
    
    output_text.insert(tk.END, "\nScan complete!\n")
    return files_found

def safe_delete():
    try:
        with open("all_temp_files.txt", "r") as f:
            files = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        messagebox.showerror("Error", "Please scan files first!")
        return
    
    if not files:
        messagebox.showinfo("Info", "No files to delete.")
        return
    
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete first 20 files?")
    if not confirm:
        return
    
    deleted_count = 0
    failed_count = 0
    
    # Progress bar setup
    progress['maximum'] = min(20, len(files))
    progress['value'] = 0
    root.update_idletasks()
    
    for i, f in enumerate(files[:20], start=1):
        try:
            if temp_folder in f:
                send2trash(f)
                logging.info(f"Deleted: {f}")
                output_text.insert(tk.END, f"Deleted: {f}\n", 'success')
                deleted_count += 1
            else:
                output_text.insert(tk.END, f"Skipped (outside TEMP folder): {f}\n", 'warning')
        except Exception as e:
            logging.error(f"Failed: {f} -> {e}")
            output_text.insert(tk.END, f"Failed: {f} -> {e}\n", 'error')
            failed_count += 1
        
        # Update progress
        progress['value'] = i
        root.update_idletasks()
        time.sleep(0.05)  # slow down for visible progress bar
    
    output_text.insert(tk.END, f"\nDeletion complete. Deleted: {deleted_count}, Failed: {failed_count}\n")
    messagebox.showinfo("Deletion Complete", f"Deleted: {deleted_count}, Failed: {failed_count}")

# ===== GUI Setup =====
root = tk.Tk()
root.title("Automatic Cleanup Assistant")
root.geometry("750x550")

# Buttons
scan_btn = tk.Button(root, text="Scan Files", command=scan_temp_files, width=25, bg="lightblue")
scan_btn.pack(pady=10)

delete_btn = tk.Button(root, text="Delete Files", command=safe_delete, width=25, bg="lightcoral")
delete_btn.pack(pady=10)

# Progress Bar
progress = ttk.Progressbar(root, length=600, mode='determinate')
progress.pack(pady=10)

# Output area
output_text = tk.Text(root, height=25, width=90)
output_text.pack(pady=10)

# Text tags for colored messages
output_text.tag_config('success', foreground='green')
output_text.tag_config('error', foreground='red')
output_text.tag_config('warning', foreground='orange')

root.mainloop()
