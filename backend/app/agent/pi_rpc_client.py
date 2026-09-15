import asyncio
import json
import logging
import os
import queue
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..config import settings
from .providers import ProviderUnavailableError

logger = logging.getLogger(__name__)


@dataclass
class PiExecutionOutput:
    """Output from a Pi Coding Agent RPC execution."""
    content: str
    tool_calls_executed: List[Dict[str, Any]] = field(default_factory=list)
    raw_messages: List[Dict[str, Any]] = field(default_factory=list)
    provider: str = "ollama"
    model: str = "llama3.2:3b"
    tokens_used: int = 0
    success: bool = True
    error_message: Optional[str] = None


class PiRpcClient:
    """
    Client managing the official Pi Coding Agent (@earendil-works/pi-coding-agent)
    RPC process via the documented JSONL protocol over stdin/stdout.
    """

    # Can be set for unit tests needing a mock runner
    mock_runner: Optional[Callable[[str, str, str, int], PiExecutionOutput]] = None

    def __init__(
        self,
        project_root: Optional[Path] = None,
        timeout: float = 180.0,
    ):
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.timeout = timeout
        self.rpc_entry = (
            self.project_root
            / "node_modules"
            / "@earendil-works"
            / "pi-coding-agent"
            / "dist"
            / "bundle"
            / "rpc-entry.js"
        )
        self.extension_path = self.project_root / ".pi" / "extensions" / "lenny_tools.ts"
        self.config_dir = self.project_root / ".pi"

    async def execute(
        self,
        prompt: str,
        provider: str = "ollama",
        model_id: str = "llama3.2:3b",
        tool_bridge_port: Optional[int] = None,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> PiExecutionOutput:
        """
        Executes a prompt using Pi Coding Agent RPC mode.
        """
        # 1. Test Mock / Fake Boundary
        if PiRpcClient.mock_runner:
            logger.info("[PiRpcClient] Using injected mock_runner for test boundary")
            res = PiRpcClient.mock_runner(prompt, provider, model_id, tool_bridge_port or 0)
            if asyncio.iscoroutine(res):
                return await res
            return res

        if os.environ.get("PI_RPC_MOCK") == "true":
            logger.info("[PiRpcClient] PI_RPC_MOCK active - returning simulated response")
            return PiExecutionOutput(
                content=f"Simulated Pi Coding Agent response for: {prompt[:32]}",
                provider=provider,
                model=model_id,
                success=True,
            )

        if not self.rpc_entry.exists():
            return PiExecutionOutput(
                content="",
                success=False,
                error_message=f"Pi Coding Agent bundle not found at {self.rpc_entry}. Ensure npm install completed.",
                provider=provider,
                model=model_id,
            )

        # 2. Build full message with history if provided
        full_message_parts = []
        if system_prompt:
            full_message_parts.append(f"<instructions>\n{system_prompt}\n</instructions>")
        if conversation_history:
            history_text = "\n".join(
                f"[{h.get('role', 'user').capitalize()}]: {h.get('content', '')}"
                for h in conversation_history[-6:]
            )
            full_message_parts.append(f"<conversation_history>\n{history_text}\n</conversation_history>")
        full_message_parts.append(f"[Current Question]: {prompt}")
        final_prompt = "\n\n".join(full_message_parts)

        # 3. Prepare Environment
        env = os.environ.copy()
        env["PI_CODING_AGENT_DIR"] = str(self.config_dir)
        if tool_bridge_port:
            env["LENNY_TOOLS_PORT"] = str(tool_bridge_port)
        if settings.openai_api_key:
            env["OPENAI_API_KEY"] = settings.openai_api_key
        env["OLLAMA_API_KEY"] = "ollama"

        cmd = [
            "node",
            str(self.rpc_entry),
            "--no-session",
            "--no-builtin-tools",
            "--provider",
            provider,
            "--model",
            model_id,
            "-e",
            str(self.extension_path),
        ]

        logger.info(
            f"[PiRpcClient] Starting Pi Coding Agent RPC (provider={provider}, model={model_id}, bridge_port={tool_bridge_port})"
        )

        return await asyncio.to_thread(
            self._run_rpc_sync, cmd, env, provider, model_id, final_prompt
        )

    def _run_rpc_sync(
        self,
        cmd: List[str],
        env: Dict[str, str],
        provider: str,
        model_id: str,
        prompt: str,
    ) -> PiExecutionOutput:
        """Runs the synchronous subprocess interaction with timeout protection and process cleanup."""
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=env,
            cwd=str(self.project_root),
        )

        tool_calls: List[Dict[str, Any]] = []
        raw_messages: List[Dict[str, Any]] = []
        final_text = ""
        total_tokens = 0
        error_message: Optional[str] = None

        # Background thread to enqueue stdout lines non-blockingly
        line_queue: queue.Queue[Optional[str]] = queue.Queue()

        def _enqueue_output():
            try:
                for line in iter(proc.stdout.readline, ""):
                    line_queue.put(line)
            except Exception:
                pass
            finally:
                line_queue.put(None)  # EOF marker

        reader_thread = threading.Thread(target=_enqueue_output, daemon=True)
        reader_thread.start()

        # Dedicated background thread to drain stderr non-blockingly and avoid OS pipe deadlocks
        stderr_lines: List[str] = []

        def _enqueue_stderr():
            try:
                for s_line in iter(proc.stderr.readline, ""):
                    stderr_lines.append(s_line)
            except Exception:
                pass

        stderr_thread = threading.Thread(target=_enqueue_stderr, daemon=True)
        stderr_thread.start()

        def _get_line(timeout_sec: float) -> Optional[str]:
            if timeout_sec <= 0:
                return None
            try:
                return line_queue.get(timeout=timeout_sec)
            except queue.Empty:
                return None

        deadline = time.time() + self.timeout

        try:
            # 1. Set Model
            set_model_cmd = json.dumps({
                "id": "init_model",
                "type": "set_model",
                "provider": provider,
                "modelId": model_id,
            }) + "\n"
            proc.stdin.write(set_model_cmd)
            proc.stdin.flush()

            # Wait for set_model response, skipping asynchronous notifications/events
            while True:
                init_res_line = _get_line(min(15.0, max(0.1, deadline - time.time())))
                if not init_res_line:
                    if proc.poll() is not None:
                        err_out = "".join(stderr_lines).strip()
                        return PiExecutionOutput(
                            content="",
                            success=False,
                            error_message=f"Pi process exited prematurely with code {proc.returncode}. Stderr: {err_out}",
                            provider=provider,
                            model=model_id,
                        )
                    err_out = "".join(stderr_lines).strip()
                    raise TimeoutError(f"Timed out waiting for Pi agent set_model response ({provider}/{model_id}). Stderr: {err_out}")

                init_data = json.loads(init_res_line)
                logger.debug(f"[PiRpcClient] init event/response: {init_data}")
                if init_data.get("id") == "init_model" or init_data.get("command") == "set_model" or init_data.get("type") == "response":
                    if not init_data.get("success", False):
                        err = init_data.get("error") or init_data.get("message") or str(init_data)
                        return PiExecutionOutput(
                            content="",
                            success=False,
                            error_message=f"Pi set_model failed: {err}",
                            provider=provider,
                            model=model_id,
                        )
                    break

            # 2. Send Prompt
            prompt_cmd = json.dumps({
                "id": "user_turn",
                "type": "prompt",
                "message": prompt,
            }) + "\n"
            proc.stdin.write(prompt_cmd)
            proc.stdin.flush()

            # 3. Read Streamed Events until settled or deadline
            while time.time() < deadline:
                remaining = max(0.1, deadline - time.time())
                line = _get_line(min(5.0, remaining))
                if line is None:  # Slice timed out or EOF
                    if proc.poll() is not None:
                        break  # Subprocess exited
                    if time.time() >= deadline:
                        raise TimeoutError(f"Pi Coding Agent execution exceeded timeout limit of {self.timeout}s")
                    continue

                line_str = line.strip()
                if not line_str:
                    continue

                try:
                    event = json.loads(line_str)
                except Exception:
                    continue

                event_type = event.get("type")

                if event_type == "tool_execution_start":
                    tool_calls.append({
                        "id": event.get("toolCallId"),
                        "name": event.get("toolName"),
                        "args": event.get("args"),
                    })
                elif event_type == "tool_execution_end":
                    for tc in tool_calls:
                        if tc.get("id") == event.get("toolCallId"):
                            tc["result"] = event.get("result")

                elif event_type == "message_update":
                    usage = event.get("usage")
                    if usage and isinstance(usage, dict):
                        total_tokens = usage.get("totalTokens", total_tokens)

                elif event_type in ("turn_end", "message_end"):
                    msg = event.get("message")
                    if msg and isinstance(msg, dict):
                        raw_messages.append(msg)
                        if msg.get("stopReason") == "error" or msg.get("errorMessage"):
                            error_message = msg.get("errorMessage") or "Pi Coding Agent encountered an error."
                        if msg.get("role") == "assistant":
                            content_parts = msg.get("content", [])
                            if isinstance(content_parts, list):
                                for part in content_parts:
                                    if isinstance(part, dict) and part.get("type") == "text":
                                        txt = part.get("text", "")
                                        if txt and txt not in final_text:
                                            final_text += txt
                            elif isinstance(content_parts, str) and content_parts not in final_text:
                                final_text += content_parts

                elif event_type in ("agent_settled", "agent_end"):
                    messages_list = event.get("messages") or []
                    for m in messages_list:
                        if isinstance(m, dict) and (m.get("stopReason") == "error" or m.get("errorMessage")):
                            error_message = m.get("errorMessage") or "Pi Coding Agent encountered an error."
                    break

            if time.time() >= deadline and not final_text and not error_message:
                raise TimeoutError(f"Pi Coding Agent execution exceeded timeout limit of {self.timeout}s")

            if error_message and not final_text.strip():
                return PiExecutionOutput(
                    content="",
                    tool_calls_executed=tool_calls,
                    raw_messages=raw_messages,
                    provider=provider,
                    model=model_id,
                    tokens_used=total_tokens,
                    success=False,
                    error_message=error_message,
                )

            # 4. Request last assistant text if empty
            if not final_text.strip():
                try:
                    last_text_cmd = json.dumps({
                        "id": "last_text",
                        "type": "get_last_assistant_text",
                    }) + "\n"
                    proc.stdin.write(last_text_cmd)
                    proc.stdin.flush()
                    last_line = _get_line(5.0)
                    if last_line:
                        last_data = json.loads(last_line)
                        data = last_data.get("data") or {}
                        if data.get("text"):
                            final_text = data["text"]
                except Exception as e:
                    logger.debug(f"[PiRpcClient] get_last_assistant_text fallback: {e}")

            return PiExecutionOutput(
                content=final_text.strip(),
                tool_calls_executed=tool_calls,
                raw_messages=raw_messages,
                provider=provider,
                model=model_id,
                tokens_used=total_tokens,
                success=True,
            )

        except Exception as e:
            logger.error(f"[PiRpcClient] Subprocess error during Pi RPC execution: {e}", exc_info=True)
            try:
                if proc.poll() is None:
                    proc.kill()
            except Exception:
                pass
            stderr_out = "".join(stderr_lines).strip()
            return PiExecutionOutput(
                content="",
                success=False,
                error_message=f"Pi execution failed: {str(e)}. Stderr: {stderr_out}",
                provider=provider,
                model=model_id,
            )
        finally:
            # Guaranteed cleanup of child process to prevent orphan/zombie processes
            try:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=2)
            except Exception:
                pass

