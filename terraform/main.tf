# ILLUSTRATIVE ONLY. This file has NOT been validated with the Terraform CLI
# (terraform init/validate/plan were never run) and is never read by mapper.py
# It shows how the modeled relationships map to Terraform references.
# The AMI id is a placeholder.

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {                       # JSON: vpcs[].id
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {                  # JSON: subnets[]
  vpc_id     = aws_vpc.main.id                    # JSON field: vpc_id
  cidr_block = "10.0.1.0/24"
}

resource "aws_security_group" "web" {             # JSON: security_groups[]
  name   = "sg-web"
  vpc_id = aws_vpc.main.id                        # JSON field: vpc_id
}

resource "aws_instance" "web1" {                  # JSON: instances[]
  ami                    = "ami-00000000"         # placeholder
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id   # JSON field: subnet_id
  vpc_security_group_ids = [aws_security_group.web.id]  # JSON field: security_group_ids
}
