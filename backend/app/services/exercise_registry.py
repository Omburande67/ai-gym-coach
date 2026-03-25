"""Exercise registry service for loading and accessing exercise definitions."""

import json
from pathlib import Path
from typing import Dict, Optional

from app.models.exercise import ExerciseDefinition, ExerciseRegistry, ExerciseType


class ExerciseRegistryService:
    """Service for managing exercise definitions."""
    
    _instance: Optional['ExerciseRegistryService'] = None
    _registry: Optional[ExerciseRegistry] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the exercise registry service."""
        if self._registry is None:
            self._load_definitions()
    
    def _load_definitions(self) -> None:
        """Load exercise definitions from JSON file."""
        config_path = Path(__file__).parent.parent / "config" / "exercise_definitions.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Exercise definitions file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        # Parse exercises into ExerciseDefinition objects
        exercises = {}
        for exercise_type_str, exercise_data in data["exercises"].items():
            exercise_type = ExerciseType(exercise_type_str)
            exercises[exercise_type] = ExerciseDefinition(**exercise_data)
        
        self._registry = ExerciseRegistry(
            exercises=exercises,
            version=data.get("version", "1.0.0")
        )
    
    def get_exercise(self, exercise_type: ExerciseType) -> Optional[ExerciseDefinition]:
        """
        Get exercise definition by type.
        
        Args:
            exercise_type: The type of exercise to retrieve
            
        Returns:
            ExerciseDefinition if found, None otherwise
        """
        if self._registry is None:
            self._load_definitions()
        
        return self._registry.exercises.get(exercise_type)
    
    def get_all_exercises(self) -> Dict[ExerciseType, ExerciseDefinition]:
        """
        Get all exercise definitions.
        
        Returns:
            Dictionary mapping exercise types to their definitions
        """
        if self._registry is None:
            self._load_definitions()
        
        return self._registry.exercises
    
    def get_supported_exercise_types(self) -> list[ExerciseType]:
        """
        Get list of all supported exercise types.
        
        Returns:
            List of supported ExerciseType values
        """
        if self._registry is None:
            self._load_definitions()
        
        return list(self._registry.exercises.keys())
    
    def get_version(self) -> str:
        """
        Get the version of exercise definitions.
        
        Returns:
            Version string
        """
        if self._registry is None:
            self._load_definitions()
        
        return self._registry.version
    
    def reload_definitions(self) -> None:
        """Reload exercise definitions from file (useful for hot-reloading)."""
        self._registry = None
        self._load_definitions()


# Global instance for easy access
exercise_registry = ExerciseRegistryService()
