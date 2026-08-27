from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from src.config import ANTHROPIC_API_KEY, CODER_MODEL
from src.gitchecker.agents.planner import PlannerResponse
from src.gitchecker.agents.plannerTools import read_repo_file, set_repo_context


class CoderResponse(BaseModel):
    file_path: str
    fix_code: str
    reason: str


llm = ChatAnthropic(model=CODER_MODEL, api_key=ANTHROPIC_API_KEY, temperature=0)
parser = PydanticOutputParser(pydantic_object=CoderResponse)

explore_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
         You are a code fixing assistant. You will be given ONE specific bug
        to fix, plus the file(s) likely involved. Use the available tools to
        read the actual file content, then work out a correct fix for THIS
        issue only — do not attempt to fix any other unrelated issues, and
        do not reformat, refactor, or reword anything unrelated to the fix.

        Explain clearly and in plain language:
        - which file needs changing
        - what the bug is
        - the complete corrected content of the entire file, with your fix
          applied and everything else — including all original formatting,
          indentation, and comments — left exactly as it was
        - why the fix is correct

        You do not need to format this as JSON — another step will structure
        your answer afterward.
        """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{task}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

tools = [read_repo_file]
agent = create_tool_calling_agent(llm=llm, prompt=explore_prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

structured_llm = llm.with_structured_output(CoderResponse)

format_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
        You are given another assistant's analysis of a bug fix below,
        including the complete corrected file content. Convert it into the
        required structured fields exactly as described — do not invent new
        information, and do not alter the file content, only reformat what's
        already been decided.
        """,
        ),
        ("human", "{analysis}"),
    ]
)


async def coder_execute(
    repo_path: Path, planner_result: PlannerResponse
) -> CoderResponse:
    set_repo_context(repo_path)

    task = f"""
          Bug summary: {planner_result.bug_summary}
          Files likely involved: {planner_result.files_checked}
          suggested direction: {planner_result.suggested_fix_direction}
          
          Read the file(s), fix this specific issue, and return the complete
          corrected file content with everything else unchanged.

       """
    raw_response = await agent_executor.ainvoke({"task": task, "chat_history": []})
    output = raw_response["output"]

    if isinstance(output, list):
        output_text = "".join(
            block.get("text", "") for block in output if isinstance(block, dict)
        )
    else:
        output_text = output
    format_chain = format_prompt | structured_llm
    return await format_chain.ainvoke({"analysis": output_text})
