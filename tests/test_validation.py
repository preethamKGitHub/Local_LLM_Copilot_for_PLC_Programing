import unittest

from plc_rag.validation import REFUSAL, validate_generation


class ValidationTests(unittest.TestCase):
    def check_code(self, code):
        return validate_generation("```iecst\n" + code + "\n```")

    def test_class_field_restriction_but_not_method_inputs(self):
        valid = "CLASS Motor METHOD PUBLIC Start VAR_INPUT go : BOOL; END_VAR END_METHOD END_CLASS"
        self.assertEqual(self.check_code(valid)["status"], "passed_checks")
        result = self.check_code("CLASS Motor VAR_INPUT go : BOOL; END_VAR END_CLASS")
        self.assertEqual(result["findings"][0]["code"], "class_section")

    def test_fb_definition_does_not_require_instance_or_call(self):
        result = self.check_code("FUNCTION_BLOCK Motor VAR PRIVATE running : BOOL; END_VAR END_FUNCTION_BLOCK")
        self.assertEqual(result["status"], "passed_checks")
        self.assertEqual(result["compilation_status"], "not_run")

    def test_enumeration_and_inheritance(self):
        self.assertEqual(self.check_code("TYPE Color : (Red, Green); END_TYPE")["status"], "passed_checks")
        self.assertEqual(self.check_code("PROGRAM Main VAR Color : (Red, Green); END_VAR END_PROGRAM")["findings"][0]["code"], "inline_enumeration")
        self.assertEqual(self.check_code("CLASS Motor EXTENDS Base, Other END_CLASS")["findings"][0]["code"], "multiple_inheritance")

    def test_comments_and_strings_are_not_code(self):
        code = "CLASS Motor\n(* outer (* VAR_INPUT *) VAR_OUTPUT *)\nVAR text : STRING := 'CLASS VAR_INPUT'; END_VAR\n// VAR_INPUT\nEND_CLASS"
        self.assertEqual(self.check_code(code)["status"], "passed_checks")

    def test_refusal_missing_empty_and_truncated(self):
        self.assertEqual(validate_generation(REFUSAL)["status"], "not_applicable")
        for answer in ["", "Here is some code", "```iecst\nCLASS Motor", "```iecst\n```", "```iecst\nCLASS Motor\n```"]:
            self.assertEqual(validate_generation(answer)["status"], "warnings", answer)

    def test_every_code_block_is_checked(self):
        result = validate_generation("```iecst\nCLASS Good END_CLASS\n```\n```iecst\nCLASS Bad VAR_INPUT flag : BOOL; END_VAR END_CLASS\n```")
        self.assertEqual(result["status"], "warnings")

    def test_citation_numbers_match_included_sources(self):
        code = "```iecst\nTYPE Color : (Red, Green); END_TYPE\n```"
        self.assertEqual(validate_generation(code, source_count=1)["findings"][0]["code"], "missing_citation")
        self.assertEqual(validate_generation(code + "\n[DOC 2]", source_count=1)["findings"][0]["code"], "invalid_citation")
        self.assertEqual(validate_generation(code + "\n[DOC 1]", source_count=1)["status"], "passed_checks")


if __name__ == "__main__":
    unittest.main()