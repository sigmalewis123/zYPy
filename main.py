import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import sys
from io import StringIO
import os
import builtins

class CodeTab:
    def __init__(self, text_widget, line_number_widget, filepath=None):
        self.text_widget = text_widget
        self.line_number_widget = line_number_widget
        self.filepath = filepath
        self.modified = False
        
    def get_title(self):
        if self.filepath:
            return os.path.basename(self.filepath)
        return "Untitled"

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, width, height, corner_radius=20, bg_color="#1e1e1e", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg_color, bd=0, highlightthickness=0, **kwargs)
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.create_rounded_rect()

    def create_rounded_rect(self):
        self.create_arc((0, 0, self.corner_radius * 2, self.corner_radius * 2), start=0, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc((self.winfo_width() - self.corner_radius * 2, 0, self.winfo_width(), self.corner_radius * 2), start=90, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc((0, self.winfo_height() - self.corner_radius * 2, self.corner_radius * 2, self.winfo_height()), start=270, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc((self.winfo_width() - self.corner_radius * 2, self.winfo_height() - self.corner_radius * 2, self.winfo_width(), self.winfo_height()), start=180, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(self.corner_radius, 0, self.winfo_width() - self.corner_radius, self.winfo_height(), fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(0, self.corner_radius, self.winfo_width(), self.winfo_height() - self.corner_radius, fill=self.bg_color, outline=self.bg_color)

class SimpleCodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("ZYPY")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        # Create a rounded window using a canvas
        self.canvas = RoundedFrame(self.root, width=800, height=600, corner_radius=30, bg_color="#1e1e1e")
        self.canvas.pack(fill='both', expand=True)

        # Main Frame
        self.main_frame = ttk.Frame(self.canvas, style="TFrame")
        self.main_frame.place(relwidth=1, relheight=1)

        # Notebook (Tab bar)
        self.notebook = ttk.Notebook(self.main_frame, style="TNotebook")
        self.notebook.pack(expand=True, fill='both', pady=(0, 5))
        self.tabs = []

        # Create Menu Bar
        self.create_menu()

        # Buttons at the bottom
        self.button_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.button_frame.pack(pady=5)

        # Run and Clear Buttons
        self.run_button = ttk.Button(self.button_frame, text=" Run Code", command=self.run_code, style='Run.TButton')
        self.run_button.pack(side='left', padx=5)
        
        self.clear_button = ttk.Button(self.button_frame, text="", command=self.clear_editor)
        self.clear_button.pack(side='left', padx=5)

        # Output Section
        self.output_label = ttk.Label(self.main_frame, text="Output:", font=('Consolas', 10, 'bold'), background="#1e1e1e", foreground="#d4d4d4")
        self.output_label.pack(anchor='w', pady=(10,0))
        
        self.output_area = tk.Text(self.main_frame, font=('Consolas', 12), height=8, wrap='word', bg="#1e1e1e", fg="#f0f0f0", insertbackground="white")
        self.output_area.pack(expand=False, fill='both')

        self.create_new_tab()

    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#1e1e1e", fg="#f0f0f0")
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg="#1e1e1e", fg="#f0f0f0")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.create_new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Close Tab", command=self.close_current_tab, accelerator="Ctrl+W")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Key bindings for menu shortcuts
        self.root.bind('<Control-n>', lambda e: self.create_new_tab())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_file_as())
        self.root.bind('<Control-w>', lambda e: self.close_current_tab())
        self.root.bind('<Control-Tab>', lambda e: self.next_tab())
        self.root.bind('<Control-Shift-Tab>', lambda e: self.prev_tab())

    def create_new_tab(self):
        tab_frame = ttk.Frame(self.notebook)

        # Line Number Area
        line_number_frame = tk.Frame(tab_frame, bg="#2d2d2d")
        line_number_frame.pack(side='left', fill='y')

        line_number_widget = tk.Text(line_number_frame, width=4, bg="#2d2d2d", fg="#888888", font=('Consolas', 12), padx=10, pady=5, state=tk.DISABLED)
        line_number_widget.pack(expand=True, fill='y')

        # Code Editor Area
        code_editor = tk.Text(tab_frame, font=('Consolas', 12), wrap='none', undo=True, bg="#1e1e1e", fg="#f0f0f0", insertbackground="white")
        code_editor.pack(side='right', expand=True, fill='both')

        self.add_editor_bindings(code_editor, line_number_widget)

        code_tab = CodeTab(code_editor, line_number_widget)
        self.tabs.append(code_tab)

        self.notebook.add(tab_frame, text=code_tab.get_title())
        self.notebook.select(tab_frame)

        code_editor.bind('<<Modified>>', lambda e: self.on_text_modified(code_tab))
        return code_tab

    def add_editor_bindings(self, editor, line_number_widget):
        editor.bind("<KeyRelease>", lambda event: self.update_line_numbers(editor, line_number_widget))
        editor.bind('"', lambda event: self.auto_complete(event, '"', editor))
        editor.bind("'", lambda event: self.auto_complete(event, "'", editor))
        editor.bind("(", lambda event: self.auto_complete(event, ")", editor))
        editor.bind("[", lambda event: self.auto_complete(event, "]", editor))
        editor.bind("{", lambda event: self.auto_complete(event, "}", editor))

    def update_line_numbers(self, editor, line_number_widget):
        line_count = int(editor.index('end-1c').split('.')[0])  # Get number of lines in the text editor
        line_numbers = "\n".join(str(i + 1) for i in range(line_count))
        line_number_widget.config(state=tk.NORMAL)
        line_number_widget.delete(1.0, tk.END)
        line_number_widget.insert(tk.END, line_numbers)
        line_number_widget.config(state=tk.DISABLED)

    def get_current_tab(self):
        current_tab_index = self.notebook.index(self.notebook.select())
        return self.tabs[current_tab_index]

    def open_file(self, event=None):
        filepath = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r') as file:
                    content = file.read()
                    self.create_new_tab()
                    current_tab = self.get_current_tab()
                    current_tab.filepath = filepath
                    current_tab.text_widget.delete('1.0', tk.END)
                    current_tab.text_widget.insert('1.0', content)
                    self.notebook.tab(self.notebook.select(), text=current_tab.get_title())
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self, event=None):
        current_tab = self.get_current_tab()
        if current_tab.filepath:
            self.save_current_file(current_tab)
        else:
            self.save_file_as()

    def save_file_as(self, event=None):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if filepath:
            current_tab = self.get_current_tab()
            current_tab.filepath = filepath
            self.save_current_file(current_tab)
            self.notebook.tab(self.notebook.select(), text=current_tab.get_title())

    def save_current_file(self, tab):
        try:
            content = tab.text_widget.get('1.0', tk.END)
            with open(tab.filepath, 'w') as file:
                file.write(content)
            tab.modified = False

            current_index = self.notebook.index(self.notebook.select())
            self.notebook.tab(current_index, text=tab.get_title())
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def clear_editor(self):
        current_tab = self.get_current_tab()
        current_tab.text_widget.delete('1.0', tk.END)
        self.output_area.delete('1.0', tk.END)

    def run_code(self):
        self.output_area.delete('1.0', tk.END)
        current_tab = self.get_current_tab()
        code = current_tab.text_widget.get('1.0', tk.END)
        
        old_stdout = sys.stdout
        old_stdin = sys.stdin
        redirected_output = StringIO()
        sys.stdout = redirected_output

        # Override the input function
        def custom_input(prompt=''):
            # Print the prompt to our redirected output
            print(prompt, end='')
            
            # Create an input dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Input Required")
            dialog.geometry("300x150")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.geometry("+%d+%d" % (
                self.root.winfo_x() + (self.root.winfo_width() - 300) // 2,
                self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
            ))
            
            frame = ttk.Frame(dialog, padding="20")
            frame.pack(expand=True, fill='both')
            
            # Show the prompt
            if prompt:
                ttk.Label(frame, text=prompt, wraplength=250).pack(pady=(0, 10))
            
            # Create an entry widget
            entry = ttk.Entry(frame)
            entry.pack(fill='x', pady=(0, 20))
            entry.focus_set()
            
            # Variable to store the result
            result = []
            
            def on_ok():
                result.append(entry.get())
                dialog.destroy()
            
            # Add OK button
            ttk.Button(frame, text="OK", command=on_ok).pack()
            
            # Handle Enter key
            entry.bind('<Return>', lambda e: on_ok())
            
            # Make dialog non-resizable
            dialog.resizable(False, False)
            
            # Wait for the dialog to close
            dialog.wait_window()
            
            # Return the input or empty string if cancelled
            return result[0] if result else ''

        try:
            # Replace the built-in input function
            builtins_dict = {'input': custom_input}
            # Execute the code with our custom input function
            exec(code, builtins_dict)
            output = redirected_output.getvalue()
            self.output_area.insert('1.0', output)
        except Exception as e:
            self.output_area.insert('1.0', f"Error:\n{str(e)}")
        finally:
            sys.stdout = old_stdout
            sys.stdin = old_stdin

    def auto_complete(self, event, closing_char, editor):
        try:
            if editor.tag_ranges("sel"):
                sel_start = editor.index("sel.first")
                sel_end = editor.index("sel.last")
                selected_text = editor.get(sel_start, sel_end)
                editor.delete(sel_start, sel_end)
                opening_char = event.char
                editor.insert(sel_start, f"{opening_char}{selected_text}{closing_char}")
                return 'break'
            else:
                cursor_pos = editor.index(tk.INSERT)
                editor.insert(cursor_pos, event.char + closing_char)
                editor.mark_set(tk.INSERT, f"{cursor_pos}+1c")
                return 'break'
        except Exception as e:
            print(f"Error in auto_complete: {e}")
            return None

    def undo(self, editor):
        try:
            editor.edit_undo()
        except:
            pass
        return 'break'

    def redo(self, editor):
        try:
            editor.edit_redo()
        except:
            pass
        return 'break'

    def close_current_tab(self, event=None):
        if len(self.tabs) <= 1:
            self.create_new_tab()
            return

        current_tab_index = self.notebook.index(self.notebook.select())
        current_tab = self.tabs[current_tab_index]

        if current_tab.modified:
            if messagebox.askyesno("Save Changes", f"Do you want to save changes to {current_tab.get_title()}?"):
                self.save_file()

        self.notebook.forget(current_tab_index)
        self.tabs.pop(current_tab_index)

        if self.tabs:
            new_index = min(current_tab_index, len(self.tabs) - 1)
            self.notebook.select(new_index)

    def next_tab(self, event=None):
        if len(self.tabs) > 1:
            current = self.notebook.index(self.notebook.select())
            next_tab = (current + 1) % len(self.tabs)
            self.notebook.select(next_tab)

    def prev_tab(self, event=None):
        if len(self.tabs) > 1:
            current = self.notebook.index(self.notebook.select())
            prev_tab = (current - 1) % len(self.tabs)
            self.notebook.select(prev_tab)

    def on_text_modified(self, tab):
        if tab.text_widget.edit_modified():
            if not tab.modified:
                tab.modified = True
                current_index = self.notebook.index(self.notebook.select())
                current_title = self.notebook.tab(current_index, "text")
                if not current_title.startswith('*'):
                    self.notebook.tab(current_index, text=f"*{current_title}")
            tab.text_widget.edit_modified(False)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleCodeEditor(root)
    root.mainloop()
