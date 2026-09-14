import asyncio
import json
import logging
from typing import Any, Dict, Optional
from .tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolBridge:
    """
    Lightweight local HTTP bridge allowing the Pi Coding Agent extension
    to invoke registered Python tools directly within the active request context.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.server: Optional[asyncio.Server] = None
        self.port: Optional[int] = None

    async def start(self) -> int:
        """Starts an ephemeral HTTP server on 127.0.0.1."""
        self.server = await asyncio.start_server(self._handle_client, "127.0.0.1", 0)
        self.port = self.server.sockets[0].getsockname()[1]
        logger.info(f"[ToolBridge] Started tool bridge on port {self.port}")
        return self.port

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            # Read HTTP request line
            request_line = await reader.readline()
            if not request_line:
                return

            headers: Dict[str, str] = {}
            while True:
                line = await reader.readline()
                if not line or line == b"\r\n" or line == b"\n":
                    break
                header_str = line.decode("utf-8", errors="replace")
                if ":" in header_str:
                    k, v = header_str.split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            content_length = int(headers.get("content-length", 0))
            body_bytes = await reader.readexactly(content_length) if content_length > 0 else b""
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}

            tool_name = body.get("name", "")
            params = body.get("params", {})
            logger.info(f"[ToolBridge] Executing tool '{tool_name}' with params {params}")

            tool = self.registry.get_tool(tool_name)
            if tool:
                result = await tool.execute(**params)
            else:
                result = {"error": f"Tool '{tool_name}' not found"}

            resp_json = json.dumps(result).encode("utf-8")
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: " + str(len(resp_json)).encode("ascii") + b"\r\n"
                b"Connection: close\r\n\r\n" + resp_json
            )
            writer.write(response)
            await writer.drain()
        except Exception as e:
            logger.error(f"[ToolBridge] Error executing tool: {e}", exc_info=True)
            err_json = json.dumps({"error": str(e)}).encode("utf-8")
            writer.write(
                b"HTTP/1.1 500 Internal Server Error\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: " + str(len(err_json)).encode("ascii") + b"\r\n"
                b"Connection: close\r\n\r\n" + err_json
            )
            await writer.drain()
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def stop(self) -> None:
        """Stops the bridge server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            logger.info("[ToolBridge] Stopped tool bridge")
