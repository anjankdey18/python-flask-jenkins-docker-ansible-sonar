# jenkins pipeline setup

# to install maven from jenkins ui
go to manage jenkins -> global tool configuration or tools. then scrolldown and check maven installation -> click on add Maven -> name: maven3 -> check Install automatically -> apply -> save

##for everybody Youtube video link: 

## A If you want to run ansible playbook from jenkins host then need to install ansible on it
```sudo dnf install epel-release```
```sudo dnf install ansible ```
```ansible --version```
check the executable location: executable location = /usr/bin/ansible

Now need to configure jenkins for ansible
if you do not see ansible option like maven you need to install plugin for it.
go to manage jenkins -> plugins. search ansible with available then install

go to manage jenkins -> global tool configuration or tools. then scrolldown and check maven installation -> click on add asible -> name: ansible -> path to ansible executables directory will be /usr/bin/ -> check Install automatically -> apply -> save

## Now create jenkins pipeline
name of the pipeline is dockeransiblejenkins-pipeline -> build Triggers -> Pipeline

* to write pipeline, you can use help of pipeline Syntax
Snippet Generator => Steps -> Sample Step git:Git enter Repository URL: https://github.com/anjankdey18/dockeransiblejenkins.git enter branch: main add Credentials: click on add  user: anjankdey18 pass, id and description then select it what you enter the ID then genetate the code

for maven:
Declarative Directive Generator => Directives -> Sample Sample Directive jtools:Toolsadd Maven -> Version maven3 click on genetate Declarative Directive -> copy the code as maven 'maven3' including tools and paste it under angent any

for docker build:
get commit hash id using following command to taging docker image:
[ans@centos9ansmaster dockeransiblejenkins-cicd]$ git rev-parse --short HEAD
10341a6

Snippet Generator => Steps -> Sample Step sh:Shell Script enter git rev-parse --short HEAD then advanced and select Return standard output (you can store return value in a variable) then create a function/method as follows and add it end of the script and call it
``` 
def getVersion(){
    def commitHash = sh returnStdout: true, script: 'git rev-parse --short HEAD'
    return commitHash
}

```
create environment block:
Declarative Directive Generator => Directives -> Sample Sample Directive environment:Environment -> add -> name as DOCKER_TAG  -> value as getVersion() click on genetate Declarative Directive -> copy the code as like as maven and paste it under agent any

make sure is installed on jenkins machine:

adding jenkins user to docker group to run docker command without sudo
sudo usermod -aG docker jenkins  //if docker group is not there check on /etc/group and create group with groupadd docker

to use/get the docker group restart jenkins using sudo service jenkins restart
make sure docker autostart when jenkins reboot using sudo chkconfig docker on for ubuntu and for centos: sudo systemctl enable docker and start docker: sudo systemctl start docker


for docker push:

create password with script

for ansible playbook script for jenkins:
git the playbook file name(for example: deploy-docker.yml) to generate pipeline syntax. click on pipeline systax -> snippet generator -> steps -> sample step and select ansiblePlaybook:Invoke an ansible playbook -> Ansible tool as ansible -> Playbook file path in workspace as deploy-docker.yml -> inventory file as dev.inv which is in the same location -> ssh connection credentials as copy the pem file attribute and click on add -> jenkins -> Domain as Global credentials -> kind as SSH Username with private key enter id (ie: docker-server-access-dev) same description -> username as ec2-user -> select private key and click on add and paste the content/attribute of pem file which used to access on the server then click add. Now select it on snippet as ec2-user(docker-server-access-dev) also make sure select Disable the host SSH key check then generate.
