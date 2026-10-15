# AWS Infrastructure Dependency Mapper (POC)

## Business problem
Understanding how AWS resources relate (which subnet is in which VPC, which security groups an instance uses) means manually reading configuration and tracing IDs. A reference to a resource that is not in the inventory is easy to miss and makes troubleshooting harder. This POC reads a mock inventory, shows the relationships, and reports every reference that does not resolve.

Claude was used as a development assistant (design review, implementation, tests). There is no AI in the tool itself.

## Scope
Four resource types only: VPC, subnet, security group, EC2 instance. Terminal output only.

## How it works
`mapper.py` (standard library only)-
1. `load_inventory` reads the JSON and `validate_structure` checks it (required lists/fields, correct types, unique ids). Problems raise `InventoryError`.
2. `find_references` applies four explicit rules, nothing is inferred:

| Resource | Field | Must exist in |
|---|---|---|
| subnet | `vpc_id` | `vpcs` |
| security group | `vpc_id` | `vpcs` |
| instance | `subnet_id` | `subnets` |
| instance | `security_group_ids` (list, may be empty) | `security_groups` |

A reference to an id that is not in the expected collection (including an id of the wrong type) is reported as **MISSING**.
3. The report prints a tree, every relationship with OK/MISSING, and a summary.

Exit codes: `0` all references resolve, `1` missing references, `2` invalid input.

## Run
Requires Python 3 and no packages. On Windows use `py` if `python` is not available.
```
python mapper.py data/valid_inventory.json
python mapper.py data/missing_refs_inventory.json
python -m unittest discover -s tests -v
```
Files: `data/valid_inventory.json` (10 references, all resolve), `data/missing_refs_inventory.json` (3 deliberate broken references: `vpc-999`, `subnet-404`, `sg-ghost`), `terraform/main.tf` (illustration).

## Test results (actually executed, Python 3.13.2, Windows)
Commands: `py -m unittest discover -s tests -v`, `py mapper.py data/valid_inventory.json`, `py mapper.py data/missing_refs_inventory.json`.

- Unit tests: **15 run, all OK**. They cover the valid inventory, subnet with missing VPC, instance with missing subnet, instance with missing security group, empty `security_group_ids` (valid), wrong-type reference, the missing-refs file, and invalid input (malformed JSON, missing file, missing field/id/list, duplicate id, wrong field type, non-object top level).
- `valid_inventory.json`: 10 checked, 10 resolved, 0 missing, `RESULT: PASS`, exit code 0.
- `missing_refs_inventory.json`: 10 checked, 7 resolved, 3 missing, `RESULT: FAIL`, exit code 1.

## Terraform example
`terraform/main.tf` shows how the modeled references correspond to Terraform resources (`aws_vpc`, `aws_subnet`, `aws_security_group`, `aws_instance`). **It has not been validated with the Terraform CLI** (not installed) and is not read by the tool. The AMI id is a placeholder.

## Limitations
- Validates only what is in the supplied JSON file: ids are mock values and the inventory is assumed to be complete. Nothing is checked against real AWS.
- The JSON schema is a simplification, not a real AWS or Terraform state export.
- A "missing" reference means missing from this file, not necessarily absent in AWS.
- No cross-VPC checks (e.g. an instance using a security group from another VPC is not flagged), no CIDR, security or routing analysis.
- Resources whose parent is missing are not drawn in the tree; they appear in the relationship list as MISSING.
- Terraform example is illustrative and unvalidated.
