# VBox_control

## Description
A project for running tests inside Vbox virtual machines

## Requirements

* Python 3.11
* VBox 7

## Installing Python Libraries

### First you need to install the package manager poetry

* Instruction: [Python Poetry Installation Guide](https://python-poetry.org/docs/#installation)

To install the dependencies via poetry, run the command
`poetry install`

To activate the virtual environment, run the command
`poetry shell`

## Getting Started

* Change config.json file.

#### Config parameters

`desktop_script` - link to a repository with a script to run in a virtual machine
`branch` - branch from which the script will be downloaded. (default is 'master')
`token_file` - name of the file containing the telegram token located at `~/.telegram` folder
`chat_id_file` - name of the file containing the telegram chat id located at `~/.telegram` folder
`password` - password from the virtual machine user.
`hosts` - array with names of virtual machines to run tests

## Commands

`invoke desktop-test` - To run desktop editors tests

### Desktop-test flags

`--version` or `-v` - Specifies the version of DesktopEditor.

`--headless` or `-h` - To run virtual machines in the background

`--processes` or `-p` - Number of threads. to run tests in multithreaded mode

`--name` or `-n` - name of the virtual machine to selectively run tests
