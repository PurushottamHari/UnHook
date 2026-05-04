from typing import Any, Dict, Optional

from pymongo import UpdateOne


def create_optimistic_locking_update_op(
    filter_query: Dict[str, Any],
    update_dict: Dict[str, Any],
    version: int,
    id_for_insert: Optional[Any] = None,
) -> UpdateOne:
    """
    Creates a PyMongo UpdateOne operation with optimistic locking logic.

    Args:
        filter_query: The query to match the document.
        update_dict: The fields to $set in the document.
        version: The NEW version of the object we are trying to save.
        id_for_insert: Optional _id to use if this is an insert (upsert).

    Returns:
        UpdateOne: The configured PyMongo update operation.
    """
    query = filter_query.copy()

    # If version > 1, we must ensure the DB has version - 1
    if version > 1:
        query["version"] = version - 1
        upsert = False
    else:
        # For version 1, we ignore the check and allow a new insert (upsert)
        upsert = True

    update_body = {"$set": update_dict}

    # If we have a specific ID for insert (common in MongoDB upserts with custom _id)
    if id_for_insert is not None:
        update_body["$setOnInsert"] = {"_id": id_for_insert}

    return UpdateOne(query, update_body, upsert=upsert)
