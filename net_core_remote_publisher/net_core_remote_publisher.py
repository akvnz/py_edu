from datetime import datetime
from ftplib import FTP
import os
import glob
import shutil
import paramiko
import warnings
import subprocess
import time
from net_core_remote_publisher.variables import *

warnings.filterwarnings(action='ignore', module='.*paramiko.*')

print('Start time: ' + str(datetime.now()))
start_time = time.time()

sourceArchiveNameWithExtension = sourceArchiveName + '.' + sourceArchiveExtension
sourceArchiveFullPath = publishOutputPath + sourceArchiveName + '.' + sourceArchiveExtension

# cleanup
if os.path.exists(publishOutputPath):
    shutil.rmtree(publishOutputPath)

# get latest version of the source code
p = subprocess.Popen("git pull " + gitRepoUri + ' ' + gitBranchName, cwd=repoBasePath)
p.wait()

# publish
p = subprocess.Popen("dotnet publish -c Release -o " + publishOutputPath, cwd=publishWorkDirectory)
p.wait()

# remove unnecessary files
filesForRemove = [sourceArchiveFullPath]

for i in glob.glob(publishOutputPath + '*.pdb'):
    filesForRemove.append(i)

for i in glob.glob(publishOutputPath + 'appsettings*.json'):
    filesForRemove.append(i)

for i in glob.glob(sourceArchiveFullPath):
    filesForRemove.append(i)

for fileFullPath in filesForRemove:
    if os.path.exists(fileFullPath):
        os.remove(fileFullPath)

# make archive and copy in the publish path
shutil.make_archive(sourceArchiveName, sourceArchiveExtension, publishOutputPath)
shutil.move(sourceArchiveNameWithExtension, sourceArchiveFullPath)

# connect to FTP
ftp = FTP()
ftp.set_debuglevel(2)
ftp.connect(ftpHost, ftpPort)
ftp.login(ftpUserName, ftpUserPassword)
ftp.cwd(ftpFolderPath)

# copy archive to FTP
localFile = open(sourceArchiveFullPath, 'rb')
ftp.storbinary('STOR ' + sourceArchiveNameWithExtension, localFile)
localFile.close()
ftp.quit()
ftp.close()

# cleanup
if os.path.exists(publishOutputPath):
    shutil.rmtree(publishOutputPath)

# connect to remote server via SSH
sshClient = paramiko.SSHClient()
sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

sshClient.connect(hostname=sshRemoteHost, username=sshRemoteUser, password=sshRemoteUserPassword, port=sshRemotePort)

# set of command for update app
commands = [
    'sudo unzip -o ' + ftpFolderRootPath+ftpFolderPath + sourceArchiveNameWithExtension +
    ' -d '+ftpFolderRootPath+ftpFolderPath,

    'sudo rm -f ' + sourceArchiveNameWithExtension,

    'sudo systemctl stop evcwebapp.service',

    'sudo cp -a '+ftpFolderRootPath+ftpFolderPath+'. '+targetRootPath,

    'sudo chown -R www-data ' + targetRootPath,

    'sudo chmod u+x ' + targetRootPath + targetAppFolderName,

    'sudo systemctl start ' + daemonServiceName,

    'sudo systemctl status ' + daemonServiceName,

    'rm -rf ' + ftpFolderRootPath+ftpFolderPath + '*'
]

# run commands
for command in commands:
    print(command)
    stdin, stdout, stderr = sshClient.exec_command(command)
    print(stdout.read() + stderr.read())

# close SSH
sshClient.close()

print('End time: ' + str(datetime.now()))
print("Execution time: [%s] seconds" % (time.time() - start_time))
