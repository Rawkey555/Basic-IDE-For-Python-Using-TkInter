import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext,simpledialog
import subprocess
import subprocess
import keyword
import builtins
import re
import os

# Define theme colors
LIGHT_THEME = {
    "background": "#ffffff",
    "foreground": "#000000",
    "insertbackground": "#000000",
    "output_bg": "#f4f4f4",
    "output_fg": "#000000",
    "keyword": "#0000ff",
    "loop_cond": "#0000ff",
    "variable": "#FF0000",
    "paren": "#FFD700",
    "special": "#32CD32",
    "operator": "#0000ff",
    "relation": "#000000",
    "boolean_op": "#008000",
    "boolean_word": "#FFD700",
    "builtin_func": "#0000ff",
    "func_arg": "#000000",
    "line_number_bg": "#eeeeee",
    "line_number_fg": "#000000"
    
}

DARK_THEME = {
    "background": "#2e3440",
    "foreground": "#ffffff",
    "insertbackground": "#ffffff",
    "output_bg": "#3b4252",
    "output_fg": "#eceff4",
    "keyword": "#0000ff",
    "loop_cond": "#0000ff",
    "variable": "#FF5555",
    "paren": "#FFD700",
    "special": "#90EE90",
    "operator": "#0000ff",
    "relation": "#ffffff",
    "boolean_op": "#00ff00",
    "boolean_word": "#FFD700",
    "builtin_func": "#00ff00",
    "func_arg": "#ffffff",
    "line_number_bg": "#3b4252",
    "line_number_fg": "#ffffff"
    
}

current_theme = LIGHT_THEME

class PythonIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Python IDE")
        self.filename = None
        self.create_widgets()
        self.apply_theme()

    def create_widgets(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        open_btn = tk.Button(toolbar, text="Open", command=self.open_file, bg="green", fg="white")
        open_btn.pack(side=tk.LEFT, padx=100)

        save_btn = tk.Button(toolbar, text="Save", command=self.save_file, bg="red", fg="white")
        save_btn.pack(side=tk.LEFT, padx=100)

        run_btn = tk.Button(toolbar, text="Run", command=self.run_code, bg="blue", fg="white")
        run_btn.pack(side=tk.LEFT, padx=100)

        help_btn = tk.Button(toolbar, text="Any Help", command=self.ask_error_help, bg="black", fg="white")
        help_btn.pack(side=tk.LEFT, padx=100)

        self.dark_mode = tk.IntVar()
        tk.Checkbutton(toolbar, text="Dark Mode", variable=self.dark_mode,
                       command=self.toggle_theme).pack(side=tk.RIGHT, padx=10)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(main_frame, width=6, font=("Consolas", 12), padx=4, takefocus=0, border=0,
                                    background=current_theme['line_number_bg'], foreground=current_theme['line_number_fg'],
                                    state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        text_frame = tk.Frame(main_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.editor = scrolledtext.ScrolledText(text_frame, font=("Consolas", 12), undo=True)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self.syntax_highlight)
        self.editor.bind("<Return>", self.auto_indent)
        self.editor.bind("<KeyRelease>", self.update_line_numbers, add=True)

        output_frame = tk.Frame(main_frame)
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(output_frame, text="Output").pack(anchor=tk.W)
        self.output = scrolledtext.ScrolledText(output_frame, height=10, font=("Consolas", 12), state="disabled")
        self.output.pack(fill=tk.BOTH, expand=True)

    def update_line_numbers(self, event=None):
        lines = self.editor.index('end-1c').split('.')[0]
        line_text = "\n".join(str(i) for i in range(1, int(lines) + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_text)
        self.line_numbers.config(state='disabled')

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, content)
                self.syntax_highlight()
                self.update_line_numbers()

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                 filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.editor.get("1.0", tk.END))

    def run_code(self):
        code = self.editor.get("1.0", tk.END)
        with open("temp.py", "w") as f:
            f.write(code)
        try:
            result = subprocess.check_output(["python", "temp.py"], stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            result = e.output
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, result)
        self.output.config(state="disabled")
        os.remove("temp.py")
        error_type = result.splitlines()[-1].split(':')[0]
        self.ask_error_help(error_type)

    def ask_error_help(self):
        answer = simpledialog.askstring("Error Help",f"type the error here")
        if answer:
            explanation = self.get_error_help(answer)
            messagebox.showinfo("Error Explanation", explanation)

    def get_error_help(self, error_name):
        explanations = {
            "SyntaxError": "SyntaxError occurs when the code is not written according to Python syntax rules. Check colons, indentation, or missing parentheses.",
            "NameError": "NameError occurs when a variable or function name is not defined.",
            "TypeError": "TypeError is raised when an operation is applied to an object of inappropriate type.",
            "IndexError": "IndexError occurs when trying to access an index that is out of the range of a list or tuple.",
            "KeyError": "KeyError happens when trying to access a dictionary with a key that doesn’t exist.",
            "ZeroDivisionError":"ZeroDivisionError occurs when you are trying to divide a number with Zero Please check"
        }
        return explanations.get(error_name.strip(), "Sorry, no help found for this error.")


    def toggle_theme(self):
        global current_theme
        current_theme = DARK_THEME if self.dark_mode.get() else LIGHT_THEME
        self.apply_theme()
        self.syntax_highlight()
        self.update_line_numbers()

    def apply_theme(self):
        theme = current_theme
        self.editor.config(bg=theme["background"], fg=theme["foreground"], insertbackground=theme["insertbackground"])
        self.output.config(bg=theme["output_bg"], fg=theme["output_fg"])
        self.line_numbers.config(bg=theme["line_number_bg"], fg=theme["line_number_fg"])

    def auto_indent(self, event):
        current_line = self.editor.get("insert linestart", "insert")
        indent = re.match(r'^\s*', current_line).group(0)
        if current_line.strip().endswith(":"):
            indent += "    "
        self.editor.insert("insert", "\n" + indent)
        return "break"

    def syntax_highlight(self, event=None):
        text = self.editor.get("1.0", tk.END)
        for tag in self.editor.tag_names():
            self.editor.tag_remove(tag, "1.0", tk.END)

        theme = current_theme

        patterns = {
            "keyword": r"if|elif|else|while|for",
            "boolean_word": r"True|False",
            "builtin_func": r"print|max|min|len|import|range|input|floor|randrange|str|int|float|sum|type|sorted|open|dir|abs|round",
            "operator": r"[+*/%\\-]",
            "boolean_op": r"==|!=|<=|>=|<|>|:",
            "relation": r"(?<![=!<>])=(?!=)",
            "paren": r"[(){}\[\]]",
            
        }

        for tag, pattern in patterns.items():
            try:
                for match in re.finditer(pattern, text):
                    start = f"1.0+{match.start()}c"
                    end = f"1.0+{match.end()}c"
                    self.editor.tag_add(tag, start, end)
                    self.editor.tag_configure(tag, foreground=theme[tag])
            except re.error as e:
                print(f"Regex error in pattern '{tag}': {e}")

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("1200x700")
    app = PythonIDE(root)
    root.mainloop()

