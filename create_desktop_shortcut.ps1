$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Desktop = [Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop 'Asart Bookkeeping.lnk'
$Target = Join-Path $ProjectDir 'launch_bookkeeping.bat'
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description = 'Local bookkeeping and document archive'
$Shortcut.Save()
Write-Host "Created $ShortcutPath"
