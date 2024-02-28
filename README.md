# Automated code build, docker image creation, docker image push into docker hub
Pre-requisites:
1. Jenkins is up and running
2. Docker Installed on Jenkins instance and configured
3. Docker plugin installed on Jenkins
4. user account setup in dockerhub (https://cloud.docker.com)
5. port 8096 is opened up in firewall rules on docker server.

## Steps #01 - Create credentials for Docker Hub
Go to your Jenkins where you have installed Docker as well. Go to Manage Jenkins -> Credentials -> Click on new credentials 
Kind -> Select Username with password
Scope -> Global 
Username -> your dockerhub username
Password -> Your dockerhub password
ID -> Meaningful name (which you need to use on jenkins pipeline or jenkinsfile)
Description -> Meaningful name
Then Create.


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

## Steps#02: Now create jenkins pipeline
Click on New Item -> Enter an Item name (your pipeline name. for example: pythonAppDockerSonar-pipeline)-> select Pipeline and click ok.

name of the pipeline is pythonAppDockerSonar-pipeline 
-> build Triggers(H/2**** //it will trigger every two minutes automatically) 
-> Pipeline (Definition -> Pipeline script from SCM[meaning using jenkinsfile] -> SCM --Git Repositories --Repository URL --your repo url --Credentials your github access key/credential --Branch your branch --Script Path Your jenkinsfile)

or

-> build Triggers(H/2**** //it will trigger every two minutes automatically) 
-> Pipeline (Definition -> Pipeline script from SCM[meaning using jenkinsfile] -> SCM --Git Repositories --Repository URL --your repo url --Credentials your github access key/credential --Branch your branch --Script Path Your jenkinsfile)

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
