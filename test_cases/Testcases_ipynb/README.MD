# Testdescriptions

In this section you will find a summary of all current implemented tests. 
## Testcase 01: Get acceleration data and check time stamps
The target of this test is to verify that sending invalid configuration parameters to the tag does not harm the system. <br>
The invalid parameters should be handled correctly and give correct feedback to the user. <br>

**Expected Results**
1. Invalid Parameters are not accepted and tagged with an Error message.
2. Error messages indicates which parameter is invalid.
3. The invalid parameter should not be applied – instead the last configured parameter for this configuration should still be set.

## Testcase 02: Set configuration with valid parameters
The target of this test is to verify that sending valid configuration parameters to the tag does not cause any errors to the system. <br>

**Expected Results**
1. valid Parameters are accepted without any errors.
2. The configuration can be verified via get config.
3. All parameters which are not changed, must remain untouched.

**Valid parameters for configuration are**
| Parameters / Values |   |    |    |    |     |     |     |
|---------------------|---|----|----|----|-----|-----|-----|
| Samplerate          | 1 | 10 | 25 | 50 | 100 | 200 | 400 |
| Resolution          | 8 | 10 | 12 |    |     |     |     |
| Scale               | 2 | 4  | 8  | 16 |     |     |     |



## Testcase 03: Set configuration in loop with all valid parameters

The target of this test is similar to Testcase 02 with the differences that all valid configurations are tested in a loop. <br>

**Expected Results**
1. All valid Parameters are accepted without any errors.
2. All configuration can be verified via get config.
3. All parameters which are not changed, must remain untouched.

**Valid parameters for configuration are**
| Parameters / Values |   |    |    |    |     |     |     |
|---------------------|---|----|----|----|-----|-----|-----|
| Samplerate          | 1 | 10 | 25 | 50 | 100 | 200 | 400 |
| Resolution          | 8 | 10 | 12 |    |     |     |     |
| Scale               | 2 | 4  | 8  | 16 |     |     |     |


## Testcase 04: Set configuration with invalid parameters

The target of this test is to verify that invalid configurations parameters are not set and handled correctly. <br>

**Expected Results**
1. All valid Parameters are accepted without any errors.
2. All invalid Parameters are highlighted with a correct error message.
2. All configuration can be verified via get config.


## Testcase 05: Verify flash statistics are collectable

The target of this test is to verify that the function get_flash_statistics() collects all statistics correctly.


## Testcase 06: Change logging state

The target of this test is to verify that changing the logging state is working as expected.

**Expected Results**
1. Logging State activated - logs are available.
2. Logging State deactivated - no logs are available.
2. Changing the Logging state gives correct feedback on application.

## Testcase M01: Hard reset tag

The target of this test is to verify that a hard reset of the tag resets all flash statistics and the time. <br>

**Expected Results**
1. node pages are free.
2. Time is reseted to 1/1/1970.

## Testcase M02: Set time and recheck after long time
The target of this test is to verify that the time on the Tag is running parallel to the gateway time in a set time.

## Testcase M03: Get acceleration data and drop connection
The target of this test is to verify that when the connection to the Tag is lost, the test is interrupted correctly.
