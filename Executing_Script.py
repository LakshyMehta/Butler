#!/usr/bin/env python3
"""
Fully Dynamic RAG Butler System
LLM analyzes and understands scripts completely autonomously.
Zero hardcoded patterns - pure AI comprehension.
"""

import os
import re
import sys
import json
import glob
import shlex
import signal
import subprocess
import ast
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# ------------ Config ------------
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
SCRIPTS_DB_PATH = "scripts_db.json"
INDEX_NAME = "butler_scripts"
SCRIPT_DIR = "."
DRY_RUN = False
# -------------------------------

# OpenAI client
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Chroma (local vector store)
import chromadb

@dataclass
class ScriptAnalysis:
    """LLM-generated script analysis"""
    filename: str
    description: str
    purpose: str
    capabilities: List[str]
    usage_examples: List[str]
    argument_structure: Dict[str, Any]
    execution_context: str

class AIScriptAnalyzer:
    """Pure AI-driven script analysis without hardcoded patterns"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_script_with_ai(self, filepath: str) -> ScriptAnalysis:
        """Let LLM analyze script completely from scratch"""
        filename = os.path.basename(filepath)
        
        if filename in self.analysis_cache:
            return self.analysis_cache[filename]
        
        # Read the script content
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(8192)  # Read first 8KB for analysis
        except Exception:
            content = ""
        
        # Parse basic structure if possible
        structure_info = self._extract_basic_structure(content)
        
        # Let AI analyze everything
        analysis = self._ai_comprehensive_analysis(filename, content, structure_info)
        
        self.analysis_cache[filename] = analysis
        return analysis
    
    def _extract_basic_structure(self, content: str) -> Dict[str, Any]:
        """Extract minimal structure info for AI context"""
        structure = {
            "has_main": "if __name__ == '__main__'" in content,
            "imports": [],
            "functions": [],
            "classes": [],
            "has_argparse": "argparse" in content,
            "has_sys_argv": "sys.argv" in content,
            "line_count": len(content.split('\n'))
        }
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    structure["imports"].extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    structure["imports"].append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    structure["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    structure["classes"].append(node.name)
        except Exception:
            pass
        
        return structure
    
    def _ai_comprehensive_analysis(self, filename: str, content: str, 
                                  structure: Dict[str, Any]) -> ScriptAnalysis:
        """Let AI analyze script without any guidance or patterns"""
        
        analysis_prompt = f"""
Analyze this Python script completely from scratch. Don't use any predefined categories or assumptions.

Filename: {filename}
Imports: {structure.get('imports', [])}
Functions: {structure.get('functions', [])}
Classes: {structure.get('classes', [])}
Has CLI args: {structure.get('has_argparse') or structure.get('has_sys_argv')}

Script Content:
```python
{content}
```

Provide a comprehensive analysis in JSON format:
{{
    "description": "What this script does in plain English",
    "purpose": "The main goal/intent of this script",
    "capabilities": ["list of specific things this script can do"],
    "usage_examples": ["natural language examples of how someone might ask to use this"],
    "argument_structure": {{
        "input_method": "how it receives input (cli_args/hardcoded/interactive/file/api)",
        "expected_inputs": ["what inputs it expects"],
        "input_format": "description of input format"
    }},
    "execution_context": "how this script should be run and what it interacts with"
}}

Analyze the actual code logic, not just keywords. Understand what the script ACTUALLY does.
Return only valid JSON.
"""
        
        try:
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert code analyzer. Analyze scripts by understanding their actual logic and functionality, not by keyword matching."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1
            )
            
            ai_analysis = json.loads(response.choices[0].message.content.strip())
            
            return ScriptAnalysis(
                filename=filename,
                description=ai_analysis.get("description", f"Script: {filename}"),
                purpose=ai_analysis.get("purpose", "Automation script"),
                capabilities=ai_analysis.get("capabilities", []),
                usage_examples=ai_analysis.get("usage_examples", []),
                argument_structure=ai_analysis.get("argument_structure", {}),
                execution_context=ai_analysis.get("execution_context", "")
            )
            
        except Exception as e:
            # Minimal fallback
            return ScriptAnalysis(
                filename=filename,
                description=f"Script: {filename}",
                purpose="Automation",
                capabilities=["execute script"],
                usage_examples=[f"Run {filename}"],
                argument_structure={"input_method": "unknown"},
                execution_context="Command line execution"
            )

class IntelligentButler:
    """Fully AI-driven butler with zero hardcoded patterns"""
    
    def __init__(self):
        self.analyzer = AIScriptAnalyzer()
        self.collection = None
        self.script_knowledge: Dict[str, ScriptAnalysis] = {}
    
    def discover_scripts(self, script_dir: str) -> List[ScriptAnalysis]:
        """Discover and AI-analyze all scripts"""
        me = os.path.abspath(__file__)
        me_base = os.path.basename(me)
        
        analyses = []
        
        for path in glob.glob(os.path.join(script_dir, "*.py")):
            base = os.path.basename(path)
            if base == me_base:
                continue
            
            print(f"🧠 AI analyzing {base}...")
            analysis = self.analyzer.analyze_script_with_ai(path)
            analyses.append(analysis)
            self.script_knowledge[base] = analysis
            
            # Show what AI discovered
            print(f"   📝 Purpose: {analysis.purpose}")
            print(f"   🎯 Capabilities: {', '.join(analysis.capabilities[:3])}...")
        
        return analyses
    
    def build_knowledge_base(self, analyses: List[ScriptAnalysis]):
        """Build AI knowledge base from pure AI understanding"""
        chroma_client = chromadb.Client()
        
        try:
            chroma_client.delete_collection(INDEX_NAME)
        except Exception:
            pass
        
        self.collection = chroma_client.create_collection(name=INDEX_NAME)
        
        ids, docs, metas = [], [], []
        
        for i, analysis in enumerate(analyses):
            # Create comprehensive document from AI analysis
            doc_parts = [
                analysis.description,
                analysis.purpose,
                f"Capabilities: {' | '.join(analysis.capabilities)}",
                f"Usage examples: {' | '.join(analysis.usage_examples)}",
                f"Execution: {analysis.execution_context}"
            ]
            
            rich_document = " || ".join(doc_parts)
            
            ids.append(str(i))
            docs.append(rich_document)
            metas.append({
                "script": analysis.filename,
                "purpose": analysis.purpose,
                "capabilities": json.dumps(analysis.capabilities),
                "argument_structure": json.dumps(analysis.argument_structure),
                "execution_context": analysis.execution_context
            })
        
        # Generate embeddings
        embeddings = []
        batch_size = 10
        
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            batch_embeddings = client.embeddings.create(
                model=EMBED_MODEL, 
                input=batch
            ).data
            embeddings.extend([emb.embedding for emb in batch_embeddings])
        
        self.collection.add(
            ids=ids,
            documents=docs,
            metadatas=metas,
            embeddings=embeddings
        )
    
    def find_matching_script(self, user_request: str) -> Optional[Dict[str, Any]]:
        """Find best script using pure semantic similarity"""
        if not self.collection:
            return None
        
        # Generate query embedding
        query_embedding = client.embeddings.create(
            model=EMBED_MODEL, 
            input=user_request
        ).data[0].embedding
        
        # Search for best matches
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=['documents', 'metadatas', 'distances']
        )
        
        if not results or not results.get("metadatas") or not results["metadatas"][0]:
            return None
        
        # Return best match with confidence
        best_meta = results["metadatas"][0][0]
        confidence = 1 - results["distances"][0][0] if results.get("distances") else 0.5
        
        return {
            "script": best_meta["script"],
            "confidence": confidence,
            "purpose": best_meta["purpose"],
            "capabilities": json.loads(best_meta.get("capabilities", "[]")),
            "argument_structure": json.loads(best_meta.get("argument_structure", "{}")),
            "execution_context": best_meta["execution_context"]
        }
    
    def ai_execution_planning(self, user_request: str, script_info: Dict[str, Any]) -> Dict[str, Any]:
        """Let AI figure out how to execute the script"""
        
        script_analysis = self.script_knowledge.get(script_info["script"])
        
        planning_prompt = f"""
User Request: "{user_request}"

Selected Script: {script_info['script']}
Script Purpose: {script_info['purpose']}
Script Capabilities: {script_info['capabilities']}
Argument Structure: {script_info['argument_structure']}
Execution Context: {script_info['execution_context']}

Based on the user's request and script analysis, determine how to execute this script.

Provide execution plan in JSON:
{{
    "should_execute": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "why this script matches or doesn't match the request",
    "execution_method": "how to run it (direct/with_args/interactive)",
    "command_line_args": ["list", "of", "arguments", "to", "pass"],
    "expected_behavior": "what will happen when this runs",
    "user_confirmation_needed": true/false
}}

Think about what the user actually wants and whether this script can do it.
Be conservative - if unsure, set confidence lower.
Return only valid JSON.
"""
        
        try:
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an intelligent execution planner. Analyze whether a script can fulfill a user's request and plan how to execute it properly."},
                    {"role": "user", "content": planning_prompt}
                ],
                temperature=0.1
            )
            
            plan = json.loads(response.choices[0].message.content.strip())
            return plan
            
        except Exception as e:
            return {
                "should_execute": True,
                "confidence": 0.3,
                "reasoning": f"Fallback execution plan due to error: {e}",
                "execution_method": "direct",
                "command_line_args": [],
                "expected_behavior": "Run script with default behavior",
                "user_confirmation_needed": True
            }
    
    def smart_confirmation(self, user_request: str, plan: Dict[str, Any]) -> bool:
        """Intelligent confirmation based on confidence and risk"""
        script = plan.get("script", "unknown")
        confidence = plan.get("confidence", 0)
        reasoning = plan.get("reasoning", "")
        expected = plan.get("expected_behavior", "")
        
        if confidence >= 0.85:
            print(f"🎯 High confidence match: {script}")
            print(f"📋 Will: {expected}")
            return True
        
        if confidence >= 0.65:
            print(f"🤔 Found: {script} (confidence: {confidence:.2f})")
            print(f"💭 Reasoning: {reasoning}")
            print(f"📋 Expected: {expected}")
            
            response = input("Proceed? (y/n/modify): ").strip().lower()
            
            if response == 'y':
                return True
            elif response == 'modify':
                new_request = input("How would you rephrase? ")
                return self.process_request(new_request)
            else:
                return False
        else:
            print(f"❓ Low confidence match: {script} ({confidence:.2f})")
            print(f"💭 {reasoning}")
            print("🚫 Skipping execution due to low confidence.")
            return False
    
    def execute_intelligently(self, script: str, plan: Dict[str, Any]) -> bool:
        """Execute script based on AI planning"""
        script_path = os.path.join(SCRIPT_DIR, script)
        
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script}")
            return False
        
        args = plan.get("command_line_args", [])
        method = plan.get("execution_method", "direct")
        
        # Build command
        cmd = ["python", script_path] + [str(arg) for arg in args]
        
        if DRY_RUN:
            print(f"🔎 DRY RUN: {shlex.join(cmd)}")
            print(f"📋 Expected: {plan.get('expected_behavior', 'Unknown')}")
            return True
        
        try:
            print(f"🚀 Executing: {shlex.join(cmd)}")
            
            if method == "interactive":
                # For interactive scripts, don't capture output
                proc = subprocess.run(cmd, check=False, timeout=300)
            else:
                # For direct execution
                proc = subprocess.run(
                    cmd, 
                    check=False, 
                    timeout=300,
                    text=True
                )
            
            success = proc.returncode == 0
            
            if success:
                print("✅ Execution completed successfully")
            else:
                print(f"⚠️ Script exited with code {proc.returncode}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print("⏱️ Script timed out (5 minutes)")
            return False
        except KeyboardInterrupt:
            print("\n⛔ Interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Execution error: {e}")
            return False
    
    def process_request(self, user_request: str) -> bool:
        """Complete AI-driven request processing"""
        print(f"\n🧠 AI Processing: '{user_request}'")
        
        # 1. Find matching script using AI knowledge
        match = self.find_matching_script(user_request)
        if not match:
            print("🤷 No suitable script found for this request.")
            print("💡 Try rephrasing or add a relevant script to the directory.")
            return False
        
        # 2. AI planning
        plan = self.ai_execution_planning(user_request, match)
        plan["script"] = match["script"]  # Ensure script name is included
        
        if not plan.get("should_execute", True):
            print(f"🚫 AI determined this request cannot be fulfilled by {match['script']}")
            print(f"💭 Reasoning: {plan.get('reasoning', 'Unknown')}")
            return False
        
        # 3. Smart confirmation
        if not self.smart_confirmation(user_request, plan):
            return False
        
        # 4. Execute
        return self.execute_intelligently(match["script"], plan)
    
    def show_discovered_scripts(self):
        """Show what AI discovered about available scripts"""
        if not self.script_knowledge:
            print("No scripts analyzed yet.")
            return
        
        print("\n🧠 AI-Discovered Scripts:")
        print("=" * 60)
        
        for script, analysis in self.script_knowledge.items():
            print(f"\n🔧 {script}")
            print(f"   🎯 Purpose: {analysis.purpose}")
            print(f"   📝 Description: {analysis.description}")
            print(f"   ⚡ Capabilities: {', '.join(analysis.capabilities[:5])}")
            if analysis.usage_examples:
                print(f"   💬 Example: \"{analysis.usage_examples[0]}\"")
    
    def main_loop(self):
        """Main interactive loop"""
        print("🤖 Intelligent RAG Butler Starting...")
        print("🧠 Pure AI analysis - no hardcoded patterns!")
        
        # AI script discovery and analysis
        analyses = self.discover_scripts(SCRIPT_DIR)
        
        if not analyses:
            print("❌ No Python scripts found in directory.")
            print("💡 Add your automation scripts and restart.")
            sys.exit(1)
        
        print(f"✅ AI analyzed {len(analyses)} scripts")
        
        # Build AI knowledge base
        print("🧠 Building intelligent knowledge base...")
        self.build_knowledge_base(analyses)
        
        print("\n=== 🏠 INTELLIGENT BUTLER READY ===")
        print("Just tell me what you want to do in natural language!")
        print("Type 'help' for commands, 'scripts' to see capabilities, 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in {"quit", "exit", "bye", "q"}:
                print("👋 Butler shutting down. Goodbye!")
                break
            elif user_input.lower() in {"help", "h", "?"}:
                self._show_help()
            elif user_input.lower() in {"scripts", "list", "show"}:
                self.show_discovered_scripts()
            elif user_input.lower() == "refresh":
                print("🔄 Re-analyzing scripts with fresh AI...")
                self.analyzer.analysis_cache.clear()
                analyses = self.discover_scripts(SCRIPT_DIR)
                self.build_knowledge_base(analyses)
                print("✅ AI knowledge base refreshed")
            else:
                # Process natural language request
                self.process_request(user_input)
    
    def _show_help(self):
        """Show help"""
        print("""
🤖 Intelligent Butler Help:

Natural Language Interface:
  Just describe what you want to do! Examples:
  • "I need to send a message to Sarah"
  • "Can you help me call my doctor?"
  • "I want to schedule something for tomorrow"
  • "Please open my email application"

The AI will understand your request and find the right script.

System Commands:
  • help     - Show this help
  • scripts  - See what the AI discovered about your scripts
  • refresh  - Re-analyze all scripts with AI
  • quit     - Exit

The butler uses pure AI understanding - no predefined patterns!
        """)

def main():
    """Entry point"""
    butler = IntelligentButler()
    
    # Single command mode
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        
        print("🤖 Single-shot AI mode")
        analyses = butler.discover_scripts(SCRIPT_DIR)
        if not analyses:
            print("❌ No scripts to analyze")
            sys.exit(2)
        
        butler.build_knowledge_base(analyses)
        success = butler.process_request(query)
        sys.exit(0 if success else 1)
    else:
        # Interactive mode
        butler.main_loop()

if __name__ == "__main__":
    main()