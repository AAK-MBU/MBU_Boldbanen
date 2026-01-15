"""Module to handle item processing"""
# from mbu_rpa_core.exceptions import ProcessError, BusinessError

from mbu_msoffice_integration.sharepoint_class import Sharepoint

from helpers import config, helper_functions


def process_item(item_data: dict, item_reference: str):
    """Function to handle item processing"""

    assert item_data, "Item data is required"
    assert item_reference, "Item reference is required"

    file_name = item_data.get("file_name")

    digilederteam_sharepoint_api = Sharepoint(**config.DIGILEDERTEAM_SHAREPOINT_KWARGS)

    digidaglig_sharepoint_api = Sharepoint(**config.DIGIDAGLIG_SHAREPOINT_KWARGS)

    binary_excel = digilederteam_sharepoint_api.fetch_file_using_open_binary(file_name=file_name, folder_name="")

    pdf_path = r"C:\tmp\Boldbanen\boldbanen.pdf"

    helper_functions.export_excel_to_pdf(binary_excel=binary_excel, pdf_path=pdf_path)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    digidaglig_sharepoint_api.upload_file_from_bytes(
        binary_content=pdf_bytes,
        file_name="Boldbanen.pdf",
        folder_name="General/Boldbaner"
    )
