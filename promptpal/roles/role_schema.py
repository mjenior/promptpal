from importlib import resources

import yaml
from jsonschema import validate

# Load the role schema from the YAML file
with resources.open_text("promptpal.roles", "role_schema.yaml") as file:
    ROLE_SCHEMA = yaml.safe_load(file)


def validate_role(role_data):
    """
    Validate the role data against the role schema.

    Args:
        role_data (dict): The role data to validate.

    Raises:
        ValidationError: If the role data does not conform to the schema.
    """
    validate(instance=role_data, schema=ROLE_SCHEMA)
