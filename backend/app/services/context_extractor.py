"""Auto-generate APP_CONTEXT.md from RAG index"""
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class AppContextExtractor:
    """Extract app context from RAG index to create APP_CONTEXT.md"""
    
    def __init__(self, rag_service):
        self.rag_service = rag_service
    
    def extract_context(self) -> str:
        """Generate APP_CONTEXT.md content from RAG index"""
        try:
            # Get all indexed data
            screens = self._extract_screens()
            navigation = self._extract_navigation()
            ui_elements = self._extract_ui_elements()
            sample_code = self._extract_sample_code()
            
            # Build markdown document
            context = self._build_context_doc(screens, navigation, ui_elements, sample_code)
            
            logger.info("Generated app context from RAG index")
            return context
            
        except Exception as e:
            logger.error(f"Failed to extract app context: {e}")
            return self._get_template()
    
    def _extract_screens(self) -> List[str]:
        """Extract screen/view names from RAG index"""
        try:
            # Query RAG for screens
            result = self.rag_service.query("List all screens and views", k=20)
            
            screens = []
            for snippet in result.get("code_snippets", []):
                # Look for View/Screen in paths and content
                path = snippet.get("path", "")
                if "View.swift" in path or "Screen.swift" in path:
                    screen_name = Path(path).stem
                    if screen_name not in screens:
                        screens.append(screen_name)
            
            return sorted(screens)
            
        except Exception as e:
            logger.warning(f"Failed to extract screens: {e}")
            return []
    
    def _extract_navigation(self) -> Dict:
        """Extract navigation patterns"""
        try:
            result = self.rag_service.query("navigation patterns, NavigationLink, TabView", k=10)
            
            nav_info = {
                "patterns": [],
                "entry_screen": None
            }
            
            for snippet in result.get("code_snippets", []):
                content = snippet.get("content", "")
                if "NavigationLink" in content:
                    nav_info["patterns"].append("NavigationLink (push navigation)")
                if "TabView" in content:
                    nav_info["patterns"].append("TabView (tab-based navigation)")
                if "sheet" in content or ".sheet(" in content:
                    nav_info["patterns"].append("Modal sheets")
                
                # Try to find entry point
                if "@main" in content or "App.swift" in snippet.get("path", ""):
                    # Extract entry screen from content
                    lines = content.split("\n")
                    for line in lines:
                        if "View()" in line:
                            # Try to extract view name
                            parts = line.split("View()")
                            if parts:
                                potential_entry = parts[0].strip().split()[-1]
                                nav_info["entry_screen"] = potential_entry
            
            # Deduplicate patterns
            nav_info["patterns"] = list(set(nav_info["patterns"]))
            
            return nav_info
            
        except Exception as e:
            logger.warning(f"Failed to extract navigation: {e}")
            return {"patterns": [], "entry_screen": None}
    
    def _extract_ui_elements(self) -> List[str]:
        """Extract common UI elements and accessibility IDs"""
        try:
            result = self.rag_service.query("accessibilityIdentifier, TextField, Button", k=15)
            
            elements = []
            for snippet in result.get("code_snippets", []):
                content = snippet.get("content", "")
                
                # Look for accessibility identifiers
                if ".accessibilityIdentifier(" in content:
                    lines = content.split("\n")
                    for line in lines:
                        if ".accessibilityIdentifier(" in line:
                            # Extract identifier name
                            parts = line.split('accessibilityIdentifier("')
                            if len(parts) > 1:
                                id_name = parts[1].split('"')[0]
                                elements.append(f"`{id_name}`")
            
            return list(set(elements[:20]))  # Top 20 unique IDs
            
        except Exception as e:
            logger.warning(f"Failed to extract UI elements: {e}")
            return []
    
    def _extract_sample_code(self) -> str:
        """Get a sample code snippet to understand the app"""
        try:
            result = self.rag_service.query("View body", k=1)
            
            if result.get("code_snippets"):
                snippet = result["code_snippets"][0]
                return snippet.get("content", "")[:500]  # First 500 chars
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract sample code: {e}")
            return ""
    
    def _build_context_doc(self, screens: List[str], navigation: Dict, 
                          ui_elements: List[str], sample_code: str) -> str:
        """Build the markdown document"""
        
        doc = f"""# App Context (Auto-Generated from Codebase)

**Generated:** This file was automatically created by analyzing your app's source code.  
**Last Updated:** {self._get_timestamp()}

---

## Screens

The following screens/views were detected in your codebase:

"""
        if screens:
            for screen in screens:
                doc += f"- {screen}\n"
        else:
            doc += "- (No screens detected - make sure code is indexed)\n"
        
        doc += "\n---\n\n## Navigation Patterns\n\n"
        
        if navigation["patterns"]:
            for pattern in navigation["patterns"]:
                doc += f"- {pattern}\n"
        else:
            doc += "- (No navigation patterns detected)\n"
        
        if navigation["entry_screen"]:
            doc += f"\n**Entry Screen:** {navigation['entry_screen']}\n"
        
        doc += "\n---\n\n## Common UI Elements\n\n"
        doc += "Accessibility identifiers found in codebase:\n\n"
        
        if ui_elements:
            for element in ui_elements[:15]:  # Top 15
                doc += f"- {element}\n"
        else:
            doc += "- (No accessibility identifiers detected)\n"
        
        doc += "\n---\n\n## Notes\n\n"
        doc += "- This context is auto-generated from your indexed codebase\n"
        doc += "- Run `python -m app.cli generate-context` to regenerate\n"
        doc += "- Edit this file to add more specific information\n"
        doc += "- Include test credentials, expected behaviors, etc.\n"
        
        return doc
    
    def _get_template(self) -> str:
        """Fallback template if extraction fails"""
        return """# App Context

## Overview

Describe your app here (auto-extraction failed).

## Main Features

1. Feature 1
2. Feature 2

## User Flows

Describe common user flows.

---

**Note:** Auto-generation failed. Fill this out manually or check RAG indexing.
"""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_to_file(self, output_path: str = "APP_CONTEXT.md") -> bool:
        """Extract context and save to file"""
        try:
            context = self.extract_context()
            
            with open(output_path, 'w') as f:
                f.write(context)
            
            logger.info(f"Saved app context to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save app context: {e}")
            return False
