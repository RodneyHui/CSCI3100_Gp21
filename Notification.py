from datetime import datetime, timedelta
import Database as db
import KanbanInfoDatabase as kdb
import sqlite3
from pathlib import Path

DB_PATH = Path("kanban.db")
Due = 14

def UpcomingTask():
    Now = datetime.now()
    Threshold = Now + timedelta(days=Due)

    Connection = sqlite3.connect(DB_PATH)
    Query = Connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'KANBAN'")
    Data = Query.fetchone()
    if Data is not None:
        Query = Connection.execute("SELECT * FROM KANBAN")
        Data = Query.fetchall()
        Connection.close()
    else:
        Connection.close()
        return []

    Notifications = []
    Notifications.append("\n" + "-"*50 + "\n")

    for Datum in Data:
        TaskID = Datum[0]
        Title = Datum[1]
        Status = Datum[2]
        PersonInCharge = Datum[3]
        CreationDate = Datum[4]
        DueDateStr = Datum[5]
        Creator = Datum[6]
        Editor = Datum[7]
        AddtionalInfo = Datum[8]

        if not isinstance(DueDateStr, str) or not DueDateStr.strip():
            continue
        try:
            DueDate_base = datetime.strptime(DueDateStr.strip(), "%Y-%m-%d")
            DueDate = DueDate_base.replace(hour=23, minute=59, second=59, microsecond=999999)
        except (ValueError, TypeError):
            continue
        if DueDate.date() < Now.date() or (Now.date() <= DueDate.date() <= Threshold.date()):
            TimeLeft = DueDate - Now
            if TimeLeft < timedelta(0):
                OverdueDelta = -TimeLeft  
                Days = OverdueDelta.days
                Hours = int(OverdueDelta.seconds // 3600)
                Minutes = int((OverdueDelta.seconds % 3600) // 60)
                DueIn = f"{Days}d {Hours:02d}h {Minutes:02d}m"
                DueMessage = f"[Task overdue by {DueIn}]\n"
            else:
                Days = TimeLeft.days
                Hours = int(TimeLeft.seconds // 3600)
                Minutes = int((TimeLeft.seconds % 3600) // 60)
                DueIn = f"{Days}d {Hours:02d}h {Minutes:02d}m"
                if DueDate_base.date() == Now.date():
                    DueIn = f"0d {Hours:02d}h {Minutes:02d}m"
                DueMessage = f"[Task due in {DueIn}]\n"
            PersonInCharge = kdb.GetUserByPhone(PersonInCharge)
            Creator = kdb.GetUserByPhone(Creator)
            Editor = kdb.GetUserByPhone(Editor)
            Message = [
                f"{DueMessage}",
                f"Task ID: {TaskID}\n",
                f"Title: {Title}\n",
                f"Status: {Status}\n",
                f"Person in charge: {PersonInCharge}\n",
                f"Creation date: {CreationDate}\n",
                f"Due date: {DueDateStr}\n",
                f"Creator: {Creator}\n",
                f"Editor: {Editor}\n",
                f"Additional information: {AddtionalInfo}",
            ]
            Notifications.append("".join(Message))
            Notifications.append("\n" + "-"*50 + "\n")
    return Notifications

def PrintNotification():
    Notifications = UpcomingTask()
    if Notifications is None:
        return
    for Task in Notifications:
        print(Task)