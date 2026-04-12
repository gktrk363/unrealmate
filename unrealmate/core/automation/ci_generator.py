"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - ci_generator.py                              ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  Purpose: CI/CD pipeline generation for UE projects                          ║
║  Created: 2026-01-23                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

CI/CD pipeline generator for Unreal Engine projects.
Generates GitHub Actions, GitLab CI, and Jenkins configurations.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from pathlib import Path


class CIGenerator:
    """CI/CD configuration generator."""

    def __init__(self, project_root: Path):
        """
        Initialize CI generator.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.project_name = project_root.name

    def generate_github_actions(self) -> str:
        """
        Generate GitHub Actions workflow.

        Returns:
            str: GitHub Actions YAML content
        """
        workflow = f"""# UnrealMate Generated GitHub Actions Workflow
# © 2026 G & E ZYNTH

name: Unreal Engine Build

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v3
      with:
        lfs: true
    
    - name: Setup Unreal Engine
      run: |
        # Add your UE installation path
        echo "UE_ROOT=C:\\\\Program Files\\\\Epic Games\\\\UE_5.3" >> $GITHUB_ENV
    
    - name: Build Project
      run: |
        $UE_ROOT\\\\Engine\\\\Build\\\\BatchFiles\\\\RunUAT.bat BuildCookRun `
          -project="${{{{ github.workspace }}}}\\\\{self.project_name}.uproject" `
          -platform=Win64 `
          -clientconfig=Development `
          -cook `
          -build `
          -stage `
          -pak `
          -archive `
          -archivedirectory="${{{{ github.workspace }}}}\\\\Build"
    
    - name: Upload Build Artifacts
      uses: actions/upload-artifact@v3
      with:
        name: {self.project_name}-Build
        path: Build/
    
    - name: Run Tests (Optional)
      run: |
        # Add your test commands here
        echo "Running tests..."

# Crafted with UnrealMate by G & E ZYNTH
"""
        return workflow

    def generate_gitlab_ci(self) -> str:
        """
        Generate GitLab CI configuration.

        Returns:
            str: GitLab CI YAML content
        """
        config = f"""# UnrealMate Generated GitLab CI Configuration
# © 2026 G & E ZYNTH

stages:
  - build
  - test
  - deploy

variables:
  UE_ROOT: "C:\\\\Program Files\\\\Epic Games\\\\UE_5.3"
  PROJECT_NAME: "{self.project_name}"

build_windows:
  stage: build
  tags:
    - windows
    - unreal
  script:
    - git lfs pull
    - |
      & "$env:UE_ROOT\\\\Engine\\\\Build\\\\BatchFiles\\\\RunUAT.bat" BuildCookRun `
        -project="$CI_PROJECT_DIR\\\\${{PROJECT_NAME}}.uproject" `
        -platform=Win64 `
        -clientconfig=Development `
        -cook `
        -build `
        -stage `
        -pak `
        -archive `
        -archivedirectory="$CI_PROJECT_DIR\\\\Build"
  artifacts:
    paths:
      - Build/
    expire_in: 1 week

test:
  stage: test
  tags:
    - windows
  script:
    - echo "Running tests..."
  dependencies:
    - build_windows

# Crafted with UnrealMate by G & E ZYNTH
"""
        return config

    def generate_jenkins(self) -> str:
        """
        Generate Jenkinsfile.

        Returns:
            str: Jenkinsfile content
        """
        jenkinsfile = f"""// UnrealMate Generated Jenkinsfile
// © 2026 G & E ZYNTH

pipeline {{
    agent {{
        label 'windows && unreal'
    }}
    
    environment {{
        UE_ROOT = 'C:\\\\Program Files\\\\Epic Games\\\\UE_5.3'
        PROJECT_NAME = '{self.project_name}'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
                bat 'git lfs pull'
            }}
        }}
        
        stage('Build') {{
            steps {{
                bat '''
                    "%UE_ROOT%\\\\Engine\\\\Build\\\\BatchFiles\\\\RunUAT.bat" BuildCookRun ^
                        -project="%WORKSPACE%\\\\%PROJECT_NAME%.uproject" ^
                        -platform=Win64 ^
                        -clientconfig=Development ^
                        -cook ^
                        -build ^
                        -stage ^
                        -pak ^
                        -archive ^
                        -archivedirectory="%WORKSPACE%\\\\Build"
                '''
            }}
        }}
        
        stage('Test') {{
            steps {{
                echo 'Running tests...'
            }}
        }}
        
        stage('Archive') {{
            steps {{
                archiveArtifacts artifacts: 'Build/**', fingerprint: true
            }}
        }}
    }}
    
    post {{
        success {{
            echo 'Build successful!'
        }}
        failure {{
            echo 'Build failed!'
        }}
    }}
}}

// Crafted with UnrealMate by G & E ZYNTH
"""
        return jenkinsfile

    def save_github_actions(self) -> Path:
        """Save GitHub Actions workflow to file."""
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = workflows_dir / "unreal-build.yml"
        workflow_file.write_text(self.generate_github_actions(), encoding="utf-8")

        return workflow_file

    def save_gitlab_ci(self) -> Path:
        """Save GitLab CI configuration to file."""
        ci_file = self.project_root / ".gitlab-ci.yml"
        ci_file.write_text(self.generate_gitlab_ci(), encoding="utf-8")

        return ci_file

    def save_jenkins(self) -> Path:
        """Save Jenkinsfile to file."""
        jenkins_file = self.project_root / "Jenkinsfile"
        jenkins_file.write_text(self.generate_jenkins(), encoding="utf-8")

        return jenkins_file


# © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers

