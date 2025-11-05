import os
import subprocess
import pikepdf
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import logging
import shutil
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='pdf_cleaner.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global cancel flag
cancel_flag = threading.Event()

def check_qpdf():
    """Check if qpdf is installed on the system."""
    try:
        subprocess.run(["qpdf", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_backup(file_path, backup_folder):
    """Create a backup of the original file."""
    try:
        os.makedirs(backup_folder, exist_ok=True)
        backup_path = os.path.join(backup_folder, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        logging.info(f"Backup created: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Backup failed for {file_path}: {e}")
        return False

def process_pdfs(folder_path, progress_var, progress_bar, status_label, 
                 start_button, cancel_button, create_backup_flag):
    """Process all PDFs in the selected folder."""
    start_button.config(state=tk.DISABLED)
    cancel_button.config(state=tk.NORMAL)
    cancel_flag.clear()
    
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    total = len(pdf_files)
    
    if total == 0:
        messagebox.showinfo("No PDFs", "No PDF files found in the selected folder.")
        start_button.config(state=tk.NORMAL)
        cancel_button.config(state=tk.DISABLED)
        return
    
    # Track results
    results = {"success": 0, "skipped": 0, "errors": 0}
    
    temp_folder = os.path.join(folder_path, "_temp_unlocked")
    backup_folder = os.path.join(folder_path, "_backups_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    try:
        os.makedirs(temp_folder, exist_ok=True)
        
        for idx, filename in enumerate(pdf_files, start=1):
            # Check if cancel was requested
            if cancel_flag.is_set():
                status_label.config(text="❌ Processing cancelled by user.")
                logging.info("Processing cancelled by user")
                break
            
            file_path = os.path.join(folder_path, filename)
            temp_unlocked_path = os.path.join(temp_folder, filename)
            
            status_label.config(text=f"Processing {idx}/{total}: {filename}")
            status_label.update()
            logging.info(f"Processing: {filename}")
            
            try:
                # Create backup if requested
                if create_backup_flag:
                    if not create_backup(file_path, backup_folder):
                        logging.warning(f"Continuing without backup for: {filename}")
                
                # 🔓 Step 1: Remove restrictions
                subprocess.run(
                    ["qpdf", "--decrypt", file_path, temp_unlocked_path],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                
                # 🔗 Step 2: Remove links
                pdf = pikepdf.open(temp_unlocked_path)
                links_removed = 0
                
                for page in pdf.pages:
                    if "/Annots" in page:
                        annots = page["/Annots"]
                        original_count = len(annots)
                        new_annots = [a for a in annots if a.get("/Subtype") != "/Link"]
                        page["/Annots"] = new_annots
                        links_removed += original_count - len(new_annots)
                
                temp_clean_path = file_path + ".tmp"
                pdf.save(temp_clean_path)
                pdf.close()
                
                # Replace original file
                os.replace(temp_clean_path, file_path)
                
                results["success"] += 1
                logging.info(f"Success: {filename} (removed {links_removed} links)")
                
            except subprocess.CalledProcessError:
                status_label.config(text=f"⚠️ Skipped (locked): {filename}")
                results["skipped"] += 1
                logging.warning(f"Skipped (locked): {filename}")
                
            except Exception as e:
                status_label.config(text=f"❌ Error: {filename}")
                results["errors"] += 1
                logging.error(f"Error processing {filename}: {e}")
            
            # Update progress bar
            progress = int((idx / total) * 100)
            progress_var.set(progress)
            progress_bar.update()
        
    finally:
        # Cleanup temp folder
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder, ignore_errors=True)
            logging.info("Temp folder cleaned up")
        
        # Remove backup folder if empty (no backups were created)
        if os.path.exists(backup_folder) and not os.listdir(backup_folder):
            os.rmdir(backup_folder)
    
    # Show summary
    if not cancel_flag.is_set():
        status_label.config(text="✅ Processing complete!")
        summary_message = (
            f"Processing Complete!\n\n"
            f"✅ Successfully processed: {results['success']}\n"
            f"⚠️ Skipped (locked): {results['skipped']}\n"
            f"❌ Errors: {results['errors']}\n\n"
            f"Total files: {total}"
        )
        
        if create_backup_flag and results['success'] > 0:
            summary_message += f"\n\nBackups saved in:\n{backup_folder}"
        
        messagebox.showinfo("Summary", summary_message)
        logging.info(f"Summary - Success: {results['success']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
    
    start_button.config(state=tk.NORMAL)
    cancel_button.config(state=tk.DISABLED)
    progress_var.set(0)

def select_folder(entry):
    """Open folder selection dialog."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry.delete(0, tk.END)
        entry.insert(0, folder_selected)

def start_processing(entry, progress_var, progress_bar, status_label, 
                     start_button, cancel_button, backup_var):
    """Start processing in a separate thread."""
    folder_path = entry.get().strip()
    
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showwarning("Invalid Path", "Please select a valid folder.")
        return
    
    thread = threading.Thread(
        target=process_pdfs,
        args=(folder_path, progress_var, progress_bar, status_label, 
              start_button, cancel_button, backup_var.get()),
        daemon=True
    )
    thread.start()

def cancel_processing(status_label):
    """Signal the processing thread to stop."""
    cancel_flag.set()
    status_label.config(text="Cancelling... Please wait.")

def show_help():
    """Display help information."""
    help_text = """PDF Cleaner & Unlocker

This tool removes restrictions and hyperlinks from PDF files.

Requirements:
• Python packages: pikepdf
• External tool: qpdf

Installation:
pip install pikepdf

qpdf installation:
• Windows: choco install qpdf
• macOS: brew install qpdf
• Linux: sudo apt-get install qpdf

Usage:
1. Select a folder containing PDF files
2. Choose whether to create backups
3. Click "Start Cleaning"

Note: Only use this tool on PDFs you own or have 
permission to modify. Removing security features 
from copyrighted materials may be illegal.

Logs are saved to: pdf_cleaner.log
"""
    messagebox.showinfo("Help", help_text)

# 🌟 GUI Setup
def create_gui():
    """Create and configure the GUI."""
    root = tk.Tk()
    root.title("PDF Cleaner & Unlocker v2.0")
    root.geometry("550x380")
    root.resizable(False, False)
    
    # Check for qpdf
    if not check_qpdf():
        messagebox.showerror(
            "Missing Dependency", 
            "qpdf is not installed!\n\n"
            "Please install qpdf:\n"
            "• Windows: choco install qpdf\n"
            "• macOS: brew install qpdf\n"
            "• Linux: sudo apt-get install qpdf\n\n"
            "The application will now close."
        )
        root.destroy()
        return
    
    # Header
    tk.Label(
        root, 
        text="PDF Cleaner & Unlocker", 
        font=("Arial", 14, "bold")
    ).pack(pady=10)
    
    # Folder selection
    tk.Label(
        root, 
        text="Select Folder Containing PDFs:", 
        font=("Arial", 11)
    ).pack(pady=5)
    
    frame = tk.Frame(root)
    frame.pack(pady=5)
    
    entry = tk.Entry(frame, width=45)
    entry.pack(side=tk.LEFT, padx=5)
    
    browse_btn = tk.Button(
        frame, 
        text="Browse", 
        command=lambda: select_folder(entry)
    )
    browse_btn.pack(side=tk.LEFT)
    
    # Options
    options_frame = tk.Frame(root)
    options_frame.pack(pady=10)
    
    backup_var = tk.BooleanVar(value=True)
    tk.Checkbutton(
        options_frame, 
        text="Create backups before processing", 
        variable=backup_var,
        font=("Arial", 10)
    ).pack()
    
    # Buttons frame
    button_frame = tk.Frame(root)
    button_frame.pack(pady=15)
    
    start_button = tk.Button(
        button_frame, 
        text="Start Cleaning", 
        bg="#4CAF50", 
        fg="white",
        font=("Arial", 11, "bold"),
        width=15,
        command=lambda: start_processing(
            entry, progress_var, progress_bar, status_label, 
            start_button, cancel_button, backup_var
        )
    )
    start_button.pack(side=tk.LEFT, padx=5)
    
    cancel_button = tk.Button(
        button_frame, 
        text="Cancel", 
        bg="#f44336", 
        fg="white",
        font=("Arial", 11, "bold"),
        width=15,
        state=tk.DISABLED,
        command=lambda: cancel_processing(status_label)
    )
    cancel_button.pack(side=tk.LEFT, padx=5)
    
    # Progress bar
    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(
        root, 
        length=450, 
        variable=progress_var, 
        maximum=100
    )
    progress_bar.pack(pady=10)
    
    # Status label
    status_label = tk.Label(
        root, 
        text="Ready to process. Select a folder and click 'Start Cleaning'.", 
        font=("Arial", 10),
        wraplength=500
    )
    status_label.pack(pady=10)
    
    # Help button
    help_button = tk.Button(
        root, 
        text="?", 
        command=show_help,
        font=("Arial", 10, "bold"),
        width=3
    )
    help_button.place(x=510, y=10)
    
    # Log startup
    logging.info("Application started")
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()