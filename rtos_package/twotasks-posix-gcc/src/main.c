/* Standard includes. */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <stdarg.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
#include <string.h>
#include <getopt.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <sys/time.h>
#include <time.h>

/* FreeRTOS kernel includes. */
#include "FreeRTOS.h"
#include "task.h"

/* Spidev includes. */
#include <linux/types.h>
#include <linux/spi/spidev.h>

/*GPIO includes*/
//#include <wiringPi.h>
                                                                                                                                                                     
/* Constant definitions. */
#define MAX_SPI_BUFSIZ 8192
#define LOOPS 10000
#define SPEED 16000000
#define BYTES 3

#define SEC_TO_NS(sec) ((sec)*1000000000)

/* Function declarations */
void vTask1(void *pvParameters);
void vTask2(void *pvParameters);
int spiOpen(unsigned spiChan, unsigned spiBaud, unsigned spiFlags);
int spiClose(int fd);
int spiXfer(int fd, unsigned speed, char *txBuf, char *rxBuf, unsigned count);
void write32(unsigned long int val);
void stimSetup();


/* Opens a spi device, returns positive integer if successful, negative errror code otherwise*/
int spiOpen(unsigned spiChan, unsigned spiBaud, unsigned spiFlags){
    int i, fd;
    char spiMode;
    char spiBits =8;
    char dev[32];

    spiMode = spiFlags & 3;
    spiBits = 8;

    if ((fd= open("/dev/spidev0.0", O_RDWR))<0){
        return -1;
    }

    if (ioctl(fd, SPI_IOC_WR_MODE, &spiMode)<0){
        close(fd);
        return -2;
    }
    if (ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &spiBits)<0){
        close(fd);
        return -3;
    }
    if(ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &spiBaud)<0){
        close(fd);
        return -4;
    }
    return fd;

}

/*Closes the spi device, returns are same as spiOpen*/
int spiClose(int fd){
    return close(fd);
}

/*Given a buffer of size "count" bytes, transfers via spi, miso results are put into txbuf*/
int spiXfer(int fd, unsigned speed, char *txBuf, char *rxBuf, unsigned count){
    int err;
    struct spi_ioc_transfer spi;

    memset(&spi, 0, sizeof(spi));

    spi.tx_buf = (unsigned long)txBuf;
    spi.rx_buf = (unsigned long)rxBuf;
    spi.len = count;
    spi.speed_hz = speed;
    spi.delay_usecs = 0;
    spi.bits_per_word = 8;
    spi.cs_change = 0;

    err = ioctl(fd, SPI_IOC_MESSAGE(1), &spi);

    return err;
}

/* Constants for spi portion*/
int bytes = BYTES;
int speed = SPEED;
int loops = LOOPS;
int fd;
char RXBuf[4] = {1,2,3,4};
char TXBuf[4] = {1,2,3,4};
uint64_t starttime;
uint64_t endtime;
uint64_t arr[10000];

/*Creates RTOS tasks, initializes spi, schedules the RTOS tasks*/
int main(int argc, char * argv[])
{

    
    fd = spiOpen(0, speed, 0);
    if (fd<0) return 1;
    
    stimSetup();
    write32(0xa06080ff); //Setting the electrode magnitudes
    write32(0xa04080ff);


    xTaskCreate(&vTask1, "Task 1", 1024, NULL, (6|portPRIVILEGE_BIT), NULL);

    vTaskStartScheduler();

    return 0;
}

/*Task 1 continuously sends spi commands across spidev0.0 connection*/
void vTask1(void *pvParameters)
{

    for (;;)
    {
        /*
        struct timespec ts;
        starttime = endtime;
        clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
        endtime = SEC_TO_NS((uint64_t)ts.tv_sec) + (uint64_t)ts.tv_nsec;
        arr[i] = (endtime-starttime);
        printf("%ld\n", arr[i]);
       */
       write24(code);
       write24(code);

    }
}

/*void write32(unsigned long int val){
    char a = (val&0xff);
    char b = (val>>8)&0xff;
    char c = (val>>16) &0xff;
    char d = (val>>24) & 0xff;
    char buf[4] = {d,c,b,a};
    spiXfer(fd, speed, buf, buf, bytes);
}
*/

void write24(unsigned long int val){
    char a = (val&0xff);
    char b = (val>>8)&0xff;
    char c = (val>>16) &0xff;
    char buf[3] = {c,b,a};
    spiXfer(fd, speed, buf, buf, bytes);
}

void stimSetup(){
    write24(0x006300);
}
