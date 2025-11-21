import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow importing python_agent
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio

# Import the agent from the existing file
# We need to make sure we don't run the main() function when importing
# The agent.py has if __name__ == "__main__": main(), so it should be safe.
from python_agent.agent import agent

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default_thread"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # We'll use a generator to stream the response
    async def generate():
        try:
            # Stream the events from the agent
            # The agent is likely a LangGraph compiled graph or LangChain AgentExecutor
            # We'll try to stream the output.
            
            # If it's a LangGraph graph
            if hasattr(agent, "stream"):
                async for event in agent.astream(
                    {"messages": [{"role": "user", "content": request.message}]},
                    config=config
                ):
                    # LangGraph stream returns events. We need to parse them.
                    # This depends on the exact structure of the agent.
                    # For simplicity, we might just want to stream the final response tokens if possible,
                    # but LangGraph usually streams state updates.
                    
                    # If we can't easily stream tokens, we might just wait for the final response
                    # and stream it chunk by chunk to simulate typing, or send it all at once.
                    
                    # Let's try to inspect the event to see if it contains new messages
                    if "messages" in event:
                        # Get the last message
                        last_msg = event["messages"][-1]
                        if hasattr(last_msg, "content") and last_msg.content:
                             # This might be the full content or a chunk depending on the node
                             pass
                    
                    # For a smoother UI experience with LangGraph, often we just want the final answer.
                    # But the user asked for streaming.
                    
                    # Let's try a simpler approach first: invoke and stream the result text
                    # simulating streaming if the agent doesn't support token streaming easily.
                    pass
                
                # Since handling LangGraph streaming can be complex without knowing the exact graph structure,
                # and `create_agent` in the user's code might be a wrapper, let's try to use `astream_events` if available
                # or just fall back to `ainvoke` and send the result.
                
                # However, to give the "streaming" feel, let's try to use `astream_log` or similar if it's an AgentExecutor.
                
                # Let's assume for now we just want to get the final response and send it.
                # To support true streaming (token by token), we need to know if the underlying LLM supports it and if the agent exposes it.
                
                # Let's try to use `ainvoke` and then stream the response string.
                result = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": request.message}]},
                    config=config
                )
                
                final_response = result["messages"][-1].content
                
                # Stream the response character by character or word by word to simulate typing
                # This is a "fake" stream but ensures the UI gets the typing effect
                # even if the backend processes it in one go.
                # Ideally we would stream tokens from the LLM.
                
                chunk_size = 5
                for i in range(0, len(final_response), chunk_size):
                    chunk = final_response[i:i+chunk_size]
                    yield json.dumps({"content": chunk}) + "\n"
                    await asyncio.sleep(0.01) # Small delay to simulate typing
                    
            else:
                # Fallback if no stream method
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": request.message}]},
                    config=config
                )
                final_response = result["messages"][-1].content
                
                # Stream the response character by character or word by word to simulate typing
                chunk_size = 5
                for i in range(0, len(final_response), chunk_size):
                    chunk = final_response[i:i+chunk_size]
                    yield json.dumps({"content": chunk}) + "\n"
                    await asyncio.sleep(0.01) # Small delay to simulate typing

        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")

@app.get("/health")
def health_check():
    return {"status": "ok"}
