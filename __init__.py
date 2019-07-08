import time
import os
from aqt.main import AnkiQt

oldBackup = AnkiQt.backup
nbDayInMonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def backup(self, *args, **kwargs):
    r = oldBackup(self, *args, **kwargs)
    currentTime = time.localtime(time.time())
    year = int(time.strftime("%Y",currentTime))
    month = int(time.strftime("%m",currentTime))
    day = int(time.strftime("%d",currentTime))

    monthsToKeep = []
    for nbMonth in range(12):
        if nbMonth<month:
            monthsToKeep.append((year, month-nbMonth))
        else:
            monthsToKeep.append((year-1, month-nbMonth+12))

    nbDayThisMonth = nbDayInMonth[month-1]
    nbDayPreviousMonth = nbDayInMonth[(month-2) % 12]

    daysToKeep = []
    for nbDay in range(nbDayThisMonth):
        if nbDay<day:
            daysToKeep.append((year, month, day-nbDay))
        else:
            if month == 1:
                daysToKeep.append((year-1, 12, day-nbDay+nbDayPreviousMonth))
            else:
                daysToKeep.append((year, month-1, day-nbDay+nbDayPreviousMonth))
    filesWeMustHave = {f"backup-yearly-{year}.colpkg",
                       f"backup-monthly-{year}-{month}.colpkg",
                       f"backup-daily-{year}-{month}-{day}.colpkg"}
    filesToKeep = ([f"backup-monthly-{yearToHave}-{monthToHave}.colpkg" for yearToHave, monthToHave in monthsToKeep]+
                   [f"backup-daily-{yearToHave}-{monthToHave}-{dayToHave}.colpkg" for yearToHave, monthToHave, dayToHave in daysToKeep])
    dir = self.pm.backupFolder()
    for file in os.listdir(dir):
        if (file.startswith("backup-monthy-") or file.startswith("backup-daily-")) and file not in filesToKeep:
            os.unlink(os.path.join(dir, file))

    for file in filesWeMustHave:
        newpath = os.path.join(dir, file)
        if not os.path.exists(newpath):
            with open(self.pm.collectionPath(), "rb") as f:
                data = f.read()
            b = self.BackupThread(newpath, data)
            b.start()
    return r
AnkiQt.backup = backup
