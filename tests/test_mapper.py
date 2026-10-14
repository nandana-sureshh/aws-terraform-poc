import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import mapper  # noqa: E402

VALID_FILE = os.path.join(ROOT, "data", "valid_inventory.json")
MISSING_FILE = os.path.join(ROOT, "data", "missing_refs_inventory.json")


def load_valid():
    """Fresh copy of the valid inventory so each test can modify it safely."""
    with open(VALID_FILE, encoding="utf-8") as f:
        return json.load(f)


def missing_of(data):
    return [r for r in mapper.find_references(data) if not r["exists"]]


def run_main(path):
    """Run the program on a file; return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = mapper.main([path])
    return code, out.getvalue(), err.getvalue()


class TestReferences(unittest.TestCase):
    def test_valid_inventory_all_references_resolve(self):
        data = mapper.load_inventory(VALID_FILE)
        self.assertEqual(len(mapper.find_references(data)), 10)
        self.assertEqual(missing_of(data), [])
        code, out, _ = run_main(VALID_FILE)
        self.assertEqual(code, 0)
        self.assertIn("RESULT: PASS", out)

    def test_subnet_with_nonexistent_vpc(self):
        data = load_valid()
        data["subnets"][0]["vpc_id"] = "vpc-999"
        missing = missing_of(data)
        self.assertEqual(len(missing), 1)
        self.assertEqual((missing[0]["source"], missing[0]["target"]),
                         ("subnet-public", "vpc-999"))

    def test_instance_with_nonexistent_subnet(self):
        data = load_valid()
        data["instances"][0]["subnet_id"] = "subnet-404"
        missing = missing_of(data)
        self.assertEqual(len(missing), 1)
        self.assertEqual((missing[0]["source"], missing[0]["target"]),
                         ("i-web1", "subnet-404"))

    def test_instance_with_nonexistent_security_group(self):
        data = load_valid()
        data["instances"][0]["security_group_ids"] = ["sg-web", "sg-ghost"]
        missing = missing_of(data)
        self.assertEqual(len(missing), 1)  # sg-web still resolves
        self.assertEqual((missing[0]["source"], missing[0]["target"]),
                         ("i-web1", "sg-ghost"))

    def test_empty_security_group_list_is_valid(self):
        data = load_valid()
        data["instances"][0]["security_group_ids"] = []
        mapper.validate_structure(data)  # must not raise
        self.assertEqual(missing_of(data), [])

    def test_wrong_type_reference_counts_as_missing(self):
        data = load_valid()
        data["instances"][0]["subnet_id"] = "vpc-main"  # a VPC id, not a subnet
        self.assertEqual(len(missing_of(data)), 1)

    def test_missing_refs_file_reports_all_three_and_exit_1(self):
        code, out, _ = run_main(MISSING_FILE)
        self.assertEqual(code, 1)
        self.assertIn("RESULT: FAIL - 3 missing", out)
        for target in ("vpc-999", "subnet-404", "sg-ghost"):
            self.assertIn(target, out)


class TestInvalidInput(unittest.TestCase):
    def assert_invalid(self, data):
        with self.assertRaises(mapper.InventoryError):
            mapper.validate_structure(data)

    def test_malformed_json_gives_exit_2(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "bad.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write('{"vpcs": [')
            code, _, err = run_main(path)
        self.assertEqual(code, 2)
        self.assertIn("not valid JSON", err)

    def test_missing_file_gives_exit_2(self):
        code, _, err = run_main(os.path.join(ROOT, "no_such_file.json"))
        self.assertEqual(code, 2)
        self.assertIn("ERROR", err)

    def test_missing_required_field(self):
        data = load_valid()
        del data["instances"][0]["subnet_id"]
        self.assert_invalid(data)

    def test_missing_id(self):
        data = load_valid()
        del data["vpcs"][0]["id"]
        self.assert_invalid(data)

    def test_missing_collection(self):
        data = load_valid()
        del data["subnets"]
        self.assert_invalid(data)

    def test_duplicate_id(self):
        data = load_valid()
        data["subnets"][1]["id"] = data["subnets"][0]["id"]
        self.assert_invalid(data)

    def test_wrong_field_type(self):
        data = load_valid()
        data["instances"][0]["security_group_ids"] = "sg-web"  # should be a list
        self.assert_invalid(data)

    def test_top_level_not_an_object(self):
        self.assert_invalid([])


if __name__ == "__main__":
    unittest.main()
