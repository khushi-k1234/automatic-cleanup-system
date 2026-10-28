import tkinter as tk
from tkinter import messagebox

def analyze_log():
    success = 0
    failed = 0
    total = 0

    try:
        with open("deletion_log.txt", "r") as f:
            for line in f:
                # Match dono format: INFO - Deleted / ERROR - Failed
                if "Deleted:" in line:
                    success += 1
                elif "Failed:" in line:
                    failed += 1
        total = success + failed
    except FileNotFoundError:
        messagebox.showerror("Error", "deletion_log.txt not found!")
        return

    summary = (
        "📄 FILE DELETION SUMMARY\n\n"
        f"Total Files Processed: {total}\n"
        f"✅ Successfully Deleted: {success}\n"
        f"❌ Failed to Delete: {failed}\n"
    )

    output_box.config(state=tk.NORMAL)
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, summary)
    output_box.config(state=tk.DISABLED)

    messagebox.showinfo("Summary", summary)


root = tk.Tk()
root.title("Student 5 - File Deletion Report")
root.geometry("550x400")

title = tk.Label(root, text="Student 5: Analyze File Deletion Logs", font=("Arial", 14, "bold"))
title.pack(pady=10)

desc = tk.Label(root, text="Click below to analyze results from deletion_log.txt (created by Student 4).", wraplength=500)
desc.pack()

analyze_btn = tk.Button(root, text="📊 Analyze Log File", bg="lightgreen", font=("Arial", 12), command=analyze_log)
analyze_btn.pack(pady=10)

output_box = tk.Text(root, height=10, width=60, font=("Courier", 10), state=tk.DISABLED)
output_box.pack(pady=10)

root.mainloop()
