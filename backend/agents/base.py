"""
Base agent interface and implementation.

This module defines the base agent interface and provides a basic implementation
that can be extended by specific agent types.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field

# Type variable for agent results
T = TypeVar('T')

class AgentConfig(BaseModel):
    """Base configuration for an agent."""
    name: str
    description: str = ""
    version: str = "1.0.0"

    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for agent-specific configuration

class AgentResult(BaseModel, Generic[T]):
    """Result of an agent operation."""
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseAgent(ABC):
    """
    Base agent interface.

    This abstract class defines the common interface for all agents.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the agent with the given configuration.

        Args:
            config: The agent configuration
        """
        self.config = config
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> AgentResult:
        """
        Initialize the agent.

        This method should be called before using the agent.

        Returns:
            An AgentResult indicating success or failure
        """
        self._initialized = True
        return AgentResult(success=True, data=f"Initialized {self.config.name}")

    @abstractmethod
    async def run(self, task: str) -> AgentResult:
        """
        Run a task.

        Args:
            task: The task to run

        Returns:
            An AgentResult containing the result of the task
        """
        if not self._initialized:
            return AgentResult(
                success=False,
                error="Agent not initialized. Call initialize() first."
            )
        return AgentResult(success=True)

    @abstractmethod
    async def run_sequence(self, tasks: List[str]) -> List[AgentResult]:
        """
        Run a sequence of tasks.

        This method should be implemented to run multiple tasks in a single session
        for better performance.

        Args:
            tasks: The tasks to run

        Returns:
            A list of AgentResults containing the results of the tasks
        """
        if not self._initialized:
            return [AgentResult(
                success=False,
                error="Agent not initialized. Call initialize() first."
            )]

        results = []
        for task in tasks:
            results.append(await self.run(task))
        return results

    @abstractmethod
    async def cleanup(self) -> AgentResult:
        """
        Clean up resources.

        This method should be called when the agent is no longer needed.

        Returns:
            An AgentResult indicating success or failure
        """
        self._initialized = False
        return AgentResult(success=True)

    async def __aenter__(self):
        """
        Enter the agent context.

        This method allows the agent to be used as an async context manager.

        Returns:
            The agent instance
        """
        await self.initialize()
        return self

    async def __aexit__(self, *_):
        """
        Exit the agent context.

        This method allows the agent to be used as an async context manager.
        """
        await self.cleanup()


class SimpleAgent(BaseAgent):
    """
    A simple agent implementation.

    This class provides a basic implementation of the BaseAgent interface
    that can be used for testing or as a starting point for custom agents.
    """

    async def initialize(self) -> AgentResult:
        """
        Initialize the agent.

        Returns:
            An AgentResult indicating success
        """
        await super().initialize()
        return AgentResult(success=True, data=f"Initialized {self.config.name}")

    async def run(self, task: str) -> AgentResult:
        """
        Run a task.

        Args:
            task: The task to run

        Returns:
            An AgentResult containing the task as data
        """
        if not self._initialized:
            return AgentResult(
                success=False,
                error="Agent not initialized. Call initialize() first."
            )

        return AgentResult(success=True, data=f"Executed task: {task}")

    async def run_sequence(self, tasks: List[str]) -> List[AgentResult]:
        """
        Run a sequence of tasks.

        Args:
            tasks: The tasks to run

        Returns:
            A list of AgentResults containing the tasks as data
        """
        if not self._initialized:
            return [AgentResult(
                success=False,
                error="Agent not initialized. Call initialize() first."
            )]

        return [AgentResult(success=True, data=f"Executed task: {task}") for task in tasks]

    async def cleanup(self) -> AgentResult:
        """
        Clean up resources.

        Returns:
            An AgentResult indicating success
        """
        await super().cleanup()
        return AgentResult(success=True, data=f"Cleaned up {self.config.name}")
