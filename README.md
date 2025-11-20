# Removal-of-restrictions-and-hyperlinks-from-pdf-
Done with hyperlinks in pdf. An single mistouch and goes to another website..... OR restrictions in copy paste
# PDF Cleaner & Unlocker v2.0

A powerful Python-based GUI application that removes restrictions and hyperlinks from PDF files in bulk. Perfect for cleaning up PDF collections while maintaining document integrity.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-brightgreen.svg)

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Automation Setup](#automation-setup)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Legal Notice](#legal-notice)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **🔓 Remove PDF Restrictions**: Unlock password-protected PDFs and remove editing/printing restrictions
- **🔗 Remove Hyperlinks**: Strip all hyperlinks from PDF documents
- **📦 Batch Processing**: Process entire folders of PDFs automatically
- **🤖 Auto-Processing**: Automatically clean new PDFs when added to monitored folders
- **💾 Automatic Backups**: Optional backup creation before processing
- **📊 Real-time Progress**: Visual progress bar with detailed status updates
- **⏸️ Cancellation Support**: Stop processing at any time with graceful cleanup
- **📝 Comprehensive Logging**: Detailed log files for troubleshooting and auditing
- **📈 Summary Reports**: View statistics after processing completion
- **🖥️ User-Friendly GUI**: Clean, intuitive interface built with Tkinter
- **🛡️ Dependency Checking**: Automatic verification of required tools

## 📦 Prerequisites

### Required Software

1. **Python 3.7 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version`

2. **qpdf** (external command-line tool)
   - Required for PDF decryption and restriction removal

### Python Dependencies

- `pikepdf` - PDF manipulation library
- `tkinter` - GUI framework (usually included with Python)
- `watchdog` - File system monitoring (for automation only)

## 🚀 Installation

### Step 1: Install qpdf

#### Windows
```bash
# Using Chocolatey
choco install qpdf

# Or download installer from:
# https://github.com/qpdf/qpdf/releases
```

#### macOS
```bash
# Using Homebrew
brew install qpdf
```

#### Linux
```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install qpdf

# Fedora/RHEL
sudo dnf install qpdf

# Arch Linux
sudo pacman -S qpdf
```

### Step 2: Install Python Dependencies

```bash
# Basic installation
pip install pikepdf

# For automation features
pip install pikepdf watchdog
```

### Step 3: Download the Script

Save the `pdf_cleaner.py` file to your desired location.

### Step 4: Verify Installation

Run the script:
```bash
python pdf_cleaner.py
```

If `qpdf` is not installed, you'll see an error message with installation instructions.

## 📖 Usage

### Basic Usage

1. **Launch the Application**
   ```bash
   python pdf_cleaner.py
   ```

2. **Select Your Folder**
   - Click the "Browse" button
   - Navigate to the folder containing your PDF files
   - Click "Select Folder"

3. **Configure Options**
   - ✅ Check "Create backups before processing" (recommended for first use)
   - ❌ Uncheck if you're confident and want to save space

4. **Start Processing**
   - Click "Start Cleaning"
   - Monitor progress in the status bar
   - View real-time updates for each file

5. **Review Results**
   - View the summary report showing:
     - Successfully processed files
     - Skipped files (locked/protected)
     - Errors encountered
     - Backup location (if applicable)

### Advanced Usage

#### Processing Specific File Types

The tool automatically processes all `.pdf` files in the selected folder. It does not process subdirectories.

#### Cancelling Operations

- Click the "Cancel" button during processing
- The current file will complete processing
- Remaining files will be skipped
- Cleanup will occur automatically

#### Viewing Logs

Check the `pdf_cleaner.log` file in the same directory as the script for detailed operation logs.

## 🤖 Automation Setup

### Automatically Process New PDFs on Windows

Set up your system to automatically clean PDFs whenever new files are added to a folder. This is perfect for download folders, email attachments, or any location where PDFs regularly appear.

#### Method 1: Windows Task Scheduler (Recommended)

This method watches a folder and processes new PDFs automatically in the background.

**Step 1: Create the Automation Script**

Create a new file called `pdf_auto_cleaner.py` with the following content:

```python
import time
import sys
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import logging

# Configuration
WATCH_FOLDER = r"C:\Users\YourUsername\Downloads"  # Change this to your folder
PROCESS_DELAY = 5  # Wait 5 seconds after file creation before processing

# Setup logging
logging.basicConfig(
    filename='pdf_auto_cleaner.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PDFHandler(FileSystemEventHandler):
    def __init__(self):
        self.pending_files = {}
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            # Schedule the file for processing
            self.pending_files[event.src_path] = time.time()
            logging.info(f"New PDF detected: {event.src_path}")
    
    def process_pending(self):
        current_time = time.time()
        files_to_process = []
        
        for filepath, detection_time in list(self.pending_files.items()):
            if current_time - detection_time >= PROCESS_DELAY:
                if os.path.exists(filepath):
                    files_to_process.append(filepath)
                del self.pending_files[filepath]
        
        for filepath in files_to_process:
            self.process_pdf(filepath)
    
    def process_pdf(self, filepath):
        try:
            logging.info(f"Processing: {filepath}")
            # Run the PDF cleaner script
            result = subprocess.run(
                [sys.executable, 'pdf_cleaner.py', '--auto', filepath],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logging.info(f"Successfully processed: {filepath}")
            else:
                logging.error(f"Error processing {filepath}: {result.stderr}")
        except Exception as e:
            logging.error(f"Exception processing {filepath}: {str(e)}")

def main():
    # Validate watch folder
    if not os.path.exists(WATCH_FOLDER):
        print(f"Error: Watch folder does not exist: {WATCH_FOLDER}")
        logging.error(f"Watch folder does not exist: {WATCH_FOLDER}")
        sys.exit(1)
    
    print(f"Monitoring folder: {WATCH_FOLDER}")
    print("Press Ctrl+C to stop")
    logging.info(f"Starting PDF auto-cleaner, monitoring: {WATCH_FOLDER}")
    
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
            event_handler.process_pending()
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping PDF auto-cleaner...")
        logging.info("PDF auto-cleaner stopped by user")
    
    observer.join()

if __name__ == "__main__":
    main()
```

**Important**: Change `WATCH_FOLDER` to your actual folder path (e.g., `C:\Users\John\Downloads`).

**Step 2: Modify the Main Script for Automation**

Add command-line support to `pdf_cleaner.py` by adding this code at the end of the file:

```python
def process_single_file_cli(filepath):
    """Process a single PDF file from command line"""
    if not os.path.exists(filepath):
        logging.error(f"File not found: {filepath}")
        return False
    
    folder = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    
    # Process without GUI
    try:
        process_pdfs(folder, create_backup=True, single_file=filename)
        return True
    except Exception as e:
        logging.error(f"Error processing {filepath}: {str(e)}")
        return False

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == '--auto':
        # Command-line mode for automation
        process_single_file_cli(sys.argv[2])
    else:
        # Normal GUI mode
        root = tk.Tk()
        app = PDFCleanerGUI(root)
        root.mainloop()
```

**Step 3: Create a Windows Task**

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create a New Task**
   - Click "Create Task" (not "Create Basic Task")
   - Name it: "PDF Auto Cleaner"
   - Description: "Automatically clean PDFs when added to folder"
   - Select "Run whether user is logged on or not"
   - Check "Run with highest privileges"

3. **Configure Triggers**
   - Go to the "Triggers" tab
   - Click "New"
   - Begin the task: "At log on"
   - Click "OK"

4. **Configure Actions**
   - Go to the "Actions" tab
   - Click "New"
   - Action: "Start a program"
   - Program/script: `pythonw.exe` (for background) or `python.exe` (for visible window)
   - Add arguments: `"C:\path\to\pdf_auto_cleaner.py"`
   - Start in: `C:\path\to\` (folder containing the scripts)
   - Click "OK"

5. **Configure Settings**
   - Go to the "Settings" tab
   - Check "Allow task to be run on demand"
   - Check "Run task as soon as possible after a scheduled start is missed"
   - Uncheck "Stop the task if it runs longer than"
   - Click "OK"

6. **Save and Test**
   - Enter your Windows password when prompted
   - Right-click the task and select "Run"
   - Check the log file to verify it's working

#### Method 2: Startup Folder (Simple)

For a simpler approach that runs when Windows starts:

**Step 1: Create a Batch File**

Create `start_pdf_monitor.bat`:

```batch
@echo off
cd /d "C:\path\to\your\scripts"
pythonw pdf_auto_cleaner.py
```

**Step 2: Add to Startup**

1. Press `Win + R`, type `shell:startup`, press Enter
2. Copy `start_pdf_monitor.bat` to the Startup folder
3. The monitor will start automatically on boot

#### Method 3: Windows Service (Advanced)

For always-on monitoring even when not logged in:

**Step 1: Install NSSM (Non-Sucking Service Manager)**

```bash
choco install nssm
```

**Step 2: Create the Service**

```bash
nssm install PDFCleaner "C:\Python39\python.exe" "C:\path\to\pdf_auto_cleaner.py"
nssm set PDFCleaner AppDirectory "C:\path\to\"
nssm set PDFCleaner DisplayName "PDF Auto Cleaner Service"
nssm set PDFCleaner Description "Automatically processes new PDF files"
nssm set PDFCleaner Start SERVICE_AUTO_START
nssm start PDFCleaner
```

**Step 3: Manage the Service**

```bash
# Stop the service
nssm stop PDFCleaner

# Start the service
nssm start PDFCleaner

# Remove the service
nssm remove PDFCleaner confirm
```

### Automation Features

- **Instant Processing**: New PDFs are detected and processed within seconds
- **Background Operation**: Runs silently without interrupting your work
- **Automatic Backups**: Original files are backed up before processing
- **Error Logging**: All operations logged for troubleshooting
- **Resource Efficient**: Minimal CPU and memory usage

### Customizing Automation Behavior

Edit `pdf_auto_cleaner.py` to customize:

```python
# Change the monitored folder
WATCH_FOLDER = r"C:\Users\YourUsername\Downloads"

# Adjust processing delay (in seconds)
PROCESS_DELAY = 5  # Wait before processing new files

# Enable/disable backups
create_backup=True  # Change to False to disable backups

# Monitor subdirectories
observer.schedule(event_handler, WATCH_FOLDER, recursive=True)  # Add recursive=True
```

### Stopping Automation

**Task Scheduler Method:**
1. Open Task Scheduler
2. Find "PDF Auto Cleaner"
3. Right-click → Disable or Delete

**Startup Folder Method:**
1. Press `Win + R`, type `shell:startup`
2. Delete `start_pdf_monitor.bat`
3. Kill the process: `taskkill /F /IM pythonw.exe`

**Windows Service Method:**
```bash
nssm stop PDFCleaner
nssm remove PDFCleaner confirm
```

### Automation Best Practices

✅ **Do:**
- Test with a few files first before full automation
- Keep backups enabled initially
- Monitor log files regularly
- Use a dedicated folder for auto-processing
- Ensure sufficient disk space for backups

❌ **Don't:**
- Monitor system folders (Windows, Program Files)
- Disable backups until you're confident
- Process files you don't have rights to modify
- Monitor folders with thousands of PDFs without testing

## 🔧 How It Works

### Processing Pipeline

The application follows a two-step process for each PDF:

```
1. Restriction Removal (qpdf)
   ├─ Removes password protection
   ├─ Removes printing restrictions
   ├─ Removes editing restrictions
   └─ Removes copying restrictions

2. Link Removal (pikepdf)
   ├─ Scans all pages for annotations
   ├─ Identifies link annotations
   ├─ Removes link annotations
   └─ Preserves other annotations
```

### Technical Details

#### Step 1: Decryption with qpdf
```bash
qpdf --decrypt input.pdf output.pdf
```
- Uses `qpdf` to create an unlocked copy
- Removes all security restrictions
- Preserves document content and formatting

#### Step 2: Link Removal with pikepdf
```python
for page in pdf.pages:
    if "/Annots" in page:
        annots = page["/Annots"]
        new_annots = [a for a in annots if a.get("/Subtype") != "/Link"]
        page["/Annots"] = new_annots
```
- Opens the unlocked PDF
- Iterates through each page
- Filters out link annotations
- Preserves other annotations (comments, highlights, etc.)

### Folder Structure

During processing, the tool creates temporary folders:

```
your_pdf_folder/
├── document1.pdf (processed)
├── document2.pdf (processed)
├── _temp_unlocked/ (temporary, auto-deleted)
└── _backups_20250105_143022/ (if backup enabled)
    ├── document1.pdf (original)
    └── document2.pdf (original)
```

## ⚙️ Configuration

### Backup Settings

**Enabled by default** - Creates timestamped backup folders

```python
backup_var = tk.BooleanVar(value=True)  # Change to False to disable by default
```

### Logging Configuration

Modify logging settings in the code:

```python
logging.basicConfig(
    filename='pdf_cleaner.log',      # Log file name
    level=logging.INFO,              # Logging level (DEBUG, INFO, WARNING, ERROR)
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### GUI Customization

Window size and appearance:

```python
root.geometry("550x380")  # Window size (width x height)
root.resizable(False, False)  # Allow/prevent resizing
```

## 📝 Logging

### Log File Location

`pdf_cleaner.log` in the same directory as the script

### Log Levels

- **INFO**: Normal operations (file processing, backups, etc.)
- **WARNING**: Non-critical issues (skipped locked files)
- **ERROR**: Critical failures (processing errors, backup failures)

### Example Log Output

```
2025-01-05 14:30:22 - INFO - Application started
2025-01-05 14:30:45 - INFO - Processing: document1.pdf
2025-01-05 14:30:45 - INFO - Backup created: /path/to/backups/document1.pdf
2025-01-05 14:30:46 - INFO - Success: document1.pdf (removed 3 links)
2025-01-05 14:30:47 - WARNING - Skipped (locked): protected.pdf
2025-01-05 14:30:50 - INFO - Summary - Success: 5, Skipped: 1, Errors: 0
```

## 🔍 Troubleshooting

### Common Issues

#### "qpdf is not installed"
**Solution**: Install qpdf using the instructions in the [Installation](#installation) section.

#### "No PDF files found in the selected folder"
**Solution**: 
- Verify the folder contains `.pdf` files (case-insensitive)
- Check file extensions are exactly `.pdf` (not `.PDF.pdf` or similar)

#### "Error: [Errno 13] Permission denied"
**Solution**:
- Close any PDFs that are open in other applications
- Run the application with administrator/sudo privileges
- Check folder permissions

#### Files are skipped (locked)
**Solution**:
- Some PDFs have encryption that `qpdf --decrypt` cannot remove
- Try opening the PDF in a viewer and re-saving it
- Use a different PDF tool to remove the encryption first

#### Application freezes or becomes unresponsive
**Solution**:
- Processing runs in a separate thread; the UI should remain responsive
- For very large files or folders, processing may take time
- Use the Cancel button if needed

#### Backup folder not created
**Solution**:
- Check the "Create backups" checkbox is enabled
- Verify write permissions in the target folder
- Check available disk space

#### Automation not working
**Solution**:
- Check Task Scheduler shows the task as "Running"
- Verify the watch folder path is correct
- Check `pdf_auto_cleaner.log` for errors
- Ensure `watchdog` is installed: `pip install watchdog`
- Test manually: `python pdf_auto_cleaner.py`

#### Service starts but doesn't process files
**Solution**:
- Verify paths in the service configuration are absolute
- Check service has appropriate permissions
- Review log files for error messages
- Ensure Python and all dependencies are accessible from service context

### Debug Mode

Enable detailed logging:

```python
logging.basicConfig(
    filename='pdf_cleaner.log',
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## ⚖️ Legal Notice

### Important Usage Guidelines

**⚠️ DISCLAIMER**: This tool is provided for legitimate use only.

#### Permitted Uses
✅ Removing restrictions from PDFs you created  
✅ Processing PDFs you have explicit permission to modify  
✅ Unlocking your own password-protected documents  
✅ Personal document management and organization  

#### Prohibited Uses
❌ Circumventing copyright protection  
❌ Removing security from copyrighted materials without permission  
❌ Processing documents you don't own or have rights to modify  
❌ Any use that violates copyright laws or terms of service  

### Legal Compliance

- Users are solely responsible for ensuring their use complies with applicable laws
- Copyright laws vary by jurisdiction
- The Digital Millennium Copyright Act (DMCA) and similar laws may apply
- Consult with a legal professional if uncertain about your use case

### No Warranty

This software is provided "AS IS" without warranty of any kind. The authors are not liable for any damages arising from its use.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Provide detailed steps to reproduce
3. Include Python version, OS, and relevant logs
4. Describe expected vs. actual behavior

### Suggesting Enhancements

1. Open an issue with the "enhancement" label
2. Clearly describe the feature and its benefits
3. Provide use cases and examples

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Add comments for complex logic
- Update documentation for new features
- Test thoroughly before submitting

## 🎯 Roadmap

### Planned Features

- [x] Subdirectory processing option
- [x] Command-line interface (CLI) mode
- [x] Automated processing with file monitoring
- [ ] Dark mode theme
- [ ] PDF metadata editing
- [ ] Batch file size optimization
- [ ] Image extraction tool
- [ ] Multi-language support
- [ ] Drag-and-drop file support
- [ ] Preview before processing
- [ ] Cloud folder monitoring (Dropbox, Google Drive)
- [ ] Email notifications for processed files
- [ ] Web dashboard for monitoring

### Version History

#### v2.0 (Current)
- ✨ Added backup functionality
- ✨ Implemented cancellation support
- ✨ Added comprehensive logging
- ✨ Created summary reports
- ✨ Added dependency checking
- ✨ Automated processing with Windows Task Scheduler
- ✨ File system monitoring support
- 🐛 Fixed cleanup issues
- 🎨 Improved UI design

#### v1.0
- 🎉 Initial release
- 🔓 Basic PDF unlocking
- 🔗 Link removal
- 📊 Progress tracking

## 📞 Support

### Getting Help

- **Documentation**: Read this README thoroughly
- **Logs**: Check `pdf_cleaner.log` for detailed error information
- **Issues**: Open an issue on the repository
- **Community**: Join discussions in the Issues section

### System Requirements

- **OS**: Windows 7+, macOS 10.12+, Linux (any modern distribution)
- **Python**: 3.7 or higher
- **RAM**: 512MB minimum (more for large PDFs)
- **Disk**: Space for backups (if enabled)

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- **qpdf** - PDF transformation library by Jay Berkenbilt
- **pikepdf** - Python library for PDF manipulation
- **watchdog** - Python library for file system monitoring
- **Python Tkinter** - Standard GUI framework
- **Community Contributors** - Thanks to all who report issues and suggest improvements

## 📚 Additional Resources

### Documentation
- [qpdf Documentation](https://qpdf.readthedocs.io/)
- [pikepdf Documentation](https://pikepdf.readthedocs.io/)
- [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Watchdog Documentation](https://python-watchdog.readthedocs.io/)
- [Windows Task Scheduler Guide](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)

### Related Tools
- [PDFtk](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/) - PDF manipulation toolkit
- [PyPDF2](https://pypdf2.readthedocs.io/) - Alternative PDF library
- [Ghostscript](https://www.ghostscript.com/) - PDF processing interpreter
- [NSSM](https://nssm.cc/) - Windows service manager

---

**Made with ❤️ for the PDF processing community**

*Last Updated: November 20, 2025*