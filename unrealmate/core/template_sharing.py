"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       UnrealMate - Template Sharing                          ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Collaboration and template sharing                                 ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
Export, import, and share project templates.
"""

import os
import json
import shutil
import hashlib
import logging
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class TemplateMetadata:
    """Metadata for a project template."""
    name: str
    version: str
    description: str
    author: str
    created_at: datetime
    updated_at: datetime
    ue_version: str
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    file_count: int = 0
    size_bytes: int = 0
    checksum: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "ue_version": self.ue_version,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "file_count": self.file_count,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TemplateMetadata":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", "Unknown"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data.get("updated_at", data["created_at"])),
            ue_version=data.get("ue_version", "5.0"),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            file_count=data.get("file_count", 0),
            size_bytes=data.get("size_bytes", 0),
            checksum=data.get("checksum", ""),
        )


@dataclass
class Template:
    """Represents a project template."""
    metadata: TemplateMetadata
    path: Path
    is_local: bool = True
    
    @property
    def id(self) -> str:
        """Generate unique ID for the template."""
        return f"{self.metadata.name}_{self.metadata.version}"


class TemplateExporter:
    """
    Exports Unreal Engine projects as shareable templates.
    """
    
    # Files/folders to exclude from templates
    DEFAULT_EXCLUDES = {
        # Build artifacts
        "Binaries",
        "Intermediate",
        "DerivedDataCache",
        "Build",
        ".vs",
        
        # IDE files
        "*.sln",
        "*.vcxproj*",
        ".idea",
        
        # Version control
        ".git",
        ".svn",
        ".p4ignore",
        
        # Temp files
        "*.log",
        "*.tmp",
        "__pycache__",
        "*.pyc",
        
        # Large assets (optional)
        "Saved",
    }
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.excludes: Set[str] = self.DEFAULT_EXCLUDES.copy()
    
    def add_exclude(self, pattern: str) -> None:
        """Add an exclude pattern."""
        self.excludes.add(pattern)
    
    def remove_exclude(self, pattern: str) -> None:
        """Remove an exclude pattern."""
        self.excludes.discard(pattern)
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded."""
        name = path.name
        
        for pattern in self.excludes:
            if pattern.startswith("*"):
                # Wildcard pattern
                if name.endswith(pattern[1:]):
                    return True
            else:
                # Direct match
                if name == pattern:
                    return True
        
        return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_ue_version(self) -> str:
        """Detect Unreal Engine version from project."""
        uproject_files = list(self.project_path.glob("*.uproject"))
        if uproject_files:
            try:
                with open(uproject_files[0], 'r') as f:
                    data = json.load(f)
                    return data.get("EngineAssociation", "5.0")
            except:
                pass
        return "5.0"
    
    def export(self,
               output_path: str,
               name: str,
               description: str = "",
               author: str = "gktrk363",
               version: str = "1.0.0",
               tags: Optional[List[str]] = None,
               include_content: bool = True) -> Optional[str]:
        """
        Export the project as a template ZIP file.
        
        Args:
            output_path: Path for the output ZIP file
            name: Template name
            description: Template description
            author: Author name
            version: Template version
            tags: Optional tags for categorization
            include_content: Whether to include Content folder
        
        Returns:
            Path to the created ZIP file, or None on failure
        """
        output_path = Path(output_path)
        if not output_path.suffix:
            output_path = output_path.with_suffix('.zip')
        
        if not include_content:
            self.add_exclude("Content")
        
        # Collect files
        files_to_include: List[Path] = []
        total_size = 0
        
        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            rel_root = root_path.relative_to(self.project_path)
            
            # Filter directories
            dirs[:] = [d for d in dirs if not self._should_exclude(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                if not self._should_exclude(file_path):
                    files_to_include.append(file_path)
                    total_size += file_path.stat().st_size
        
        # Create metadata
        metadata = TemplateMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            ue_version=self._get_ue_version(),
            tags=tags or [],
            dependencies=[],
            file_count=len(files_to_include),
            size_bytes=total_size,
        )
        
        try:
            # Create ZIP file
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add metadata
                zf.writestr("template.json", json.dumps(metadata.to_dict(), indent=2))
                
                # Add files
                for file_path in files_to_include:
                    rel_path = file_path.relative_to(self.project_path)
                    zf.write(file_path, f"template/{rel_path}")
                    logger.debug(f"Added: {rel_path}")
            
            # Calculate checksum
            metadata.checksum = self._calculate_checksum(output_path)
            
            logger.info(f"Template exported: {output_path} ({len(files_to_include)} files)")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            return None


class TemplateImporter:
    """
    Imports templates into new or existing projects.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            self.templates_dir = Path.home() / ".unrealmate" / "templates"
        
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_template(self, template_path: str) -> Optional[TemplateMetadata]:
        """
        Validate a template file and return its metadata.
        
        Args:
            template_path: Path to the template ZIP file
        
        Returns:
            Template metadata if valid, None otherwise
        """
        template_path = Path(template_path)
        
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            return None
        
        try:
            with zipfile.ZipFile(template_path, 'r') as zf:
                # Check for metadata
                if "template.json" not in zf.namelist():
                    logger.error("Invalid template: missing template.json")
                    return None
                
                # Parse metadata
                with zf.open("template.json") as mf:
                    data = json.load(mf)
                    return TemplateMetadata.from_dict(data)
                    
        except zipfile.BadZipFile:
            logger.error("Invalid template: not a valid ZIP file")
            return None
        except json.JSONDecodeError:
            logger.error("Invalid template: malformed template.json")
            return None
        except Exception as e:
            logger.error(f"Error validating template: {e}")
            return None
    
    def import_template(self,
                       template_path: str,
                       target_path: str,
                       project_name: Optional[str] = None,
                       overwrite: bool = False) -> bool:
        """
        Import a template to create a new project.
        
        Args:
            template_path: Path to the template ZIP file
            target_path: Where to create the new project
            project_name: Name for the new project (optional)
            overwrite: Whether to overwrite existing files
        
        Returns:
            True if successful, False otherwise
        """
        metadata = self.validate_template(template_path)
        if not metadata:
            return False
        
        target_path = Path(target_path)
        
        if target_path.exists() and not overwrite:
            if any(target_path.iterdir()):
                logger.error(f"Target directory not empty: {target_path}")
                return False
        
        try:
            target_path.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(template_path, 'r') as zf:
                # Extract template files
                for member in zf.namelist():
                    if member.startswith("template/"):
                        # Remove template/ prefix
                        rel_path = member[9:]
                        if rel_path:
                            target_file = target_path / rel_path
                            
                            if member.endswith('/'):
                                target_file.mkdir(parents=True, exist_ok=True)
                            else:
                                target_file.parent.mkdir(parents=True, exist_ok=True)
                                with zf.open(member) as src:
                                    with open(target_file, 'wb') as dst:
                                        dst.write(src.read())
            
            # Rename .uproject if project_name specified
            if project_name:
                uproject_files = list(target_path.glob("*.uproject"))
                if uproject_files:
                    old_name = uproject_files[0].stem
                    new_uproject = target_path / f"{project_name}.uproject"
                    uproject_files[0].rename(new_uproject)
                    
                    # Update project name in file
                    with open(new_uproject, 'r') as f:
                        content = json.load(f)
                    
                    # Update file may need project name in description
                    with open(new_uproject, 'w') as f:
                        json.dump(content, f, indent=2)
            
            logger.info(f"Template imported to: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import template: {e}")
            return False
    
    def list_templates(self) -> List[Template]:
        """List all available templates in the templates directory."""
        templates = []
        
        for file in self.templates_dir.glob("*.zip"):
            metadata = self.validate_template(str(file))
            if metadata:
                templates.append(Template(
                    metadata=metadata,
                    path=file,
                    is_local=True
                ))
        
        return templates
    
    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name."""
        for template in self.list_templates():
            if template.metadata.name == name:
                return template
        return None
    
    def register_template(self, template_path: str) -> bool:
        """Register a template by copying it to the templates directory."""
        template_path = Path(template_path)
        
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            return False
        
        metadata = self.validate_template(str(template_path))
        if not metadata:
            return False
        
        # Copy to templates directory
        target = self.templates_dir / f"{metadata.name}_{metadata.version}.zip"
        shutil.copy2(template_path, target)
        
        logger.info(f"Template registered: {metadata.name}")
        return True


class TemplateSharingManager:
    """
    Central manager for template operations.
    """
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else None
        self.exporter = TemplateExporter(project_path) if project_path else None
        self.importer = TemplateImporter()
    
    def export_current_project(self,
                               output_path: str,
                               name: str,
                               description: str = "",
                               **kwargs) -> Optional[str]:
        """Export current project as template."""
        if not self.exporter:
            logger.error("No project path configured")
            return None
        
        return self.exporter.export(
            output_path=output_path,
            name=name,
            description=description,
            **kwargs
        )
    
    def import_to_new_project(self,
                             template_name: str,
                             target_path: str,
                             project_name: Optional[str] = None) -> bool:
        """Import a registered template to a new project."""
        template = self.importer.get_template(template_name)
        
        if not template:
            logger.error(f"Template not found: {template_name}")
            return False
        
        return self.importer.import_template(
            template_path=str(template.path),
            target_path=target_path,
            project_name=project_name
        )
    
    def list_available_templates(self) -> List[Dict]:
        """List all available templates with metadata."""
        templates = self.importer.list_templates()
        return [
            {
                "name": t.metadata.name,
                "version": t.metadata.version,
                "description": t.metadata.description,
                "author": t.metadata.author,
                "ue_version": t.metadata.ue_version,
                "tags": t.metadata.tags,
            }
            for t in templates
        ]
    
    def get_template_info(self, template_path: str) -> Optional[Dict]:
        """Get detailed info about a template file."""
        metadata = self.importer.validate_template(template_path)
        if metadata:
            return metadata.to_dict()
        return None
    
    def share(self, template_name: str) -> Dict[str, Any]:
        """
        Share a template (mock implementation).
        
        Args:
            template_name: Name of template to share
            
        Returns:
            Dict with success status and url
        """
        template = self.importer.get_template(template_name)
        if not template:
            return {"success": False, "error": f"Template '{template_name}' not found"}
            
        # Mock sharing - in reality this would upload to a server
        return {
            "success": True, 
            "url": f"https://unrealmate.io/share/{template.id}",
            "expires": "7 days"
        }


# Developer signature
DEVELOPER_SIGNATURE = "gktrk363"
MODULE_VERSION = "1.0.0"
