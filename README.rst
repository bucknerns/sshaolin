SSHaolin: SSH from Ninjas
=========================

Example no logging
------------------

::

    In [1]: from sshaolin.client import SSHClient

    In [2]: client = SSHClient("192.168.0.69", 22, "mega255", look_for_keys=True)

    In [3]: client.execute_command("ls /")
    Out[3]:
    <CommandResponse object>
    stdin =
    exit_status = 0
    stderr =
    stdout = bin
    boot
    dead.letter
    dev
    etc
    home
    initrd.img
    initrd.img.old
    lib
    lib64
    lost+found
    media
    mnt
    opt
    proc
    root
    run
    sbin
    shares
    srv
    sys
    tftpboot
    tmp
    usr
    var
    vmlinuz
    vmlinuz.old

Example with logging
--------------------

::

    In [1]: from sshaolin.client import SSHClient

    In [2]: from sshaolin.common import logging_formatter

    In [3]: import logging

    In [4]: root = logging.getLogger()

    In [5]: root.addHandler(logging.StreamHandler())

    In [6]: root.handlers[0].setFormatter(logging_formatter)

    In [7]: root.setLevel(logging.INFO)

    In [8]: client = SSHClient("192.168.0.69", 22, "mega255", look_for_keys=True)

    In [9]: client.execute_command("ls /")
    2016-03-24 18:58:25,274: INFO: sshaolin.client.SSHClient:
    ==========================================
    CALL
    ------------------------------------------
    execute_command args..........: ('ls /',)
    execute_command kwargs........: {}
    ------------------------------------------

    2016-03-24 18:58:25,294: INFO: paramiko.transport: Connected (version 2.0, client OpenSSH_6.9p1)
    2016-03-24 18:58:25,477: INFO: paramiko.transport: Authentication (publickey) successful!
    2016-03-24 18:58:26,921: INFO: sshaolin.client.SSHClient:
    ==========================================
    RESPONSE
    ------------------------------------------
    response stdout......: bin
    boot
    dead.letter
    dev
    etc
    home
    initrd.img
    initrd.img.old
    lib
    lib64
    lost+found
    media
    mnt
    opt
    proc
    root
    run
    sbin
    shares
    srv
    sys
    tftpboot
    tmp
    usr
    var
    vmlinuz
    vmlinuz.old
    response stderr......:
    response exit_status.: 0
    response elapsed.....: 1.64562487602
    ------------------------------------------

    Out[9]:
    <CommandResponse object>
    stdin =
    exit_status = 0
    stderr =
    stdout = bin
    boot
    dead.letter
    dev
    etc
    home
    initrd.img
    initrd.img.old
    lib
    lib64
    lost+found
    media
    mnt
    opt
    proc
    root
    run
    sbin
    shares
    srv
    sys
    tftpboot
    tmp
    usr
    var
    vmlinuz
    vmlinuz.old

