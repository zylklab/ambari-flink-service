# Flink ambari service

## Install flink service

### Download Flink 1.8.1
1. Download [flink-1.8.1-bin-scala_2.12.tgz](https://www.apache.org/dyn/closer.lua/flink/flink-1.8.1/flink-1.8.1-bin-scala_2.12.tgz)
2. Donwload [flink-shaded-hadoop-2-uber-2.8.3-7.0.jar](https://repo.maven.apache.org/maven2/org/apache/flink/flink-shaded-hadoop-2-uber/2.8.3-7.0/flink-shaded-hadoop-2-uber-2.8.3-7.0.jar)
3. Decompress **flink-1.8.1-bin-scala_2.12.tgz** in *flink/*
4. Put **flink-shaded-hadoop-2-uber-2.8.3-7.0.jar** in *flink/lib/flink-shaded-hadoop-2-uber-2.8.3-7.0.jar*
5. Compress *flink/* with tar.gz 
6. Put in *./package/files/flink-bin-1.8.1/flink.tar.gz*

**There is a copy ot this jar at [https://services.zylk.net/ambari/flink.tar.gz](https://services.zylk.net/ambari/flink.tar.gz)**

### Set up Advanced flink-site 

* **security.kerberos.login.keytab** set your kerberos keytab
* **security.kerberos.login.principal** set your kerberos principal

### BUG
* Cluster must be kerberized

### TODO LIST

 * Cluster without kerberos enabled
 * Templates for log4j
 * Send metrics to ambari metrics collector
 * Check the flink status ```ỳarn -list```
 * Quicklinks
 * define alarms based on statistics alarms.json
 * Satistics panels
 * Add kdestroy or check command yarn with keytab
