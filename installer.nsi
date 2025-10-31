; GunSonu Installer (NSIS) — Hardened Uninstall (recursive), Versioned OutFile
!define APPNAME "GunSonu"
!define COMPANY "GunSonu"
!define VERSION "1.0.0"

OutFile "dist\GunSonu_Setup_1.0.0.exe"
InstallDir "$PROGRAMFILES\${APPNAME}" ; default, overwritten on x64 in .onInit
RequestExecutionLevel admin
SetCompress auto
SetCompressor /SOLID lzma

!include "MUI2.nsh"
!include "x64.nsh"
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "Turkish"

Function .onInit
  ${If} ${RunningX64}
    SetRegView 64
    StrCpy $InstDir "$PROGRAMFILES64\${APPNAME}"
  ${Else}
    SetRegView 32
  ${EndIf}
FunctionEnd

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File /oname=GunSonu.exe "dist\GunSonu\GunSonu.exe"

  ; Uninstaller + ARP registration
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANY}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\GunSonu.exe"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\GunSonu.exe"
SectionEnd

Section "Uninstall"
  ExecWait 'taskkill /F /IM GunSonu.exe'
  Delete "$DESKTOP\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  RMDir  "$SMPROGRAMS\${APPNAME}"
  Delete /REBOOTOK "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
