import unittest

from claim_support import classify_response_claims, split_claims


class ClaimSupportTests(unittest.TestCase):
    def test_split_claims_handles_sentences_and_bullets(self) -> None:
        response = "Paris is the capital of France.\n- It has a population of 2 million."
        self.assertEqual(
            split_claims(response),
            ["Paris is the capital of France.", "It has a population of 2 million."],
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


if __name__ == "__main__":
    unittest.main()
