import sys
import os

# Add the script directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Change to script directory
os.chdir(script_dir)

# Import and run the main application
if __name__ == "__main__":
    try:
        from gui_script_runner import main
        main()
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start KiKit Runner:\n{str(e)}")
        root.destroy()