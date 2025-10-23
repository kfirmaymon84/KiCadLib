import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json
import time

class ScriptRunner:
    def __init__(self, root):
        self.root = root
        self.root.title("KiKit Runner")
        self.root.geometry("700x500")
        
        # Configuration file path
        self.config_file = "kicad_runner_config.json"
        
        # Variables to store file paths
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.preset_file = tk.StringVar()
        self.kicad_path = tk.StringVar()
        
        # Load saved settings
        self.load_settings()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weight
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # KiCad path selection
        ttk.Label(main_frame, text="KiCad Bin Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.kicad_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_kicad_path).grid(row=0, column=2, pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Input file selection
        ttk.Label(main_frame, text="Input File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_input_file).grid(row=2, column=2, pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output_file).grid(row=3, column=2, pady=5)
        
        # Preset file selection
        ttk.Label(main_frame, text="Preset File:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.preset_file, width=50).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_preset_file).grid(row=4, column=2, pady=5)
        
        # Command template
        ttk.Label(main_frame, text="Command Template:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.command_template = tk.Text(main_frame, height=4, width=60)
        self.command_template.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.command_template.insert('1.0', 'kikit panelize --preset "{preset_file}" "{input_file}" "{output_file}"')
        
        # Info label
        ttk.Label(main_frame, text="Use {input_file}, {output_file}, {preset_file} as placeholders in your command").grid(row=7, column=0, columnspan=3, pady=5)
        
        # Run button
        self.run_button = ttk.Button(main_frame, text="Run Command", command=self.run_command)
        self.run_button.grid(row=8, column=0, columnspan=3, pady=20)
        
        # Output text area
        ttk.Label(main_frame, text="Output:").grid(row=9, column=0, sticky=tk.W, pady=5)
        
        # Create frame for text widget and scrollbar
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = tk.Text(output_frame, height=10, width=60)
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main_frame row weight for output area
        main_frame.rowconfigure(10, weight=1)
    
    def browse_kicad_path(self):
        folder = filedialog.askdirectory(
            title="Select KiCad Bin Directory (e.g., C:\\Program Files\\KiCad\\9.0\\bin)",
            initialdir="C:\\Program Files"
        )
        if folder:
            # Validate that this is a proper KiCad bin directory
            if self.validate_kicad_path(folder):
                self.kicad_path.set(folder)
                self.save_settings()
                messagebox.showinfo("Success", f"KiCad path set to:\n{folder}")
            else:
                messagebox.showerror(
                    "Invalid Path", 
                    f"The selected directory does not appear to be a valid KiCad bin directory.\n\n"
                    f"Please select the 'bin' folder inside your KiCad installation.\n"
                    f"Example: C:\\Program Files\\KiCad\\9.0\\bin"
                )
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[("KiCad PCB files", "*.kicad_pcb"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-detect panel folder and files
            self.auto_detect_panel_files(filename)
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Select Output File",
            filetypes=[("KiCad PCB files", "*.kicad_pcb"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def browse_preset_file(self):
        filename = filedialog.askopenfilename(
            title="Select Preset File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.preset_file.set(filename)
    
    def auto_detect_panel_files(self, input_file_path):
        """Auto-detect panel folder and populate output/preset file paths"""
        try:
            # Get the directory containing the input file
            input_dir = os.path.dirname(input_file_path)
            input_filename = os.path.basename(input_file_path)
            input_name_without_ext = os.path.splitext(input_filename)[0]
            
            # Look for a "panel" folder (case insensitive) in the same directory
            panel_folder = None
            
            for item in os.listdir(input_dir):
                item_path = os.path.join(input_dir, item)
                if os.path.isdir(item_path) and item.lower() == 'panel':
                    panel_folder = item_path
                    break
            
            if panel_folder:
                self.output_text.insert(tk.END, f"Found panel folder: {panel_folder}\n")
                
                # Look for output file in panel folder
                output_file_found = False
                preset_file_found = False
                
                # Search for potential output files
                potential_output_names = [
                    f"{input_name_without_ext}.kicad_pcb",  # Same name as input
                    f"{input_name_without_ext}_panel.kicad_pcb",  # With _panel suffix
                    f"panel.kicad_pcb",  # Generic panel name
                ]
                
                for output_name in potential_output_names:
                    output_path = os.path.join(panel_folder, output_name)
                    if os.path.exists(output_path):
                        self.output_file.set(output_path)
                        self.output_text.insert(tk.END, f"Auto-detected output file: {output_name}\n")
                        output_file_found = True
                        break
                
                # If no existing output file found, suggest a path
                if not output_file_found:
                    suggested_output = os.path.join(panel_folder, f"{input_name_without_ext}.kicad_pcb")
                    self.output_file.set(suggested_output)
                    self.output_text.insert(tk.END, f"Suggested output file: {os.path.basename(suggested_output)}\n")
                
                # Look for KiKit preset files
                preset_extensions = ['.json', '.kikit', '.preset']
                potential_preset_names = [
                    'kikit.json',
                    'preset.json',
                    'panel.json',
                    f"{input_name_without_ext}.json",
                    'config.json'
                ]
                
                for preset_name in potential_preset_names:
                    preset_path = os.path.join(panel_folder, preset_name)
                    if os.path.exists(preset_path):
                        self.preset_file.set(preset_path)
                        self.output_text.insert(tk.END, f"Auto-detected preset file: {preset_name}\n")
                        preset_file_found = True
                        break
                
                # Also check for any .json files in panel folder
                if not preset_file_found:
                    for item in os.listdir(panel_folder):
                        if item.lower().endswith('.json'):
                            preset_path = os.path.join(panel_folder, item)
                            self.preset_file.set(preset_path)
                            self.output_text.insert(tk.END, f"Found JSON file (assumed preset): {item}\n")
                            preset_file_found = True
                            break
                
                # Show summary
                if output_file_found and preset_file_found:
                    self.output_text.insert(tk.END, "✓ Auto-detection complete - output and preset files found!\n\n")
                elif output_file_found or preset_file_found:
                    found_items = []
                    if output_file_found:
                        found_items.append(f"Output: {os.path.basename(self.output_file.get())}")
                    if preset_file_found:
                        found_items.append(f"Preset: {os.path.basename(self.preset_file.get())}")
                    
                    self.output_text.insert(tk.END, f"✓ Partially auto-detected: {', '.join(found_items)}\n\n")
                else:
                    self.output_text.insert(tk.END, "Panel folder found but no preset/output files detected\n\n")
                
                self.output_text.update()
            else:
                self.output_text.insert(tk.END, "No 'panel' folder found in input file directory\n\n")
                self.output_text.update()
                
        except Exception as e:
            self.output_text.insert(tk.END, f"Error during auto-detection: {str(e)}\n\n")
            self.output_text.update()
    
    def run_command(self):
        # Get the command template
        command_template = self.command_template.get('1.0', tk.END).strip()
        
        if not command_template:
            messagebox.showerror("Error", "Please enter a command template")
            return
        
        # Check if output file is open and handle it
        output_file = self.output_file.get()
        if output_file and os.path.exists(output_file):
            # Debug: Always show the file check dialog to test closing
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.END, f"Checking if file is open: {output_file}\n")
            self.output_text.update()
            
            is_open = self.is_file_open(output_file)
            self.output_text.insert(tk.END, f"File open status: {is_open}\n")
            self.output_text.update()
            
            if is_open or True:  # Force the dialog to always appear for testing
                response = messagebox.askyesnocancel(
                    "File Open", 
                    f"The output file appears to be open:\n{os.path.basename(output_file)}\n\n"
                    "Would you like to:\n"
                    "• Yes: Try to close it automatically\n"
                    "• No: Continue anyway (may fail)\n"
                    "• Cancel: Stop the operation",
                    icon="warning"
                )
                if response is None:  # Cancel
                    return
                elif response:  # Yes - try to close
                    success = self.close_file_aggressively(output_file)
                    if not success:
                        retry_response = messagebox.askyesno(
                            "Could Not Close File",
                            f"Unable to automatically close the file:\n{os.path.basename(output_file)}\n\n"
                            "Please close it manually in KiCad and try again.\n\n"
                            "Continue anyway?",
                            icon="warning"
                        )
                        if not retry_response:
                            return
        
        # Replace placeholders with actual file paths
        command = command_template.format(
            input_file=self.input_file.get() or "{input_file}",
            output_file=self.output_file.get() or "{output_file}",
            preset_file=self.preset_file.get() or "{preset_file}"
        )
        
        # Clear output text
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, f"Running command: {command}\n\n")
        self.output_text.update()
        
        # Disable run button while running
        self.run_button.config(state='disabled')
        
        try:
            # Run the command in KiCad Command Prompt environment
            # Use user-specified KiCad path or try to find KiCad installation
            kicad_bin_path = self.kicad_path.get().strip()
            
            # Validate user-specified path
            if kicad_bin_path and not self.validate_kicad_path(kicad_bin_path):
                self.output_text.insert(tk.END, f"Warning: Specified KiCad path is invalid: {kicad_bin_path}\n")
                self.output_text.insert(tk.END, "Trying to auto-detect KiCad installation...\n")
                kicad_bin_path = ""
            
            if not kicad_bin_path:
                # Try to find KiCad installation path
                kicad_paths = [
                    r"C:\Program Files\KiCad\9.0\bin",
                    r"C:\Program Files (x86)\KiCad\9.0\bin",
                    r"C:\KiCad\9.0\bin"
                ]
                
                for path in kicad_paths:
                    if self.validate_kicad_path(path):
                        kicad_bin_path = path
                        break
            
            if kicad_bin_path and self.validate_kicad_path(kicad_bin_path):
                # Set up environment variables like KiCad Command Prompt does
                env = os.environ.copy()
                env['PATH'] = f"{kicad_bin_path};{env.get('PATH', '')}"
                env['KICAD_USER_TEMPLATE_DIR'] = os.path.join(os.path.expanduser('~'), 'Documents', 'KiCad', '9.0', 'template')
                
                self.output_text.insert(tk.END, f"Using KiCad from: {kicad_bin_path}\n")
                
                # Check if kikit is available
                if not self.check_kikit_installation(kicad_bin_path, env):
                    self.output_text.insert(tk.END, "\n❌ KiKit is not installed!\n")
                    self.output_text.insert(tk.END, "To install KiKit, run the following command in KiCad Command Prompt:\n")
                    self.output_text.insert(tk.END, "pip install kikit\n\n")
                    self.output_text.insert(tk.END, "Or open KiCad Command Prompt and run:\n")
                    self.output_text.insert(tk.END, f'"{os.path.join(kicad_bin_path, "python.exe")}" -m pip install kikit\n\n')
                    
                    response = messagebox.askyesno(
                        "KiKit Not Installed",
                        "KiKit is not installed in your KiCad environment.\n\n"
                        "Would you like to try installing it automatically?\n"
                        "(This will run: pip install kikit)",
                        icon="warning"
                    )
                    
                    if response:
                        self.install_kikit(kicad_bin_path, env)
                        return
                    else:
                        self.run_button.config(state='normal')
                        return
                
                self.output_text.update()
            else:
                env = os.environ.copy()
                self.output_text.insert(tk.END, "Warning: Valid KiCad installation not found!\n")
                self.output_text.insert(tk.END, "Please set the correct KiCad bin path (e.g., C:\\Program Files\\KiCad\\9.0\\bin)\n")
                self.output_text.insert(tk.END, "Attempting to run with system PATH...\n\n")
                self.output_text.update()
            
            # Use KiCad Command Prompt if available
            if kicad_bin_path and self.validate_kicad_path(kicad_bin_path):
                kicad_cmd_bat = os.path.join(kicad_bin_path, "kicad-cmd.bat")
                if os.path.exists(kicad_cmd_bat):
                    # Run command through KiCad Command Prompt
                    cmd_command = f'"{kicad_cmd_bat}" && {command}'
                    self.output_text.insert(tk.END, f"Running through KiCad Command Prompt...\n")
                    self.output_text.update()
                else:
                    cmd_command = command
            else:
                cmd_command = command
            
            process = subprocess.Popen(
                cmd_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line
            for line in iter(process.stdout.readline, ''):
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
                self.output_text.update()
            
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                self.output_text.insert(tk.END, "\n✓ Command completed successfully!")
                
                # Suggest reopening output file if it exists
                if output_file and os.path.exists(output_file):
                    self.output_text.insert(tk.END, f"\n\nOutput file created: {os.path.basename(output_file)}")
                    response = messagebox.askyesno(
                        "Open Output File", 
                        f"Command completed successfully!\n\n"
                        f"Would you like to open the output file?\n{os.path.basename(output_file)}",
                        icon="question"
                    )
                    if response:
                        self.open_file_with_default_app(output_file)
            else:
                self.output_text.insert(tk.END, f"\n✗ Command failed with return code {process.returncode}")
                
        except Exception as e:
            self.output_text.insert(tk.END, f"\nError running command: {str(e)}")
            
        finally:
            # Re-enable run button
            self.run_button.config(state='normal')
            self.output_text.see(tk.END)
    
    def is_file_open(self, file_path):
        """Check if a file is currently open by multiple methods"""
        if not os.path.exists(file_path):
            return False
        
        # Method 1: Try to open file in exclusive mode
        try:
            with open(file_path, 'r+b') as f:
                pass
            # If we got here, file is not exclusively locked
        except (IOError, OSError, PermissionError) as e:
            if "being used by another process" in str(e) or "Permission denied" in str(e):
                return True
        
        # Method 2: Try to rename the file temporarily
        try:
            temp_name = file_path + ".tmp_check"
            os.rename(file_path, temp_name)
            os.rename(temp_name, file_path)
            return False  # File is not open
        except (OSError, IOError, PermissionError):
            return True  # File is likely open
        
        # Method 3: Use psutil to check if any process has the file open
        try:
            import psutil
            file_path_abs = os.path.abspath(file_path)
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for f in proc.open_files():
                        if hasattr(f, 'path') and os.path.abspath(f.path) == file_path_abs:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except ImportError:
            pass
        
        return False
    
    def close_file_if_open(self, file_path):
        """Attempt to close a file by terminating processes that have it open"""
        self.output_text.insert(tk.END, f"Attempting to close file: {os.path.basename(file_path)}\n")
        self.output_text.update()
        
        try:
            import psutil
            file_path = os.path.abspath(file_path)
            
            # Find processes that have the file open
            processes_to_close = []
            self.output_text.insert(tk.END, "Scanning for processes with file open...\n")
            self.output_text.update()
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    open_files = proc.open_files()
                    if open_files:
                        for f in open_files:
                            if hasattr(f, 'path') and os.path.abspath(f.path) == file_path:
                                processes_to_close.append(proc)
                                self.output_text.insert(tk.END, f"Found process: {proc.info['name']} (PID: {proc.info['pid']})\n")
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if processes_to_close:
                self.output_text.insert(tk.END, f"Found {len(processes_to_close)} process(es) with file open\n")
                for proc in processes_to_close:
                    try:
                        proc_name = proc.info['name']
                        self.output_text.insert(tk.END, f"Closing {proc_name} (PID: {proc.info['pid']})\n")
                        self.output_text.update()
                        
                        # Try graceful termination first
                        proc.terminate()
                        proc.wait(timeout=5)
                        
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        try:
                            # Force kill if graceful termination fails
                            proc.kill()
                        except psutil.NoSuchProcess:
                            pass
                    except Exception as e:
                        self.output_text.insert(tk.END, f"Error closing process: {str(e)}\n")
                
                # Wait a moment and check if file is still open
                time.sleep(1)
                if not self.is_file_open(file_path):
                    self.output_text.insert(tk.END, f"✓ Successfully closed file: {os.path.basename(file_path)}\n")
                    return True
                else:
                    self.output_text.insert(tk.END, f"✗ File may still be open: {os.path.basename(file_path)}\n")
                    return False
            else:
                # No specific processes found, try closing common KiCad processes
                self.output_text.insert(tk.END, "No specific processes found, trying to close KiCad applications...\n")
                self.output_text.update()
                return self.close_kicad_processes_fallback(file_path)
                
        except ImportError:
            # psutil not available, try simpler approach
            return self.close_file_simple(file_path)
        except Exception as e:
            self.output_text.insert(tk.END, f"Error attempting to close file: {str(e)}\n")
            return False
    
    def close_kicad_processes_fallback(self, file_path):
        """Fallback method to close KiCad processes when file is locked"""
        try:
            import psutil
            kicad_process_names = ['kicad.exe', 'pcbnew.exe', 'eeschema.exe', 'kicad-cli.exe']
            closed_any = False
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in [name.lower() for name in kicad_process_names]:
                        self.output_text.insert(tk.END, f"Closing KiCad process: {proc.info['name']} (PID: {proc.info['pid']})\n")
                        self.output_text.update()
                        
                        # Ask user for confirmation
                        response = messagebox.askyesno(
                            "Close KiCad Application",
                            f"Close {proc.info['name']} to free the file?\n\n"
                            f"Make sure to save your work first!",
                            icon="warning"
                        )
                        
                        if response:
                            proc.terminate()
                            try:
                                proc.wait(timeout=5)
                            except psutil.TimeoutExpired:
                                proc.kill()
                            closed_any = True
                            time.sleep(1)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if closed_any:
                time.sleep(2)
                result = not self.is_file_open(file_path)
                if result:
                    self.output_text.insert(tk.END, "✓ File is now available!\n")
                else:
                    self.output_text.insert(tk.END, "✗ File may still be locked\n")
                return result
            
            return False
        except ImportError:
            return self.close_file_simple(file_path)
        except Exception as e:
            self.output_text.insert(tk.END, f"Error in fallback close: {str(e)}\n")
            return False
    
    def close_file_aggressively(self, file_path):
        """Aggressively close all KiCad processes to free the file"""
        self.output_text.insert(tk.END, f"\n=== ATTEMPTING TO CLOSE FILE: {os.path.basename(file_path)} ===\n")
        self.output_text.update()
        
        success = False
        
        # Step 1: Try to close all KiCad processes without asking
        kicad_processes = ['pcbnew.exe', 'kicad.exe', 'eeschema.exe', 'kicad-cli.exe']
        
        for proc_name in kicad_processes:
            try:
                # Check if process is running
                result = subprocess.run(
                    ['tasklist', '/fi', f'imagename eq {proc_name}'],
                    capture_output=True, text=True, shell=True
                )
                
                if proc_name.lower() in result.stdout.lower():
                    self.output_text.insert(tk.END, f"Found {proc_name} - attempting to close...\n")
                    self.output_text.update()
                    
                    # Force close the process
                    kill_result = subprocess.run(
                        ['taskkill', '/f', '/im', proc_name],
                        capture_output=True, text=True, shell=True
                    )
                    
                    if kill_result.returncode == 0:
                        self.output_text.insert(tk.END, f"✓ Successfully closed {proc_name}\n")
                        success = True
                    else:
                        self.output_text.insert(tk.END, f"✗ Failed to close {proc_name}: {kill_result.stderr}\n")
                    
                    self.output_text.update()
                    time.sleep(1)
            
            except Exception as e:
                self.output_text.insert(tk.END, f"Error processing {proc_name}: {str(e)}\n")
        
        # Step 2: Wait and check if file is now available
        self.output_text.insert(tk.END, "Waiting for processes to fully close...\n")
        self.output_text.update()
        time.sleep(3)
        
        # Step 3: Test if file is now available
        file_now_available = not self.is_file_open(file_path)
        
        if file_now_available:
            self.output_text.insert(tk.END, "✓ SUCCESS: File is now available for writing!\n")
            success = True
        else:
            self.output_text.insert(tk.END, "✗ FAILED: File is still locked\n")
            
            # Step 4: Last resort - try to delete and recreate
            try:
                backup_path = file_path + ".backup"
                if os.path.exists(file_path):
                    self.output_text.insert(tk.END, "Attempting to backup and recreate file...\n")
                    os.rename(file_path, backup_path)
                    # Create empty file
                    with open(file_path, 'w') as f:
                        f.write("")
                    os.remove(file_path)  # Remove the empty file we just created
                    os.rename(backup_path, file_path)  # Restore original
                    self.output_text.insert(tk.END, "✓ File manipulation successful\n")
                    success = True
            except Exception as e:
                self.output_text.insert(tk.END, f"File manipulation failed: {str(e)}\n")
        
        self.output_text.insert(tk.END, f"=== FILE CLOSING ATTEMPT COMPLETE ===\n\n")
        self.output_text.update()
        
        return success
    
    def close_file_if_open(self, file_path):
        """Simple approach to close file without psutil"""
        try:
            # Try to find and close KiCad processes
            kicad_processes = ['kicad.exe', 'pcbnew.exe', 'eeschema.exe', 'kicad-cli.exe']
            closed_any = False
            
            self.output_text.insert(tk.END, "Checking for KiCad processes...\n")
            self.output_text.update()
            
            for proc_name in kicad_processes:
                try:
                    result = subprocess.run(
                        ['tasklist', '/fi', f'imagename eq {proc_name}'],
                        capture_output=True, text=True, shell=True
                    )
                    if proc_name.lower() in result.stdout.lower():
                        self.output_text.insert(tk.END, f"Found {proc_name} running\n")
                        self.output_text.update()
                        
                        # Ask user if they want to close this process
                        response = messagebox.askyesno(
                            "Close KiCad Application",
                            f"Found {proc_name} running.\n\n"
                            f"Close it to free the file?\n"
                            f"(Make sure to save your work first!)",
                            icon="warning"
                        )
                        if response:
                            self.output_text.insert(tk.END, f"Closing {proc_name}...\n")
                            self.output_text.update()
                            subprocess.run(['taskkill', '/f', '/im', proc_name], 
                                         capture_output=True, shell=True)
                            closed_any = True
                            time.sleep(2)
                except Exception as e:
                    self.output_text.insert(tk.END, f"Error checking {proc_name}: {str(e)}\n")
            
            if closed_any:
                time.sleep(2)  # Give time for processes to fully close
                result = not self.is_file_open(file_path)
                if result:
                    self.output_text.insert(tk.END, "✓ File should now be available!\n")
                else:
                    self.output_text.insert(tk.END, "✗ File may still be locked\n")
                return result
            else:
                self.output_text.insert(tk.END, "No KiCad processes found running\n")
            
            return False
        except Exception as e:
            self.output_text.insert(tk.END, f"Error in simple close: {str(e)}\n")
            return False
    
    def open_file_with_default_app(self, file_path):
        """Open a file with the default application"""
        try:
            os.startfile(file_path)  # Windows
        except AttributeError:
            try:
                subprocess.run(['open', file_path])  # macOS
            except FileNotFoundError:
                subprocess.run(['xdg-open', file_path])  # Linux
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def check_kikit_installation(self, kicad_bin_path, env):
        """Check if KiKit is installed in the KiCad Python environment"""
        try:
            kicad_cmd_bat = os.path.join(kicad_bin_path, "kicad-cmd.bat")
            if os.path.exists(kicad_cmd_bat):
                # Use KiCad Command Prompt to check for kikit
                result = subprocess.run(
                    f'"{kicad_cmd_bat}" && kikit --help',
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=15
                )
                return result.returncode == 0
            else:
                # Fallback to direct python check
                python_exe = os.path.join(kicad_bin_path, "python.exe")
                if not os.path.exists(python_exe):
                    return False
                
                result = subprocess.run(
                    [python_exe, "-m", "pip", "show", "kikit"],
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=10
                )
                return result.returncode == 0
        except Exception:
            return False
    
    def install_kikit(self, kicad_bin_path, env):
        """Attempt to install KiKit in the KiCad Python environment"""
        try:
            kicad_cmd_bat = os.path.join(kicad_bin_path, "kicad-cmd.bat")
            
            self.output_text.insert(tk.END, "Installing KiKit...\n")
            self.output_text.update()
            
            if os.path.exists(kicad_cmd_bat):
                # Use KiCad Command Prompt to install kikit
                install_command = f'"{kicad_cmd_bat}" && pip install kikit'
                process = subprocess.Popen(
                    install_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            else:
                # Fallback to direct python approach
                python_exe = os.path.join(kicad_bin_path, "python.exe")
                if not os.path.exists(python_exe):
                    messagebox.showerror("Error", f"Neither kicad-cmd.bat nor python.exe found at: {kicad_bin_path}")
                    return False
                
                process = subprocess.Popen(
                    [python_exe, "-m", "pip", "install", "kikit"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env
                )
            
            # Read output line by line
            for line in iter(process.stdout.readline, ''):
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
                self.output_text.update()
            
            process.wait()
            
            if process.returncode == 0:
                self.output_text.insert(tk.END, "\n✓ KiKit installed successfully!\n")
                self.output_text.insert(tk.END, "You can now run KiKit commands.\n\n")
                messagebox.showinfo("Success", "KiKit has been installed successfully!")
                return True
            else:
                self.output_text.insert(tk.END, f"\n✗ KiKit installation failed with return code {process.returncode}\n")
                messagebox.showerror("Error", "KiKit installation failed. Please install manually.")
                return False
                
        except Exception as e:
            self.output_text.insert(tk.END, f"\nError installing KiKit: {str(e)}\n")
            messagebox.showerror("Error", f"Error installing KiKit: {str(e)}")
            return False
        finally:
            self.run_button.config(state='normal')
    
    def validate_kicad_path(self, path):
        """Validate that a path is a proper KiCad bin directory"""
        if not path or not os.path.exists(path):
            return False
        
        # Check for key KiCad files
        kicad_executables = ['kicad.exe', 'pcbnew.exe', 'kicad-cmd.bat']
        python_dir = os.path.join(path, 'Plugins')
        
        # Check if it's a bin directory with KiCad executables
        has_kicad_exe = any(os.path.exists(os.path.join(path, exe)) for exe in kicad_executables)
        
        # Check for Python environment (where kikit would be installed)
        has_python = os.path.exists(python_dir) or os.path.exists(os.path.join(path, 'python.exe'))
        
        # Check for kicad-cmd.bat specifically (this is the key file for KiCad Command Prompt)
        has_cmd_bat = os.path.exists(os.path.join(path, 'kicad-cmd.bat'))
        
        return has_kicad_exe or has_python or has_cmd_bat
    
    def load_settings(self):
        """Load settings from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.kicad_path.set(config.get('kicad_path', ''))
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to configuration file"""
        try:
            config = {
                'kicad_path': self.kicad_path.get()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

def main():
    root = tk.Tk()
    app = ScriptRunner(root)
    root.mainloop()

if __name__ == "__main__":
    main()