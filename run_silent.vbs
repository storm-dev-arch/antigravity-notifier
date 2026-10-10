Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonPath = "C:\Users\storm\AppData\Local\Programs\Python\Python314\python.exe"
scriptPath = scriptDir & "\notifier_service.py"

WshShell.Run """" & pythonPath & """ """ & scriptPath & """", 0, False
