def schema_to_dict(schema) -> dict:
    if not schema:
        return {}
    elif hasattr(schema, "dict"):
        return schema.dict(exclude_none=True)
    elif isinstance(schema, dict):
        return {k: v for k, v in schema.items() if v is not None}
    return {}
