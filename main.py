try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
except ImportError:
    print("Error: tkinter is not installed. Please install Python with tkinter support.")
    exit(1)

import sys
from io import StringIO
import os

class CodeTab:
    def __init__(self, text_widget, filepath=None):
        self.text_widget = text_widget
        self.filepath = filepath
        self.modified = False
        
    def get_title(self):
        if self.filepath:
            return os.path.basename(self.filepath)
        return "Untitled"

class SimpleCodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("ZYPY")
        self.root.geometry("800x600")

#
        style = ttk.Style()
        style.configure('Run.TButton', padding=5)
#
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)

    #
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill='both', pady=(0, 5))
    #
        self.tabs = []

    #
        self.create_menu()

       #
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=5)

      #
        self.run_button = ttk.Button(self.button_frame, text="▶ Run Code", command=self.run_code, style='Run.TButton')
        self.run_button.pack(side='left', padx=5)

   #
        self.clear_button = ttk.Button(self.button_frame, text="🗑 Clear", command=self.clear_editor)
        self.clear_button.pack(side='left', padx=5)

       #
        self.output_label = ttk.Label(self.main_frame, text="Output:", font=('Consolas', 10, 'bold'))
        self.output_label.pack(anchor='w', pady=(10,0))
        
        self.output_area = tk.Text(self.main_frame, font=('Consolas', 12), height=8, wrap='word', bg='#f0f0f0')
        self.output_area.pack(expand=False, fill='both')

#
        self.create_new_tab()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
   #
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.create_new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Close Tab", command=self.close_current_tab, accelerator="Ctrl+W")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

  #
        self.root.bind('<Control-n>', lambda e: self.create_new_tab())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_file_as())
        self.root.bind('<Control-w>', lambda e: self.close_current_tab())
        self.root.bind('<Control-Tab>', lambda e: self.next_tab())
        self.root.bind('<Control-Shift-Tab>', lambda e: self.prev_tab())

    def create_new_tab(self):
        ##
        tab_frame = ttk.Frame(self.notebook)
        
        ##
        code_editor = tk.Text(tab_frame, font=('Consolas', 12), wrap='none', undo=True)
        code_editor.pack(expand=True, fill='both')
        
     #
        self.add_editor_bindings(code_editor)
        
     #
        code_tab = CodeTab(code_editor)
        self.tabs.append(code_tab)
        
       #
        self.notebook.add(tab_frame, text=code_tab.get_title())
        self.notebook.select(tab_frame)
        
       #
        code_editor.bind('<<Modified>>', lambda e: self.on_text_modified(code_tab))
        
        return code_tab

    def add_editor_bindings(self, editor):
        editor.bind('"', lambda event: self.auto_complete(event, '"', editor))
        editor.bind("'", lambda event: self.auto_complete(event, "'", editor))
        editor.bind("(", lambda event: self.auto_complete(event, ")", editor))
        editor.bind("[", lambda event: self.auto_complete(event, "]", editor))
        editor.bind("{", lambda event: self.auto_complete(event, "}", editor))
        editor.bind('<Control-z>', lambda e: self.undo(editor))
        editor.bind('<Control-y>', lambda e: self.redo(editor))
        editor.bind("<BackSpace>", lambda e: self.handle_backspace(e, editor))

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
        redirected_output = StringIO()
        sys.stdout = redirected_output

        try:
            exec(code)
            output = redirected_output.getvalue()
            self.output_area.insert('1.0', output)
        except Exception as e:
            self.output_area.insert('1.0', f"Error:\n{str(e)}")
        finally:
            sys.stdout = old_stdout

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

    def handle_backspace(self, event, editor):
        cursor_pos = editor.index(tk.INSERT)
        
        try:
            char_before = editor.get(f"{cursor_pos} - 1c", cursor_pos)
            char_after = editor.get(cursor_pos, f"{cursor_pos} + 1c")
            
            pairs = {'"': '"', "'": "'", "(": ")", "[": "]", "{": "}"}
            
            if char_before in pairs and char_after == pairs[char_before]:
                editor.delete(f"{cursor_pos} - 1c", f"{cursor_pos} + 1c")
                return 'break'
        except:
            pass
        
        return None

    def close_current_tab(self, event=None):
        if len(self.tabs) <= 1: 
            self.create_new_tab()
            return
            
        current_tab_index = self.notebook.index(self.notebook.select())
        current_tab = self.tabs[current_tab_index]
        
  
        if current_tab.modified:
            if messagebox.askyesno("Save Changes", 
                f"Do you want to save changes to {current_tab.get_title()}?"):
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
