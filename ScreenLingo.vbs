' Double-click to start ScreenLingo (no PowerShell window required)
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = root

pythonw = root & "\.venv\Scripts\pythonw.exe"
mainpy = root & "\main.py"

If Not fso.FileExists(pythonw) Then
  MsgBox "Run install.ps1 or run.bat once first to set up ScreenLingo.", vbExclamation, "ScreenLingo"
  WScript.Quit 1
End If

shell.Run """" & pythonw & """ """ & mainpy & """", 0, False
