"""
The three personas - configured once at startup.

Poet: Pure generation (void)
Librarian: Document search (library)
Researcher: Web search (internet)
"""

from .persona import Persona


# Poet: Pure generation, no external sources
POET = Persona(
    name="poet",
    data_source="void",
    show_thinking=False,
    trace=True
)


# Librarian: Document search, show reasoning
LIBRARIAN = Persona(
    name="librarian",
    data_source="library",
    show_thinking=True,
    trace=True
)


# Researcher: Web search, show reasoning
RESEARCHER = Persona(
    name="researcher",
    data_source="internet",
    show_thinking=True,
    trace=True
)


def get_persona(name: str) -> Persona:
    """
    Get persona by name.

    Args:
        name: Persona name (poet/librarian/researcher)

    Returns:
        Persona instance

    Raises:
        ValueError: If persona name unknown
    """
    personas = {
        "poet": POET,
        "librarian": LIBRARIAN,
        "researcher": RESEARCHER
    }

    persona = personas.get(name.lower())
    if not persona:
        valid = ", ".join(personas.keys())
        raise ValueError(f"Unknown persona: {name}. Valid: {valid}")

    return persona


def list_personas() -> list:
    """Get list of available persona names"""
    return ["poet", "librarian", "researcher"]
