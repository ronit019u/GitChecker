from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from src.config import ANTHROPIC_API_KEY, PLANNER_MODEL
from src.gitchecker.agents.plannerTools import (
    list_files,
    read_repo_file,
    set_repo_context,
)
from src.gitchecker.schema.check import Issue


class PlannerResponse(BaseModel):
    issues: list[Issue]


llm = ChatAnthropic(model=PLANNER_MODEL, api_key=ANTHROPIC_API_KEY)

explore_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
         You are a code analysis assistant. Use the available tools to explore
        the repository and find ALL real issues related to the user's task —
        not just the single most important one.

        For each issue you find, explain clearly:
        - which files are involved
        - a clear summary of the bug
        - your suggested direction for fixing it

        If, after genuinely exploring, you find NO real issue related to the
        task, say so clearly — reporting zero issues is a complete and valid
        answer. Do NOT create issues just to have something to report.

        You do not need to format this as JSON — just explain each issue
        clearly and separately, since another step will structure your
        answer afterward.
        """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{task}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

tools = [list_files, read_repo_file]
agent = create_tool_calling_agent(llm=llm, prompt=explore_prompt, tools=tools)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

structured_response = llm.with_structured_output(PlannerResponse, method="json_schema")

format_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
        You are given another assistant's analysis of a repository below,
        which may describe multiple separate issues. Convert it into the
        required structured list — one entry per distinct issue, each with
        a unique sequential id starting from 1. If the analysis found no
        issues, return an empty list.
            """,
        ),
        ("human", "{analysis}"),
    ]
)


async def planner_execute(repo_path: Path, task: str) -> PlannerResponse:
    set_repo_context(repo_path)

    raw_response = await agent_executor.ainvoke({"task": task, "chat_history": []})
    output = raw_response["output"]

    # chatAnthropic can sometimes gives output in a unfiltered list so we change the list into the string then parse it
    # the if inside for loop is to ignore the mixed or unrelated stuff
    if isinstance(output, list):
        output_text = "".join(
            block.get("text", "") for block in output if isinstance(block, dict)
        )
    else:
        output_text = output
    format_chain = format_prompt | structured_response
    return await format_chain.ainvoke({"analysis": output_text})
