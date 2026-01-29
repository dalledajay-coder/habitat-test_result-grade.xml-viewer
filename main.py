"""
XML Test Results Viewer
A Windows application to view JUnit XML test reports in a tree structure.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import json
import os
import sys


class XMLTestViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Test Results Viewer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a2e")
        
        # Style configuration
        self.setup_styles()
        
        # Main container
        self.main_frame = ttk.Frame(root, style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Content area
        self.content_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Tree view with scrollbar
        self.create_tree_view()
        
        # Details panel
        self.create_details_panel()
        
        # Status bar
        self.create_status_bar()
        
        # Store test data
        self.test_data = {}
        self.failed_suites = {}
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Colors
        bg_dark = "#1a1a2e"
        bg_medium = "#16213e"
        bg_light = "#0f3460"
        accent = "#e94560"
        success = "#00d9a0"
        text_light = "#eaeaea"
        text_muted = "#a0a0a0"
        
        # Frame styles
        style.configure("Main.TFrame", background=bg_dark)
        style.configure("Tree.TFrame", background=bg_medium)
        style.configure("Details.TFrame", background=bg_medium)
        
        # Label styles
        style.configure("Header.TLabel", 
                       background=bg_dark, 
                       foreground=text_light,
                       font=("Segoe UI", 24, "bold"))
        style.configure("SubHeader.TLabel",
                       background=bg_dark,
                       foreground=text_muted,
                       font=("Segoe UI", 10))
        style.configure("Status.TLabel",
                       background=bg_medium,
                       foreground=text_muted,
                       font=("Segoe UI", 9))
        
        # Button styles
        style.configure("Open.TButton",
                       background=bg_light,
                       foreground=text_light,
                       font=("Segoe UI", 10, "bold"),
                       padding=(20, 10))
        style.map("Open.TButton",
                 background=[("active", accent)])
        
        style.configure("Copy.TButton",
                       background=accent,
                       foreground=text_light,
                       font=("Segoe UI", 9),
                       padding=(8, 4))
        style.map("Copy.TButton",
                 background=[("active", "#ff6b6b")])
        
        # Treeview styles
        style.configure("Custom.Treeview",
                       background=bg_medium,
                       foreground=text_light,
                       fieldbackground=bg_medium,
                       font=("Consolas", 10),
                       rowheight=28)
        style.configure("Custom.Treeview.Heading",
                       background=bg_light,
                       foreground=text_light,
                       font=("Segoe UI", 10, "bold"))
        style.map("Custom.Treeview",
                 background=[("selected", bg_light)],
                 foreground=[("selected", text_light)])
        
    def create_header(self):
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X)
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="XML Test Results Viewer",
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Open button
        self.open_btn = ttk.Button(header_frame,
                                   text="📂 Open XML File",
                                   style="Open.TButton",
                                   command=self.open_file)
        self.open_btn.pack(side=tk.RIGHT, padx=5)
        
        # Subtitle
        subtitle_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        subtitle_frame.pack(fill=tk.X, pady=(5, 0))
        self.subtitle_label = ttk.Label(subtitle_frame,
                                        text="Open a JUnit XML file to view test results",
                                        style="SubHeader.TLabel")
        self.subtitle_label.pack(side=tk.LEFT)
        
    def create_tree_view(self):
        # Left panel for tree
        tree_frame = ttk.Frame(self.content_frame, style="Tree.TFrame")
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Tree container with border
        tree_container = tk.Frame(tree_frame, bg="#0f3460", bd=2)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(tree_container,
                                 style="Custom.Treeview",
                                 yscrollcommand=y_scroll.set,
                                 xscrollcommand=x_scroll.set,
                                 columns=("status", "tests", "failures", "time", "action"),
                                 selectmode="browse")
        
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        
        # Column configuration
        self.tree.heading("#0", text="Test Suite / Test Case", anchor=tk.W)
        self.tree.heading("status", text="Status", anchor=tk.CENTER)
        self.tree.heading("tests", text="Tests", anchor=tk.CENTER)
        self.tree.heading("failures", text="Failures", anchor=tk.CENTER)
        self.tree.heading("time", text="Time", anchor=tk.CENTER)
        self.tree.heading("action", text="", anchor=tk.CENTER)
        
        self.tree.column("#0", width=450, minwidth=300)
        self.tree.column("status", width=100, minwidth=80, anchor=tk.CENTER)
        self.tree.column("tests", width=60, minwidth=50, anchor=tk.CENTER)
        self.tree.column("failures", width=60, minwidth=50, anchor=tk.CENTER)
        self.tree.column("time", width=80, minwidth=60, anchor=tk.CENTER)
        self.tree.column("action", width=80, minwidth=60, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Bind single click on action column for copy
        self.tree.bind("<Button-1>", self.on_click)
        
        # Bind motion for cursor change on action column
        self.tree.bind("<Motion>", self.on_motion)
        
        # Tags for coloring
        self.tree.tag_configure("failure", foreground="#e94560")
        self.tree.tag_configure("success", foreground="#00d9a0")
        self.tree.tag_configure("skipped", foreground="#ffa500")
        self.tree.tag_configure("suite_fail", foreground="#ff6b6b")
        self.tree.tag_configure("suite_pass", foreground="#00d9a0")
        
    def create_details_panel(self):
        # Right panel for details
        details_frame = ttk.Frame(self.content_frame, style="Details.TFrame", width=400)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        details_frame.pack_propagate(False)
        
        # Details container
        details_container = tk.Frame(details_frame, bg="#16213e", bd=2)
        details_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header with copy button
        header_row = tk.Frame(details_container, bg="#16213e")
        header_row.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        details_label = tk.Label(header_row, 
                                text="Details",
                                bg="#16213e",
                                fg="#eaeaea",
                                font=("Segoe UI", 14, "bold"))
        details_label.pack(side=tk.LEFT)
        
        self.copy_btn = tk.Button(header_row,
                                  text="📋 Copy Failures",
                                  bg="#e94560",
                                  fg="white",
                                  font=("Segoe UI", 9, "bold"),
                                  bd=0,
                                  padx=12,
                                  pady=4,
                                  cursor="hand2",
                                  command=self.copy_selected_failures)
        self.copy_btn.pack(side=tk.RIGHT)
        self.copy_btn.bind("<Enter>", lambda e: self.copy_btn.config(bg="#ff6b6b"))
        self.copy_btn.bind("<Leave>", lambda e: self.copy_btn.config(bg="#e94560"))
        
        # Text area for details
        text_frame = tk.Frame(details_container, bg="#0f3460", bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = tk.Text(text_frame,
                                    bg="#1a1a2e",
                                    fg="#eaeaea",
                                    font=("Consolas", 10),
                                    wrap=tk.WORD,
                                    yscrollcommand=text_scroll.set,
                                    padx=10,
                                    pady=10,
                                    bd=0)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.details_text.yview)
        
        # Configure text tags
        self.details_text.tag_configure("header", foreground="#00d9a0", font=("Consolas", 11, "bold"))
        self.details_text.tag_configure("error", foreground="#e94560")
        self.details_text.tag_configure("info", foreground="#a0a0a0")
        
    def create_status_bar(self):
        status_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame,
                                      text="Ready",
                                      style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        self.stats_label = ttk.Label(status_frame,
                                     text="",
                                     style="Status.TLabel")
        self.stats_label.pack(side=tk.RIGHT)
        
    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Open XML Test Results",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filepath:
            self.load_xml(filepath)
            
    def load_xml(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Clear existing data
            self.tree.delete(*self.tree.get_children())
            self.test_data.clear()
            self.failed_suites.clear()
            
            # Parse based on root element
            if root.tag == "testsuites":
                self.parse_testsuites(root)
            elif root.tag == "testsuite":
                self.parse_testsuite(root, "")
                
            # Update UI
            filename = os.path.basename(filepath)
            self.subtitle_label.config(text=f"Loaded: {filename}")
            
            total_tests = root.get("tests", "0")
            total_failures = root.get("failures", "0")
            total_errors = root.get("errors", "0")
            total_time = root.get("time", "0")
            
            self.stats_label.config(
                text=f"Tests: {total_tests} | Failures: {total_failures} | Errors: {total_errors} | Time: {total_time}s"
            )
            self.status_label.config(text=f"Loaded {filepath}")
            
        except ET.ParseError as e:
            messagebox.showerror("Parse Error", f"Failed to parse XML: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            
    def parse_testsuites(self, root):
        for suite in root.findall("testsuite"):
            self.parse_testsuite(suite, "")
            
    def parse_testsuite(self, suite, parent_id):
        name = suite.get("name", "Unknown")
        tests = suite.get("tests", "0")
        failures = int(suite.get("failures", "0"))
        errors = int(suite.get("errors", "0"))
        skipped = int(suite.get("skipped", "0"))
        time = suite.get("time", "0")
        
        has_failures = failures > 0 or errors > 0
        
        # Status label
        if has_failures:
            status = "❌ FAILURE"
            tag = "suite_fail"
            action = "📋 Copy"
        else:
            status = "✅ PASS"
            tag = "suite_pass"
            action = ""
            
        suite_id = self.tree.insert(
            parent_id, "end",
            text=f"📁 {name}",
            values=(status, tests, failures, f"{float(time):.3f}s", action),
            tags=(tag,),
            open=has_failures  # Auto-expand failed suites
        )
        
        # Store suite data for copying
        if has_failures:
            self.failed_suites[suite_id] = {
                "name": name,
                "tests": tests,
                "failures": failures,
                "errors": errors,
                "failed_testcases": []
            }
        
        # Parse test cases
        for testcase in suite.findall("testcase"):
            self.parse_testcase(testcase, suite_id, has_failures)
            
    def parse_testcase(self, testcase, parent_id, suite_has_failures):
        name = testcase.get("name", "Unknown")
        classname = testcase.get("classname", "")
        time = testcase.get("time", "0")
        
        # Check for failure
        failure = testcase.find("failure")
        error = testcase.find("error")
        skipped = testcase.find("skipped")
        
        testcase_data = {
            "name": name,
            "classname": classname,
            "time": time,
            "failure": None
        }
        
        if failure is not None:
            status = "❌ FAIL"
            tag = "failure"
            action = "📋 Copy"
            testcase_data["failure"] = {
                "message": failure.get("message", ""),
                "type": failure.get("type", ""),
                "content": failure.text or ""
            }
        elif error is not None:
            status = "⚠️ ERROR"
            tag = "failure"
            action = "📋 Copy"
            testcase_data["failure"] = {
                "message": error.get("message", ""),
                "type": error.get("type", ""),
                "content": error.text or ""
            }
        elif skipped is not None:
            status = "⏭️ SKIP"
            tag = "skipped"
            action = ""
        else:
            status = "✅ PASS"
            tag = "success"
            action = ""
            
        case_id = self.tree.insert(
            parent_id, "end",
            text=f"  📄 {name}",
            values=(status, "", "", f"{float(time):.3f}s", action),
            tags=(tag,)
        )
        
        # Store test case data
        self.test_data[case_id] = testcase_data
        
        # Add to failed suite data if it has failure
        if testcase_data["failure"] and parent_id in self.failed_suites:
            self.failed_suites[parent_id]["failed_testcases"].append(testcase_data)
            
    def on_motion(self, event):
        """Change cursor to hand when hovering over clickable copy button"""
        column = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        
        if column == "#5" and item_id:
            # Check if this item has a copy action
            if item_id in self.failed_suites or (item_id in self.test_data and self.test_data[item_id].get("failure")):
                self.tree.config(cursor="hand2")
                return
        self.tree.config(cursor="")
        
    def on_click(self, event):
        """Handle click on action column for copy"""
        column = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        
        if not item_id:
            return
            
        # Check if clicked on action column (#5) - the copy button
        if column == "#5":
            # Check if this item has failures
            if item_id in self.failed_suites or (item_id in self.test_data and self.test_data[item_id].get("failure")):
                self.tree.selection_set(item_id)
                self.root.after(50, self.copy_selected_failures)  # Small delay to let selection update
            
    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        
        # Clear details
        self.details_text.delete(1.0, tk.END)
        
        # Check if it's a test case with data
        if item_id in self.test_data:
            data = self.test_data[item_id]
            
            self.details_text.insert(tk.END, "TEST CASE\n", "header")
            self.details_text.insert(tk.END, f"Name: {data['name']}\n", "info")
            self.details_text.insert(tk.END, f"Class: {data['classname']}\n", "info")
            self.details_text.insert(tk.END, f"Time: {data['time']}s\n\n", "info")
            
            if data["failure"]:
                self.details_text.insert(tk.END, "FAILURE DETAILS\n", "header")
                self.details_text.insert(tk.END, f"Type: {data['failure']['type']}\n", "error")
                self.details_text.insert(tk.END, f"Message: {data['failure']['message']}\n\n", "error")
                self.details_text.insert(tk.END, "Stack Trace:\n", "header")
                self.details_text.insert(tk.END, data["failure"]["content"], "error")
                
        elif item_id in self.failed_suites:
            data = self.failed_suites[item_id]
            
            self.details_text.insert(tk.END, "TEST SUITE\n", "header")
            self.details_text.insert(tk.END, f"Name: {data['name']}\n", "info")
            self.details_text.insert(tk.END, f"Tests: {data['tests']}\n", "info")
            self.details_text.insert(tk.END, f"Failures: {data['failures']}\n", "info")
            self.details_text.insert(tk.END, f"Errors: {data['errors']}\n\n", "info")
            
            self.details_text.insert(tk.END, "Click 'Copy Failures' to copy failure details\n", "info")
            
    def copy_selected_failures(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a test suite or test case")
            return
            
        item_id = selection[0]
        
        # Determine what to copy
        failures_to_copy = []
        
        if item_id in self.failed_suites:
            # Copy all failures in this suite
            suite_data = self.failed_suites[item_id]
            failures_to_copy = suite_data["failed_testcases"]
        elif item_id in self.test_data and self.test_data[item_id]["failure"]:
            # Copy single test case failure
            failures_to_copy = [self.test_data[item_id]]
        else:
            messagebox.showinfo("Info", "No failures to copy in selected item")
            return
            
        if not failures_to_copy:
            messagebox.showinfo("Info", "No failures found")
            return
            
        # Format as YAML (more readable for AI)
        yaml_output = self.format_as_yaml(failures_to_copy)
        
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(yaml_output)
        
        # Show confirmation
        self.status_label.config(text=f"Copied {len(failures_to_copy)} failure(s) to clipboard")
        messagebox.showinfo("Copied", f"Copied {len(failures_to_copy)} failure(s) to clipboard")
        
    def format_as_yaml(self, failures):
        """Format failures as YAML for better AI readability"""
        lines = ["# Test Failures Report", "failures:"]
        
        for f in failures:
            lines.append(f"  - name: \"{f['name']}\"")
            if f.get('classname'):
                lines.append(f"    classname: \"{f['classname']}\"")
            if f.get('failure'):
                lines.append("    failure:")
                lines.append(f"      type: \"{f['failure']['type']}\"")
                # Escape message for YAML
                message = f['failure']['message'].replace('"', '\\"').replace('\n', '\\n')
                lines.append(f"      message: \"{message}\"")
                # For content, use block scalar
                content = f['failure']['content']
                if content:
                    lines.append("      stacktrace: |")
                    for line in content.split('\n')[:50]:  # Limit to first 50 lines
                        lines.append(f"        {line}")
                    if len(content.split('\n')) > 50:
                        lines.append("        ... (truncated)")
                        
        return '\n'.join(lines)
    
    def format_as_json(self, failures):
        """Format failures as JSON"""
        output = []
        for f in failures:
            item = {
                "name": f['name'],
                "classname": f.get('classname', ''),
            }
            if f.get('failure'):
                item["failure"] = {
                    "message": f['failure']['message'],
                    "type": f['failure']['type'],
                    "content": f['failure']['content'][:2000]  # Truncate long content
                }
            output.append(item)
        return json.dumps(output, indent=2)


def main():
    root = tk.Tk()
    
    # Set window icon if available
    try:
        if sys.platform == "win32":
            root.iconbitmap(default='')
    except:
        pass
    
    app = XMLTestViewer(root)
    
    # Handle command line argument for file path
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            root.after(100, lambda: app.load_xml(filepath))
    
    root.mainloop()


if __name__ == "__main__":
    main()
