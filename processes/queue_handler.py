"""Module to hande queue population"""

import asyncio
import json
import logging

from automation_server_client import Workqueue
from mbu_msoffice_integration.sharepoint_class import Sharepoint

from helpers import config, helper_functions

logger = logging.getLogger(__name__)


def retrieve_items_for_queue() -> list[dict]:
    """Function to populate queue"""
    items: list[dict] = []

    year_quarter, today = helper_functions.get_current_quarter()
    next_year_quarter = helper_functions.get_next_quarter()

    # The current quarter is always queued - a missing file is a real problem and
    # should surface as an error during processing.
    current_boldbane_file_name = f"{config.BOLDBANE_FILE_NAME_PREFIX} {year_quarter}"

    logger.info("Queueing current quarter file: %s", current_boldbane_file_name)

    items.append(
        {
            "reference": f"boldbanen_{year_quarter}_{today}",
            "data": {"file_name": current_boldbane_file_name},
        }
    )

    # Next quarter is only queued once the file has actually been made available.
    next_boldbane_file_name = f"{config.BOLDBANE_FILE_NAME_PREFIX} {next_year_quarter}"

    digilederteam_sharepoint_api = Sharepoint(**config.DIGILEDERTEAM_SHAREPOINT_KWARGS)

    if helper_functions.file_exists_in_sharepoint(
        sharepoint_api=digilederteam_sharepoint_api,
        file_name=f"{next_boldbane_file_name}.xlsx",
        folder_name=config.BOLDBANE_SOURCE_FOLDER,
    ):
        logger.info("Queueing next quarter file: %s", next_boldbane_file_name)

        items.append(
            {
                "reference": f"boldbanen_{next_year_quarter}_{today}",
                "data": {"file_name": next_boldbane_file_name},
            }
        )

    else:
        logger.info(
            "No file found for next quarter (%s). Nothing queued for it.",
            next_year_quarter,
        )

    return items


def create_sort_key(item: dict) -> str:
    """
    Create a sort key based on the entire JSON structure.
    Converts the item to a sorted JSON string for consistent ordering.
    """
    return json.dumps(item, sort_keys=True, ensure_ascii=False)


async def concurrent_add(workqueue: Workqueue, items: list[dict]) -> None:
    """
    Populate the workqueue with items to be processed.
    Uses concurrency and retries with exponential backoff.

    Args:
        workqueue (Workqueue): The workqueue to populate.
        items (list[dict]): List of items to add to the queue.

    Returns:
        None

    Raises:
        Exception: If adding an item fails after all retries.
    """
    sem = asyncio.Semaphore(config.MAX_CONCURRENCY)

    async def add_one(it: dict):
        reference = str(it.get("reference") or "")
        data = {"item": it}

        async with sem:
            for attempt in range(1, config.MAX_RETRIES + 1):
                try:
                    await asyncio.to_thread(workqueue.add_item, data, reference)
                    logger.info("Added item to queue with reference: %s", reference)
                    return True

                except Exception as e:
                    if attempt >= config.MAX_RETRIES:
                        logger.error(
                            "Failed to add item %s after %d attempts: %s",
                            reference,
                            attempt,
                            e,
                        )
                        return False

                    backoff = config.RETRY_BASE_DELAY * (2 ** (attempt - 1))

                    logger.warning(
                        "Error adding %s (attempt %d/%d). Retrying in %.2fs... %s",
                        reference,
                        attempt,
                        config.MAX_RETRIES,
                        backoff,
                        e,
                    )
                    await asyncio.sleep(backoff)

    if not items:
        logger.info("No new items to add.")
        return

    sorted_items = sorted(items, key=create_sort_key)
    logger.info(
        "Processing %d items sorted by complete JSON structure", len(sorted_items)
    )

    results = await asyncio.gather(*(add_one(i) for i in sorted_items))
    successes = sum(1 for r in results if r)
    failures = len(results) - successes

    logger.info(
        "Summary: %d succeeded, %d failed out of %d", successes, failures, len(results)
    )
