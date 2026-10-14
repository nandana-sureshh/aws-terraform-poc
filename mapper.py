"""AWS Infrastructure Dependency Mapper (POC).

Reads a mock JSON inventory of VPCs, subnets, security groups and EC2
instances, shows how they reference each other, and reports references
that point to resources that are not in the inventory.

Usage: python mapper.py data/valid_inventory.json
Exit codes: 0 = all references resolve, 1 = missing references, 2 = invalid input
"""

import json
import sys

COLLECTIONS = ["vpcs", "subnets", "security_groups", "instances"]

# The complete set of relationship rules:
# collection -> list of (reference field, collection the target must be in, is it a list?)
REFERENCE_RULES = {
    "subnets": [("vpc_id", "vpcs", False)],
    "security_groups": [("vpc_id", "vpcs", False)],
    "instances": [
        ("subnet_id", "subnets", False),
        ("security_group_ids", "security_groups", True),
    ],
}


class InventoryError(Exception):
    """Raised when the input file is not a usable inventory."""


def load_inventory(path):
    """Read the JSON file and check its structure. Returns the parsed data."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as err:
        raise InventoryError(f"cannot read '{path}': {err.strerror}")
    except json.JSONDecodeError as err:
        raise InventoryError(f"'{path}' is not valid JSON: {err}")
    validate_structure(data)
    return data


def _check_id_string(value, where):
    if not isinstance(value, str) or not value:
        raise InventoryError(f"{where} must be a non-empty string")


def validate_structure(data):
    """Raise InventoryError if the data is not shaped like an inventory."""
    if not isinstance(data, dict):
        raise InventoryError("top level of the file must be a JSON object")

    seen_ids = set()
    for collection in COLLECTIONS:
        if collection not in data:
            raise InventoryError(f"missing required list '{collection}'")
        if not isinstance(data[collection], list):
            raise InventoryError(f"'{collection}' must be a list")

        for index, resource in enumerate(data[collection]):
            where = f"{collection}[{index}]"
            if not isinstance(resource, dict):
                raise InventoryError(f"{where} must be an object")
            if "id" not in resource:
                raise InventoryError(f"{where} is missing required field 'id'")
            _check_id_string(resource["id"], f"{where}.id")
            if resource["id"] in seen_ids:
                raise InventoryError(f"duplicate id '{resource['id']}'")
            seen_ids.add(resource["id"])

            for field, _target, is_list in REFERENCE_RULES.get(collection, []):
                if field not in resource:
                    raise InventoryError(f"{where} is missing required field '{field}'")
                if is_list:
                    if not isinstance(resource[field], list):
                        raise InventoryError(f"{where}.{field} must be a list")
                    for item in resource[field]:
                        _check_id_string(item, f"{where}.{field} entries")
                else:
                    _check_id_string(resource[field], f"{where}.{field}")


def find_references(data):
    """Return one dict per reference, with 'exists' saying if the target is present."""
    ids_by_collection = {c: {r["id"] for r in data[c]} for c in COLLECTIONS}
    references = []
    for collection, rules in REFERENCE_RULES.items():
        for resource in data[collection]:
            for field, target_collection, is_list in rules:
                targets = resource[field] if is_list else [resource[field]]
                for target in targets:
                    references.append({
                        "source": resource["id"],
                        "field": field,
                        "target": target,
                        "exists": target in ids_by_collection[target_collection],
                    })
    return references


def print_tree(data):
    """Show VPC -> subnet -> instance, plus each VPC's security groups."""
    print("Infrastructure Dependency Map")
    print("=============================")
    for vpc in data["vpcs"]:
        print(f"{vpc['id']} (vpc)")
        for subnet in data["subnets"]:
            if subnet["vpc_id"] != vpc["id"]:
                continue
            print(f"  {subnet['id']} (subnet)")
            for inst in data["instances"]:
                if inst["subnet_id"] != subnet["id"]:
                    continue
                groups = ", ".join(inst["security_group_ids"]) or "none"
                print(f"    {inst['id']} (instance) security groups: {groups}")
        for sg in data["security_groups"]:
            if sg["vpc_id"] == vpc["id"]:
                print(f"  {sg['id']} (security group)")
    print("(Resources whose parent is missing are not shown above; see Relationships.)")


def print_report(data, references):
    print_tree(data)

    print("\nRelationships")
    print("-------------")
    for ref in references:
        status = "OK" if ref["exists"] else "MISSING"
        print(f"{ref['source']:<14} -> {ref['target']:<14} [{ref['field']}] {status}")

    missing = [r for r in references if not r["exists"]]
    print("\nValidation Summary")
    print("------------------")
    counts = ", ".join(f"{len(data[c])} {c}" for c in COLLECTIONS)
    print(f"Resources: {counts}")
    print(f"References checked: {len(references)}  "
          f"Resolved: {len(references) - len(missing)}  Missing: {len(missing)}")
    if missing:
        print(f"RESULT: FAIL - {len(missing)} missing reference(s)")
        for ref in missing:
            print(f"  - {ref['source']} references {ref['target']} "
                  f"via {ref['field']}, which does not exist in the inventory")
    else:
        print("RESULT: PASS - all references resolve")
    print("Validated: file structure, unique ids, references resolve within this file.")
    print("Assumed (not checked): ids are mock values; the inventory is complete; "
          "nothing was checked against real AWS or the Terraform CLI.")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python mapper.py <inventory.json>", file=sys.stderr)
        return 2
    try:
        data = load_inventory(argv[0])
    except InventoryError as err:
        print(f"ERROR: invalid inventory: {err}", file=sys.stderr)
        return 2

    references = find_references(data)
    print_report(data, references)
    return 1 if any(not r["exists"] for r in references) else 0


if __name__ == "__main__":
    sys.exit(main())
