Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")
folder = files.GetParentFolderName(WScript.ScriptFullName)

exe = folder & "\Eclipse Client.exe"
If files.FileExists(exe) Then
    shell.Run """" & exe & """", 0, False
Else
    shell.Run "pyw -3 """ & folder & "\lib\bootstrap.py""", 0, False
End If
