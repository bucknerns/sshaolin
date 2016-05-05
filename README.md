[![license](https://img.shields.io/github/license/bucknerns/sshaolin.svg?maxAge=2592000)](https://github.com/bucknerns/sshaolin/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/bucknerns/sshaolin.svg)](https://github.com/bucknerns/sshaolin/issues)

# SSHaolin: SSH for Ninjas

Tired of dealing with python SSH interfaces that are far too complicated!
Want a nice simple python SSH interface that just works!
SSHaolin aims to give you that experience and more!
Built on top of [paramiko](https://github.com/paramiko/paramiko),
SSHaolin is the python interface that makes it simple to write that ssh script
you've been meaning to do for years!

Built into the SSHaolin core is verbose logging that shows you every
command that is running along with the ability to decipher both stdout and
stderr straight from your logs!

Also included are interfaces for both persistent ssh sessions (_SSHShell_) and
sftp session (_SFTPShell_). Both are easy to use and provide a great speed
boost as opposed to connecting and reconnecting for every action!

Have an issue? Submit it [here](https://github.com/bucknerns/sshaolin/issues)!

## Installation:

Recommended:
```
$ pip install git+https://github.com/bucknerns/sshaolin
```

## Requirements:

* [paramiko](https://github.com/paramiko/paramiko)
* [PySocks](https://github.com/Anorov/PySocks)

## Features:

* Easily send commands over ssh!
* Creating persistent ssh sessions!
* Creating persistent sftp sessions!
* Easy connection cleanup! (No more manual closing!)

## Examples:

Running `ls -ltr` on server `foo` as user `bar` with password `blah`
```python
from sshaolin.client import SSHClient

client = SSHClient(hostname='foo', username='bar', password='blah')
response = client.execute_command('ls -ltr')

# It comes with an exit status!
print(response.exit_status)

# It comes with stdout!
print(response.stdout)

# It comes with stderr!
print(response.stderr)
```

Transferring local file `example.txt` to server `foo` as user `bar` with RSA
file authentication `/home/bar/.ssh/id_rsa` at `/usr/local/src/example.txt` and
`/usr/local/src/example2.txt`
```python
from sshaolin.client import SSHClient

client = SSHClient(
    hostname='foo', username='bar', key_filename='/home/bar/.ssh/id_rsa')
with open('example.txt', 'r') as fp:
    data = fp.read()

# Context managers to ensure the closing of a connection!
with client.create_sftp() as sftp:
    sftp.write_file(data=data, remote_path='/usr/local/src/example.txt')

# If you don't want to mess with context managers you can store it as a
# variable! SSHaolin will clean it up when the program exits!
sftp = client.create_sftp()
sftp.write_file(data=data, remote_path='/usr/local/src/example2.txt')
```

Sudoing to `privelegeduser1`, cd'ing to `/usr/local/executables` and running
`perl randomperlscript.pl`
```python
from sshaolin.client import SSHClient

client = SSHClient(
    hostname='foo', username='bar', key_filename='/home/bar/.ssh/id_rsa')
shell = client.create_shell()
# No more need to do hacky workarounds to sudo to another user!
shell.execute_command('sudo su privelegeduser1')
shell.execute_command('cd /usr/local/executables')
perl_response = shell.execute_command('perl randomperlscript.pl')
shell.close()  # We can close things manually as well!

if perl_response.exit_status == 0:
    print('Success!')
else:
    raise Exception('Failed to execute randomperlscript.pl correctly')
```

## Contributing:
1. Fork the [repository](https://github.com/bucknerns/sshaolin)!
2. Commit some stuff!
3. Submit a pull request!
