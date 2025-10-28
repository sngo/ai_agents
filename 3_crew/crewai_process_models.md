# 📘 CrewAI Process Models: Sequential vs. Hierarchical

CrewAI provides two main process models for coordinating agents:
**Sequential** and **Hierarchical**. Understanding when and how to use
each is key to building effective agent workflows.

------------------------------------------------------------------------

## 🔹 1. Sequential Process Model

**Concept:**\
- Agents work in a **fixed pipeline**.\
- Each task passes directly to the next agent in order.\
- No central control or re-evaluation --- tasks flow one way.

**When to Use:**\
- The process is **predictable and repeatable**.\
- You always know the exact sequence of steps.\
- Example: data extraction → cleaning → analysis → reporting.

**Analogy:**\
- Like an **assembly line** in a factory.

**Code Example:**

``` python
from crewai import Agent, Task, Process

# Define agents
researcher = Agent(name="Research Agent", role="Researcher", goal="Find recent papers on AI in healthcare")
summarizer = Agent(name="Summarizer Agent", role="Summarizer", goal="Summarize the research findings")
writer = Agent(name="Writer Agent", role="Writer", goal="Write a full report from the summary")
reviewer = Agent(name="Reviewer Agent", role="Reviewer", goal="Check and improve the final report")

# Define tasks
tasks = [
    Task(description="Find recent papers on AI in healthcare", agent=researcher),
    Task(description="Summarize the research findings", agent=summarizer),
    Task(description="Write a detailed report on AI in healthcare", agent=writer),
    Task(description="Review and refine the report", agent=reviewer)
]

# Run sequential process
process = Process(process_type="sequential", tasks=tasks)
result = process.run("Write a report on AI in healthcare")
print(result)
```

------------------------------------------------------------------------

## 🔹 2. Hierarchical Process Model

**Concept:**\
- A **Manager Agent** oversees and coordinates.\
- The manager breaks a large goal into subtasks.\
- Delegates subtasks to specialized worker agents.\
- Evaluates results and may reassign, refine, or repeat.

**When to Use:**\
- The workflow is **variable, flexible, or unpredictable**.\
- The number or type of steps may change depending on the goal.\
- Oversight or iteration is needed.

**Analogy:**\
- Like a **project manager supervising a team**.

**Code Example:**

``` python
from crewai import Agent, Task, Process

# Define agents
manager = Agent(name="Manager Agent", role="Manager", goal="Oversee report creation and assign tasks")
researcher = Agent(name="Research Agent", role="Researcher", goal="Find recent papers on AI in healthcare")
summarizer = Agent(name="Summarizer Agent", role="Summarizer", goal="Summarize the research findings")
writer = Agent(name="Writer Agent", role="Writer", goal="Write a full report from the summary")
reviewer = Agent(name="Reviewer Agent", role="Reviewer", goal="Check and improve the final report")

# Define initial manager task
manager_task = Task(
    description="Coordinate the creation of a report on AI in healthcare by assigning subtasks to other agents.",
    agent=manager,
    expected_output="A reviewed and polished report on AI in healthcare"
)

# Run hierarchical process
process = Process(process_type="hierarchical", tasks=[manager_task])
result = process.run("Write a report on AI in healthcare")
print(result)
```

------------------------------------------------------------------------

## 🔹 3. Key Differences

  -----------------------------------------------------------------------
  Feature                     Sequential 🚶       Hierarchical 🧑‍💼
  --------------------------- ------------------- -----------------------
  Flow                        Fixed pipeline      Dynamic delegation

  Flexibility                 Low                 High

  Error handling              Blindly passes to   Manager can
                              next step           reassign/refine

  Oversight                   None                Manager supervises

  Use case                    Simple, repeatable  Complex, variable
                              workflows           workflows
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 🔹 4. Example Use Cases

-   **Sequential:**
    -   Data preprocessing pipeline\
    -   Document formatting flow\
    -   Standardized business process
-   **Hierarchical:**
    -   Research & report generation\
    -   Customer support workflows with varied requests\
    -   Any task requiring conditional logic or iteration

------------------------------------------------------------------------

✅ **Rule of Thumb:**\
- Choose **Sequential** for **predictable assembly-line workflows**.\
- Choose **Hierarchical** for **adaptive, manager-led orchestration**.
