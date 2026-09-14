import asyncio
import json
import sys
from typing import Any, Dict

from ...database import get_session_maker, check_database_health
from .registry import ToolRegistry


async def run_tool_cli(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    await check_database_health()
    session_maker = get_session_maker()
    async with session_maker() as db:
        registry = ToolRegistry(db)
        tool = registry.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not recognized"}
        return await tool.execute(**args)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python -m app.agent.tools.runner <tool_name> [json_args]"}))
        sys.exit(1)

    tool_name = sys.argv[1]
    args = {}
    if len(sys.argv) >= 3:
        try:
            args = json.loads(sys.argv[2])
        except Exception as e:
            print(json.dumps({"error": f"Failed to parse arguments JSON: {e}"}))
            sys.exit(1)

    try:
        result = asyncio.run(run_tool_cli(tool_name, args))
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
