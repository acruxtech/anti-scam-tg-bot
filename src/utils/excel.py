from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter
from openpyxl.cell.cell import Cell
from openpyxl.styles import Alignment

from src.entities.scammers.service import scammers_service
from src.entities.scammers.models import Scammer


async def create_list_scammer():
    wb = Workbook()
    ws: Worksheet = wb.active
    scammers = await scammers_service.get_scammer_list()

    ws.cell(row=1, column=1, value="№")
    ws.cell(row=1, column=2, value="ID")
    ws.cell(row=1, column=3, value="Username")
    ws.cell(row=1, column=4, value="First Name")
    ws.cell(row=1, column=5, value="Первое появления в БД")
    ws.cell(row=1, column=6, value="Время подтверждения")

    index = 2
    scammer: Scammer
    for scammer in scammers:
        ws.cell(row=index, column=1, value=index - 1)
        ws.cell(row=index, column=2, value=scammer.id)
        ws.cell(row=index, column=3, value=scammer.username)
        ws.cell(row=index, column=4, value=scammer.first_name)
        ws.cell(row=index, column=5, value=scammer.datetime_first)
        ws.cell(row=index, column=6, value=scammer.datetime_confirmed)
        index += 1

    column_widths = []

    for col_cells in ws.iter_cols(min_col=1, max_col=6):
        cell_lens = []
        cell: Cell
        for cell in col_cells:
            cell.alignment = Alignment(horizontal="center")
            cell_lens.append(len(str(cell.value)))
        print(cell_lens)
        column_widths.append(max(cell_lens) + 5)

    print(column_widths)

    for i in range(1, ws.max_column + 1):
        ws.column_dimensions[get_column_letter(i)].width = column_widths[i - 1]

    wb.save("te2st.xlsx")
