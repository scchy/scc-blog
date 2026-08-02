#!/usr/bin/env python3
"""
Wiki Manager - Core operations for LLM Wiki management.
Used by OpenClaw subagent for ingest/query/lint operations.
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class WikiManager:
    """LLM Wiki manager - implements Karpathy's LLM Wiki pattern."""
    
    def __init__(self, wiki_root: str):
        self.wiki_root = Path(wiki_root)
        self.raw_dir = self.wiki_root / "raw"
        self.wiki_dir = self.wiki_root / "wiki"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure wiki directory structure exists."""
        dirs = [
            self.raw_dir,
            self.wiki_dir,
            self.wiki_dir / "sources",
            self.wiki_dir / "entities",
            self.wiki_dir / "concepts"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def ingest(self, source_file: str) -> Dict[str, Any]:
        """
        Ingest a source file into the wiki.
        
        Args:
            source_file: Filename relative to raw/ directory
            
        Returns:
            {
                "success": bool,
                "source_page": str,
                "entities_created": List[str],
                "concepts_created": List[str]
            }
        """
        print(f"📥 Ingesting: {source_file}")
        
        source_path = self.raw_dir / source_file
        if not source_path.exists():
            return {"success": False, "error": f"File not found: {source_file}"}
        
        # Read content
        content = self._read_file(source_path)
        
        # Extract information (simplified - in real use would use LLM)
        analysis = self._analyze_content(content, source_file)
        
        # Create source page
        source_page_name = self._slugify(Path(source_file).stem)
        source_page_path = self.wiki_dir / "sources" / f"{source_page_name}.md"
        source_content = self._generate_source_page(
            title=Path(source_file).stem,
            filename=source_file,
            analysis=analysis
        )
        self._write_file(source_page_path, source_content)
        print(f"   ✓ Created source page: {source_page_path.name}")
        
        # Create entity pages
        entities_created = []
        for entity in analysis.get("entities", []):
            page = self._create_entity_page(entity, source_page_name)
            if page:
                entities_created.append(page)
        
        # Create concept pages
        concepts_created = []
        for concept in analysis.get("concepts", []):
            page = self._create_concept_page(concept, source_page_name)
            if page:
                concepts_created.append(page)
        
        # Update index
        self._update_index(source_page_name, entities_created, concepts_created)
        
        # Append log
        self._append_log("ingest", source_file)
        
        return {
            "success": True,
            "source_page": str(source_page_path),
            "entities_created": entities_created,
            "concepts_created": concepts_created
        }
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the wiki for information.
        
        Args:
            question: Query question
            
        Returns:
            {"answer": str, "sources": List[str]}
        """
        print(f"🔍 Query: {question}")
        
        # Read index
        index = self._read_index()
        
        # Find relevant pages (simplified)
        pages = self._find_relevant_pages(question)
        
        # Read page contents
        contents = []
        for page in pages[:3]:  # Top 3 pages
            content = self._read_wiki_page(page)
            if content:
                contents.append(f"=== {page} ===\n{content[:1000]}")
        
        # Generate answer (simplified)
        answer = self._generate_answer(question, contents)
        
        return {
            "answer": answer,
            "sources": pages
        }
    
    def lint(self) -> Dict[str, Any]:
        """Health check the wiki."""
        print("🔧 Linting wiki...")
        
        issues = []
        stats = {"total_pages": 0, "sources": 0, "entities": 0, "concepts": 0}
        
        # Count pages
        for subdir in ["sources", "entities", "concepts"]:
            dir_path = self.wiki_dir / subdir
            if dir_path.exists():
                pages = list(dir_path.glob("*.md"))
                stats[f"{subdir}"] = len(pages)
                stats["total_pages"] += len(pages)
        
        # Check for index
        if not (self.wiki_dir / "index.md").exists():
            issues.append({"type": "missing", "file": "index.md"})
        
        # Check for log
        if not (self.wiki_dir / "log.md").exists():
            issues.append({"type": "missing", "file": "log.md"})
        
        self._append_log("lint", f"Found {len(issues)} issues")
        
        return {"issues": issues, "stats": stats}
    
    # ========== Helper Methods ==========
    
    def _analyze_content(self, content: str, filename: str) -> Dict:
        """Analyze content to extract entities and concepts."""
        # Simplified analysis - in production would use LLM
        analysis = {
            "summary": f"Analysis of {filename}",
            "key_points": ["Point 1", "Point 2"],
            "entities": [],
            "concepts": []
        }
        
        # Extract potential entities (capitalized words)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        for word in list(set(words))[:5]:  # Top 5
            analysis["entities"].append({
                "name": word,
                "type": "unknown",
                "description": f"Mentioned in {filename}"
            })
        
        # Extract potential concepts (key phrases)
        lines = content.split('\n')[:20]  # First 20 lines
        for line in lines:
            if len(line) > 20 and len(line) < 100:
                analysis["concepts"].append({
                    "name": line.strip()[:50],
                    "description": "Extracted from content"
                })
                if len(analysis["concepts"]) >= 3:
                    break
        
        return analysis
    
    def _generate_source_page(self, title: str, filename: str, analysis: Dict) -> str:
        """Generate source page content."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        entities_links = "\n".join([f"- [[{e['name'].replace(' ', '-')}]]" 
                                     for e in analysis.get("entities", [])])
        concepts_links = "\n".join([f"- [[{c['name'].replace(' ', '-')[:30]}]]" 
                                     for c in analysis.get("concepts", [])])
        key_points = "\n".join([f"{i+1}. {p}" for i, p in enumerate(analysis.get("key_points", []))])
        
        return f"""# {title}

**Source**: raw/{filename}  
**Date**: {today}  
**Type**: article

## Summary

{analysis.get('summary', 'No summary available')}

## Key Points

{key_points if key_points else "_No key points extracted_"}

## Entities

{entities_links if entities_links else "_No entities found_"}

## Concepts

{concepts_links if concepts_links else "_No concepts found_"}

---

_Auto-generated on {today}_
"""
    
    def _create_entity_page(self, entity: Dict, source_name: str) -> Optional[str]:
        """Create or update entity page."""
        name = entity.get("name", "").strip().replace(" ", "-")
        if not name:
            return None
        
        page_name = self._slugify(name)
        page_path = self.wiki_dir / "entities" / f"{page_name}.md"
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        if page_path.exists():
            # Append source
            existing = self._read_file(page_path)
            if source_name not in existing:
                updated = existing + f"\n- [[{source_name}]]"
                self._write_file(page_path, updated)
            return page_name
        
        content = f"""# {entity.get('name', name)}

**Type**: {entity.get('type', 'unknown')}

## Description

{entity.get('description', 'No description')}

## Sources

- [[{source_name}]]

---

_Created on {today}_
"""
        self._write_file(page_path, content)
        print(f"   ✓ Created entity: {page_name}")
        return page_name
    
    def _create_concept_page(self, concept: Dict, source_name: str) -> Optional[str]:
        """Create or update concept page."""
        name = concept.get("name", "").strip()[:30].replace(" ", "-")
        if not name:
            return None
        
        page_name = self._slugify(name)
        page_path = self.wiki_dir / "concepts" / f"{page_name}.md"
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        if page_path.exists():
            existing = self._read_file(page_path)
            if source_name not in existing:
                updated = existing + f"\n- [[{source_name}]]"
                self._write_file(page_path, updated)
            return page_name
        
        content = f"""# {concept.get('name', name)[:50]}

## Definition

{concept.get('description', 'No definition')}

## Sources

- [[{source_name}]]

---

_Created on {today}_
"""
        self._write_file(page_path, content)
        print(f"   ✓ Created concept: {page_name}")
        return page_name
    
    def _update_index(self, source: str, entities: List[str], concepts: List[str]):
        """Update index.md."""
        index_path = self.wiki_dir / "index.md"
        today = datetime.now().strftime("%Y-%m-%d")
        
        if index_path.exists():
            content = self._read_file(index_path)
        else:
            content = "# Wiki Index\n\n## Sources\n\n"
        
        if f"[[{source}]]" not in content:
            content += f"- [[{source}]] ({today})\n"
            self._write_file(index_path, content)
            print(f"   ✓ Updated index")
    
    def _append_log(self, operation: str, detail: str):
        """Append to log.md."""
        log_path = self.wiki_dir / "log.md"
        today = datetime.now().strftime("%Y-%m-%d")
        entry = f"## [{today}] {operation} | {detail}\n\n"
        
        if log_path.exists():
            existing = self._read_file(log_path)
            content = existing + entry
        else:
            content = f"# Wiki Log\n\n{entry}"
        
        self._write_file(log_path, content)
    
    def _read_index(self) -> Dict:
        """Read index.md."""
        index_path = self.wiki_dir / "index.md"
        if not index_path.exists():
            return {}
        return {"content": self._read_file(index_path)}
    
    def _find_relevant_pages(self, question: str) -> List[str]:
        """Find relevant pages for query."""
        pages = []
        
        # Scan all wiki pages
        for subdir in ["sources", "entities", "concepts"]:
            dir_path = self.wiki_dir / subdir
            if dir_path.exists():
                for page in dir_path.glob("*.md"):
                    pages.append(page.stem)
        
        # Simple keyword matching
        keywords = question.lower().split()
        relevant = []
        for page in pages:
            page_lower = page.lower()
            if any(kw in page_lower for kw in keywords):
                relevant.append(page)
        
        return relevant[:5] if relevant else pages[:3]
    
    def _read_wiki_page(self, page_name: str) -> str:
        """Read a wiki page."""
        for subdir in ["sources", "entities", "concepts"]:
            page_path = self.wiki_dir / subdir / f"{page_name}.md"
            if page_path.exists():
                return self._read_file(page_path)
        return ""
    
    def _generate_answer(self, question: str, contents: List[str]) -> str:
        """Generate answer from contents."""
        # Simplified - in production would use LLM
        if not contents:
            return f"No relevant information found for: {question}"
        
        summary = f"Based on {len(contents)} sources:\n\n"
        summary += "The wiki contains information about this topic. "
        summary += "Please refer to the sources for detailed information."
        return summary
    
    def _read_file(self, path: Path) -> str:
        """Read file content."""
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"   ⚠️  Failed to read {path}: {e}")
            return ""
    
    def _write_file(self, path: Path, content: str):
        """Write file content."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"   ⚠️  Failed to write {path}: {e}")
    
    def _slugify(self, text: str) -> str:
        """Convert text to filename-friendly slug."""
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]


def main():
    """CLI entry point for subagent."""
    if len(sys.argv) < 3:
        print("Usage: wiki_manager.py <operation> <wiki_root> [args...]")
        print("  operation: ingest|query|lint")
        sys.exit(1)
    
    operation = sys.argv[1]
    wiki_root = sys.argv[2]
    
    manager = WikiManager(wiki_root)
    
    if operation == "ingest":
        if len(sys.argv) < 4:
            print("Usage: wiki_manager.py ingest <wiki_root> <source_file>")
            sys.exit(1)
        result = manager.ingest(sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif operation == "query":
        if len(sys.argv) < 4:
            print("Usage: wiki_manager.py query <wiki_root> <question>")
            sys.exit(1)
        result = manager.query(sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif operation == "lint":
        result = manager.lint()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown operation: {operation}")
        sys.exit(1)


if __name__ == "__main__":
    main()