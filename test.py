import paramiko
import os
import datetime

sftp_host = '50.20.249.5'
sftp_username = 'root'
sftp_password = '04090409qwerT'
remote_directory = '/root/BBC/database-backups/'

# Create an SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the server
ssh.connect(sftp_host, username=sftp_username, password=sftp_password)
print("Connection successfully established ... ")

# Create an SFTP session
sftp = ssh.open_sftp()

sftp.chdir(remote_directory)
print(f"Changed to remote directory: {remote_directory}")

print("Uploading file to the server... this may take a while depending on the size of the database.")
local_file_path = os.path.join(os.getcwd(), 'instance/site.db')
sftp.put(local_file_path, os.path.join(remote_directory, 'site.db'))
print(f"File {local_file_path} uploaded successfully to {remote_directory}")

remote_filename = f'Backup-{datetime.datetime.now().strftime("%Y-%m-%d")}.db'
sftp.rename(os.path.join(remote_directory, 'site.db'), os.path.join(remote_directory, remote_filename))
print(f"File renamed to {remote_filename}")

sftp.close()