"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UnrealMate - NLP Commands                             ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  Purpose: Natural language command parser for UnrealMate CLI                 ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Natural language processing for CLI commands.
Allows users to type commands in plain English.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class CommandIntent:
    """Represents a parsed command intent."""
    command: str
    subcommand: Optional[str]
    arguments: Dict[str, str]
    confidence: float
    original_input: str
    suggestions: List[str] = field(default_factory=list)


@dataclass
class CommandDefinition:
    """Defines a command and its natural language triggers."""
    name: str
    subcommands: List[str]
    triggers: List[str]  # Natural language phrases that map to this command
    description: str
    example_phrases: List[str]


class NLPCommandParser:
    """
    Natural language parser for UnrealMate commands.
    Converts plain English to CLI commands.
    """
    
    def __init__(self):
        self.commands: List[CommandDefinition] = []
        self.synonyms: Dict[str, str] = {}
        self._register_default_commands()
        self._register_synonyms()
        logger.info("NLPCommandParser initialized")
    
    def _register_default_commands(self) -> None:
        """Register default UnrealMate commands."""
        self.commands = [
            # Build commands
            CommandDefinition(
                name="build",
                subcommands=["project", "plugin", "clean", "rebuild"],
                triggers=[
                    "build", "compile", "make", "construct", 
                    "create build", "generate build"
                ],
                description="Build the Unreal Engine project",
                example_phrases=[
                    "build the project",
                    "compile my game",
                    "make a build",
                    "rebuild everything",
                    "clean and build"
                ]
            ),
            
            # Blueprint commands
            CommandDefinition(
                name="blueprint",
                subcommands=["analyze", "list", "graph", "complexity"],
                triggers=[
                    "blueprint", "bp", "analyze blueprint", 
                    "check blueprint", "scan blueprint"
                ],
                description="Analyze Blueprint assets",
                example_phrases=[
                    "analyze blueprints",
                    "check my blueprints",
                    "scan bp complexity",
                    "show blueprint graph"
                ]
            ),
            
            # Asset commands
            CommandDefinition(
                name="asset",
                subcommands=["list", "find", "unused", "duplicates", "clean"],
                triggers=[
                    "asset", "assets", "find asset", "search asset",
                    "list asset", "show asset", "clean asset"
                ],
                description="Manage project assets",
                example_phrases=[
                    "find unused assets",
                    "list all assets",
                    "show duplicate assets",
                    "clean orphaned assets"
                ]
            ),
            
            # Performance commands
            CommandDefinition(
                name="performance",
                subcommands=["analyze", "profile", "report", "optimize"],
                triggers=[
                    "performance", "perf", "profil", "optimize",
                    "speed", "benchmark", "analyze performance"
                ],
                description="Performance analysis and optimization",
                example_phrases=[
                    "analyze performance",
                    "profile the game",
                    "optimize project",
                    "check performance issues"
                ]
            ),
            
            # Config commands
            CommandDefinition(
                name="config",
                subcommands=["show", "edit", "validate", "backup", "restore"],
                triggers=[
                    "config", "configuration", "settings", "preferences",
                    "ini", "setup"
                ],
                description="Manage project configuration",
                example_phrases=[
                    "show config",
                    "edit settings",
                    "validate configuration",
                    "backup config files"
                ]
            ),
            
            # Git commands
            CommandDefinition(
                name="git",
                subcommands=["status", "log", "diff", "lfs"],
                triggers=[
                    "git", "version control", "source control",
                    "commit", "push", "pull", "repository"
                ],
                description="Git integration commands",
                example_phrases=[
                    "show git status",
                    "git log",
                    "check version control"
                ]
            ),
            
            # Migrate commands
            CommandDefinition(
                name="migrate",
                subcommands=["assets", "project", "version"],
                triggers=[
                    "migrate", "migration", "upgrade", "transfer",
                    "move", "copy project"
                ],
                description="Migration tools",
                example_phrases=[
                    "migrate assets",
                    "upgrade to new version",
                    "migrate project"
                ]
            ),
            
            # Backup commands
            CommandDefinition(
                name="backup",
                subcommands=["create", "restore", "list", "schedule"],
                triggers=[
                    "backup", "back up", "save", "snapshot",
                    "archive"
                ],
                description="Backup management",
                example_phrases=[
                    "create a backup",
                    "backup the project",
                    "restore from backup"
                ]
            ),
            
            # Template commands
            CommandDefinition(
                name="template",
                subcommands=["create", "apply", "list", "export", "import"],
                triggers=[
                    "template", "boilerplate", "starter",
                    "scaffold", "generate template"
                ],
                description="Project template management",
                example_phrases=[
                    "create a template",
                    "apply template",
                    "list available templates"
                ]
            ),
            
            # Help commands
            CommandDefinition(
                name="help",
                subcommands=["commands", "about", "version"],
                triggers=[
                    "help", "assist", "support", "how to",
                    "what can", "guide", "tutorial"
                ],
                description="Help and documentation",
                example_phrases=[
                    "help me",
                    "show help",
                    "how to build",
                    "what can you do"
                ]
            ),
        ]
    
    def _register_synonyms(self) -> None:
        """Register word synonyms for better matching."""
        self.synonyms = {
            # Verbs
            "analyse": "analyze",
            "check": "analyze",
            "scan": "analyze",
            "verify": "validate",
            "examine": "analyze",
            "inspect": "analyze",
            
            # Nouns
            "bp": "blueprint",
            "blueprints": "blueprint",
            "cfg": "config",
            "configs": "config",
            "assets": "asset",
            "file": "asset",
            "files": "asset",
            "perf": "performance",
            "speed": "performance",
            "optimise": "optimize",
            
            # Actions
            "compile": "build",
            "make": "build",
            "construct": "build",
            "create": "build",
            "remove": "clean",
            "delete": "clean",
            "erase": "clean",
        }
    
    def _normalize_input(self, text: str) -> str:
        """Normalize input text for processing."""
        # Lowercase
        text = text.lower().strip()
        
        # Remove punctuation except hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        
        # Replace synonyms
        words = text.split()
        normalized_words = [self.synonyms.get(w, w) for w in words]
        
        return ' '.join(normalized_words)
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _find_best_command_match(self, input_text: str) -> Tuple[Optional[CommandDefinition], float]:
        """Find the best matching command for input."""
        best_match: Optional[CommandDefinition] = None
        best_score = 0.0
        
        for cmd in self.commands:
            # Check direct name match
            if cmd.name in input_text:
                score = 0.9
                if score > best_score:
                    best_score = score
                    best_match = cmd
                continue
            
            # Check triggers
            for trigger in cmd.triggers:
                if trigger in input_text:
                    score = 0.85
                    if score > best_score:
                        best_score = score
                        best_match = cmd
                    break
                
                # Fuzzy match
                similarity = self._calculate_similarity(trigger, input_text)
                if similarity > best_score:
                    best_score = similarity
                    best_match = cmd
            
            # Check example phrases
            for phrase in cmd.example_phrases:
                similarity = self._calculate_similarity(phrase, input_text)
                if similarity > best_score:
                    best_score = similarity
                    best_match = cmd
        
        return best_match, best_score
    
    def _find_subcommand(self, input_text: str, command: CommandDefinition) -> Optional[str]:
        """Find matching subcommand from input."""
        for subcommand in command.subcommands:
            if subcommand in input_text:
                return subcommand
        
        # Default subcommand mapping
        default_actions = {
            "build": "project",
            "blueprint": "analyze",
            "asset": "list",
            "performance": "analyze",
            "config": "show",
            "git": "status",
            "backup": "create",
            "template": "list",
            "help": "commands",
        }
        
        return default_actions.get(command.name)
    
    def _extract_arguments(self, input_text: str) -> Dict[str, str]:
        """Extract arguments from natural language input."""
        args = {}
        
        # Path extraction
        path_match = re.search(r'(?:in|from|at|path)\s+["\']?([^\s"\']+)["\']?', input_text)
        if path_match:
            args["path"] = path_match.group(1)
        
        # Output format
        if "json" in input_text:
            args["format"] = "json"
        elif "html" in input_text:
            args["format"] = "html"
        elif "xml" in input_text:
            args["format"] = "xml"
        
        # Verbosity
        if "verbose" in input_text or "detailed" in input_text:
            args["verbose"] = "true"
        if "quiet" in input_text or "silent" in input_text:
            args["quiet"] = "true"
        
        # Recursive
        if "recursive" in input_text or "all" in input_text:
            args["recursive"] = "true"
        
        return args
    
    def parse(self, input_text: str) -> CommandIntent:
        """
        Parse natural language input into a command intent.
        
        Args:
            input_text: User's natural language input
        
        Returns:
            CommandIntent with parsed command and confidence
        """
        normalized = self._normalize_input(input_text)
        
        # Find matching command
        command, confidence = self._find_best_command_match(normalized)
        
        if command is None:
            return CommandIntent(
                command="",
                subcommand=None,
                arguments={},
                confidence=0.0,
                original_input=input_text,
                suggestions=self._get_suggestions(input_text)
            )
        
        # Find subcommand
        subcommand = self._find_subcommand(normalized, command)
        
        # Extract arguments
        arguments = self._extract_arguments(normalized)
        
        return CommandIntent(
            command=command.name,
            subcommand=subcommand,
            arguments=arguments,
            confidence=confidence,
            original_input=input_text,
            suggestions=[]
        )
    
    def _get_suggestions(self, input_text: str) -> List[str]:
        """Get command suggestions when no match found."""
        suggestions = []
        normalized = self._normalize_input(input_text)
        
        # Find closest matches
        scored_commands = []
        for cmd in self.commands:
            for phrase in cmd.example_phrases:
                score = self._calculate_similarity(normalized, phrase)
                scored_commands.append((cmd.name, phrase, score))
        
        # Sort by score and get top 3
        scored_commands.sort(key=lambda x: x[2], reverse=True)
        seen = set()
        for cmd_name, phrase, score in scored_commands[:5]:
            if cmd_name not in seen:
                suggestions.append(f"{cmd_name}: \"{phrase}\"")
                seen.add(cmd_name)
                if len(suggestions) >= 3:
                    break
        
        return suggestions
    
    def to_cli_command(self, intent: CommandIntent) -> str:
        """
        Convert a CommandIntent to a CLI command string.
        
        Args:
            intent: Parsed command intent
        
        Returns:
            CLI command string
        """
        if not intent.command:
            return ""
        
        parts = ["unrealmate", intent.command]
        
        if intent.subcommand:
            parts.append(intent.subcommand)
        
        for key, value in intent.arguments.items():
            if value == "true":
                parts.append(f"--{key}")
            else:
                parts.append(f"--{key}={value}")
        
        return ' '.join(parts)
    
    def get_help(self, command_name: Optional[str] = None) -> str:
        """Get help text for commands."""
        if command_name:
            for cmd in self.commands:
                if cmd.name == command_name:
                    help_text = f"📌 {cmd.name.upper()}\n"
                    help_text += f"   {cmd.description}\n\n"
                    help_text += "   Subcommands:\n"
                    for sub in cmd.subcommands:
                        help_text += f"   - {sub}\n"
                    help_text += "\n   Example phrases:\n"
                    for phrase in cmd.example_phrases[:3]:
                        help_text += f"   - \"{phrase}\"\n"
                    return help_text
            return f"Command '{command_name}' not found."
        
        # General help
        help_text = "🚀 UnrealMate NLP Commands\n\n"
        help_text += "Speak naturally! Examples:\n"
        for cmd in self.commands[:5]:
            if cmd.example_phrases:
                help_text += f"  - \"{cmd.example_phrases[0]}\"\n"
        help_text += "\nType any command in plain English!"
        
        return help_text


class IntentClassifier:
    """
    Classifies user intent into action categories.
    """
    
    INTENTS = {
        "CREATE": ["create", "make", "build", "generate", "new", "add"],
        "DELETE": ["delete", "remove", "clean", "erase", "destroy"],
        "UPDATE": ["update", "modify", "change", "edit", "fix"],
        "READ": ["show", "list", "find", "get", "display", "view", "check"],
        "ANALYZE": ["analyze", "scan", "profile", "inspect", "examine"],
        "HELP": ["help", "how", "what", "guide", "tutorial", "explain"],
    }
    
    @classmethod
    def classify(cls, text: str) -> str:
        """Classify text into an intent category."""
        text = text.lower()
        
        for intent, keywords in cls.INTENTS.items():
            for keyword in keywords:
                if keyword in text:
                    return intent
        
        return "UNKNOWN"


# Developer signature
DEVELOPER_SIGNATURE = "G & E ZYNTH"
MODULE_VERSION = "1.0.0"

