#!/bin/bash
# ---------------------------------------------------------------
# Wilson Bui
# The "Add Account" shell script
# Version 1.0 - 12/14/2017
# This script provisions administrative users to Bastion Servers 
# ---------------------------------------------------------------

#sh add_account.sh [UNAME] "ssh-rsa [KEY]"

function bail()
{
  local msg="${1}"
  echo "***: ${msg}"
  exit 1
}

function bailOnError()
{
  local rc="$1"
  local msg="$2"
  if [ "$rc" != "0" ] ; then
    bail "${msg} Error code = $rc"
  fi
}

if [ "$#" != "2" ] ; then
  bail "Usage: $0 <acctname> <sshkey>"
fi

u="$1"
k="$2"

base="/home/${u}"
sshdir="${base}/.ssh"
sshfile="${sshdir}/authorized_keys"

if [ -d "${base}" ] ; then
  bail "Directory ${base} already exists!"
fi

useradd -m "$u"
bailOnError "$?" "Failed to useradd ${u}."

mkdir "${sshdir}"
bailOnError "$?" "Failed to mkdir ${sshdir}."

echo "$k" > "${sshfile}"
bailOnError "$?" "Failed to create ${sshfile}."

chmod 400 ${sshfile}
bailOnError "$?" "Failed to chmod 400 ${sshfile}."

chmod 700 ${sshdir}
bailOnError "$?" "Failed to chmod 700 ${sshdir}."

chown -R "${u}:${u}" "${sshdir}"
bailOnError "$?" "Failed to chown -R ${sshdir}."

usermod -G root "${u}"
bailOnError "$?" "Failed to add user to root group."

echo "> Done"
echo
ls -alR "${base}"
echo
exit 0
