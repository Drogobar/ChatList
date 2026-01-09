; Скрипт Inno Setup для создания установщика ChatList
; Версия: 1.0.0

#define MyAppName "ChatList"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ChatList"
#define MyAppURL "https://github.com/your-repo/chatlist"
#define MyAppExeName "ChatList-1.0.0.exe"
#define MyAppId "{{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}"

[Setup]
; Примечание: значение AppId идентифицирует это приложение. Не используйте одно и то же AppId в двух установщиках.
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=installer
OutputBaseFilename=ChatList-Setup-{#MyAppVersion}
SetupIconFile=app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion
; Примечание: не используйте "Flags: ignoreversion" для любых файлов общих документов

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\app.ico"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconFilename: "{app}\app.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"
Type: dirifempty; Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usUninstall:
      begin
        // Дополнительные действия при удалении (если необходимо)
        // Например, удаление файлов конфигурации пользователя
      end;
    usPostUninstall:
      begin
        // Действия после удаления
        // Например, удаление записей реестра или других данных
      end;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  // Проверка, запущено ли приложение
  if CheckForMutexes('ChatListMutex') then
  begin
    if MsgBox('Приложение ChatList запущено. Закройте его перед удалением.', mbError, MB_OK) = IDOK then
    begin
      Result := False;
    end
    else
    begin
      Result := False;
    end;
  end
  else
  begin
    Result := True;
  end;
end;
