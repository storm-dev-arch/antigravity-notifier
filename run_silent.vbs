Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
scriptPath = scriptDir & "\notifier_service.py"

Function FindPython()
    Dim localApp, pythonRoot, subFolder, target, testRun
    localApp = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%")
    
    ' 1. Search dynamically in current user's %LOCALAPPDATA%\Programs\Python first (instant, avoids WindowsApps stub)
    pythonRoot = localApp & "\Programs\Python"
    If fso.FolderExists(pythonRoot) Then
        For Each subFolder In fso.GetFolder(pythonRoot).SubFolders
            target = subFolder.Path & "\pythonw.exe"
            If fso.FileExists(target) Then
                FindPython = """" & target & """"
                Exit Function
            End If
            target = subFolder.Path & "\python.exe"
            If fso.FileExists(target) Then
                FindPython = """" & target & """"
                Exit Function
            End If
        Next
    End If

    ' 2. Check pythonw directly in PATH
    On Error Resume Next
    testRun = WshShell.Run("pythonw.exe -c ""import sys""", 0, True)
    If Err.Number = 0 And testRun = 0 Then
        FindPython = "pythonw.exe"
        Exit Function
    End If
    Err.Clear

    ' 3. Check py.exe launcher
    testRun = WshShell.Run("py.exe -3 -c ""import sys""", 0, True)
    If Err.Number = 0 And testRun = 0 Then
        FindPython = "py.exe -3"
        Exit Function
    End If
    Err.Clear

    ' 4. Fallback to python.exe
    FindPython = "python.exe"
End Function

pythonExe = FindPython()
WshShell.CurrentDirectory = scriptDir
WshShell.Run pythonExe & " """ & scriptPath & """", 0, False
