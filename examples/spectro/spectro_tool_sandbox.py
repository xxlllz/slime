import asyncio
import gc
import os
import subprocess
import tempfile
from typing import Any

import psutil

TOOL_CONFIGS = {
    "max_turns": 10,
    "max_tool_calls": 6,
    "tool_concurrency": 32,
    "python_timeout": 120,
    "python_memory_limit": "4GB",
    "python_cpu_limit": 1,
    "max_memory_usage": 81920,
    "cleanup_threshold": 6144,
    "aggressive_cleanup_threshold": 3072,
    "force_cleanup_threshold": 9216,
}

SEMAPHORE = asyncio.Semaphore(TOOL_CONFIGS["tool_concurrency"])


def _get_memory_usage() -> float:
    return psutil.Process().memory_info().rss / 1024 / 1024


def _cleanup_memory():
    for _ in range(3):
        gc.collect()


class SkillReader:
    VALID_SKILLS = {"h_nmr", "c_nmr", "hsqc", "ir", "raman", "uv", "msms", "simnmr", "reasoning"}

    def __init__(self, skills_dir=None):
        self.skills_dir = skills_dir or os.environ.get("SPECTRO_SKILLS_DIR")
        self._cache = {}

    async def read_skill(self, name: str) -> str:
        if name not in self.VALID_SKILLS:
            return f"Error: Unknown skill '{name}'. Valid skills: {', '.join(sorted(self.VALID_SKILLS))}"
        if not self.skills_dir:
            return "Error: SPECTRO_SKILLS_DIR is not set"
        if name in self._cache:
            return self._cache[name]
        path = os.path.join(self.skills_dir, f"skill_{name}.md")
        if not os.path.exists(path):
            return f"Error: Skill file not found: {path}"
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self._cache[name] = content
        return content


class PythonSandbox:
    def __init__(self, timeout=120, memory_limit="4GB"):
        self.timeout = timeout
        self.memory_limit = memory_limit

    async def execute_code(self, code: str) -> str:
        if _get_memory_usage() > TOOL_CONFIGS["max_memory_usage"]:
            _cleanup_memory()
            return "Error: Memory usage too high, please try again"

        indented_code = "\n".join("    " + line for line in code.split("\n"))
        wrapped_code = f"""import sys
import traceback
from io import StringIO
import resource

try:
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024 * 1024 * 1024, -1))
except Exception:
    pass

old_stdout = sys.stdout
old_stderr = sys.stderr
stdout_capture = StringIO()
stderr_capture = StringIO()
sys.stdout = stdout_capture
sys.stderr = stderr_capture

try:
{indented_code}

    stdout_output = stdout_capture.getvalue()
    stderr_output = stderr_capture.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    result = ""
    if stdout_output:
        result += f"Output:\\n{{stdout_output}}"
    if stderr_output:
        result += f"\\nErrors:\\n{{stderr_output}}"
    print(result)

except Exception as e:
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    error_msg = f"Error: {{str(e)}}\\nTraceback:\\n{{traceback.format_exc()}}"
    print(error_msg)"""

        temp_dir = tempfile.mkdtemp(prefix="spectro_sandbox_")
        script_path = os.path.join(temp_dir, "code.py")
        try:
            with open(script_path, "w") as f:
                f.write(wrapped_code)

            env = os.environ.copy()
            env["PYTHONPATH"] = temp_dir
            env["PYTHONUNBUFFERED"] = "1"

            process = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=temp_dir,
                text=True,
            )
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                if process.returncode == 0:
                    return stdout.strip()
                else:
                    return f"Error: Process exited with code {process.returncode}\n{stderr}"
            except subprocess.TimeoutExpired:
                process.kill()
                return f"Error: Code execution timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error: Failed to execute code: {str(e)}"
        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.python_sandbox = PythonSandbox(
            timeout=TOOL_CONFIGS["python_timeout"],
            memory_limit=TOOL_CONFIGS["python_memory_limit"],
        )
        self.skill_reader = SkillReader()
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool(
            "read_skill",
            {
                "type": "function",
                "function": {
                    "name": "read_skill",
                    "description": (
                        "Read a spectroscopy analysis skill file containing domain knowledge "
                        "for interpreting spectra (chemical shift ranges, coupling patterns, "
                        "functional group rules, etc.)."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Spectrum type name, e.g. h_nmr, c_nmr, ir, raman, uv, msms, hsqc, simnmr",
                            }
                        },
                        "required": ["name"],
                    },
                },
            },
        )
        self.register_tool(
            "run_code",
            {
                "type": "function",
                "function": {
                    "name": "run_code",
                    "description": (
                        "Execute Python code to analyze spectral data. The code should extract "
                        "structural information (functional groups, coupling patterns, etc.) from the spectrum."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Self-contained Python code to execute",
                            }
                        },
                        "required": ["code"],
                    },
                },
            },
        )

    def register_tool(self, name: str, tool_spec: dict[str, Any]):
        self.tools[name] = tool_spec

    def get_tool_specs(self) -> list[dict[str, Any]]:
        return list(self.tools.values())

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        if tool_name == "read_skill":
            skill_name = arguments.get("name", "")
            return await self.skill_reader.read_skill(skill_name)
        elif tool_name == "run_code":
            code = arguments.get("code", "")
            if not code.strip():
                return "Error: No code provided"
            return await self.python_sandbox.execute_code(code)
        else:
            return f"Error: Unknown tool '{tool_name}'"


tool_registry = ToolRegistry()
