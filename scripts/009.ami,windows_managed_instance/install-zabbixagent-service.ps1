[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri https://cdn.zabbix.com/zabbix/binaries/stable/7.2/7.2.3/zabbix_agent-7.2.3-windows-amd64-openssl.msi -OutFile "C:\Users\Administrator\Downloads\zabbix_agent-windows-amd64-openssl.msi"
msiexec /i "C:\Users\Administrator\Downloads\zabbix_agent-windows-amd64-openssl.msi"
# 手動でサービスの状態を「自動(遅延開始)」→「自動」に変更する必要あり