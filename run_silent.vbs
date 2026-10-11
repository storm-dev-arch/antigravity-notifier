Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Users\storm\AppData\Local\Programs\Python\Python314\pythonw.exe"" """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\app.py""", 0, False
