# 🧠 Using Memory MCP to Improve BDD Automation

## Why Use Memory for BDD?

Memory allows the agent to **remember across test sessions**, not just within a single run:

1. **Remember successful patterns** - "Last time, adding a todo worked with this selector"
2. **Learn from failures** - "This selector failed 3 times, try alternative"
3. **Store common test data** - Reusable values, configurations
4. **Cross-session intelligence** - Agent gets smarter over time

---

## 🔧 Setup Memory MCP Server

### Option 1: Use mcp-mem0 (Recommended)

```bash
# Install
npm install -g @coleam00/mcp-mem0

# Or use npx directly
npx @coleam00/mcp-mem0
```

### Option 2: Use OpenMemory MCP

```bash
npm install -g @openmemory/mcp-server
```

---

## 📝 Update Your Configuration

Add to `config/mcp-config.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "chromium", "--isolated"],
      "env": {}
    },
    "assertion": {
      "command": "python",
      "args": ["assertion_server_python.py"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./test-results"],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": ["@coleam00/mcp-mem0"],
      "env": {}
    }
  }
}
```

---

## 🎯 Enhanced System Prompt with Memory

```python
system_prompt = f"""You are an expert BDD testing engineer with PERSISTENT MEMORY across test sessions.

## Available Tools:
1. **Browser Automation** (Playwright): browser_navigate, browser_fill_form, browser_press_key, browser_take_screenshot
2. **Assertions**: assert_equals, assert_contains, assert_count, assert_greater_than
3. **Filesystem**: write_file, read_file, list_directory
4. **Memory**: store_memory, retrieve_memory, search_memory - USE THIS TO LEARN AND IMPROVE

## Memory Usage Guidelines:

**ALWAYS store successful patterns:**
- When you discover a working selector: store it
- When you learn an application workflow: remember it
- When you find a reliable approach: save it for next time

**Example Memory Usage:**
```
After successfully adding a todo:
1. Store: "todo_app_add_item_selector" → "input#new-todo"
2. Store: "todo_app_add_item_action" → "fill input#new-todo then press Enter"
3. Store: "todo_app_list_selector" → "ul.todo-list li"

Next time you see "add todo":
1. Retrieve: "todo_app_add_item_action"
2. Apply the stored pattern immediately
```

**Store these types of information:**
- Element selectors that work
- Common workflows (login, navigation, form submission)
- Application-specific patterns
- Failure patterns to avoid
- Timing requirements (which pages need longer waits)

**Before taking any action, CHECK MEMORY FIRST:**
1. Search memory for similar scenarios
2. Use stored knowledge if available
3. Only explore if no memory exists
4. Always store new learnings

Your task:
1. Parse Gherkin feature file
2. **Check memory for relevant patterns FIRST**
3. Execute scenarios using stored knowledge when available
4. **Store new successful patterns to memory**
5. Take screenshots at key moments
6. Generate test report

Execute efficiently by learning from past runs and building institutional knowledge.
"""
```

---

## 💻 Update Agent Code

```python
async def test_full_bdd_agent_with_memory():
    # ... (your existing setup) ...
    
    # Add memory server parameters
    memory_params = StdioServerParameters(
        command="npx",
        args=["@coleam00/mcp-mem0"]
    )
    
    # Connect to all 4 servers (including memory)
    async with stdio_client(playwright_params) as (p_read, p_write), \
               stdio_client(assertion_params) as (a_read, a_write), \
               stdio_client(filesystem_params) as (f_read, f_write), \
               stdio_client(memory_params) as (m_read, m_write):
        
        async with ClientSession(p_read, p_write) as playwright_session, \
                   ClientSession(a_read, a_write) as assertion_session, \
                   ClientSession(f_read, f_write) as filesystem_session, \
                   ClientSession(m_read, m_write) as memory_session:
            
            await playwright_session.initialize()
            await assertion_session.initialize()
            await filesystem_session.initialize()
            await memory_session.initialize()
            
            print("✅ All MCP servers connected (including Memory)\n")
            
            # Collect tools from all 4 servers
            all_tools = []
            
            # ... (add playwright, assertion, filesystem tools) ...
            
            # Add memory tools
            m_tools = await memory_session.list_tools()
            for tool in m_tools.tools:
                all_tools.append({
                    "type": "function",
                    "function": {
                        "name": f"memory_{tool.name}",
                        "description": f"[Memory] {tool.description}",
                        "parameters": tool.inputSchema
                    }
                })
            
            print(f"✅ Found {len(all_tools)} tools total (with memory)\n")
            
            # Helper function to execute tools
            async def execute_tool(tool_name: str, arguments: dict):
                parts = tool_name.split("_", 1)
                server_name, actual_tool_name = parts
                
                if server_name == "playwright":
                    return await playwright_session.call_tool(actual_tool_name, arguments)
                elif server_name == "assertion":
                    return await assertion_session.call_tool(actual_tool_name, arguments)
                elif server_name == "filesystem":
                    return await filesystem_session.call_tool(actual_tool_name, arguments)
                elif server_name == "memory":
                    return await memory_session.call_tool(actual_tool_name, arguments)
                else:
                    return {"error": f"Unknown server: {server_name}"}
            
            # ... (rest of your agent execution code) ...
```

---

## 📊 Example: How Agent Uses Memory

### First Test Run:
```
Agent: "I need to add a todo item"
Agent: [checks memory] "No memory found for 'add_todo'"
Agent: [explores] "Trying selector input#new-todo..."
Agent: [success!] "It worked!"
Agent: [stores memory] key="todo_add_selector" value="input#new-todo"
Agent: [stores memory] key="todo_add_action" value="fill then press Enter"
```

### Second Test Run (Same Feature):
```
Agent: "I need to add a todo item"
Agent: [checks memory] "Found 'todo_add_selector' = input#new-todo"
Agent: [checks memory] "Found 'todo_add_action' = fill then press Enter"
Agent: [applies immediately] "Using stored pattern"
Agent: ✅ Much faster! No exploration needed!
```

### Third Test Run (Different Feature on Same App):
```
Agent: "I need to delete a todo item"
Agent: [checks memory] "No delete pattern stored"
Agent: [explores] "Trying various selectors..."
Agent: [success!] "Found it: button.destroy"
Agent: [stores memory] key="todo_delete_selector" value="button.destroy"
```

---

## 🎯 Benefits of Memory

1. **Faster Execution** - No rediscovery of selectors
2. **More Reliable** - Uses proven patterns
3. **Smarter Over Time** - Learns from every run
4. **Cross-Feature Learning** - Knowledge transfers
5. **Failure Avoidance** - Remembers what didn't work

---

## 🔍 Memory Tool Examples

Typical memory tools available:

```python
# Store memory
await session.call_tool("store_memory", {
    "key": "login_username_selector",
    "value": "input[name='username']",
    "metadata": {"app": "myapp", "page": "login"}
})

# Retrieve memory
result = await session.call_tool("retrieve_memory", {
    "key": "login_username_selector"
})

# Search memory
results = await session.call_tool("search_memory", {
    "query": "login selectors",
    "limit": 5
})
```

---

## 📈 Expected Improvements

**Without Memory:**
- First run: 60 seconds
- Second run: 60 seconds
- Third run: 60 seconds

**With Memory:**
- First run: 60 seconds (learning)
- Second run: 30 seconds (using memory)
- Third run: 20 seconds (optimized patterns)

---

## 🚀 Quick Start

1. Add memory server to config
2. Update system prompt to encourage memory usage
3. Add memory session to agent code
4. Run tests - agent will automatically start learning!

---

## 📝 Complete Integration Example

### Step 1: Update `config/mcp-config.json`

Add memory server to your existing configuration.

### Step 2: Update System Prompt in `agent/main.py` or Jupyter

Replace your system prompt with the enhanced version that includes memory instructions.

### Step 3: Update Agent Initialization

Add memory session alongside other MCP sessions:

```python
# Initialize all 4 MCP servers
playwright_params = StdioServerParameters(...)
assertion_params = StdioServerParameters(...)
filesystem_params = StdioServerParameters(...)
memory_params = StdioServerParameters(
    command="npx",
    args=["@coleam00/mcp-mem0"]
)

# Connect to all servers
async with stdio_client(playwright_params) as (p_read, p_write), \
           stdio_client(assertion_params) as (a_read, a_write), \
           stdio_client(filesystem_params) as (f_read, f_write), \
           stdio_client(memory_params) as (m_read, m_write):
    
    async with ClientSession(p_read, p_write) as playwright_session, \
               ClientSession(a_read, a_write) as assertion_session, \
               ClientSession(f_read, f_write) as filesystem_session, \
               ClientSession(m_read, m_write) as memory_session:
        
        # Initialize all sessions
        await playwright_session.initialize()
        await assertion_session.initialize()
        await filesystem_session.initialize()
        await memory_session.initialize()
        
        # Collect tools from all servers including memory
        # ... (add memory tools to all_tools list)
        
        # Execute agent with memory capabilities
        # ... (your agent execution code)
```

### Step 4: Update Tool Execution Router

Make sure your execute_tool function handles memory tools:

```python
async def execute_tool(tool_name: str, arguments: dict):
    parts = tool_name.split("_", 1)
    server_name, actual_tool_name = parts
    
    if server_name == "memory":
        return await memory_session.call_tool(actual_tool_name, arguments)
    # ... (handle other servers)
```

### Step 5: Run Your Tests

The agent will now automatically:
- Check memory before actions
- Store successful patterns
- Reuse learned knowledge
- Get faster over time

---

## 🎓 Best Practices

1. **Clear Memory Keys**: Use descriptive names like `app_action_selector` not `x` or `temp`
2. **Structured Storage**: Group related memories (e.g., `login_username`, `login_password`, `login_submit`)
3. **Metadata**: Add context to memories for better retrieval
4. **Periodic Cleanup**: Clear outdated patterns if application changes
5. **Version Control**: Consider versioning memories if UI changes frequently

---

## 🔧 Troubleshooting

**Memory not persisting?**
- Check if memory server is running
- Verify storage location/permissions
- Check memory server logs

**Agent not using memory?**
- Ensure system prompt emphasizes memory usage
- Check if memory tools are in tools list
- Verify agent is calling memory tools (check logs)

**Memory retrieval slow?**
- Limit search results
- Use specific keys instead of broad searches
- Consider indexing strategies

---

## 📚 Resources

- [MCP Memory Servers](https://github.com/coleam00/mcp-mem0)
- [OpenMemory MCP](https://github.com/openmemory/mcp-server)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

---

## 🎯 Summary

Adding Memory MCP to your BDD automation system:
- ✅ Makes agent learn from experience
- ✅ Speeds up test execution over time
- ✅ Improves reliability with proven patterns
- ✅ Builds institutional knowledge
- ✅ Reduces exploration/discovery overhead

**The agent becomes smarter with every test run!** 🧠✨
