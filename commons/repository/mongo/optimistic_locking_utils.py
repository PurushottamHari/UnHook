from typing import Any, Dict, Optional

from pymongo import UpdateOne
from pymongo.results import BulkWriteResult


def create_optimistic_locking_update_op(
    filter_query: Dict[str, Any],
    update_dict: Dict[str, Any],
    version: int,
    id_for_insert: Optional[Any] = None,
) -> UpdateOne:
    """
    Creates a PyMongo UpdateOne operation with strict optimistic locking.

    Args:
        filter_query: The query to match the document.
        update_dict: The fields to $set in the document.
        version: The NEW version of the object we are trying to save.
        id_for_insert: Optional _id to use if this is an insert (upsert).

    Returns:
        UpdateOne: The configured PyMongo update operation.

    Raises:
        ValueError: If version field is missing or inconsistent in update_dict.
    """
    # Strict validation of version field
    if "version" not in update_dict:
        raise ValueError(
            "Optimistic locking requires a 'version' field in the update dictionary."
        )

    if update_dict["version"] != version:
        raise ValueError(
            f"Inconsistent version detected. Argument version ({version}) "
            f"does not match version in update_dict ({update_dict['version']})."
        )

    query = filter_query.copy()

    if version > 1:
        # Update existing document: version must match previous version
        query["version"] = version - 1
        upsert = False
    else:
        # Create new document: document must not exist (no version field)
        query["version"] = {"$exists": False}
        upsert = True

    update_body = {"$set": update_dict}

    # Use $setOnInsert for the _id to avoid issues if we are upserting with a specific ID
    if id_for_insert is not None:
        update_body["$setOnInsert"] = {"_id": id_for_insert}

    return UpdateOne(query, update_body, upsert=upsert)


def validate_bulk_write_result(
    result: BulkWriteResult, expected_count: int, model_name: str
):
    """
    Validates that all operations in a bulk write were successful.
    Matches + Upserts must equal the expected count.

    Args:
        result: The result from collection.bulk_write()
        expected_count: Number of operations attempted
        model_name: Name of the model (for error messaging)

    Raises:
        ValueError: If not all operations succeeded (optimistic lock failure).
    """
    actual_count = result.matched_count + result.upserted_count
    if actual_count < expected_count:
        raise ValueError(
            f"Optimistic lock failure in batch operation for {model_name}: "
            f"matched {result.matched_count}, upserted {result.upserted_count} "
            f"out of {expected_count} documents. "
            "This usually means one or more documents were updated by another process "
            "or already exist."
        )
