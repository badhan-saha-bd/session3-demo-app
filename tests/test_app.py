import unittest

from app import response_for


class ResponseTests(unittest.TestCase):
    def test_health_endpoint(self):
        status, payload = response_for("/health")
        self.assertEqual(status, 201)
        self.assertEqual(payload, {"status": "ok"})

    def test_root_endpoint(self):
        status, payload = response_for("/")
        self.assertEqual(status, 200)
        self.assertEqual(payload["application"], "session3-training-app")

    def test_unknown_endpoint(self):
        status, payload = response_for("/missing")
        self.assertEqual(status, 404)
        self.assertEqual(payload, {"error": "not found"})


if __name__ == "__main__":
    unittest.main()
