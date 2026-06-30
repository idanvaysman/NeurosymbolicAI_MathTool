import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from io import StringIO
from pydantic import BaseModel, Field
from ollama import Client

# For embedding nicely rendered math formulas into Tkinter
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# 1. Define the Schema for Structured Output
# ---------------------------------------------------------------------------
class SymPyScript(BaseModel):
    reasoning: str = Field(description="Step-by-step logic on how to translate the English prompt into SymPy math.")
    sympy_code: str = Field(
        description="Pure Python code using SymPy. The final result MUST be assigned to a variable named 'result'.")


# ---------------------------------------------------------------------------
# 2. Performance Tracking Class
# ---------------------------------------------------------------------------
class PerformanceStats:
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.elapsed_time = 0.0


# ---------------------------------------------------------------------------
# 3. Define the Agent Wrapper Class
# ---------------------------------------------------------------------------
class SymPyAgent:
    def __init__(self):
        self.client = Client(host="http://10.16.121.138:11434")
        self.model_name = "qwen2.5-coder:14b-instruct-q6_K"

        self.system_instruction = (
            "You are an expert mathematical agent that translates English word problems "
            "into precise SymPy code. You must define all necessary symbols using sp.symbols(). "
            "Crucially, you must always assign the final symbolic answer to a variable named 'result'."
        )

    def _generate_code(self, english_prompt: str, stats: PerformanceStats) -> SymPyScript:
        t0 = time.time()
        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": f"Translate this problem into SymPy code: {english_prompt}"}
            ],
            options={"temperature": 0.1},
            format=SymPyScript.model_json_schema(),
        )
        stats.elapsed_time += (time.time() - t0)
        stats.input_tokens += response.get('prompt_eval_count', 0)
        stats.output_tokens += response.get('eval_count', 0)
        return SymPyScript.model_validate_json(response.message.content)

    def _execute_code(self, code_str: str):
        """Executes SymPy code and returns the raw SymPy object."""
        exec_scope = {"sp": __import__("sympy")}
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        try:
            exec(code_str, exec_scope, exec_scope)
            sys.stdout = old_stdout
            if "result" in exec_scope:
                return exec_scope["result"]
            else:
                raise ValueError("The 'result' variable was not defined by the script.")
        except Exception as e:
            sys.stdout = old_stdout
            raise RuntimeError(f"Runtime Execution Error: {str(e)}")

    def run_agent_pipeline(self, english_prompt: str):
        """Runs the Framework agent loop and captures aggregate metrics."""
        import sympy as sp
        stats = PerformanceStats()

        structured_output = self._generate_code(english_prompt, stats)

        t_exec_start = time.time()
        raw_result = self._execute_code(structured_output.sympy_code)
        stats.elapsed_time += (time.time() - t_exec_start)

        latex_str = sp.latex(raw_result)
        return f"${latex_str}$", stats

    def run_direct_llm(self, english_prompt: str):
        """Solves the problem using a pure zero-shot prompt directly to the LLM."""
        stats = PerformanceStats()

        system_direct = (
            "You are a math solver. Output ONLY the clean math result. "
            "Use standard LaTeX mathematical notation wrapped in $ characters if possible. "
            "Do not write explanations, sentences, or steps."
        )

        t0 = time.time()
        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_direct},
                {"role": "user", "content": english_prompt}
            ],
            options={"temperature": 0.1}
        )
        stats.elapsed_time = time.time() - t0
        stats.input_tokens = response.get('prompt_eval_count', 0)
        stats.output_tokens = response.get('eval_count', 0)

        direct_output = response.message.content.strip()
        if not direct_output.startswith("$"):
            direct_output = f"${direct_output}$"

        return direct_output, stats


# ---------------------------------------------------------------------------
# 4. Tkinter GUI Implementation
# ---------------------------------------------------------------------------
class MathAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Framework vs. Direct LLM Side-by-Side Solver")
        self.root.geometry("900x650")
        self.agent = SymPyAgent()

        # Input Frame
        input_frame = ttk.LabelFrame(root, text=" Enter Your Math Problem ", padding=10)
        input_frame.pack(fill="x", padx=15, pady=10)

        self.prompt_entry = ttk.Entry(input_frame, font=("Segoe UI", 11))
        self.prompt_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.prompt_entry.insert(0, "derivative of 5*x**2 + integration of cos(x)")
        self.prompt_entry.bind("<Return>", lambda event: self.handle_submit())

        self.submit_btn = ttk.Button(input_frame, text="Run Benchmarks", command=self.handle_submit)
        self.submit_btn.pack(side="right")

        # Side-by-Side Math Display Container
        answers_container = ttk.Frame(root)
        answers_container.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Column Frame: Agent Framework
        left_frame = ttk.LabelFrame(answers_container, text=" Agent Framework (SymPy Verified) ", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.fig_left, self.ax_left = plt.subplots(figsize=(4, 2))
        self.ax_left.axis("off")
        self.canvas_left = FigureCanvasTkAgg(self.fig_left, master=left_frame)
        self.canvas_left.get_tk_widget().pack(fill="both", expand=True)

        # Right Column Frame: Direct LLM Answer
        right_frame = ttk.LabelFrame(answers_container, text=" Direct LLM Output (Zero-Shot Guess) ", padding=5)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.fig_right, self.ax_right = plt.subplots(figsize=(4, 2))
        self.ax_right.axis("off")
        self.canvas_right = FigureCanvasTkAgg(self.fig_right, master=right_frame)
        self.canvas_right.get_tk_widget().pack(fill="both", expand=True)

        # Performance Comparison Table
        table_frame = ttk.LabelFrame(root, text=" Metrics Analysis Table ", padding=10)
        table_frame.pack(fill="x", padx=15, pady=10)

        self.tree = ttk.Treeview(table_frame, columns=("Metric", "Framework (SymPy)", "Direct LLM"), show='headings',
                                 height=4)
        self.tree.heading("Metric", text="Performance Metric")
        self.tree.heading("Framework (SymPy)", text="Agent Framework (SymPy)")
        self.tree.heading("Direct LLM", text="Direct LLM Output")

        self.tree.column("Metric", anchor="center", width=200)
        self.tree.column("Framework (SymPy)", anchor="center", width=250)
        self.tree.column("Direct LLM", anchor="center", width=250)
        self.tree.pack(fill="x", expand=True)

        self.status_label = ttk.Label(root, text="Ready", font=("Segoe UI", 9, "italic"), foreground="gray")
        self.status_label.pack(anchor="w", padx=20, pady=(0, 10))

        # Initial placeholders
        self.render_latex_panels(r"$\text{Waiting for computation...}$", r"$\text{Waiting for computation...}$")

    def sanitize_latex(self, latex_str: str) -> str:
        """Sanitizes mathematical LaTeX strings to prevent Matplotlib parser crashes
        and simplifies multi-line layouts (such as vertical column vectors or matrices)
        into elegant transposed row vectors compatible with horizontal layouts.
        """
        if not latex_str:
            return ""

        import re

        # Normalize boundaries to single dollar signs
        latex_str = latex_str.strip()
        if latex_str.startswith("$$") and latex_str.endswith("$$"):
            latex_str = "$" + latex_str[2:-2].strip() + "$"
        if not latex_str.startswith("$"):
            latex_str = "$" + latex_str
        if not latex_str.endswith("$"):
            latex_str = latex_str + "$"

        # Strip limits/operators unsupported by Matplotlib's mathtext
        latex_str = latex_str.replace(r"\limits", "")
        latex_str = latex_str.replace(r"\operatorname", r"\text")

        # Flatten matrices (pmatrix, bmatrix, matrix, array) into horizontal transposed vectors
        # Example: \begin{pmatrix} a \\ b \end{pmatrix} -> \left( a, b \right)^T
        matrix_patterns = [
            (r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", r"\left( \1 \right)^T"),
            (r"\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}", r"\left[ \1 \right]^T"),
            (r"\\begin\{matrix\}(.*?)\\end\{matrix\}", r"\left( \1 \right)^T"),
            (r"\\begin\{array\}\{[a-zA-Z0-9]*\}(.*?)\\end\{array\}", r"\left[ \1 \right]"),
        ]

        for pattern, replacement in matrix_patterns:
            # Loop up to 5 times to handle nested matrices if any
            for _ in range(5):
                match = re.search(pattern, latex_str, re.DOTALL)
                if not match:
                    break
                content = match.group(1)
                # Split entries by LaTeX newline characters, strip, and join with commas
                rows = [row.strip() for row in content.split(r"\\") if row.strip()]
                flat_content = ", ".join(rows)
                latex_str = latex_str.replace(match.group(0), replacement.replace(r"\1", flat_content))

        # Flatten any other remaining double backslashes into commas to avoid vertical clipping
        latex_str = latex_str.replace(r"\\", ", ")

        # Compress any multiple consecutive spaces
        latex_str = " ".join(latex_str.split())

        return latex_str

    def get_adaptive_font_size(self, latex_str: str) -> int:
        """Calculates an adaptive font size to prevent long equations from overflowing."""
        length = len(latex_str)
        if length > 120:
            return 8
        elif length > 80:
            return 10
        elif length > 50:
            return 12
        return 14

    def render_latex_panels(self, left_latex: str, right_latex: str):
        """Refreshes both rendering canvases side-by-side cleanly and safely."""
        left_latex = self.sanitize_latex(left_latex)
        right_latex = self.sanitize_latex(right_latex)

        size_left = self.get_adaptive_font_size(left_latex)
        size_right = self.get_adaptive_font_size(right_latex)

        # Draw and paint Left Canvas
        self.ax_left.clear()
        self.ax_left.axis("off")
        try:
            self.ax_left.text(0.5, 0.5, left_latex, size=size_left, color="darkgreen",
                              horizontalalignment="center", verticalalignment="center")
            self.fig_left.tight_layout()
            self.canvas_left.draw()
        except Exception:
            # Safe local fallback drawing
            self.ax_left.clear()
            self.ax_left.axis("off")
            self.ax_left.text(0.5, 0.5, r"$\text{[Math Engine Render Error]}$", size=12, color="red",
                              horizontalalignment="center", verticalalignment="center")
            self.fig_left.tight_layout()
            try:
                self.canvas_left.draw()
            except Exception:
                pass

        # Draw and paint Right Canvas
        self.ax_right.clear()
        self.ax_right.axis("off")
        try:
            self.ax_right.text(0.5, 0.5, right_latex, size=size_right, color="darkblue",
                               horizontalalignment="center", verticalalignment="center")
            self.fig_right.tight_layout()
            self.canvas_right.draw()
        except Exception:
            self.ax_right.clear()
            self.ax_right.axis("off")
            self.ax_right.text(0.5, 0.5, r"$\text{[Math Engine Render Error]}$", size=12, color="red",
                               horizontalalignment="center", verticalalignment="center")
            self.fig_right.tight_layout()
            try:
                self.canvas_right.draw()
            except Exception:
                pass

    def update_table(self, agent_stats: PerformanceStats, direct_stats: PerformanceStats):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree.insert("", "end", values=("Input (Prompt) Tokens", f"{agent_stats.input_tokens} tkn",
                                            f"{direct_stats.input_tokens} tkn"))
        self.tree.insert("", "end", values=("Output (Gen) Tokens", f"{agent_stats.output_tokens} tkn",
                                            f"{direct_stats.output_tokens} tkn"))
        self.tree.insert("", "end",
                         values=("Total Token Volume", f"{agent_stats.input_tokens + agent_stats.output_tokens} tkn",
                                 f"{direct_stats.input_tokens + direct_stats.output_tokens} tkn"))
        self.tree.insert("", "end", values=("Total Processing Time", f"{agent_stats.elapsed_time:.3f} sec",
                                            f"{direct_stats.elapsed_time:.3f} sec"))

    def handle_submit(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a valid math prompt.")
            return

        self.status_label.config(text="Processing and solving via both pipelines...", foreground="blue")
        self.root.update_idletasks()

        try:
            # Run both execution paths
            agent_latex, agent_stats = self.agent.run_agent_pipeline(prompt)
            direct_latex, direct_stats = self.agent.run_direct_llm(prompt)

            # Repaint GUI elements
            self.render_latex_panels(agent_latex, direct_latex)
            self.update_table(agent_stats, direct_stats)
            self.status_label.config(text="Success! Compare calculations and metrics below.", foreground="green")

        except Exception as e:
            self.status_label.config(text="A pipeline calculation error occurred.", foreground="red")
            messagebox.showerror("Execution Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = MathAgentGUI(root)
    root.mainloop()