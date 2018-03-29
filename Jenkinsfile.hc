pipeline {
  agent any
  environment { 
    IMAGE = "ensembl-prodinf/hc_app"
    REPO = "gitlab.ebi.ac.uk:5005"
    GROUP = "ensembl-production"
    IDENTITY = 'ebigitlab'
    DOCKERFILE = "Dockerfile.hc"
  }
  stages {
    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */
    	steps {
          checkout scm
        }
    }
    stage('Push image') {
        steps {  
          withCredentials([usernamePassword(credentialsId: env.IDENTITY, passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
            sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPassword} ${env.REPO}"
            sh "docker build -t ${repo}/${group}/${image}:latest -f ${env.DOCKERFILE} ."
            sh "docker push ${env.REPO}/${env.GROUP}/${env.IMAGE}:latest"
          }
       }
    }	
  }
}
