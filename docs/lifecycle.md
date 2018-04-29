# Study Management Life-Cycle
At any point during the life-cycle of a Study or Deployment, the *dateModified* attribute will automatically be updated to the current date and time if an update to the Study or Deployment goes through to the database. In order for an update to go through, the *dateModified* on the proposed updates must match the *dateModified* in the database. Whenever a Deployment is created or successfully updated, the *dateModfied* of the parent Study will also be updated.

The following attributes can be updated at any point in the life-cycle of a Study or Deployment:
- *status* (can be set to **TERMINATED**)
- *archived* (archiving a Study or Deployment will automatically set its status to **TERMINATED** and make it hidden by default)

## Study Life-Cycle

### CREATED (Study)
A new Study initially has a status of **CREATED**. While a Study is **CREATED**, updates to the design of the Study can be made, which includes updating the following attributes:
- *name*
- *description*
- *status* (can be set to **DESIGNED**)
- *equipmentList*

### DESIGNED (Study)
Once the user is satisfied with the design of the Study, the user must set the status to **DESIGNED**. Once the design of the Study is locked in, individual Deployments for the Study can be created. While a Study is **DESIGNED**, updates to the following attributes can be made:
- *status* (can be set to **DEPLOYED**)
- *deploymentList* (see Deployment Life-Cycle below)

### DEPLOYED (Study)
When a Study is **DEPLOYED**, data can be collected for its existing Deployments. Additional Deployments can also be created during this time.
- *status* (can be set to **PAUSED**)
- *deploymentList* (See Deployment Life-Cycle below)

### PAUSED (Study)
When a Study is **PAUSED**, data collection is halted for its individual Deployments. A Study will automatically become **PAUSED** if all of its Deployments are *PAUSED* or *TERMINATED*. Functionally, there is no difference between a Study in the **DESIGNED** state and a Study in the **PAUSED** state. Semantically, however, a **PAUSED** Study indicates that it was **DEPLOYED** at some point in time and that data may have been collected for it.
- *status* (can be set to **DEPLOYED**)
- *deploymentList* (See Deployment Life-Cycle below)

### TERMINATED (Study)
When a Study is **TERMINATED**, all of its Deployments will automatically be **TERMINATED** as well, and no further updates can be made to the Study or its Deployments (except for changing whether or not they are *archived*).

## Deployment Life-Cycle

### CREATED (Deployment)
A new Deployment initially has a status of **CREATED**. While a Deployment is **CREATED**, updates to the design of the Deployment can be made, which includes updating the following attributes:
- *name*
- *description*
- *status* (can be set to **DESIGNED**)
- *goalSampleSize*
- *facility* (equipmentList of the parent Study must be a subset of the equipmentList of the chosen Facility)

### DESIGNED (Deployment)
Once the user is satisfied with the design of the Deployment, the user must set the status to **DESIGNED**. While a Deployment is **DESIGNED**, updates to the following attributes can be made:
- *status* (can be set to **DEPLOYED**)

### DEPLOYED (Deployment)
When a Deployment is **DEPLOYED**, data can be collected for it provided that its parent Study is also **DEPLOYED**.
- *status* (can be set to **PAUSED**)
- *currentSampleSize*

### PAUSED (Deployment)
When a Deployment is **PAUSED**, data collection is halted. A Deployment will automatically become **PAUSED** if its *currentSampleSize* equals its *goalSampleSize*. Functionally, there is no difference between a Deployment in the **DESIGNED** state and a Deployment in the **PAUSED** state. Semantically, however, a **PAUSED** Deployment indicates that it was **DEPLOYED** at some point in time and that data may have been collected for it.
- *status* (can be set to **DEPLOYED**)

### TERMINATED (Deployment)
When a Deployment is **TERMINATED**, no further updates can be made to it (except for changing whether or not it is *archived*).
