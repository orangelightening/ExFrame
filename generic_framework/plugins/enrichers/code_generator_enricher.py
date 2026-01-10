"""
Code Generator Enricher Plugin

Generates code examples from pattern descriptions.
Supports multiple programming languages.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.enrichment_plugin import EnrichmentPlugin, EnrichmentContext


class CodeGeneratorEnricher(EnrichmentPlugin):
    """
    Generates code examples from patterns.

    Analyzes pattern solutions and examples to generate
    working code in various programming languages.

    Configuration:
        - languages: List[str] (default: ["python"]) - Languages to generate
        - max_examples: int (default: 2) - Max code examples per pattern
        - include_tests: bool (default: true) - Generate test cases
        - include_comments: bool (default: true) - Add explanatory comments
    """

    name = "Code Generator Enricher"

    # Language templates
    TEMPLATES = {
        "python": {
            "function": 'def {function_name}({params}):\n    """{description}"""\n    {body}\n    return {return_var}',
            "comment": "# {comment}",
            "test": 'assert {function_name}({test_input}) == {expected_output}',
        },
        "javascript": {
            "function": 'function {function_name}({params}) {\n    // {description}\n    {body}\n    return {return_var};\n}',
            "comment": "// {comment}",
            "test": 'console.assert({function_name}({test_input}) === {expected_output});',
        },
        "java": {
            "function": 'public static {return_type} {function_name}({params}) {\n    // {description}\n    {body}\n    return {return_var};\n}',
            "comment": "// {comment}",
            "test": 'assert {function_name}({test_input}) == {expected_output};',
        },
        "cpp": {
            "function": '{return_type} {function_name}({params}) {\n    // {description}\n    {body}\n    return {return_var};\n}',
            "comment": "// {comment}",
            "test": 'assert({function_name}({test_input}) == {expected_output});',
        },
        "go": {
            "function": 'func {function_name}({params}) {return_type} {\n    // {description}\n    {body}\n    return {return_var}\n}',
            "comment": "// {comment}",
            "test": 'if {function_name}({test_input}) != {expected_output} { t.Fatal(...) }',
        },
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.languages = self.config.get("languages", ["python"])
        self.max_examples = self.config.get("max_examples", 2)
        self.include_tests = self.config.get("include_tests", True)
        self.include_comments = self.config.get("include_comments", True)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Generate code examples for patterns."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()

            # Generate code for each language
            code_examples = {}
            for language in self.languages:
                if language in self.TEMPLATES:
                    code = await self._generate_code(pattern, language, context)
                    if code:
                        code_examples[language] = code

            if code_examples:
                enriched["code_examples"] = code_examples

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    async def _generate_code(
        self,
        pattern: Dict[str, Any],
        language: str,
        context: EnrichmentContext
    ) -> Optional[Dict[str, Any]]:
        """Generate code for a specific language."""
        solution = pattern.get("solution", "")
        pattern_name = pattern.get("name", "")
        examples = pattern.get("examples", [])[:self.max_examples]

        if not solution and not examples:
            return None

        template = self.TEMPLATES.get(language)
        if not template:
            return None

        # Extract function name from pattern name
        function_name = self._to_function_name(pattern_name, language)

        # Generate code from solution or examples
        code_blocks = []

        # Main implementation
        impl = self._generate_implementation(solution, pattern, language, template, function_name)
        if impl:
            code_blocks.append({
                "type": "implementation",
                "code": impl,
                "description": f"{function_name} implementation"
            })

        # Test cases from examples
        if self.include_tests:
            tests = self._generate_tests(examples, language, template, function_name)
            if tests:
                code_blocks.append({
                    "type": "tests",
                    "code": tests,
                    "description": "Test cases"
                })

        # Usage example
        usage = self._generate_usage(pattern, language, template, function_name)
        if usage:
            code_blocks.append({
                "type": "usage",
                "code": usage,
                "description": "Usage example"
            })

        return {
            "language": language,
            "blocks": code_blocks
        }

    def _to_function_name(self, pattern_name: str, language: str) -> str:
        """Convert pattern name to function name."""
        # Remove special characters, use snake_case or camelCase
        import re

        # Clean name
        clean = re.sub(r'[^\w\s]', '', pattern_name)
        words = clean.split()

        if not words:
            return "example_function"

        if language in ["java", "javascript", "cpp", "go"]:
            # camelCase
            return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        else:
            # snake_case
            return '_'.join(w.lower() for w in words)

    def _generate_implementation(
        self,
        solution: str,
        pattern: Dict[str, Any],
        language: str,
        template: Dict[str, str],
        function_name: str
    ) -> Optional[str]:
        """Generate the main implementation."""
        if not solution:
            return None

        # Try to extract code-like structure from solution
        lines = solution.split('\n')
        code_lines = []
        indent = "    "

        for line in lines:
            line = line.strip()
            if not line or line.startswith('-'):
                continue

            # Convert pseudo-code to actual code
            if language == "python":
                code_lines.append(f"{indent}{self._to_python_line(line)}")
            elif language in ["javascript", "java", "cpp", "go"]:
                code_lines.append(f"{indent}{self._to_c_style_line(line)}")

        if not code_lines:
            return None

        # Wrap in function template
        body = '\n'.join(code_lines)

        if language == "python":
            params = "value, mask=0xFF"
            return_var = "value"
            return_type = None
        elif language in ["javascript", "java", "cpp", "go"]:
            params = "value, mask"
            return_var = "value"
            return_type = "int" if language in ["java", "cpp"] else None

        # Format function
        if language == "python":
            return template["function"].format(
                function_name=function_name,
                params=params,
                description=solution[:100],
                body=body.strip(),
                return_var=return_var
            )
        else:
            return_type_str = return_type or "int"
            return template["function"].format(
                return_type=return_type_str,
                function_name=function_name,
                params=params,
                description=solution[:100],
                body=body.strip(),
                return_var=return_var
            )

    def _to_python_line(self, line: str) -> str:
        """Convert pseudocode line to Python."""
        line = line.lower()

        # Common patterns
        if "xor" in line and "^" not in line:
            line = line.replace("xor", "^")
        if "and" in line and "&&" not in line:
            line = line.replace(" and ", " and ")
        if "or" in line and "||" not in line:
            line = line.replace(" or ", " or ")

        return line

    def _to_c_style_line(self, line: str) -> str:
        """Convert pseudocode line to C-style syntax."""
        line = line.lower()

        if "xor" in line and "^" not in line:
            line = line.replace("xor", "^")

        return line + ";"

    def _generate_tests(
        self,
        examples: List[Any],
        language: str,
        template: Dict[str, str],
        function_name: str
    ) -> Optional[str]:
        """Generate test cases from examples."""
        if not examples:
            return None

        test_lines = []

        for example in examples[:self.max_examples]:
            if not isinstance(example, dict):
                continue

            # Extract test input/output
            if "input" in example and "output" in example:
                test_input = example["input"]
                expected_output = example["output"]
            elif "value" in example and "result" in example:
                test_input = example["value"]
                expected_output = example["result"]
            else:
                continue

            # Generate test
            try:
                test = template["test"].format(
                    function_name=function_name,
                    test_input=str(test_input),
                    expected_output=str(expected_output)
                )
                test_lines.append(test)
            except KeyError:
                continue

        if not test_lines:
            return None

        return '\n'.join(test_lines)

    def _generate_usage(
        self,
        pattern: Dict[str, Any],
        language: str,
        template: Dict[str, str],
        function_name: str
    ) -> Optional[str]:
        """Generate a usage example."""
        pattern_name = pattern.get("name", "").lower()
        function_name = self._to_function_name(pattern_name, language)

        if language == "python":
            return f"# Example usage\nresult = {function_name}(0x55, 0xFF)\nprint(f\"Result: {{result}}\")"
        elif language == "javascript":
            return f"// Example usage\nconst result = {function_name}(0x55, 0xFF);\nconsole.log(`Result: ${result}`);"
        elif language == "java":
            return f"// Example usage\nint result = {function_name}(0x55, 0xFF);\nSystem.out.println(\"Result: \" + result);"
        elif language == "cpp":
            return f"// Example usage\nint result = {function_name}(0x55, 0xFF);\nstd::cout << \"Result: \" << result << std::endl;"
        elif language == "go":
            return f"// Example usage\nresult := {function_name}(0x55, 0xFF)\nfmt.Printf(\"Result: %d\\n\", result)"

        return None

    def get_supported_formats(self) -> List[str]:
        """Code generation works best with markdown formats."""
        return ["markdown", "md"]


class CodeSnippetEnricher(EnrichmentPlugin):
    """
    Adds inline code snippets to pattern descriptions.

    Extracts code-like content from solutions and examples
    and formats them as code blocks.
    """

    name = "Code Snippet Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.languages = self.config.get("languages", ["python", "javascript"])

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add code snippets to patterns."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()

            # Extract code snippets
            snippets = self._extract_snippets(pattern)
            if snippets:
                enriched["code_snippets"] = snippets

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    def _extract_snippets(self, pattern: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract code snippets from pattern."""
        snippets = []

        # Check solution
        solution = pattern.get("solution", "")
        if self._has_code(solution):
            snippets.append({
                "language": self._detect_language(solution),
                "code": solution,
                "source": "solution"
            })

        # Check examples
        for example in pattern.get("examples", []):
            if isinstance(example, dict):
                for key, value in example.items():
                    if isinstance(value, str) and self._has_code(value):
                        snippets.append({
                            "language": self._detect_language(value),
                            "code": value,
                            "source": f"example.{key}"
                        })

        return snippets

    def _has_code(self, text: str) -> bool:
        """Check if text contains code."""
        code_indicators = [
            "function", "def ", "class ", "=>", "return ",
            "var ", "let ", "const ", "int ", "String ",
            "for(", "while(", "if(", "else{"
        ]
        return any(indicator in text for indicator in code_indicators)

    def _detect_language(self, code: str) -> str:
        """Detect programming language from code snippet."""
        code_lower = code.lower()

        if "def " in code_lower or "import " in code_lower:
            return "python"
        elif "function" in code_lower or "=>" in code_lower or "const " in code_lower:
            return "javascript"
        elif "public static" in code_lower or "System.out" in code_lower:
            return "java"
        elif "std::" in code_lower or "#include" in code_lower:
            return "cpp"
        elif "func " in code_lower or "fmt." in code_lower:
            return "go"

        return "text"
