# How-to deploy a vanilla elasticsearch in docker containers using kitchen-ci and ansible

Using kitchen-ci allow us to benefit easily of a systemd compatible container

I use it mainly when developing [ansible-elasticsearch](https://github.com/elastic/ansible-elasticsearch) role to
compare the configuration of a "vanilla" elasticsearch deployment (only package installation) with the configuration
resulting of the role which is more opinionated.

Platforms tested:
- centos 7
- ubuntu 18.04

## Requirements

- ruby
- bundler

## Getting started

```
bundle install
kitchen converge [main-centos-7|main-ubuntu-1804]
kitchen login [main-centos-7|main-ubuntu-1804]
```

## Options

TODO manage Ansible variables via environment variables

You can change the following variables in [`main.yml`](./main.yml):
- `major_version`: select elasticsearch major version to install (`7.x` or `6.x`)
- `package`: path of a local package to install (DEB or RPM) instead of using elastic repository

