#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

/*-----------------------------------------------------------
 * Application specific definitions.
 *
 * These definitions should be adjusted for your particular hardware and
 * application requirements.
 *
 * THESE PARAMETERS ARE DESCRIBED WITHIN THE 'CONFIGURATION' SECTION OF THE
 * FreeRTOS API DOCUMENTATION AVAILABLE ON THE FreeRTOS.org WEB SITE.  See
 * http://www.freertos.org/a00110.html
 *----------------------------------------------------------*/

#define configUSE_PREEMPTION					1
#define configUSE_PORT_OPTIMISED_TASK_SELECTION	0
#define configCPU_CLOCK_HZ                      1500000000
#define configTICK_RATE_HZ						( 2) /* In this non-real time simulated environment the tick frequency has to be at least a multiple of the Win32 tick frequency, and therefore very slow. */
#define configMINIMAL_STACK_SIZE				( ( unsigned short ) 70 ) /* In this simulated case, the stack only has to hold one small structure as the real stack is part of the win32 thread. */
#define configMAX_TASK_NAME_LEN					( 12 )
#define configUSE_16_BIT_TICKS					0
#define configIDLE_SHOULD_YIELD					0
#define configUSE_MUTEXES						1
#define configUSE_RECURSIVE_MUTEXES				1
#define configQUEUE_REGISTRY_SIZE				20
#define configUSE_APPLICATION_TASK_TAG			1
#define configUSE_COUNTING_SEMAPHORES			1
#define configUSE_ALTERNATIVE_API				0
#define configUSE_QUEUE_SETS					1
#define configUSE_TASK_NOTIFICATIONS			1


#define configMAX_PRIORITIES					( 7 )

/* Memory allocation related definitions. */
#define configSUPPORT_STATIC_ALLOCATION			0
#define configTOTAL_HEAP_SIZE					( ( size_t ) ( 65 * 1024 ) )

/* Hook function related definitions. */
#define configUSE_IDLE_HOOK                     0
#define configUSE_TICK_HOOK                     0
#define configCHECK_FOR_STACK_OVERFLOW          0
#define configUSE_MALLOC_FAILED_HOOK            0
#define configUSE_DAEMON_TASK_STARTUP_HOOK      0

/* Run time and task stats gathering related definitions. */
#define configGENERATE_RUN_TIME_STATS			0
#define configUSE_TRACE_FACILITY				0
#define configUSE_STATS_FORMATTING_FUNCTIONS	0

/* Co-routine related configuration options. */
#define configUSE_CO_ROUTINES 					0
#define configMAX_CO_ROUTINE_PRIORITIES			( 2 )

/* Software timer related definitions. */
/* The maximum possible task priority is configMAX_PRIORITIES - 1.
The priority of the timer task is deliberately set higher to ensure
it is correctly capped back to configMAX_PRIORITIES - 1. */
#define configUSE_TIMERS						1
#define configTIMER_TASK_PRIORITY				( configMAX_PRIORITIES - 1 )
#define configTIMER_QUEUE_LENGTH				20
#define configTIMER_TASK_STACK_DEPTH			( configMINIMAL_STACK_SIZE * 2 )

/* Define to trap errors during development. */
//#define configASSERT( x ) if( ( x ) == 0 ) vAssertCalled( __FILE__, __LINE__ )
extern void vAssertCalled( const char * const pcFileName,  unsigned long ulLine );

/* Enables the test whereby a stack larger than the total heap size is
requested. */
//#define configSTACK_DEPTH_TYPE uint32_t

/* Set the following definitions to 1 to include the API function, or zero
to exclude the API function.  In most cases the linker will remove unused
functions anyway. */
#define INCLUDE_vTaskPrioritySet				1
#define INCLUDE_uxTaskPriorityGet				1
#define INCLUDE_vTaskDelete						1
#define INCLUDE_vTaskCleanUpResources			0
#define INCLUDE_vTaskSuspend					1
#define INCLUDE_vTaskDelayUntil					1
#define INCLUDE_vTaskDelay						1
#define INCLUDE_uxTaskGetStackHighWaterMark		1
#define INCLUDE_uxTaskGetStackHighWaterMark2	1
#define INCLUDE_xTaskGetSchedulerState			1
#define INCLUDE_xTimerGetTimerDaemonTaskHandle	1
#define INCLUDE_xTaskGetIdleTaskHandle			1
#define INCLUDE_xTaskGetHandle					1
#define INCLUDE_eTaskGetState					1
#define INCLUDE_xSemaphoreGetMutexHolder		1
#define INCLUDE_xTimerPendFunctionCall			1
#define INCLUDE_xTaskAbortDelay					1

#endif /* FREERTOS_CONFIG_H */
