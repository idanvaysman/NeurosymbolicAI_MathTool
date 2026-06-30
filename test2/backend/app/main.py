import os
import sys
import time
from io import StringIO
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ollama import Client


class SymPyScript(BaseModel):
    reasoning: str = Field(description="Step-by-step logic on how to translate the English prompt into SymPy math.")
    sympy_code: str = Field(description="Pure Python code using SymPy. The final result MUST be assigned to a variable named 'result'.")


class SolveRequest(BaseModel):
    prompt: str = Field(min_length=1)


class PerformanceStats:
    def __init__(self) -> None:
        self.input_tokens = 0
        self.output_tokens = 0
        self.elapsed_time = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "elapsed_time": round(self.elapsed_time, 3),
        }


class SymPyAgent:
    def __init__(self) -> None:
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "180"))
        self.client = Client(host=os.getenv("OLLAMA_HOST", "http://10.16.121.138:11434"), timeout=self.timeout)
        self.model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:14b-instruct-q6_K")
        self.system_instruction = (
            "You are an expert mathematical agent that translates English word problems into precise SymPy code. "
            "You must define all necessary symbols using sp.symbols(). Always use active evaluation functions like "
            "sp.integrate(), sp.diff(), and sp.limit() instead of sp.Integral(), sp.Derivative(), or sp.Limit(). "
            "If an integral or equation is complex, simplify the expression first. Crucially, you must always assign "
            "the final solved symbolic answer to a variable named 'result'."
        )

    def _response_metrics(self, response: Any) -> tuple[int, int]:
        prompt_tokens = getattr(response, "prompt_eval_count", None)
        output_tokens = getattr(response, "eval_count", None)
        if prompt_tokens is None and isinstance(response, dict):
            prompt_tokens = response.get("prompt_eval_count", 0)
        if output_tokens is None and isinstance(response, dict):
            output_tokens = response.get("eval_count", 0)
        return int(prompt_tokens or 0), int(output_tokens or 0)

    def _generate_code(self, prompt_text: str, stats: PerformanceStats) -> SymPyScript:
        t0 = time.time()
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": prompt_text},
                ],
                options={"temperature": 0.1},
                format=SymPyScript.model_json_schema(),
            )
        except Exception as exc:
            raise RuntimeError(f"Model request failed while generating SymPy code: {exc}") from exc
        stats.elapsed_time += time.time() - t0
        prompt_tokens, output_tokens = self._response_metrics(response)
        stats.input_tokens += prompt_tokens
        stats.output_tokens += output_tokens
        return SymPyScript.model_validate_json(response.message.content)

    def _execute_code(self, code_str: str) -> Any:
        exec_scope = {"sp": __import__("sympy")}
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        try:
            exec(code_str, exec_scope, exec_scope)
            sys.stdout = old_stdout
            if "result" in exec_scope:
                return exec_scope["result"]
            raise ValueError("The 'result' variable was not defined by the script.")
        except Exception as exc:
            sys.stdout = old_stdout
            raise RuntimeError(f"Runtime Execution Error: {exc}") from exc

    def _format_final_answer(self, original_prompt: str, calculation_result: str) -> str:
        formatting_instruction = (
            "You are a helpful math assistant. Your job is to take a user's original question and the raw mathematical result "
            "calculated by a computer, and combine them into a clean, clear, and well-formatted final response. "
            "If there is an error of any kind, say 'Error, try another prompt...'."
        )
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": formatting_instruction},
                    {
                        "role": "user",
                        "content": f"Original Question: {original_prompt}\nCalculated Raw Result: {calculation_result}\n\nPlease provide the final formatted answer:",
                    },
                ],
                options={"temperature": 0.3},
            )
        except Exception as exc:
            raise RuntimeError(f"Model request failed while formatting the final answer: {exc}") from exc
        return str(response.message.content).strip()

    def run_agent_pipeline(self, english_prompt: str) -> dict[str, Any]:
        import sympy as sp

        stats = PerformanceStats()
        max_retries = 3
        last_error = ""

        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    feedback_prompt = (
                        f"Your previous SymPy code attempt failed with this error:\n---\n{last_error}\n---\n"
                        f"Please write a corrected, robust SymPy script to solve: {english_prompt}"
                    )
                    structured_output = self._generate_code(feedback_prompt, stats)
                else:
                    structured_output = self._generate_code(english_prompt, stats)

                exec_start = time.time()
                raw_result = self._execute_code(structured_output.sympy_code)
                stats.elapsed_time += time.time() - exec_start

                if hasattr(raw_result, "doit"):
                    try:
                        evaluated_result = raw_result.doit()
                        if evaluated_result != raw_result:
                            raw_result = evaluated_result
                    except Exception:
                        pass

                if hasattr(raw_result, "has") and raw_result.has(sp.Integral):
                    try:
                        numeric_value = raw_result.evalf()
                        if numeric_value.is_number:
                            latex_str = sp.latex(raw_result) + r" \approx " + sp.latex(numeric_value)
                        else:
                            latex_str = sp.latex(raw_result)
                    except Exception:
                        latex_str = sp.latex(raw_result)
                else:
                    latex_str = sp.latex(raw_result)

                formatted_answer = self._format_final_answer(english_prompt, str(raw_result))
                return {
                    "result_text": formatted_answer,
                    "raw_result": str(raw_result),
                    "latex": latex_str,
                    "stats": stats.to_dict(),
                }
            except Exception as exc:
                last_error = str(exc)
                time.sleep(0.1)
                stats.elapsed_time += 0.1

        return {
            "result_text": "Error, try another prompt...",
            "raw_result": "",
            "latex": r"$\text{ERROR: Pipeline compilation failed after 3 structural retries.}$",
            "stats": stats.to_dict(),
        }

    def run_direct_llm(self, english_prompt: str) -> dict[str, Any]:
        stats = PerformanceStats()
        system_direct = (
            "You are a math solver. Output ONLY the clean math result. Use standard LaTeX mathematical notation wrapped in $ characters if possible. "
            "Do not write explanations, sentences, or steps."
        )

        t0 = time.time()
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_direct},
                    {"role": "user", "content": english_prompt},
                ],
                options={"temperature": 0.1},
            )
        except Exception as exc:
            raise RuntimeError(f"Model request failed while running the direct LLM path: {exc}") from exc
        stats.elapsed_time = time.time() - t0
        prompt_tokens, output_tokens = self._response_metrics(response)
        stats.input_tokens = prompt_tokens
        stats.output_tokens = output_tokens

        direct_output = str(response.message.content).strip()
        if not direct_output.startswith("$"):
            direct_output = f"${direct_output}$"

        return {
            "result_text": direct_output,
            "stats": stats.to_dict(),
        }


app = FastAPI(title="Local Math Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/api/solve")
def solve(request: SolveRequest) -> dict[str, Any]:
    try:
        agent = SymPyAgent()
        framework_result = agent.run_agent_pipeline(request.prompt)
        direct_result = agent.run_direct_llm(request.prompt)
        return {"framework": framework_result, "direct": direct_result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
