We show the details in our commit study, including categoriazation, and extensive case study. 

# How to do commit categorization based on the taxonomy.

Despite some automation is used when selecting raw commits we still need to manually analyze the code changes and Issues tracking system.

We use four sources of data to help us understand and category each commit:
 - code diff
 - commit message 
 - issue description
 - developers' discussion   

Analyzing Code diff is the most effective and accurate way to categorize the commit. The key principle for **code diff** analysis is to understand **how each commit changes the configuration in different categories** described in Table II. Apart form code diff, **commit message** and **issue description** (also developers' discussion, as supplementary information) can help us **validate** and **reason about** our result as they are written in natrual language. 

Here we walk through examples to show the process that we study and categorize commits.

## Interface (Section IV)

### AddParam

#### Add.NewCode

This is the case that adds new parmameters along with brand new modules.

In the commit of [HDFS-13607][4], the code diff is:

~~~
+  public static final String DFS_JOURNALNODE_EDIT_CACHE_SIZE_KEY =
+      "dfs.journalnode.edit-cache-size.bytes";
+  public static final int DFS_JOURNALNODE_EDIT_CACHE_SIZE_DEFAULT = 1024 * 1024;

+  class JournaledEditsCache {
+    ...
+    JournaledEditsCache(Configuration conf) {
+      capacity = conf.getInt(DFSConfigKeys.DFS_JOURNALNODE_EDIT_CACHE_SIZE_KEY,
+          DFSConfigKeys.DFS_JOURNALNODE_EDIT_CACHE_SIZE_DEFAULT);
+      ... //The use code of capacity
+    }
+    ...
+  }
~~~

The commit message is:
> Enhance JournalNode with an **in-memory cache** of recent edit transactions.

In this commit, developers implemented the class 'JournaledEditsCache' and added a paramter `dfs.journalnode.edit-cache-size.bytes` to control the size of edit cache.
In other words, `dfs.journalnode.edit-cache-size.bytes`co-evolves with the code (class JournaledEditsCache). So we categorize it as **Add with New Code**.

#### Add.Parameterization

This is the case that adds new parameters in an existing module/feature. Meanwhile the value of the parameter is previously a constant value.

In the commit of [SPARK-20950][6], the code diff is:
~~~
-  static final int DISK_WRITE_BUFFER_SIZE = 1024 * 1024;
+  private final int diskWriteBufferSize = conf.get(package$.MODULE$.SHUFFLE_DISK_WRITE_BUFFER_SIZE());
...
-  private byte[] writeBuffer = new byte[DISK_WRITE_BUFFER_SIZE];
+  private byte[] writeBuffer = new byte[diskWriteBufferSize];
~~~

When we track the new added parameter and its variable usage in the code base, we try to see whether this value is newly-added or comes from an constant value (parameterization). 
In the case, the new added variable `diskWriteBufferSize` is load from a new configuration parameter by using a configuration getter method (can be identified by our script). Then we track how it is used in the commit diff and find out that the value is used to construct `writeBuffer`, which is hard-coded (`1024*1024`) before. Therefore, we categorize it as **Parameterization**.


#### Add.CodeChange

This is the case that adds new parmeters due to changes in existing modules. However, the value doesn't come from a previous constant value but directly configurable.

In the commit of [HDFS-12291][5], the code diff is:

~~~
+  public static final String  DFS_STORAGE_POLICY_SATISFIER_QUEUE_LIMIT_KEY =
+      "dfs.storage.policy.satisfier.queue.limit";
+  public static final int  DFS_STORAGE_POLICY_SATISFIER_QUEUE_LIMIT_DEFAULT =
+      1000;

   public BlockStorageMovementNeeded(Namesystem namesystem,
-      StoragePolicySatisfier sps) {
+      StoragePolicySatisfier sps, int queueLimit) {
     this.namesystem = namesystem;
     this.sps = sps;
+    this.maxQueuedItem = queueLimit;
}

   this.storageMovementNeeded = new BlockStorageMovementNeeded(namesystem,
-      this);
+      this, conf.getInt(
+          DFSConfigKeys.DFS_STORAGE_POLICY_SATISFIER_QUEUE_LIMIT_KEY,
+          DFSConfigKeys.DFS_STORAGE_POLICY_SATISFIER_QUEUE_LIMIT_DEFAULT));

~~~

`dfs.storage.policy.satisfier.queue.limit` is added as a new parameter. It is added with the change of method `BlockStorageMovementNeeded`. The key thing here is that `BlockStorageMovementNeeded` needs a queue limit and the limit is controled by `dfs.storage.policy.satisfier.queue.limit`. This is different from parameterization, which case is the previous hard-coded value is inappropriate. So we categorize it as **Add with Code Change**.

### RemoveParam

#### Rmv.RmvModule

This is the case that removes parameters with existing modules.

In the commit of [HBASE-17972][7], the code diff is:

~~~
-  public final static String MERGE_THREADS = "hbase.regionserver.thread.merge";        
-  public final static int MERGE_THREADS_DEFAULT = 1;

-  int mergeThreads = conf.getInt(MERGE_THREADS, MERGE_THREADS_DEFAULT);        
-  this.mergePool = (ThreadPoolExecutor) Executors.newFixedThreadPool(      
-      mergeThreads, new ThreadFactory() {
-    ...
-  }
~~~

From the [issue discription][8]:
> mergePool is not in use, we should remove it from CompactSplitThread

Configuration parameter `hbase.regionserver.thread.merge` is removed along with method `mergePool`, so we categorize it as Remove with **Remove Module**.

#### Rmv.Replace

This is the case that replaces parameters with constants or automation logic.

In the commit of [HDFS-12412][9], the code diff is:

~~~
-  public static final String  DFS_DN_EC_RECONSTRUCTION_STRIPED_READ_THREADS_KEY = 
-      "dfs.datanode.ec.reconstruction.stripedread.threads";        
-  public static final int     DFS_DN_EC_RECONSTRUCTION_STRIPED_READ_THREADS_DEFAULT = 20;


-  private void initializeStripedReadThreadPool(int num){
+  private void initializeStripedReadThreadPool() {
     ...
-    stripedReadPool = new ThreadPoolExecutor(1, num, 60, TimeUnit.SECONDS,...)
+    stripedReadPool = new ThreadPoolExecutor(1, Integer.MAX_VALUE, 60, TimeUnit.SECONDS,...)
     ...
   }

-  initializeStripedReadThreadPool(conf.getInt(
-      DFSConfigKeys.DFS_DN_EC_RECONSTRUCTION_STRIPED_READ_THREADS_KEY,
-      DFSConfigKeys.DFS_DN_EC_RECONSTRUCTION_STRIPED_READ_THREADS_DEFAULT));
+  initializeStripedReadThreadPool();
~~~

Configuration parameter `dfs.datanode.ec.reconstruction.stripedread.threads` is removed and replaced with a hard-coded value `Integer.MAX_VALUE`. So we categorize it as **Remove and Replace**. 

### ModifyParam

#### Mod.Naming

This is the case that modifies a existing parameter.

In the commit of [SPARK-19724][10], the code diff is:

~~~
   val ALLOW_CREATING_MANAGED_TABLE_USING_NONEMPTY_LOCATION =
-      buildConf("spark.sql.allowCreatingManagedTableUsingNonemptyLocation")
+      buildConf("spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation")
       .doc("......")
       .internal()
       .booleanConf
       .createWithDefault(false)
~~~

The name of configuration parameter `spark.sql.allowCreatingManagedTableUsingNonemptyLocation` changed to `spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation` (add a legacy prefix). We categorize it as **Modify Naming**.

#### Mod.DefaultValue

This is the case that modifies default values of existing parameters.

In the commit of [HDFS-11998][11], the code diff is:
~~~
   public static final String DFS_USE_DFS_NETWORK_TOPOLOGY_KEY =    
       "dfs.use.dfs.network.topology";
-  public static final boolean DFS_USE_DFS_NETWORK_TOPOLOGY_DEFAULT = false;
+  public static final boolean DFS_USE_DFS_NETWORK_TOPOLOGY_DEFAULT = true;
~~~

The default value of configuration parameter `dfs.use.dfs.network.topology` changed from false to true. So we categorize it as **Modify Default Value**

#### Mod.Constraint

This is the case that modifies constraints of existing parameters. The constraint includes value type, value range, dependence, etc.

In the commit of [HDFS-12716][12], the code diff is:

~~~
-  if (volFailuresTolerated < 0 || volFailuresTolerated >= volsConfigured) {
+  if (volFailuresTolerated < -1 || volFailuresTolerated >= volsConfigured) {
     throw new DiskErrorException("Invalid value configured for "
         + "dfs.datanode.failed.volumes.tolerated - " + volFailuresTolerated
-        + ". Value configured is either less than 0 or >= "
+        + ". Value configured is either less than -1 or >= "
         + "to the number of configured volumes (" + volsConfigured + ").");
 }
~~~

The value range constraint of Configuration parameter `dfs.datanode.failed.volumes.tolerated` changed from [0,volsConfigured) to [-1,volsConfigured). The [issue description][13]:
> Support 'dfs.datanode.failed.volumes.tolerated' to accept special 'negative value 'x' to tolerate failures of upto "n-x"

So we categorize it as **Modify Constraint**.

## Usage (Section V)

### Parse

This is the case that modifies configuration parsing code.

In the commit of [HBASE-21639][14], the code diff is:

~~~
-  this.conf.getInt("hbase.region.replica.replication.buffersize", 128 * 1024 * 1024));
+  this.conf.getLong("hbase.region.replica.replication.buffersize", 128 * 1024 * 1024));
~~~

The configuration parameter `hbase.region.replica.replication.buffersize` was previously parsed by `conf.getInt` and changed to `conf.getLong`. So we categorize it as evolution on configuration **Parse**. The commit message also validate our categorization:
> maxHeapUsage value not read properly from config during EntryBuffers initialization

### Check

This is the case that modifies configuration checking code, including add check code and modifie existing check code (e.g., change check conditions).

In the commit of [CASSANDRA-13622][15], the code diff is:

~~~
+  if (conf.commitlog_segment_size_in_mb <= 0)
+    throw new ConfigurationException("commitlog_segment_size_in_mb must be positive, but was "
+        + conf.commitlog_segment_size_in_mb, false);
+  else if (conf.commitlog_segment_size_in_mb >= 2048)
+    throw new ConfigurationException("commitlog_segment_size_in_mb must be smaller than 2048, but was "
+        + conf.commitlog_segment_size_in_mb, false);
~~~

The commit added checking code for configuration parameter `commitlog_segment_size_in_mb`, as mentioned in the commit message:
> Improve config validation and documentation on overflow and NPE

Note that this commit also added error handling code of the parameter, but the initial purpose is to add a check on the parameter, and the error handling is a part of the checking.  
So we category it as evolution on configuration **Check**.

### Handle

#### Handle.Action

This is the case that modifies misconfiguration handle code, including add handle code and modifie existing handle code (e.g. change excpetion type).

In the commit of [CASSANDRA-14991][16], the code diff is:

~~~
-  SSLFactory.initHotReloading(conf.server_encryption_options, conf.client_encryption_options, false);
+  try{
+  SSLFactory.initHotReloading(conf.server_encryption_options, conf.client_encryption_options, false);
+  } 
+  catch(IOException e){
+  throw new ConfigurationException("Failed to initialize SSL hot reloading", e);
+  }
~~~

This commit added error-handling code for `initHotReloading`, which is configuration-related because it has two confiuration related parameters (`conf.server_encryption_options` and `conf.client_encryption_options`), and the exception type also validate this. So we categorize it as evolution on **Handle Action** for misconfiguration.

#### Handle.Message

This is the case that modifies misconfiguration handle message, including excpetion message, log.

In the commit of [SPARK-25073][17], the code diff is:

~~~
   if (amMem > maxMem) {
     throw new IllegalArgumentException(s"Required AM memory ($amMemory" +
         "+$amMemoryOverhead MB) is above the max threshold ($maxMem MB) of this cluster! " +
-        "Please increase the value of 'yarn.scheduler.maximum-allocation-mb'.")
+        "Please check the values of 'yarn.scheduler.maximum-allocation-mb' and/or "
+        "'yarn.nodemanager.resource.memory-mb'.")
~~~

The commit changed the exception message because one configuration parameter is missing. And from the commit message:
> As the error message is bit misleading to the user, we can keep the error message same as executor memory validation message.

We categorize it as evolution on **Handle Message** for misconfiguration. The feedback message quality (L1-L4) we used in our paper is a refinement of previous work [\[3\]][3], based our own study and analysis. The criterion for different quality level based on "configuration hints", "parameter name" and "guidance for fixing".

### Use

#### Use.Change

This is the case that modifies existing code that use configuration parameters, including get fine-grained control, change domain/Scope, parameter overriding, change the functional purpose of parameter, parameter replacement and fix buggy parameter values.

In the commit of [HBASE-20986][18], the code diff is:

~~~
-  public static long getWALBlockSize(Configuration conf, FileSystem fs, Path dir) throws IOException {
-    return conf.getLong("hbase.regionserver.hlog.blocksize",
-        CommonFSUtils.getDefaultBlockSize(fs, dir) * 2);
-  }
+  public static long getWALBlockSize(Configuration conf, FileSystem fs, Path dir,
+      boolean isRecoverEdits) throws IOException {
+    long defaultBlockSize = CommonFSUtils.getDefaultBlockSize(fs, dir) * 2;
+    if (isRecoverEdits) {
+      return conf.getLong("hbase.regionserver.recoverededits.blocksize", defaultBlockSize);
+    }
+    return conf.getLong("hbase.regionserver.hlog.blocksize", defaultBlockSize);
+  }
~~~

The parameter `hbase.regionserver.hlog.blocksize` is devied into hbase.regionserver.recoverededits.blocksize and hbase.regionserver.hlog.blocksize for different use. From the [issue Description][19]:
> Since the block size of recovered edits and hlog are the same right now, if we set a large value to block size, name node may not able to assign enough space when we do log splitting. But setting a large value to hlog block size can help reduce the number of region server asking for a new block. Thus I think separate the config of block size is necessary.

We categorize it as configuration **Use Change**.

#### Use.Add

This is the case that adds code to reuse a **existing** configuration parameter.

In the commit of [HDFS-11576][20], the code diff is:

~~~
   public static final String  DFS_HEARTBEAT_INTERVAL_KEY = "dfs.heartbeat.interval";
   public static final long    DFS_HEARTBEAT_INTERVAL_DEFAULT = 3;

+  ...
+  long heartbeatIntervalSecs = conf.getTimeDuration(
+      DFSConfigKeys.DFS_HEARTBEAT_INTERVAL_KEY,
+      DFSConfigKeys.DFS_HEARTBEAT_INTERVAL_DEFAULT, TimeUnit.SECONDS);
+  long blockRecoveryTimeout = getBlockRecoveryTimeout(heartbeatIntervalSecs);
+  pendingRecoveryBlocks = new PendingRecoveryBlocks(blockRecoveryTimeout);
+  ...
~~~

This commit added a new use of configuration parameter `dfs.heartbeat.interval`, which was already defined previously. So we categorize it as **Use Add** for existing parameter.

## Doc (SECTION VI)

### User manuals

This is the case that changes the configuration-realted content in user manual (e.g. configuration file).

In the commit of [SPARK-26080][21], the code diff is:

~~~
   <tr>
     <td><code>spark.executor.pyspark.memory</code></td>
       <td>Not set</td>
       <td>
         The amount of memory to be allocated to PySpark in each executor, in MiB unless otherwise specified.
         ...
         ...
+        NOTE: Python memory usage may not be limited on platforms that do not support resource limiting, 
+        such as Windows.
       <td>
   </tr>
~~~

This commit improved `../docs/configuration.md` about the constraint of using `spark.executor.pyspark.memory` (i.e., warning the memory limit). We categorize it as evolution on configuration related **User manuals**.

### Code comments

This is the case that changes the configuration-realted content in code comments.

In the commit of [CASSANDRA-14226][22], the code diff is:

~~~
+  /*
+   * RPC address and interface refer to the address/interface used for the native protocol used to communicate with
+   * clients. It's still called RPC in some places even though Thrift RPC is gone. If you see references to native
+   * address or native port it's derived from the RPC address configuration.
+   *
+   * native_transport_port is the port that is paired with RPC address to bind on.
+   */
      
    public String rpc_address;
    public String rpc_interface;
    public boolean rpc_interface_prefer_ipv6 = false;
    public int native_transport_port = 9042;
    ...
~~~

This commit added code comments in `../config/Config.java` and `../config/DatabaseDescriptor.java`, and the comments describe the parameter `native_transport_port` and related design details.
So we categorize it as evolution on configuration related **Code comments**.

## Note: Categorization principle

One commit may touch sevral parts as described above. As mentioned in the paper, we categorized and studied each commit based on how it **essentially** revised the original configuration design/implementation. In this way, we can find the problem of original design/implementation. For example in the commit of [HBASE-19660][23], the code diff is:

~~~
//HConstants.java
-  public static final int DEFAULT_HBASE_CLIENT_RETRIES_NUMBER = 10;
+  public static final int DEFAULT_HBASE_CLIENT_RETRIES_NUMBER = 15;
...

//hbase-default.xml
   <property>
     <name>hbase.client.retries.number</name>
-    <value>10</value>  
+    <value>15</value>  
     ...
   </property>  
~~~

Although this commit touched two parts in the toxonomy (change default value & documentation), it's essential improvment is to change the default value and the docuemtnation change is actually came along with it. So we categorize it as Mdf.DefaultValue. 

# How to do extensive case study based on JIRA/GitHub issus tracking system.

Although commit diff provide the most fine-grained code change, it lacks of high level information to do the extensive study. Here, we use the rich information in the issue tracking system (All the commits in our study are linked to JIRA issues or GitHub PRs) which is from developers' perspective. From developers' description and discussion, we can obtain the rationale and scenario that motivate the evolution. 

* Note You can search the Issue Id in [JIRA](https://issues.apache.org/jira/) to check corresponding issue.

For example in Section IV.A.1).(a), we want to know the rationale of parameterization. To give an example: [commit 8ee8e00f1][24]. The code diff is:

~~~
+  def codegenCacheMaxEntries: Int = getConf(StaticSQLConf.CODEGEN_CACHE_MAX_ENTRIES)
...
   private val cache = CacheBuilder.newBuilder()
-    .maximumSize(100)
+    .maximumSize(SQLConf.get.codegenCacheMaxEntries)
~~~

We can see from the code diff that this commit change the constant value `100` to a configuration parameter `spark.sql.codegen.cache.maxEntries`. However, we can't get the rationale of this change from the code diff alone with the commit message, which is: 
> Add a static config to control cache size for generated classes.

So we link to its issue [SPARK-24727][25]. And from the issue description we can infer that the rationale behind the change is because of **performance**:

> The cache 100 in CodeGenerator is too small for realtime streaming calculation, although is ok for offline calculation. Because realtime streaming calculation is mostly more complex in one driver, and performance sensitive. I suggest spark support configging for user with default 100, such as spark.codegen.cache=1000

Another example for Section IV.B, When we try to figure out the reason behind default value change of [commit afb42aea][26]. The code diff is:
~~~
-  public static final boolean DFS_NAMENODE_EDITS_ASYNC_LOGGING_DEFAULT = false;
+  public static final boolean DFS_NAMENODE_EDITS_ASYNC_LOGGING_DEFAULT = true;
~~~

We can see from the code diff that this commit change change the default value of `dfs.namenode.edits.asynclogging`. However, we don't know the reason behind this change from the code diff and commit message, which is:
> Enable async edit logging by default.

However, from the developer's discussion under issue [HDFS-12603][27] and [HDFS-7964][28], we can know it is enabling a previously disabled feature flag:
> Should we consider turning this on by default in newer versions of Hadoop?

> +1. It was off by default due to concerns about correctness. We have been running it in production for quite a while with no issues so far.

[1]:	https://dl.acm.org/doi/10.1145/2517349.2522727 "[1]"
[2]:	[2] "https://ieeexplore.ieee.org/document/8451922"
[3]: https://dl.acm.org/doi/abs/10.1145/2771783.2771817
[4]:	https://github.com/apache/hadoop/commit/c81ac2ff0220b180cd6cbbf18221290c3783bfd5
[5]:	https://github.com/apache/hadoop/commit/bfd3f8bd8a9ae2186ec3e4addc71f912ec7b8923
[6]:	https://github.com/apache/spark/commit/565e7a8d4ae7879ee704fb94ae9b3da31e202d7e#
[7]:	https://github.com/apache/hbase/commit/5ff04c5e7fdf12946a3f0ae15ed7e83209f0e617
[8]:	https://issues.apache.org/jira/browse/HBASE-17972
[9]:	https://github.com/apache/hadoop/commit/123342cd0759ff88801d4f5ab10987f6e3f344b0
[10]:	https://github.com/apache/spark/commit/4a11209539130c6a075119bf87c5ad854d42978e
[11]:	https://github.com/apache/hadoop/commit/9ae9467f920e95ca989d7d51775b39e1b9fee300
[12]:	https://github.com/apache/hadoop/commit/3108d27edde941d153a58f71fb1096cce2995531
[13]:	https://issues.apache.org/jira/browse/HDFS-12716
[14]:	https://github.com/apache/hbase/commit/6da0b4ec34727240e433825382cfc30366340097
[15]:	https://github.com/apache/cassandra/commit/a586f6c88dab173663b765261d084ed8410efe81
[16]:	https://github.com/apache/cassandra/commit/16ef9ac37c21c4f9091cd1f3658e54abddab8ad8
[17]:	https://github.com/apache/spark/commit/c20916a5dc4a7e771463838e797cb944569f6259
[18]:	https://github.com/apache/hbase/commit/bd01fa763985491e196e296f0f627274ce04e619
[19]:	https://issues.apache.org/jira/browse/HBASE-20986
[20]:	https://github.com/apache/hadoop/commit/5304698dc8c5667c33e6ed9c4a827ef57172a723
[21]:	https://github.com/apache/spark/commit/9cda9a892d03f60a76cd5d9b4546e72c50962c85
[22]:	https://github.com/apache/cassandra/commit/518ddbf9d21491d341a3d7e2f2a2e65409595e07
[23]:	https://github.com/apache/hbase/commit/b3a4fca48ffcac44ec1e1d53a99caa18b7e14cbf
[24]:	https://github.com/apache/spark/pull/21705/commits/8ee8e00f156e577b32b01d015b8bd24f72ae7340
[25]:	https://issues.apache.org/jira/browse/SPARK-24727
[26]:	https://github.com/apache/hadoop/commit/afb42aeabf1317b755ab79e0265bc90920c896ac
[27]:	https://issues.apache.org/jira/browse/HDFS-12603
[28]:	https://issues.apache.org/jira/browse/HDFS-7964
[29]:	https://github.com/apache/hbase/commit/83be50c2ab01b428df3b0496215fda8d66ae1bd6
