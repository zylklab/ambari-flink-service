## Flink ambari service

### Install flink service
Setting Advanced flink-site 

⋅⋅* **env.java.home** set your JAVA_HOME
⋅⋅* **security.kerberos.login.keytab** set your kerberos keytab
⋅⋅* **security.kerberos.login.principal** set your kerberos principal

### BUG
Cluster must be kerberized
Stopping from Ambari NOT kill the YARN application
