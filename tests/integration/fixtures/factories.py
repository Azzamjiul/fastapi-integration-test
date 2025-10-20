"""
Data factories for creating test data.
Provides centralized factory functions that can be customized per feature.
"""
from typing import Dict, Any


def create_todo_data(
    title: str = "Default Test Todo",
    description: str = "Default test description",
    completed: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Factory function for creating todo test data.

    This is a CENTRALIZED factory that can be OVERRIDDEN or CUSTOMIZED per feature.

    Args:
        title: Todo title
        description: Todo description
        completed: Completion status
        **kwargs: Additional fields to override defaults

    Returns:
        Dictionary with todo data

    Example usage in tests:
        # Use default values
        todo = create_todo_data()

        # Override specific fields
        todo = create_todo_data(title="Custom Title", completed=True)

        # Add custom fields
        todo = create_todo_data(priority="high", tags=["urgent"])

    Example override in feature conftest.py:
        import pytest
        from tests.integration.fixtures.factories import create_todo_data as base_create_todo_data

        @pytest.fixture
        def create_todo_data():
            # Return customized factory for this feature
            def _factory(**kwargs):
                # Add feature-specific defaults
                defaults = {
                    "title": "Feature-specific title",
                    "completed": True,
                    "priority": "high"
                }
                defaults.update(kwargs)
                return base_create_todo_data(**defaults)
            return _factory
    """
    data = {
        "title": title,
        "description": description,
        "completed": completed,
    }
    data.update(kwargs)
    return data


def create_multiple_todos(count: int = 3, **base_kwargs) -> list[Dict[str, Any]]:
    """
    Factory for creating multiple todo items.

    Args:
        count: Number of todos to create
        **base_kwargs: Base fields to apply to all todos

    Returns:
        List of todo data dictionaries

    Example:
        todos = create_multiple_todos(5, completed=False)
        # Creates 5 todos, all with completed=False
    """
    return [
        create_todo_data(
            title=f"{base_kwargs.get('title', 'Test Todo')} {i+1}",
            **{k: v for k, v in base_kwargs.items() if k != 'title'}
        )
        for i in range(count)
    ]
