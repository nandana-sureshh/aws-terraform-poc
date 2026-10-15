Prompt 1
--------

POC Proposal: AWS Infrastructure Dependency Mapper
Context
I am a DevOps engineer trainee focusing on AWS Cloud Infrastructure, Networking, and Terraform. I have been asked to build a very small, practical POC that demonstrates my technical skills and how I use Claude effectively during development.
I currently do not have access to an AWS account or the Terraform CLI. Therefore, the POC must be completely testable locally using mock data.
Claude is to be used as a development assistant for brainstorming, designing, implementing, reviewing, and testing the solution. AI must not be integrated into the finished POC.
Business Problem
Understanding the relationships between AWS infrastructure resources can require engineers to manually inspect configuration files and trace resource references. Missing references in an infrastructure inventory can also make the configuration harder to review and troubleshoot.
Proposed Solution
Build a simple AWS Infrastructure Dependency Mapper using Python and mock JSON data.
The tool should read a sample infrastructure inventory, identify and display relationships between resources, and report references to resources that do not exist in the supplied inventory.
Initial Scope
Represent only four AWS resource types: VPC, subnet, EC2 instance, and security group.
The program should:
Read infrastructure data from a JSON file.
Identify resource relationships from explicitly defined references.
Display the relationships in the terminal.
Detect missing resource references.
Produce a clear summary of the validation results.
Include automated tests for valid data, missing references, and invalid input.
Include a small illustrative Terraform configuration to demonstrate how the modeled resource relationships correspond to Terraform resources. Do not claim that Terraform configuration has been validated by the Terraform CLI.
Constraints
No AWS account or credentials.
No Terraform CLI.
No cloud deployment.
No AI integration into the finished tool.
No web interface, dashboard, database, or graphical dependency diagram.
Avoid CIDR validation, security analysis, route simulation, and unrelated features.
Keep the code understandable for a beginner and the implementation small.
Reliability Requirements
Use predefined test cases with known expected results. Ensure that missing references are not silently ignored. Distinguish actual validation results from assumptions in the mock data, and document the limitations of the tool.
Expected Deliverables
A Python program.
A mock JSON infrastructure inventory.
Automated tests.
A small illustrative Terraform example.
A README containing the business problem, scope, architecture, execution instructions, test results, and limitations.
Your First Task
Before writing code, review this proposal. Identify any ambiguity, recommend the simplest reliable data structure and relationship rules, and define the expected terminal output and test cases.
Do not expand the scope or generate the implementation yet. Wait until the requirements are agreed upon.so Make a plan accordingly


prompt 2
--------

The requirements review looks good. Please proceed with the implementation, keeping the POC small, beginner-friendly, and within the original scope.
Please follow these decisions:
Use exit code 0 when all references resolve, 1 when references are missing, and 2 when the input is invalid.
Treat a reference pointing to an ID that does not exist in the expected resource collection as a missing reference, including wrong-type references.
Keep cross-VPC consistency checks, CIDR validation, security analysis, and route simulation out of scope.
Use Python’s built-in unittest framework. Do not install external packages.
Prioritize these six core test scenarios:
Valid inventory where all references resolve.
Subnet referencing a nonexistent VPC.
EC2 instance referencing a nonexistent subnet.
EC2 instance referencing a nonexistent security group.
Invalid input, such as malformed JSON or a missing required field.
Empty security_group_ids list, which should be valid.
Retain essential input validation for malformed JSON, duplicate IDs, incorrect field types, and missing required fields, but avoid unnecessary features.
Keep the output terminal-based. Do not create a web interface or graphical diagram.
Include a small illustrative Terraform configuration in terraform/main.tf. Clearly document that it has not been validated using the Terraform CLI.
Create the planned files: mapper.py, data/valid_inventory.json, data/missing_refs_inventory.json, tests/test_mapper.py, terraform/main.tf, and README.md.
Run the automated tests and execute the mapper against both inventory examples. Fix any failures and report the actual results and commands used. Do not claim that anything passed unless it was actually executed successfully.
Keep the README concise and explain the business problem, how the tool works, how to run it, the actual test results, and the limitations of using mock data.
Before finishing, summarize the files created, the checks performed, and anything that could not be verified due to the lack of AWS access and Terraform CLI. Do not expand the scope beyond these requirements.The requirements review looks good. Please proceed with the implementation, keeping the POC small, beginner-friendly, and within the original scope.
Please follow these decisions:
1. Use exit code 0 when all references resolve, 1 when references are missing, and 2 when the input is invalid.
2. Treat a reference pointing to an ID that does not exist in the expected resource collection as a missing reference, including wrong-type references.
3. Keep cross-VPC consistency checks, CIDR validation, security analysis, and route simulation out of scope.
4. Use Python’s built-in unittest framework. Do not install external packages.
5. Prioritize these six core test scenarios:
   * Valid inventory where all references resolve.
   * Subnet referencing a nonexistent VPC.
   * EC2 instance referencing a nonexistent subnet.
   * EC2 instance referencing a nonexistent security group.
   * Invalid input, such as malformed JSON or a missing required field.
   * Empty security_group_ids list, which should be valid.
6. Retain essential input validation for malformed JSON, duplicate IDs, incorrect field types, and missing required fields, but avoid unnecessary features.
7. Keep the output terminal-based. Do not create a web interface or graphical diagram.
8. Include a small illustrative Terraform configuration in terraform/main.tf. Clearly document that it has not been validated using the Terraform CLI.
9. Create the planned files: mapper.py, data/valid_inventory.json, data/missing_refs_inventory.json, tests/test_mapper.py, terraform/main.tf, and README.md.
10. Run the automated tests and execute the mapper against both inventory examples. Fix any failures and report the actual results and commands used. Do not claim that anything passed unless it was actually executed successfully.
Keep the README concise and explain the business problem, how the tool works, how to run it, the actual test results, and the limitations of using mock data.
Before finishing, summarize the files created, the checks performed, and anything that could not be verified due to the lack of AWS access and Terraform CLI. Do not expand the scope beyond these requirements

Pompt 3
-------

I want your help with a small POC, and before we start, I want to explain the context. I had a discussion with my stakeholder about my technical skillset and future project allocation. He asked me which areas I am most proficient in as im a fresher , and I told him that I would like to focus on AWS Cloud Infrastructure and Networking, along with Terraform.  He specifically wants to see how we use AI tools like Claude to build the POC not actually integrate ai into the poc.He also mentioned that we should aim to make the POC as reliable as possible and that we can use mock data if needed. Currently, I do not have access to an AWS account or Terraform in my working environment, so the POC needs to be achievable locally using mock data if necessary. I want this POC to demonstrate both my AWS and Terraform knowledge and my ability to use Claude effectively during the development process. However, it must remain very small, simple, practical, and achievable within a short time. I don’t want to overcomplicate it or build a full-fledged application. For now, please just understand this context. Help me brainstorm a few suitable POC ideas that meet these requirements, compare their feasibility and relevance, and recommend the most appropriate one. Tell me what we could demonstrate without AWS or Terraform access, and how we could validate the results.
AWS Infrastructure Dependency Mapper is a better option. No need to complicate whith much resources. a vpc, subnet,
security group and ec2 instance references might be sufficient for this build, as the expectation is much into looking for the ability to build something throught AI assistance. so how can we actually implement this by using mock data without terraform cli access and aws account.
