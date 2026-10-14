# Agent and Tools

The LangGraph state contains the user question, selected action and eventual answer. `analyze_question` chooses one of three constrained actions: retrieve knowledge, inspect status, or create a ticket. Conditional edges terminate after the selected action; application services execute the typed tool. This intentionally small graph is visible, deterministic and easy to extend.

Tools have Pydantic input schemas, bounded list sizes, domain validation, structured results, error propagation, logging and persisted execution metadata. Available tools are `search_knowledge_base`, `get_system_status`, `create_support_ticket`, `get_ticket`, and `list_recent_tickets`. Ticket creation first classifies category and priority as structured output, then invokes the tool.