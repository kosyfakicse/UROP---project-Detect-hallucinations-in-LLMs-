import unittest

from claim_support import classify_response_claims, split_claims


class ClaimSupportTests(unittest.TestCase):
    def test_split_claims_handles_sentences_and_bullets(self) -> None:
        response = "The sample report contains 20 records.\n- It was published in 2024."
        self.assertEqual(
            split_claims(response),
            ["The sample report contains 20 records.", "It was published in 2024."],
        )

    def test_classifies_supported_claim(self) -> None:
        response = "Paris is the capital of France."
        sources = ["France's capital city is Paris."]

        assessments = classify_response_claims(response, sources)

        self.assertEqual(assessments[0].classification, "supported")

    def test_classifies_partially_supported_claim(self) -> None:
        response = "Paris is the capital and largest city of France."
        sources = ["Paris is the capital of France."]

        assessments = classify_response_claims(response, sources)

        self.assertEqual(assessments[0].classification, "partially_supported")

    def test_classifies_unsupported_claim(self) -> None:
        response = "Berlin is the capital of France."
        sources = ["Paris is the capital of France."]

        assessments = classify_response_claims(response, sources)

        self.assertEqual(assessments[0].classification, "unsupported")

    def test_classifies_numeric_mismatch_as_unsupported(self) -> None:
        response = "The sample report contains 30 records."
        sources = ["The sample report contains 20 records."]

        assessments = classify_response_claims(response, sources)

        self.assertEqual(assessments[0].classification, "unsupported")


if __name__ == "__main__":
    unittest.main()
