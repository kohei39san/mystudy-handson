[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri https://cdn.zabbix.com/zabbix/binaries/stable/7.2/7.2.3/zabbix_agent-7.2.3-windows-amd64-openssl.msi -OutFile "C:\Users\Administrator\Downloads\zabbix_agent-windows-amd64-openssl.msi"
msiexec /i "C:\Users\Administrator\Downloads\zabbix_agent-windows-amd64-openssl.msi"
# �蓮�ŃT�[�r�X�̏�Ԃ��u����(�x���J�n)�v���u�����v�ɕύX����K�v����